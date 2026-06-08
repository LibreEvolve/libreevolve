"""Core evolution loop: prompt construction, LLM-driven mutation, evaluation.

Inspired by AlphaEvolve's evolutionary loop and adjacent code-evolution systems.
This synchronous loop is intentionally smaller than the paper systems.
"""
from __future__ import annotations
from collections.abc import Callable, Mapping
import copy
import hashlib
import inspect
import json
import math
import random
import re
import stat as stat_module
import unicodedata
from pathlib import Path
from libreevolve.core.best_artifacts import (
    attach_best_artifact_export,
    export_best_artifacts,
)
from libreevolve.core.budget import (
    apply_controller_budget_event,
    BudgetSnapshotError,
    CONTROLLER_BUDGET_STATE_SCHEMA,
    RunBudget,
    validate_controller_budget_replay_state,
    validate_controller_budget_state,
    validate_restored_budget_snapshot,
)
from libreevolve.core.config import Config
from libreevolve.core.candidate import (
    CandidateWorkspace,
    apply_workspace_mutation,
    extract_evolve_blocks,
    validate_evolve_blocks,
    validate_candidate_workspace_limits,
)
from libreevolve.core.database import (
    ProgramDatabase,
    archive_event_replay_audit,
    load_archive_restore_bundle,
    validate_archive_event_replay_audit,
    validate_candidate_language_policy,
    validate_seed_source_record,
)
from libreevolve.core.diff import (
    extract_proposal_metadata,
    strip_proposal_metadata,
    validate_proposal_metadata_preamble,
)
from libreevolve.core.evaluator import (
    CascadeEvaluator,
    evaluation_accounting,
    preflight_evaluator_contracts,
)
from libreevolve.core.feedback import apply_llm_feedback, build_critique_prompt
from libreevolve.core.jsonl import (
    StrictJsonlError,
    iter_strict_jsonl_objects,
    load_strict_json_object,
)
from libreevolve.core.meta_prompt import PromptDatabase, parse_prompt_mutation_response
from libreevolve.core.prompt import (
    PromptSampler,
    PromptTemplateError,
    prompt_context_policy_sha256,
    prompt_template_fields,
    validate_direct_context_files,
    validate_direct_task_description,
    validate_prompt_context_policy,
)
from libreevolve.core.provenance import (
    git_state,
    plugin_identity_record,
    plugin_provenance,
    problem_provenance,
    runtime_environment_provenance,
    source_provenance,
)
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.llm.ensemble import (
    LLM_PROVIDER_DIAGNOSTICS_SCHEMA,
    LLMEnsemble,
    build_llm,
    validate_scheduler_state_snapshot,
)
from libreevolve.llm.cancellation_policy import (
    PROVIDER_CANCELLATION_POLICY_SCHEMA,
    validate_provider_cancellation_policy,
)
from libreevolve.llm.budget_report import (
    LLM_BUDGET_REPORT_POLICY,
    LLM_BUDGET_REPORT_SCHEMA,
    LLM_BUDGET_REPORT_STATUS,
    validate_llm_budget_report,
)
from libreevolve.llm.tokenization import discover_prompt_token_counter
from libreevolve.plugins.base import PluginBase
from libreevolve.plugins.registry import (
    configured_plugin_labels,
    load_plugins as load_config_plugins,
    plugin_entry_point_spec,
)
from libreevolve.population.program import (
    Program,
    validate_program_metadata,
    validate_program_metrics,
)
from libreevolve.problems.loader import Problem

VALID_THRESHOLD = 0.0
CONTROLLER_STATE_ARTIFACT_INVENTORY_SCHEMA = (
    "libreevolve.controller_state_artifact_inventory.v1"
)
CONTROLLER_STATE_VALIDATION_SCHEMA = "libreevolve.controller_state_validation.v1"
PROMPT_SECTION_PACKING_COVERAGE_SCHEMA = (
    "libreevolve.prompt_section_packing_coverage.v1"
)
PROMPT_SECTION_PACKING_COVERAGE_VALIDATION_SCHEMA = (
    "libreevolve.prompt_section_packing_coverage_validation.v1"
)
PROMPT_CONTEXT_POLICY_COVERAGE_SCHEMA = (
    "libreevolve.prompt_context_policy_coverage.v1"
)
PROMPT_CONTEXT_POLICY_COVERAGE_VALIDATION_SCHEMA = (
    "libreevolve.prompt_context_policy_coverage_validation.v1"
)
RETRIEVAL_EVIDENCE_COVERAGE_SCHEMA = (
    "libreevolve.retrieval_evidence_coverage.v1"
)
RETRIEVAL_EVIDENCE_COVERAGE_VALIDATION_SCHEMA = (
    "libreevolve.retrieval_evidence_coverage_validation.v1"
)
_MAX_PLUGIN_METADATA_KEY_CHARS = 160
_MAX_PLUGIN_METADATA_STRING_CHARS = 4096
_MAX_PLUGIN_METADATA_DEPTH = 20
_MAX_PLUGIN_METADATA_ITEMS = 1000
_MAX_PLUGIN_METADATA_JSON_CHARS = 100_000
_MAX_PLUGIN_CONTEXT_CHARS = 4000
_MAX_META_PROMPT_CONTEXT_CHARS = 6000
_MAX_META_PROMPT_RETAINED_EVIDENCE_CHARS = 1000
_MAX_META_PROMPT_TEMPLATE_CHARS = 1200
_MAX_META_PROMPT_KEY_CHARS = 160
_MAX_META_PROMPT_TEXT_FIELD_CHARS = 500
_MAX_ABORT_MESSAGE_CHARS = 2048
_MAX_ARTIFACT_ERROR_CHARS = 500
_MAX_PLUGIN_SIDE_EFFECT_ERROR_CHARS = 500
_MAX_DIRECT_INLINE_SEED_CHARS = 1_000_000
_MAX_CRITIQUE_RETAINED_PROMPT_CHARS = 6000
_MAX_CRITIQUE_RETAINED_MUTATION_CHARS = 4000
META_PROMPT_CONTEXT_POLICY_CAPABILITIES_SCHEMA = (
    "libreevolve.meta_prompt_context_policy_capabilities.v1"
)
_META_PROMPT_CONTEXT_POLICY_CAPABILITY_SECTIONS = (
    "channel_controls",
    "feedback_selection",
    "sampling_and_context",
)
_META_PROMPT_CONTEXT_POLICY_CAPABILITIES = {
    "schema": META_PROMPT_CONTEXT_POLICY_CAPABILITIES_SCHEMA,
    "channel_controls": (
        "disabled_sections,section_priorities,mutation_instruction_variant,"
        "mutation_instruction_include_example,proposal_metadata_enabled,"
        "parent_metric_names,parent_metrics_max_chars_by_name,"
        "parent_code_paths,parent_code_required_terms,parent_code_excluded_terms,"
        "parent_code_ranking_terms,parent_code_order_policy,parent_code_limit,"
        "parent_code_max_chars_by_path,parent_code_max_chars,parent_code_truncation"
    ),
    "feedback_selection": (
        "feedback_sections,feedback_section_order,feedback_section_max_chars_by_name,"
        "llm_feedback_fields,llm_feedback_max_chars_by_field,"
        "proposal_fields,proposal_max_chars_by_field,stage_summary_fields,"
        "stage_summary_max_chars_by_field,"
        "execution_output_fields,execution_output_max_chars_by_field,"
        "sample_retry_fields,sample_retry_max_chars_by_field,"
        "program_output_fields,program_output_max_chars_by_field,"
        "validator_artifact_fields,validator_artifact_max_chars_by_field,"
        "validator_artifact_content_fields,"
        "validator_artifact_content_mode,validator_artifact_content_max_bytes,"
        "validator_artifact_content_max_chars,validator_skipped_artifact_fields,"
        "validator_skipped_artifact_max_chars_by_field,"
        "validator_diagnostic_groups,validator_metadata_keys,"
        "validator_metadata_limit,"
        "validator_metadata_max_chars_by_key,evaluator_path_fields,"
        "evaluator_path_max_chars_by_field,evaluator_dependency_fields,"
        "evaluator_dependency_max_chars_by_field,evaluator_stage_fields,"
        "evaluator_stage_max_chars_by_field,evaluator_workspace_fields,"
        "evaluator_workspace_max_chars_by_field,syntax_error_fields,"
        "syntax_error_max_chars_by_field,"
        "metric_bound_fields,metric_bound_max_chars_by_field,"
        "configured_stage_check_fields,configured_stage_check_max_chars_by_field,"
        "stage_metric_threshold_fields,stage_metric_threshold_max_chars_by_field,"
        "artifact_output_check_fields,artifact_output_check_max_chars_by_field,"
        "malformed_metric_fields,malformed_metric_max_chars_by_field,"
        "materialization_error_fields,materialization_error_max_chars_by_field,"
        "metric_aggregation_fields,metric_aggregation_max_chars_by_field,"
        "synthetic_metric_fields,synthetic_metric_max_chars_by_field,"
        "execution_diagnostic_groups,validator_boundary_fields,"
        "validator_boundary_max_chars_by_field,"
        "validator_budget_fields,validator_budget_max_chars_by_field,"
        "validator_env_fields,validator_env_max_chars_by_field,"
        "validator_resource_limit_fields,"
        "validator_resource_limit_max_chars_by_field,validator_stdin_fields,"
        "validator_stdin_max_chars_by_field,"
        "diagnostic_output_fields,diagnostic_output_max_chars_by_field,"
        "timeout_cleanup_fields,timeout_cleanup_max_chars_by_field"
    ),
    "sampling_and_context": (
        "prompt_format_weights,context_source_paths,context_source_max_chars,"
        "context_source_required_terms,context_source_excluded_terms,"
        "context_source_ranking_terms,"
        "context_source_limit,context_source_truncation,"
        "context_source_order_policy,"
        "recent_failure_limit,recent_failure_selection_policy,"
        "recent_failure_required_errors,recent_failure_excluded_errors,"
        "recent_failure_required_changed_files,"
        "recent_failure_excluded_changed_files,"
        "recent_failure_required_stage_names,"
        "recent_failure_excluded_stage_names,"
        "recent_failure_required_terms,recent_failure_excluded_terms,"
        "recent_failure_repetition_threshold,recent_failure_score_threshold,"
        "recent_failure_max_chars_by_field,"
        "inspiration_limit,"
        "inspiration_strategy,inspiration_required_metric,inspiration_excluded_metrics,"
        "inspiration_fitness_threshold,"
        "inspiration_metric_thresholds,inspiration_metric_ranking,"
        "inspiration_sample_count,extra_context_max_chars,"
        "plugin_context_enabled,plugin_context_allowlist,"
        "plugin_context_excluded_labels,plugin_context_order,plugin_context_required_terms,"
        "plugin_context_excluded_terms,plugin_context_ranking_terms,plugin_context_limit,"
        "plugin_context_max_chars,plugin_context_truncation,"
        "plugin_context_max_chars_by_label"
    ),
}
_META_PROMPT_CONTEXT_POLICY_CAPABILITY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_PLUGIN_FAILURE_ATTR = "_libreevolve_plugin_failure"
_PLUGIN_ARTIFACT_FAILURE_ATTR = "_libreevolve_plugin_artifact_failure"
_RNG_RESUME_STATUS_LEGACY_NOT_WIRED = "snapshot_persisted_restore_not_wired_into_evolve"
_RNG_RESUME_STATUS_RESTORE_SUPPORTED = "snapshot_persisted_restore_supported"
_RNG_RESUME_STATUS_RESTORED = "snapshot_restored_into_evolve"
_RNG_RESUME_STATUSES = {
    _RNG_RESUME_STATUS_LEGACY_NOT_WIRED,
    _RNG_RESUME_STATUS_RESTORE_SUPPORTED,
    _RNG_RESUME_STATUS_RESTORED,
}
_LLM_SCHEDULER_RESUME_STATUS_LEGACY_NOT_WIRED = (
    "snapshot_persisted_restore_not_wired_into_evolve"
)
_LLM_SCHEDULER_RESUME_STATUS_RESTORE_SUPPORTED = (
    "snapshot_persisted_restore_supported"
)
_LLM_SCHEDULER_RESUME_STATUS_RESTORED = "snapshot_restored_into_evolve"
_LLM_SCHEDULER_RESUME_STATUSES = {
    _LLM_SCHEDULER_RESUME_STATUS_LEGACY_NOT_WIRED,
    _LLM_SCHEDULER_RESUME_STATUS_RESTORE_SUPPORTED,
    _LLM_SCHEDULER_RESUME_STATUS_RESTORED,
}
_RNG_REPLAY_BOUNDARY_SCHEMA = "libreevolve.runtime_rng_replay_boundary.v1"
_LINEAGE_REPLAY_POLICY_SCHEMA = "libreevolve.lineage_replay_policy.v1"
_FULL_RESUME_BUNDLE_SCHEMA = "libreevolve.full_resume_bundle.v1"
FULL_RESUME_BUNDLE_VALIDATION_SCHEMA = "libreevolve.full_resume_bundle_validation.v1"
_FULL_RESUME_UNSUPPORTED_SURFACES = (
    "provider_outputs",
    "controller_pending_work",
    "plugin_internal_state",
    "validator_subprocess_state",
    "ordered_migration_event_replay",
)
_RNG_REPLAY_OWNED_SURFACES = [
    "loop_parent_explore_exploit_choice",
    "prompt_template_sampling",
    "program_database_sampling",
    "island_sampling",
    "map_elites_sampling",
]
_RNG_REPLAY_EXTERNAL_SURFACES = [
    {
        "surface": "llm_provider_outputs",
        "restored_by_runtime_rng": False,
        "boundary": "remote_or_sdk_provider_nondeterminism",
    },
    {
        "surface": "plugin_internal_randomness",
        "restored_by_runtime_rng": False,
        "boundary": "plugins_do_not_receive_runtime_rng_automatically",
    },
    {
        "surface": "validator_subprocess_randomness",
        "restored_by_runtime_rng": False,
        "boundary": "stage_rng_seeds_are_recorded_per_evaluation",
    },
]


class RuntimeRngStateError(ValueError):
    """Raised when runtime RNG state cannot be validated for restore."""


class RuntimeLLMSchedulerStateError(ValueError):
    """Raised when runtime LLM scheduler state cannot be validated for restore."""


class RuntimeBudgetStateError(ValueError):
    """Raised when runtime budget state cannot be validated for restore."""


class RuntimeLineageReplayPolicyError(ValueError):
    """Raised when runtime lineage replay policy cannot be validated."""


class RuntimeFullResumeBundleError(ValueError):
    """Raised when a composed runtime resume bundle cannot be validated."""


def build_prompt(parent: Program, inspirations: list[Program],
                 problem: Problem, extra_context: str,
                 recent_failures: list[dict | tuple[str, float]] | None = None,
                 mutation_mode: str = "diff") -> str:
    return PromptSampler().build(
        parent, inspirations, problem, extra_context,
        recent_failures=recent_failures,
        mutation_mode=mutation_mode,
    )


def _preflight_llm_backends_for_evolve(problem: Problem, config: Config):
    if not _mutation_llm_can_run(problem, config):
        return None
    try:
        return build_llm(config)
    except Exception as exc:
        raise ValueError(f"LLM backend preflight failed: {exc}") from exc


def _mutation_llm_can_run(problem: Problem, config: Config) -> bool:
    if config.max_generations <= 0:
        return False
    if config.max_llm_calls is not None and config.max_llm_calls <= 0:
        return False
    if (
        config.max_llm_provider_attempts is not None
        and config.max_llm_provider_attempts <= 0
    ):
        return False
    if config.max_llm_tokens is not None and config.max_llm_tokens <= 0:
        return False
    if (
        config.max_llm_cost_microusd is not None
        and config.max_llm_cost_microusd <= 0
    ):
        return False
    if config.max_llm_seconds is not None and config.max_llm_seconds <= 0:
        return False
    if config.llm_role_provider_attempt_limits.get("mutation") == 0:
        return False
    if config.llm_role_token_limits.get("mutation") == 0:
        return False
    if config.llm_role_cost_microusd_limits.get("mutation") == 0:
        return False
    if config.llm_role_seconds_limits.get("mutation") == 0:
        return False
    seed_count = len(problem.initial_workspaces or problem.initial_programs)
    if config.max_evaluations is not None and config.max_evaluations <= seed_count:
        return False
    return True


def _initial_run_rng(
    config: Config,
    runtime_rng_state_snapshot: Mapping[str, object] | None,
) -> tuple[random.Random, str]:
    if runtime_rng_state_snapshot is None:
        return random.Random(config.seed), _RNG_RESUME_STATUS_RESTORE_SUPPORTED
    snapshot = validate_runtime_rng_state_snapshot(runtime_rng_state_snapshot)
    if snapshot["seed"] != config.seed:
        raise ValueError("runtime RNG snapshot seed must match Config.seed")
    return (
        restore_runtime_rng_state_snapshot(snapshot),
        _RNG_RESUME_STATUS_RESTORED,
    )


def _initial_run_budget(
    config: Config,
    runtime_budget_state_snapshot: Mapping[str, object] | None,
) -> RunBudget:
    if runtime_budget_state_snapshot is None:
        return RunBudget.from_config(config)
    try:
        return RunBudget.from_restored_snapshot(config, runtime_budget_state_snapshot)
    except BudgetSnapshotError as exc:
        raise RuntimeBudgetStateError(str(exc)) from exc


def _attach_llm_call_logger(llm: object, db: ProgramDatabase) -> None:
    setter = getattr(llm, "set_call_record_sink", None)
    if callable(setter):
        setter(db.log_llm_call)


def _critique_metadata_record(
    *,
    prompt: str,
    original_diff: str,
    revised_diff: object,
    backend_idx: int,
    llm_call: dict | None,
    critique_status: dict,
    retention_mode: str = "redacted",
) -> dict:
    prompt_payload = _retained_critique_text(
        prompt,
        max_chars=_MAX_CRITIQUE_RETAINED_PROMPT_CHARS,
        mode=retention_mode,
    )
    original_payload = _retained_critique_text(
        original_diff,
        max_chars=_MAX_CRITIQUE_RETAINED_MUTATION_CHARS,
        mode=retention_mode,
    )
    revised_payload = _retained_critique_text(
        revised_diff,
        max_chars=_MAX_CRITIQUE_RETAINED_MUTATION_CHARS,
        mode=retention_mode,
    )
    return {
        "prompt": prompt_payload["text"],
        "prompt_sha256": prompt_payload["sha256"],
        "prompt_chars": prompt_payload["chars"],
        "prompt_retained_chars": prompt_payload["retained_chars"],
        "prompt_truncated": prompt_payload["truncated"],
        "prompt_redacted": prompt_payload["redacted"],
        "original_diff": original_payload["text"],
        "original_diff_sha256": original_payload["sha256"],
        "original_diff_chars": original_payload["chars"],
        "original_diff_retained_chars": original_payload["retained_chars"],
        "original_diff_truncated": original_payload["truncated"],
        "original_diff_redacted": original_payload["redacted"],
        "revised_diff": revised_payload["text"],
        "revised_diff_sha256": revised_payload["sha256"],
        "revised_diff_chars": revised_payload["chars"],
        "revised_diff_retained_chars": revised_payload["retained_chars"],
        "revised_diff_truncated": revised_payload["truncated"],
        "revised_diff_redacted": revised_payload["redacted"],
        "retention_mode": retention_mode,
        "retention_policy": prompt_payload["retention_policy"],
        "backend_idx": backend_idx,
        "llm_call": llm_call,
        **critique_status,
    }


def _retained_critique_text(value: object, *, max_chars: int, mode: str = "redacted") -> dict:
    if isinstance(value, str):
        original = value
    else:
        original = repr(value)
    if mode == "off":
        return {
            "text": None,
            "sha256": None,
            "chars": None,
            "retained_chars": 0,
            "redacted": None,
            "truncated": False,
            "retention_policy": "off_no_text_or_hash",
        }
    raw_sha256 = hashlib.sha256(original.encode("utf-8", errors="replace")).hexdigest()
    if mode == "hash_only":
        return {
            "text": None,
            "sha256": raw_sha256,
            "chars": len(original),
            "retained_chars": 0,
            "redacted": None,
            "truncated": False,
            "retention_policy": "hash_only_with_raw_sha256",
        }
    redacted = redact_sensitive_text(original)
    truncated = mode != "full" and len(redacted) > max_chars
    if truncated:
        notice = f"\n[truncated {len(redacted) - max_chars} chars]"
        keep = max(0, max_chars - len(notice))
        text = redacted[:keep] + notice
    else:
        text = redacted
    return {
        "text": text,
        "sha256": raw_sha256,
        "chars": len(original),
        "retained_chars": len(text),
        "redacted": text != original,
        "truncated": truncated,
        "retention_policy": (
            "full_secret_redacted_text_with_raw_sha256"
            if mode == "full"
            else "redact_then_prefix_truncate_with_sha256"
        ),
    }


def _bounded_llm_failure_record(role: str, exc: Exception, llm) -> dict:
    message = _retained_critique_text(exc, max_chars=_MAX_ABORT_MESSAGE_CHARS)
    return {
        "status": "failed",
        "role": role,
        "error": f"llm_{role}_failed",
        "exception": exc.__class__.__name__,
        "message": message["text"],
        "message_sha256": message["sha256"],
        "message_chars": message["chars"],
        "message_retained_chars": message["retained_chars"],
        "message_truncated": message["truncated"],
        "message_retention_policy": "redact_then_prefix_truncate_with_sha256",
        "llm_call": _last_llm_call(llm),
    }


def _llm_failure_payload_text(failure: Mapping[str, object]) -> str:
    return json.dumps(
        failure,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _retained_prompt_text(value: str, *, mode: str = "redacted") -> dict:
    if mode == "full":
        text = redact_sensitive_text(value)
        return {
            "text": text,
            "sha256": hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest(),
            "chars": len(value),
            "stored_chars": len(text),
            "redacted": text != value,
            "truncated": False,
            "retention_mode": mode,
            "retention_policy": "full_text_with_secret_redaction_and_raw_sha256",
        }
    if mode == "hash_only":
        return {
            "text": None,
            "sha256": hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest(),
            "chars": len(value),
            "stored_chars": 0,
            "redacted": None,
            "truncated": False,
            "retention_mode": mode,
            "retention_policy": "hash_only_with_raw_sha256",
        }
    if mode == "off":
        return {
            "text": None,
            "sha256": None,
            "chars": None,
            "stored_chars": 0,
            "redacted": None,
            "truncated": False,
            "retention_mode": mode,
            "retention_policy": "off_no_prompt_or_hash",
        }
    redacted = redact_sensitive_text(value)
    return {
        "text": redacted,
        "sha256": hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest(),
        "chars": len(value),
        "stored_chars": len(redacted),
        "redacted": redacted != value,
        "truncated": False,
        "retention_mode": mode,
        "retention_policy": "redact_only_with_raw_sha256",
    }


def _apply_explicit_context_retention_to_prompt(
    retained_prompt: dict,
    *,
    context_text: str,
    mode: str,
) -> dict:
    raw_context_sha = (
        hashlib.sha256(context_text.encode("utf-8", errors="replace")).hexdigest()
        if context_text
        else None
    )
    context_retention = {
        "retention_mode": mode,
        "sha256": raw_context_sha,
        "chars": len(context_text) if context_text else 0,
        "stored_chars": 0,
        "redacted": None,
        "truncated": False,
        "replacement_count": 0,
        "retention_policy": "prompt_text_not_retained",
    }
    text = retained_prompt.get("text")
    if not isinstance(text, str) or not context_text:
        retained_prompt["explicit_context_retention"] = context_retention
        return retained_prompt
    redacted_context = redact_sensitive_text(context_text)
    if mode == "off":
        replacement = "[EXPLICIT_CONTEXT_OMITTED_BY_RETENTION_POLICY]"
        context_retention.update(
            {
                "sha256": None,
                "chars": None,
                "retention_policy": "off_no_context_or_hash",
            }
        )
    elif mode == "hash_only":
        replacement = "[EXPLICIT_CONTEXT_RETAINED_AS_HASH]"
        context_retention["retention_policy"] = "hash_only_with_raw_sha256"
    else:
        replacement = redacted_context
        context_retention.update(
            {
                "stored_chars": len(redacted_context),
                "redacted": redacted_context != context_text,
                "retention_policy": (
                    "full_secret_redacted_context_with_raw_sha256"
                    if mode == "full"
                    else "redact_context_only_with_raw_sha256"
                ),
            }
        )
    replacement_count = text.count(context_text)
    if replacement_count:
        text = text.replace(context_text, replacement)
    elif mode in {"hash_only", "off"} and redacted_context:
        replacement_count = text.count(redacted_context)
        if replacement_count:
            text = text.replace(redacted_context, replacement)
            context_retention["redacted"] = redacted_context != context_text
            context_retention["truncated"] = False
    if replacement_count:
        retained_prompt["text"] = text
        retained_prompt["stored_chars"] = len(text)
    context_retention["replacement_count"] = replacement_count
    if mode in {"hash_only", "off"} and replacement_count:
        context_retention["stored_chars"] = len(replacement) * replacement_count
    retained_prompt["explicit_context_retention"] = context_retention
    return retained_prompt


def _retained_plugin_context_text(
    *,
    plugin: PluginBase,
    index: int,
    original_text: str,
    prompt_context_text: str,
    prompt_context_truncated: bool,
    mode: str,
) -> dict:
    raw_rendered = (
        _render_plugin_context_section(index, plugin, original_text)
        if original_text
        else ""
    )
    raw_sha256 = (
        hashlib.sha256(raw_rendered.encode("utf-8", errors="replace")).hexdigest()
        if raw_rendered
        else None
    )
    if mode == "off":
        return {
            "text": None,
            "sha256": None,
            "chars": None,
            "stored_chars": 0,
            "redacted": None,
            "truncated": False,
            "retention_mode": mode,
            "retention_policy": "off_no_context_or_hash",
        }
    if mode == "hash_only":
        return {
            "text": None,
            "sha256": raw_sha256,
            "chars": len(raw_rendered) if raw_rendered else 0,
            "stored_chars": 0,
            "redacted": None,
            "truncated": False,
            "retention_mode": mode,
            "retention_policy": "hash_only_with_raw_sha256",
        }
    if mode == "full":
        text = (
            redact_sensitive_text(
                _render_plugin_context_section(
                    index,
                    plugin,
                    redact_sensitive_text(original_text),
                )
            )
            if original_text
            else ""
        )
        return {
            "text": text if text else None,
            "sha256": raw_sha256,
            "chars": len(raw_rendered) if raw_rendered else 0,
            "stored_chars": len(text),
            "redacted": text != raw_rendered if raw_rendered else False,
            "truncated": False,
            "retention_mode": mode,
            "retention_policy": "full_secret_redacted_text_with_raw_sha256",
        }
    return {
        "text": prompt_context_text if prompt_context_text else None,
        "sha256": raw_sha256,
        "chars": len(raw_rendered) if raw_rendered else 0,
        "stored_chars": len(prompt_context_text),
        "redacted": prompt_context_text != raw_rendered if raw_rendered else False,
        "truncated": prompt_context_truncated,
        "retention_mode": mode,
        "retention_policy": "redact_then_prefix_truncate_with_raw_sha256",
    }


def evolve(
    problem: Problem,
    config: Config,
    plugins: list[PluginBase] | None = None,
    *,
    runtime_rng_state_snapshot: Mapping[str, object] | None = None,
    runtime_llm_scheduler_state_snapshot: Mapping[str, object] | None = None,
    runtime_archive_state_snapshot: Mapping[str, object] | None = None,
    runtime_archive_programs_by_id: Mapping[str, Program] | None = None,
    runtime_budget_state_snapshot: Mapping[str, object] | None = None,
) -> "Program | None":
    config.validate()
    run_dir = (Path(config.log_dir) / config.problem_name).resolve(strict=False)
    core_resolved_config_plugins = False
    if plugins is None:
        plugins = load_config_plugins(config.plugins, run_dir=run_dir)
        core_resolved_config_plugins = bool(config.plugins)
    _validate_plugins_for_evolve(plugins, mutation_capable=config.max_generations > 0)
    _validate_problem_for_evolve(problem, config)
    run_rng, rng_resume_status = _initial_run_rng(config, runtime_rng_state_snapshot)
    budget = _initial_run_budget(config, runtime_budget_state_snapshot)
    evaluator_sources = preflight_evaluator_contracts(
        problem,
        config.eval_stages,
        validator_env_allowlist=config.validator_env_allowlist,
        validator_network_policy=config.validator_network_policy,
        evaluator_data_include=config.evaluator_data_include,
        evaluator_data_exclude=config.evaluator_data_exclude,
    )
    preflighted_llm = _preflight_llm_backends_for_evolve(problem, config)
    source_record = source_provenance()
    source_root = Path(__file__).resolve().parents[1]
    run_provenance = {
        "git": git_state(source_root),
        "source": source_record,
        "problem": problem_provenance(
            problem.problem_dir,
            generated_roots=[run_dir],
        ),
        "config": _problem_config_source(problem),
        "plugins": plugin_provenance(plugins),
        "environment": runtime_environment_provenance(),
    }
    dotenv_source = _problem_dotenv_source(problem)
    if dotenv_source is not None:
        run_provenance["dotenv"] = dotenv_source
    llm_scheduler_resume_status = _LLM_SCHEDULER_RESUME_STATUS_RESTORE_SUPPORTED
    if runtime_llm_scheduler_state_snapshot is not None:
        if preflighted_llm is None:
            raise ValueError(
                "runtime LLM scheduler snapshot restore requires a mutation-capable run"
            )
        _restore_llm_scheduler_state_snapshot(
            preflighted_llm,
            runtime_llm_scheduler_state_snapshot,
        )
        llm_scheduler_resume_status = _LLM_SCHEDULER_RESUME_STATUS_RESTORED
    db        = ProgramDatabase(
        config,
        perf_bounds=(0.0, 1.0),
        context_sources=problem.context_sources,
        context_policy=problem.context_policy,
        objective_schema=problem.objective_schema(),
        evaluator_sources=evaluator_sources,
        run_provenance=run_provenance,
        seed_sources=_problem_seed_sources(problem),
        seed_skipped=_problem_seed_skipped(problem),
        seed_policy=_problem_seed_policy(problem),
        retrieval_query_context=_problem_retrieval_query_context(problem),
        archive_state_snapshot=runtime_archive_state_snapshot,
        archive_programs_by_id=runtime_archive_programs_by_id,
        rng=run_rng,
    )
    if preflighted_llm is not None:
        _attach_llm_call_logger(preflighted_llm, db)
    best: Program | None = None
    llm = preflighted_llm
    phase = "initializing_evaluator"

    try:
        evaluator = CascadeEvaluator(
            problem,
            timeout_sec=config.eval_timeout_sec,
            stages=config.eval_stages,
            validator_env_allowlist=config.validator_env_allowlist,
            artifact_dir=run_dir / "evaluator_artifacts",
            artifact_include=config.evaluator_artifact_include,
            artifact_exclude=config.evaluator_artifact_exclude,
            artifact_max_files=config.evaluator_artifact_max_files,
            artifact_max_bytes=config.evaluator_artifact_max_bytes,
            artifact_redact_secrets=config.evaluator_artifact_redact_secrets,
            data_include=config.evaluator_data_include,
            data_exclude=config.evaluator_data_exclude,
            output_max_chars=config.evaluator_output_max_chars,
            stdin_text=config.evaluator_stdin_text,
            stdin_file=config.evaluator_stdin_file,
            validator_network_policy=config.validator_network_policy,
        )
        prompt_token_counter, prompt_token_counter_capability = (
            discover_prompt_token_counter(
                config.backends,
                role="mutation",
                role_backend_indices=config.llm_role_backend_indices,
            )
        )
        prompt_sampler = PromptSampler(
            config.prompt_variants,
            run_rng,
            max_prompt_chars=config.prompt_max_chars,
            max_prompt_estimated_tokens=config.prompt_max_estimated_tokens,
            artifact_base_dir=run_dir,
            artifact_content_mode=config.prompt_artifact_content_mode,
            artifact_content_max_bytes=config.prompt_artifact_content_max_bytes,
            artifact_content_max_chars=config.prompt_artifact_content_max_chars,
            prompt_format_options=config.prompt_format_options,
            prompt_variant_semantic_policy=config.prompt_variant_semantic_policy,
            prompt_token_counter=prompt_token_counter,
            prompt_token_counter_name=(
                prompt_token_counter_capability.get("counter_name") or "provider"
            ),
        )
        phase = "initializing_prompt_database"
        prompt_db = PromptDatabase(
            run_dir,
            templates=config.prompt_variants or None,
            reward_bounds=(float(config.prompt_reward_bounds[0]), float(config.prompt_reward_bounds[1])),
            explore_coeff=config.prompt_explore_coeff,
            reward_mode=config.prompt_reward_mode,
            seed_semantic_policy=config.prompt_variant_semantic_policy,
            quarantine_snapshot_retention_mode=config.quarantine_snapshot_retention_mode,
        )

        recent_failures: list[dict] = []
        _MAX_FAILURES = 5

        # Seed population (diff_error=None bypasses Tier 0)
        seed_entries = _seed_workspace_entries(problem)
        for seed_index, (seed_workspace, seed_source) in enumerate(seed_entries):
            phase = "seed_evaluation"
            if budget.check_before_evaluation():
                break
            result = evaluator.evaluate(seed_workspace, diff_error=None)
            result_accounting = evaluation_accounting(result)
            budget.record_evaluation(
                result.elapsed_sec,
                seed=True,
                accounting=result_accounting,
            )
            db.log_controller_budget_event(
                {
                    "kind": "seed_evaluation",
                    "elapsed_sec": result.elapsed_sec,
                    "accounting": result_accounting,
                }
            )
            budget.check_before_evaluation()
            program = Program(
                id=_deterministic_seed_candidate_id(seed_index, seed_workspace),
                code=seed_workspace.code,
                files=dict(seed_workspace.files),
                primary_file=seed_workspace.primary_file,
                allowed_reserved_paths=seed_workspace.allowed_reserved_paths,
                static_files=seed_workspace.static_files,
                fitness=result.fitness,
                metrics=result.metrics,
                evaluation=result.to_dict(),
                metadata={
                    "candidate_type": "seed",
                    **seed_source,
                    "post_processing": _seed_post_processing_policy(),
                    "budget": budget.snapshot(),
                },
            )
            _annotate_metric_policy(program, problem)
            admission = db.admit(program, threshold=VALID_THRESHOLD)
            if not admission.get("admitted"):
                failure = db.log_seed_failure(program, admission)
                recent_failures.append(failure)
                recent_failures = recent_failures[-_MAX_FAILURES:]
            db.log(program)

        proposal_count = config.proposals_per_generation
        for proposal_loop_index in range(config.max_generations * proposal_count):
            gen = proposal_loop_index // proposal_count
            proposal_index = proposal_loop_index % proposal_count
            candidate_generation = gen + 1
            phase = f"generation:{gen}:budget_check"
            if proposal_index == 0 and budget.check_before_generation():
                break
            if budget.check_before_evaluation():
                break
            if budget.check_before_llm_call(role="mutation"):
                break
            phase = f"generation:{gen}:parent_selection"
            if config.parent_selection_strategy == "mixed":
                strategy = "explore" if run_rng.random() < config.explore_ratio else "exploit"
            else:
                strategy = config.parent_selection_strategy
            parent = db.sample(strategy=strategy)
            if parent is None:
                budget.stop_reason = "no_valid_programs" if db.best() is None else "no_parent"
                break
            parent_selection_metadata = db.last_sample_metadata()

            if proposal_index == 0:
                budget.record_generation_start()
                db.log_controller_budget_event({"kind": "generation_started"})
                phase = f"generation:{gen}:plugin_on_generation_start"
                for index, plugin in enumerate(plugins):
                    _call_plugin_hook(
                        plugin,
                        index,
                        "on_generation_start",
                        candidate_generation,
                        db,
                        generation=candidate_generation,
                        phase=phase,
                        hook_policy="fatal_run_abort",
                        parent_id=parent.id,
                    )

            prompt_program = prompt_db.select()
            prompt_context_policy = validate_prompt_context_policy(
                prompt_program.context_policy
            )
            proposal_metadata_enabled = (
                prompt_context_policy["proposal_metadata_enabled"]
                if prompt_context_policy["proposal_metadata_enabled"] is not None
                else config.capture_proposal_metadata
            )
            inspiration_strategy = (
                prompt_context_policy["inspiration_strategy"]
                or config.inspiration_strategy
            )
            inspiration_sample_count = (
                prompt_context_policy["inspiration_sample_count"]
                if prompt_context_policy["inspiration_sample_count"] is not None
                else config.num_inspirations
            )
            inspiration_required_metric = prompt_context_policy[
                "inspiration_required_metric"
            ]
            inspiration_excluded_metrics = prompt_context_policy[
                "inspiration_excluded_metrics"
            ]
            inspiration_fitness_threshold = prompt_context_policy[
                "inspiration_fitness_threshold"
            ]
            inspiration_metric_thresholds = prompt_context_policy[
                "inspiration_metric_thresholds"
            ]
            inspiration_metric_ranking = prompt_context_policy[
                "inspiration_metric_ranking"
            ]
            inspiration_pool_count = inspiration_sample_count
            if (
                (
                    inspiration_required_metric is not None
                    or inspiration_excluded_metrics
                    or inspiration_fitness_threshold is not None
                    or inspiration_metric_thresholds
                    or inspiration_metric_ranking is not None
                )
                and inspiration_sample_count > 0
            ):
                inspiration_pool_count = max(inspiration_sample_count * 5, 20)
            inspirations = db.sample_diverse(
                k=inspiration_pool_count,
                exclude_ids={parent.id},
                strategy=inspiration_strategy,
            )
            inspiration_selection_metadata = db.last_sample_metadata()
            if (
                inspiration_required_metric is not None
                or inspiration_excluded_metrics
                or inspiration_fitness_threshold is not None
                or inspiration_metric_thresholds
                or inspiration_metric_ranking is not None
            ):
                inspirations, inspiration_selection_metadata = (
                    _filter_inspirations_by_policy(
                        inspirations,
                        inspiration_selection_metadata,
                        required_metric=inspiration_required_metric,
                        excluded_metrics=inspiration_excluded_metrics,
                        fitness_threshold=inspiration_fitness_threshold,
                        metric_thresholds=inspiration_metric_thresholds,
                        metric_ranking=inspiration_metric_ranking,
                        requested_count=inspiration_sample_count,
                        pool_requested_count=inspiration_pool_count,
                    )
                )
            inspiration_selection_metadata["strategy_source"] = (
                "prompt_context_policy"
                if prompt_context_policy["inspiration_strategy"] is not None
                else "config"
            )
            inspiration_selection_metadata["configured_strategy"] = (
                config.inspiration_strategy
            )
            inspiration_selection_metadata["requested_count_source"] = (
                "prompt_context_policy"
                if prompt_context_policy["inspiration_sample_count"] is not None
                else "config"
            )
            inspiration_selection_metadata["configured_count"] = (
                config.num_inspirations
            )
            inspiration_selection_metadata["required_metric_source"] = (
                "prompt_context_policy"
                if inspiration_required_metric is not None
                else "none"
            )
            inspiration_selection_metadata["excluded_metrics_source"] = (
                "prompt_context_policy" if inspiration_excluded_metrics else "none"
            )
            inspiration_selection_metadata["fitness_threshold_source"] = (
                "prompt_context_policy"
                if inspiration_fitness_threshold is not None
                else "none"
            )
            inspiration_selection_metadata["metric_thresholds_source"] = (
                "prompt_context_policy" if inspiration_metric_thresholds else "none"
            )
            inspiration_selection_metadata["metric_ranking_source"] = (
                "prompt_context_policy"
                if inspiration_metric_ranking is not None
                else "none"
            )
            phase = f"generation:{gen}:plugin_context"
            context, plugin_context = _build_plugin_context(
                plugins,
                parent,
                inspirations,
                config=config,
                generation=candidate_generation,
                phase=phase,
                context_policy=prompt_context_policy,
            )
            prompt = prompt_sampler.build(
                parent, inspirations, problem, context,
                recent_failures=recent_failures or None,
                template=prompt_program.template,
                mutation_mode=config.mutation_mode,
                capture_proposal_metadata=proposal_metadata_enabled,
                context_policy=prompt_program.context_policy,
            )
            prompt_sampler.last_metadata["prompt_token_counter_capability"] = dict(
                prompt_token_counter_capability
            )

            if llm is None:
                phase = f"generation:{gen}:llm_build"
                llm = build_llm(config)
                _attach_llm_call_logger(llm, db)
            candidate_llm_call_start = _llm_call_count(llm)
            phase = f"generation:{gen}:llm_mutation"
            try:
                diff, backend_idx = _generate_with_budget(
                    llm,
                    budget,
                    prompt,
                    role="mutation",
                    budget_event_sink=db.log_controller_budget_event,
                )
            except Exception as exc:
                if _is_llm_budget_exhaustion(exc):
                    break
                mutation_failure = _bounded_llm_failure_record("mutation", exc, llm)
                mutation_failure["llm_calls"] = _llm_call_span(
                    llm, candidate_llm_call_start
                )
                failure_workspace = parent.workspace()
                retained_prompt = _retained_prompt_text(
                    prompt,
                    mode=config.mutation_prompt_retention_mode,
                )
                retained_prompt = _apply_explicit_context_retention_to_prompt(
                    retained_prompt,
                    context_text=prompt_sampler.last_context_text,
                    mode=config.explicit_context_retention_mode,
                )
                failure_payload = _llm_failure_payload_text(mutation_failure)
                candidate_id = _deterministic_generated_candidate_id(
                    generation=candidate_generation,
                    loop_generation_index=gen,
                    proposal_index=proposal_index,
                    parent_id=parent.id,
                    prompt_program_id=prompt_program.id,
                    mutation_text=failure_payload,
                    workspace=failure_workspace,
                )
                program = Program(
                    code=failure_workspace.code,
                    fitness=0.0,
                    id=candidate_id,
                    files=dict(failure_workspace.files),
                    primary_file=failure_workspace.primary_file,
                    allowed_reserved_paths=failure_workspace.allowed_reserved_paths,
                    static_files=failure_workspace.static_files,
                    parent_id=parent.id,
                    generation=candidate_generation,
                    lineage=parent.lineage + [parent.id],
                    metadata={
                        "candidate_type": "generated",
                        "candidate_status": "llm_mutation_failed",
                        "loop_generation_index": gen,
                        "proposal_batch": {
                            "policy": "sequential",
                            "proposal_index": proposal_index,
                            "proposal_number": proposal_index + 1,
                            "proposals_per_generation": proposal_count,
                            "loop_proposal_index": proposal_loop_index,
                        },
                        "prompt": retained_prompt["text"],
                        "prompt_retention": {
                            key: value
                            for key, value in retained_prompt.items()
                            if key != "text"
                        },
                        "diff": failure_payload,
                        "diff_error": "llm_mutation_failed",
                        "prompt_diagnostics": dict(prompt_sampler.last_metadata),
                        "proposal": {},
                        "backend_idx": None,
                        "mutation_mode": config.mutation_mode,
                        "parent_selection": parent_selection_metadata,
                        "inspiration_selection": inspiration_selection_metadata,
                        "plugin_context": plugin_context,
                        "prompt_program_id": prompt_program.id,
                        "llm_failure": mutation_failure,
                        "llm_calls": mutation_failure["llm_calls"],
                        "budget": budget.snapshot(),
                    },
                    metrics={"score": 0.0},
                    evaluation={
                        "fitness": 0.0,
                        "is_valid": False,
                        "error": "llm_mutation_failed",
                        "stdout": "",
                        "stderr": "",
                        "metadata": {"llm_failure": mutation_failure},
                    },
                )
                failure = db.log_failure(
                    program,
                    parent,
                    failure_payload,
                    "llm_mutation_failed",
                    None,
                )
                recent_failures.append(failure)
                recent_failures = recent_failures[-_MAX_FAILURES:]
                continue
            mutation_llm_call = _last_llm_call(llm)
            original_proposal_metadata = (
                extract_proposal_metadata(diff) if proposal_metadata_enabled else {}
            )
            proposal_metadata = original_proposal_metadata
            critique_metadata = None
            if config.critique_enabled:
                phase = f"generation:{gen}:llm_critique"
                (
                    diff,
                    critique_metadata,
                    selected_revised_proposal_metadata,
                ) = _run_critique_reviewers(
                    llm=llm,
                    budget=budget,
                    workspace=parent.workspace(),
                    base_prompt=prompt,
                    original_diff=diff,
                    original_proposal_metadata=original_proposal_metadata,
                    config=config,
                    capture_proposal_metadata=proposal_metadata_enabled,
                    budget_event_sink=db.log_controller_budget_event,
                )
                if proposal_metadata_enabled:
                    proposal_source = (
                        critique_metadata.get("proposal_source")
                        if isinstance(critique_metadata, dict)
                        else None
                    )
                    proposal_metadata = (
                        selected_revised_proposal_metadata
                        if proposal_source == "revised"
                        else original_proposal_metadata
                    )
            mutation_payload = (
                strip_proposal_metadata(diff) if proposal_metadata_enabled else diff
            )
            phase = f"generation:{gen}:mutation_apply"
            proposal_metadata_error = (
                validate_proposal_metadata_preamble(diff)
                if proposal_metadata_enabled
                else None
            )
            if proposal_metadata_error is not None:
                child_workspace = parent.workspace()
                diff_error = proposal_metadata_error
            else:
                child_workspace, diff_error = apply_workspace_mutation(
                    parent.workspace(), mutation_payload, mutation_mode=config.mutation_mode
                )
            _validate_workspace_size_for_config(child_workspace, config)
            phase = f"generation:{gen}:candidate_evaluation"
            result = evaluator.evaluate(child_workspace, diff_error=diff_error)
            result_accounting = evaluation_accounting(result)
            budget.record_evaluation(
                result.elapsed_sec,
                seed=False,
                accounting=result_accounting,
            )
            db.log_controller_budget_event(
                {
                    "kind": "candidate_evaluation",
                    "elapsed_sec": result.elapsed_sec,
                    "accounting": result_accounting,
                }
            )
            phase = f"generation:{gen}:llm_feedback"
            result = apply_llm_feedback(
                result,
                child_workspace,
                problem,
                config.llm_feedback,
                _BudgetedLLMProxy(
                    llm,
                    budget,
                    budget_event_sink=db.log_controller_budget_event,
                ),
                feedback_retention_mode=config.feedback_retention_mode,
            )
            budget.check_before_evaluation()
            budget.check_before_llm_call(role="feedback")
            score = result.fitness

            # Construct Program BEFORE calling on_evaluated (plugins need full object)
            child_code = child_workspace.code
            retained_prompt = _retained_prompt_text(
                prompt,
                mode=config.mutation_prompt_retention_mode,
            )
            retained_prompt = _apply_explicit_context_retention_to_prompt(
                retained_prompt,
                context_text=prompt_sampler.last_context_text,
                mode=config.explicit_context_retention_mode,
            )
            candidate_id = _deterministic_generated_candidate_id(
                generation=candidate_generation,
                loop_generation_index=gen,
                proposal_index=proposal_index,
                parent_id=parent.id,
                prompt_program_id=prompt_program.id,
                mutation_text=diff,
                workspace=child_workspace,
            )
            program = Program(code=child_code, fitness=score,
                              id=candidate_id,
                              files=dict(child_workspace.files),
                              primary_file=child_workspace.primary_file,
                              allowed_reserved_paths=child_workspace.allowed_reserved_paths,
                              static_files=child_workspace.static_files,
                              parent_id=parent.id, generation=candidate_generation,
                              lineage=parent.lineage + [parent.id],
                              metadata={"candidate_type": "generated",
                                        "loop_generation_index": gen,
                                        "proposal_batch": {
                                            "policy": "sequential",
                                            "proposal_index": proposal_index,
                                            "proposal_number": proposal_index + 1,
                                            "proposals_per_generation": proposal_count,
                                            "loop_proposal_index": proposal_loop_index,
                                        },
                                        "prompt": retained_prompt["text"],
                                        "prompt_retention": {
                                            key: value
                                            for key, value in retained_prompt.items()
                                            if key != "text"
                                        },
                                        "diff": diff,
                                        "prompt_diagnostics": dict(prompt_sampler.last_metadata),
                                        "proposal": proposal_metadata,
                                        "backend_idx": backend_idx,
                                        "critique": critique_metadata,
                                        "mutation_mode": config.mutation_mode,
                                        "causal_reward_baseline": {
                                            "source": "parent_program",
                                            "parent_id": parent.id,
                                            "score": parent.fitness,
                                        },
                                        "parent_selection": parent_selection_metadata,
                                        "inspiration_selection": inspiration_selection_metadata,
                                        "plugin_context": plugin_context,
                                        "prompt_program_id": prompt_program.id,
                                        "llm_calls": _program_llm_calls(
                                            _llm_call_span(llm, candidate_llm_call_start),
                                            mutation_llm_call,
                                            critique_metadata,
                                            result,
                                        ),
                                        "budget": budget.snapshot()},
                              metrics=result.metrics,
                              evaluation=result.to_dict())

            _annotate_metric_policy(program, problem)
            phase = f"generation:{gen}:plugin_on_evaluated"
            score = _apply_plugin_scores(
                program,
                score,
                plugins,
                generation=candidate_generation,
                phase=phase,
            )
            _annotate_metric_policy(program, problem)

            phase = f"generation:{gen}:history_logging"
            admission = db.admit(program, threshold=VALID_THRESHOLD)
            if program.fitness < VALID_THRESHOLD or not _evaluation_is_valid(program):
                failure = db.log_failure(program, parent, diff, diff_error, admission)
                recent_failures.append(failure)
                recent_failures = recent_failures[-_MAX_FAILURES:]

            backend_reward = _backend_reward(program, parent, backend_idx)
            program.metadata["backend_reward"] = backend_reward
            phase = f"generation:{gen}:backend_reward"
            llm.record_reward(
                backend_idx,
                backend_reward["reward"],
                call_id=mutation_llm_call.get("id") if mutation_llm_call else None,
            )
            program.metadata["llm_calls"] = _program_llm_calls(
                _llm_call_span(llm, candidate_llm_call_start),
                mutation_llm_call,
                critique_metadata,
                result,
            )
            db.log(program)
            prompt_reward = _prompt_reward(score, parent.fitness, config.prompt_reward_mode)
            prompt_db.record_result(
                prompt_program.id,
                prompt_reward,
                metadata={
                    "last_generation": candidate_generation,
                    "last_program_id": program.id,
                    "last_candidate_score": score,
                    "last_parent_score": parent.fitness,
                },
            )
            if (
                config.meta_prompt_evolution
                and config.meta_prompt_interval > 0
                and candidate_generation % config.meta_prompt_interval == 0
            ):
                mutation_prompt, mutation_context = _build_meta_prompt_mutation_request(
                    prompt_program,
                    prompt_db,
                    program,
                    parent,
                    prompt_reward,
                    recent_failures,
                    config,
                )
                if budget.check_before_llm_call(role="meta_prompt"):
                    phase = f"generation:{gen}:prompt_database_mutation_skipped"
                    prompt_db.mutate(
                        prompt_program.id,
                        "",
                        generation=candidate_generation,
                        metadata={
                            "source": "llm",
                            "skip_reason": "max_llm_calls",
                            "budget": _skipped_llm_budget_record(
                                role="meta_prompt",
                                stop_reason=budget.stop_reason,
                                budget=budget,
                            ),
                            "mutation_context": mutation_context,
                        },
                    )
                else:
                    phase = f"generation:{gen}:llm_meta_prompt"
                    try:
                        template, prompt_backend_idx = _generate_with_budget(
                            llm,
                            budget,
                            mutation_prompt,
                            role="meta_prompt",
                            budget_event_sink=db.log_controller_budget_event,
                        )
                    except Exception as exc:
                        phase = f"generation:{gen}:prompt_database_mutation_failed"
                        prompt_db.mutate(
                            prompt_program.id,
                            "",
                            generation=candidate_generation,
                            metadata={
                                "source": "llm",
                                **_bounded_llm_failure_record("meta_prompt", exc, llm),
                                "mutation_context": mutation_context,
                            },
                        )
                        template = None
                    if template is not None:
                        phase = f"generation:{gen}:prompt_database_mutation"
                        try:
                            (
                                template,
                                child_context_policy,
                                mutation_response_metadata,
                            ) = parse_prompt_mutation_response(
                                template,
                                parent_context_policy=prompt_program.context_policy,
                            )
                        except PromptTemplateError as exc:
                            template = ""
                            child_context_policy = None
                            mutation_response_metadata = {
                                "schema": "libreevolve.prompt_mutation_response.v1",
                                "format": "invalid",
                                "error": str(exc),
                            }
                        prompt_db.mutate(
                            prompt_program.id,
                            template,
                            generation=candidate_generation,
                            metadata={
                                "source": "llm",
                                "backend_idx": prompt_backend_idx,
                                "llm_call": _last_llm_call(llm),
                                "mutation_context": mutation_context,
                                "mutation_response": mutation_response_metadata,
                            },
                            context_policy=child_context_policy,
                        )
            if proposal_index == proposal_count - 1:
                phase = f"generation:{gen}:migration"
                db.maybe_migrate(candidate_generation)

                best = db.best()
                phase = f"generation:{gen}:plugin_on_generation_end"
                for index, plugin in enumerate(plugins):
                    _call_plugin_hook(
                        plugin,
                        index,
                        "on_generation_end",
                        candidate_generation,
                        best,
                        generation=candidate_generation,
                        phase=phase,
                        hook_policy="fatal_run_abort",
                    )
                budget.record_generation_complete()
                db.log_controller_budget_event({"kind": "generation_completed"})

        best = db.best()
        phase = "normal_finalization"
        _write_completed_runtime(
            db,
            config,
            budget,
            run_dir,
            best,
            plugins,
            llm=llm,
            run_rng=run_rng,
            rng_resume_status=rng_resume_status,
            llm_scheduler_resume_status=llm_scheduler_resume_status,
            core_resolves_config_plugins=core_resolved_config_plugins,
        )
        return best
    except BaseException as exc:
        _write_aborted_runtime(
            db,
            config,
            budget,
            run_dir,
            phase,
            exc,
            plugins,
            llm=llm,
            run_rng=run_rng,
            rng_resume_status=rng_resume_status,
            llm_scheduler_resume_status=llm_scheduler_resume_status,
            core_resolves_config_plugins=core_resolved_config_plugins,
        )
        raise


def _write_completed_runtime(
    db: ProgramDatabase,
    config: Config,
    budget: RunBudget,
    run_dir: Path,
    best: Program | None,
    plugins: list[PluginBase],
    *,
    llm: object | None = None,
    run_rng: random.Random,
    rng_resume_status: str,
    llm_scheduler_resume_status: str,
    core_resolves_config_plugins: bool = False,
) -> None:
    runtime = budget.finish(best_found=best is not None)
    runtime["status"] = "completed"
    _mark_runtime_wall_clock_status(runtime, "completed")
    db.log_controller_budget_event(
        {"kind": "stop", "stop_reason": runtime["stop_reason"]}
    )
    runtime["rng"] = _runtime_rng_state(
        run_rng,
        config.seed,
        resume_status=rng_resume_status,
    )
    best_export = export_best_artifacts(best, run_dir) if best is not None else None
    runtime["artifacts"] = _runtime_artifact_pointers(run_dir)
    attach_best_artifact_export(runtime, best_export)
    runtime["history"] = _runtime_history_summary(db, run_dir, budget)
    _attach_runtime_summaries(
        runtime,
        db,
        config,
        plugins,
        llm=llm,
        llm_scheduler_resume_status=llm_scheduler_resume_status,
        include_plugin_artifacts=True,
        core_resolves_config_plugins=core_resolves_config_plugins,
    )
    db.update_manifest_runtime(runtime)


def _write_aborted_runtime(
    db: ProgramDatabase,
    config: Config,
    budget: RunBudget,
    run_dir: Path,
    phase: str,
    exc: BaseException,
    plugins: list[PluginBase],
    *,
    llm: object | None = None,
    run_rng: random.Random,
    rng_resume_status: str,
    llm_scheduler_resume_status: str,
    core_resolves_config_plugins: bool = False,
) -> None:
    budget.stop_reason = "aborted"
    db.log_controller_budget_event({"kind": "stop", "stop_reason": "aborted"})
    runtime = budget.snapshot()
    runtime["status"] = "aborted"
    _mark_runtime_wall_clock_status(runtime, "aborted")
    runtime["rng"] = _runtime_rng_state(
        run_rng,
        config.seed,
        resume_status=rng_resume_status,
    )
    runtime["abort"] = {
        "exception_type": exc.__class__.__name__,
        **_aborted_exception_manifest(exc),
        "phase": phase,
        "role": _phase_role(phase),
        "keyboard_interrupt": isinstance(exc, KeyboardInterrupt),
    }
    plugin_failure = _plugin_failure_manifest(exc, phase)
    if plugin_failure:
        runtime["abort"]["plugin_failure"] = plugin_failure
        runtime["plugin_failures"] = [plugin_failure]
    runtime["artifacts"] = _runtime_artifact_pointers(run_dir)
    runtime["history"] = _runtime_history_summary(db, run_dir, budget)
    _attach_runtime_summaries(
        runtime,
        db,
        config,
        plugins,
        llm=llm,
        llm_scheduler_resume_status=llm_scheduler_resume_status,
        include_plugin_artifacts=True,
        plugin_artifact_errors="record",
        core_resolves_config_plugins=core_resolves_config_plugins,
    )
    try:
        db.update_manifest_runtime(runtime)
    except BaseException as finalize_exc:
        try:
            exc.add_note(
                "Failed to write aborted-run manifest runtime: "
                f"{finalize_exc.__class__.__name__}: {finalize_exc}"
            )
        except Exception:
            pass


def _mark_runtime_wall_clock_status(runtime: dict, status: str) -> None:
    wall_clock = runtime.get("wall_clock")
    if not isinstance(wall_clock, dict):
        return
    finished_at = wall_clock.get("finished_at") or wall_clock.get("updated_at")
    if not isinstance(finished_at, str):
        return
    wall_clock["final_status"] = status
    if status == "completed":
        wall_clock["completed_at"] = finished_at
    elif status == "aborted":
        wall_clock["aborted_at"] = finished_at


def _aborted_exception_manifest(exc: BaseException) -> dict:
    try:
        raw_message = str(exc)
        message_unavailable = False
    except BaseException as format_exc:
        raw_message = (
            "<exception message unavailable; "
            f"__str__ raised {format_exc.__class__.__name__}>"
        )
        message_unavailable = True
    message = redact_sensitive_text(raw_message)
    message_chars = len(message)
    message_truncated = message_chars > _MAX_ABORT_MESSAGE_CHARS
    if message_truncated:
        suffix = "...<truncated>"
        message = message[: _MAX_ABORT_MESSAGE_CHARS - len(suffix)] + suffix
    return {
        "message": message,
        "message_chars": message_chars,
        "message_truncated": message_truncated,
        "message_unavailable": message_unavailable,
    }


def _call_plugin_hook(
    plugin: PluginBase,
    index: int,
    hook: str,
    *args,
    generation: int | None = None,
    phase: str | None = None,
    hook_policy: str = "fatal_run_abort",
    parent_id: str | None = None,
    candidate_id: str | None = None,
):
    try:
        method = getattr(plugin, hook)
        return method(*args)
    except Exception as exc:
        _annotate_plugin_failure(
            exc,
            plugin,
            index,
            hook,
            generation=generation,
            phase=phase,
            hook_policy=hook_policy,
            parent_id=parent_id,
            candidate_id=candidate_id,
        )
        raise


def _call_optional_plugin_hook(
    plugin: PluginBase,
    index: int,
    hook: str,
    *args,
    generation: int | None = None,
    phase: str | None = None,
    hook_policy: str = "fatal_run_abort",
    parent_id: str | None = None,
    candidate_id: str | None = None,
):
    try:
        method = getattr(plugin, hook, None)
        if not callable(method):
            return None
        return method(*args)
    except Exception as exc:
        _annotate_plugin_failure(
            exc,
            plugin,
            index,
            hook,
            generation=generation,
            phase=phase,
            hook_policy=hook_policy,
            parent_id=parent_id,
            candidate_id=candidate_id,
        )
        raise


def _annotate_plugin_failure(
    exc: Exception,
    plugin: PluginBase,
    index: int,
    hook: str,
    *,
    generation: int | None,
    phase: str | None,
    hook_policy: str,
    parent_id: str | None = None,
    candidate_id: str | None = None,
) -> None:
    identity = _plugin_identity(plugin, index)
    record: dict[str, object] = {
        **identity,
        "hook": hook,
        "policy": hook_policy,
        "continued": False,
    }
    if generation is not None:
        record["generation"] = generation
    if phase:
        record["phase"] = phase
    if parent_id:
        record["parent_id"] = parent_id
    if candidate_id:
        record["candidate_id"] = candidate_id
    try:
        setattr(exc, _PLUGIN_FAILURE_ATTR, record)
    except Exception:
        pass


def _plugin_failure_manifest(exc: BaseException, phase: str) -> dict | None:
    raw_record = getattr(exc, _PLUGIN_FAILURE_ATTR, None)
    if not isinstance(raw_record, dict):
        return None
    record = dict(raw_record)
    record.setdefault("phase", phase)
    record["exception_type"] = exc.__class__.__name__
    record.update(_aborted_exception_manifest(exc))
    return record


def _attach_runtime_summaries(
    runtime: dict,
    db: ProgramDatabase,
    config: Config,
    plugins: list[PluginBase],
    *,
    llm: object | None = None,
    llm_scheduler_resume_status: str = _LLM_SCHEDULER_RESUME_STATUS_RESTORE_SUPPORTED,
    include_plugin_artifacts: bool,
    plugin_artifact_errors: str = "raise",
    core_resolves_config_plugins: bool = False,
) -> None:
    runtime["plugin_state"] = _runtime_plugin_state(
        config,
        plugins,
        core_resolves_config_plugins=core_resolves_config_plugins,
    )
    llm_scheduler = _runtime_llm_scheduler_state(
        llm,
        resume_status=llm_scheduler_resume_status,
    )
    runtime["llm_scheduler"] = llm_scheduler
    runtime["llm_accounting"] = _runtime_llm_accounting(config, llm_scheduler)
    runtime["llm_budget_report"] = _runtime_llm_budget_report(
        config,
        llm_scheduler,
        llm=llm,
    )
    runtime["llm_provider_diagnostics"] = _runtime_llm_provider_diagnostics(llm)
    runtime["prompt_section_packing"] = _runtime_prompt_section_packing_coverage(
        config
    )
    runtime["prompt_context_policy_coverage"] = (
        _runtime_prompt_context_policy_coverage()
    )
    runtime["lineage_replay_policy"] = _runtime_lineage_replay_policy()
    runtime["provider_cancellation_policy"] = _runtime_provider_cancellation_policy(
        config,
        llm_scheduler,
    )
    retrieval_summary = _retrieval_manifest_summary(db.all_programs())
    if retrieval_summary:
        runtime["retrieval"] = retrieval_summary
    if include_plugin_artifacts:
        plugin_artifacts, plugin_artifact_failures = _plugin_artifact_manifest(
            plugins,
            errors=plugin_artifact_errors,
        )
        if plugin_artifacts:
            runtime["plugin_artifacts"] = plugin_artifacts
        if plugin_artifact_failures:
            runtime["plugin_artifact_failures"] = plugin_artifact_failures


def _runtime_plugin_state(
    config: Config,
    plugins: list[PluginBase],
    *,
    core_resolves_config_plugins: bool = False,
) -> dict:
    configured = configured_plugin_labels(list(config.plugins))
    loaded = [_plugin_identity(plugin, index) for index, plugin in enumerate(plugins)]
    loaded_specs = [
        _plugin_spec_record(plugin, index, config, configured)
        for index, plugin in enumerate(plugins)
    ]
    configured_without_loaded = configured if configured and not loaded else []
    loaded_without_configured = loaded if loaded and not configured else []
    if configured and loaded:
        resolution = "configured_and_loaded"
    elif configured:
        resolution = "configured_without_loaded_instances"
    elif loaded:
        resolution = "loaded_without_configured_labels"
    else:
        resolution = "none"
    return {
        "configured": configured,
        "configured_count": len(configured),
        "loaded": loaded,
        "loaded_count": len(loaded),
        "loaded_specs": loaded_specs,
        "resolution": resolution,
        "configured_without_loaded_instances": configured_without_loaded,
        "loaded_without_configured_labels": loaded_without_configured,
        "core_resolves_config_plugins": core_resolves_config_plugins,
    }


def _plugin_spec_record(
    plugin: object,
    index: int,
    config: Config,
    configured: list[str],
) -> dict:
    identity = _plugin_identity(plugin, index)
    record: dict[str, object] = {
        **identity,
        "configured_label": configured[index] if index < len(configured) else None,
        "source": "loaded_instance",
    }
    module = identity.get("module")
    name = identity.get("plugin")
    entry_point_spec = plugin_entry_point_spec(plugin)
    params: dict[str, object] | None = None
    if module == "libreevolve.plugins.causal" and name == "CausalPlugin":
        params = {"history_limit": getattr(plugin, "_history_limit", None)}
    elif module == "libreevolve.plugins.modular" and name == "ModularPlugin":
        params = {}
    elif module == "libreevolve.plugins.deep_research" and name == "DeepResearchPlugin":
        params = {
            "provider": getattr(plugin, "_provider", None),
            "search_every": getattr(plugin, "_search_every", None),
            "max_events": getattr(plugin, "_max_events", None),
            "cache_mode": getattr(plugin, "_cache_mode", None),
            "retrieval_body_retention_mode": getattr(
                plugin,
                "_retrieval_body_retention_mode",
                None,
            ),
            "source_ranking_policy": getattr(
                plugin,
                "_source_ranking_policy",
                None,
            ),
            "cache_dir": _plugin_path_parameter_record(
                getattr(plugin, "_cache_dir", None),
                config,
            ),
        }
    elif module == "libreevolve.plugins.ttt_rl" and name == "TTTRLPlugin":
        params = {
            "train_every": getattr(plugin, "_train_every", None),
            "log_dir": _plugin_path_parameter_record(
                getattr(plugin, "_log_dir", None),
                config,
            ),
            "max_retained_examples": getattr(plugin, "_max_retained_examples", None),
            "max_payload_field_chars": getattr(plugin, "_max_payload_field_chars", None),
            "max_payload_total_chars": getattr(plugin, "_max_payload_total_chars", None),
        }
    elif entry_point_spec is not None:
        record["status"] = "entry_point_plugin_signature_recorded"
        record["schema"] = "libreevolve.plugin_spec.v1"
        record["source"] = "entry_point"
        record["parameter_policy"] = (
            "entry_point_constructor_options_from_manifest_safe_config"
        )
        record["direct_plugin_policy"] = _direct_plugin_constructor_policy(
            source="entry_point"
        )
        record["entry_point"] = _validate_plugin_metadata(
            f"plugin_specs[{identity['instance_id']}].entry_point",
            entry_point_spec,
        )
        record["constructor_signature"] = _custom_plugin_constructor_signature(
            plugin,
            identity,
        )
        return record
    else:
        record["status"] = "custom_plugin_signature_recorded"
        record["schema"] = "libreevolve.plugin_spec.v1"
        record["parameter_policy"] = (
            "custom_constructor_signature_only_no_parameter_values"
        )
        record["direct_plugin_policy"] = _direct_plugin_constructor_policy(
            source="direct_instance"
        )
        record["constructor_signature"] = _custom_plugin_constructor_signature(
            plugin,
            identity,
        )
        return record
    record["status"] = "ok"
    record["schema"] = "libreevolve.plugin_spec.v1"
    record["parameter_policy"] = "validated_builtin_constructor_parameters"
    record["parameters"] = _validate_plugin_metadata(
        f"plugin_specs[{identity['instance_id']}].parameters",
        params,
    )
    return record


def _direct_plugin_constructor_policy(*, source: str) -> dict:
    if source == "entry_point":
        constructor_value_policy = (
            "manifest_safe_or_schema_validated_constructor_options_captured"
        )
        package_scope_policy = (
            "entry_point_distribution_name_version_record_wheel_metadata"
        )
        paper_scope_policy = "configured_entry_point_paper_inspiration_labels"
    else:
        constructor_value_policy = (
            "constructor_values_excluded_signature_shape_only"
        )
        package_scope_policy = (
            "direct_instance_module_identity_file_hash_and_version_only"
        )
        paper_scope_policy = "not_available_for_direct_instances"
    return {
        "schema": "libreevolve.direct_plugin_policy.v1",
        "source": source,
        "constructor_value_policy": constructor_value_policy,
        "constructor_values_captured": source == "entry_point",
        "constructor_schema_policy": (
            "entry_point_declared_schema_or_manifest_safe_json"
            if source == "entry_point"
            else "not_available_for_direct_instances"
        ),
        "constructor_signature_policy": "names_kinds_required_flags_only",
        "instance_attribute_policy": "not_captured",
        "package_scope_policy": package_scope_policy,
        "paper_scope_policy": paper_scope_policy,
    }


def _custom_plugin_constructor_signature(plugin: object, identity: dict) -> dict:
    try:
        signature = inspect.signature(plugin.__class__)
    except (TypeError, ValueError):
        return {
            "status": "unavailable",
            "reason": "signature_unavailable",
            "parameter_values_captured": False,
        }
    parameters: list[dict[str, object]] = []
    for parameter in signature.parameters.values():
        parameters.append(
            {
                "name": parameter.name,
                "kind": str(parameter.kind),
                "required": parameter.default is inspect.Parameter.empty,
                "default_present": parameter.default is not inspect.Parameter.empty,
                "annotation_present": parameter.annotation is not inspect.Parameter.empty,
            }
        )
    return _validate_plugin_metadata(
        f"plugin_specs[{identity['instance_id']}].constructor_signature",
        {
            "status": "available",
            "parameter_policy": "names_kinds_required_flags_only",
            "parameter_values_captured": False,
            "parameter_count": len(parameters),
            "parameters": parameters,
        },
    )


def _plugin_path_parameter_record(path: object, config: Config) -> dict | None:
    if path is None:
        return None
    raw_path = Path(path)
    run_dir = (Path(config.log_dir) / config.problem_name).resolve(strict=False)
    resolved = raw_path.resolve(strict=False)
    record: dict[str, object] = {
        "path_redacted": True,
        "path_hash": hashlib.sha256(
            str(raw_path).encode("utf-8", errors="replace")
        ).hexdigest(),
        "resolved_path_hash": hashlib.sha256(
            str(resolved).encode("utf-8", errors="replace")
        ).hexdigest(),
    }
    if _path_within(resolved, run_dir):
        try:
            record["path"] = resolved.relative_to(run_dir).as_posix()
        except ValueError:
            pass
        record["scope"] = "within_run_dir"
    else:
        record["scope"] = "outside_run_dir"
    return record


def _runtime_llm_scheduler_state(
    llm: object | None,
    *,
    resume_status: str = _LLM_SCHEDULER_RESUME_STATUS_RESTORE_SUPPORTED,
) -> dict:
    if llm is None:
        return {
            "status": "not_initialized",
            "reason": "no_mutation_llm_was_constructed",
        }
    if resume_status not in _LLM_SCHEDULER_RESUME_STATUSES:
        raise ValueError(f"Unsupported LLM scheduler resume status: {resume_status}")
    scheduler_state = getattr(llm, "scheduler_state", None)
    if not isinstance(scheduler_state, dict):
        return {
            "status": "unavailable",
            "reason": "llm_does_not_expose_scheduler_state",
            "llm_type": _manifest_safe_type_name(llm),
        }
    snapshot = copy.deepcopy(scheduler_state)
    try:
        json.dumps(snapshot, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as exc:
        return {
            "status": "invalid",
            "reason": "scheduler_state_not_finite_json",
            "error_type": exc.__class__.__name__,
            "llm_type": _manifest_safe_type_name(llm),
        }
    if not isinstance(llm, LLMEnsemble):
        return {
            "status": "invalid",
            "reason": "scheduler_state_not_validated_by_llm_ensemble",
            "llm_type": _manifest_safe_type_name(llm),
        }
    try:
        validate_scheduler_state_snapshot(snapshot, len(llm.backends))
    except ValueError as exc:
        return {
            "status": "invalid",
            "reason": "scheduler_state_validation_failed",
            "error_type": exc.__class__.__name__,
            "error": redact_sensitive_text(str(exc))[:_MAX_ABORT_MESSAGE_CHARS],
            "llm_type": _manifest_safe_type_name(llm),
        }
    return {
        "status": "snapshot",
        "schema": "libreevolve.llm_scheduler_state.v1",
        "state": snapshot,
        "restore_entrypoint": "LLMEnsemble.restore_scheduler_state",
        "resume_status": resume_status,
    }


def _runtime_llm_accounting(config: Config, scheduler_record: dict) -> dict:
    record: dict[str, object] = {
        "schema": "libreevolve.llm_accounting.v1",
        "policy": "audit_summary_not_budget_enforced",
    }
    status = scheduler_record.get("status")
    if status != "snapshot":
        record["status"] = status if isinstance(status, str) else "unavailable"
        reason = scheduler_record.get("reason")
        if isinstance(reason, str):
            record["reason"] = reason
        else:
            record["reason"] = "llm_scheduler_snapshot_unavailable"
        return record

    state = scheduler_record["state"]
    role_accounting = copy.deepcopy(state["role_accounting"])
    role_scheduler_state = copy.deepcopy(state.get("role_scheduler_state", {}))
    role_call_limits = copy.deepcopy(state.get("role_call_limits", {}))
    record.update(
        {
            "status": "snapshot",
            "source": "llm_scheduler_state.role_accounting_and_role_scheduler_state",
            "limits": {
                "max_llm_calls": config.max_llm_calls,
                "max_llm_provider_attempts": config.max_llm_provider_attempts,
                "max_llm_tokens": config.max_llm_tokens,
                "max_llm_cost_microusd": config.max_llm_cost_microusd,
                "max_llm_seconds": config.max_llm_seconds,
                "llm_role_call_limits": dict(config.llm_role_call_limits),
                "llm_role_provider_attempt_limits": dict(
                    config.llm_role_provider_attempt_limits
                ),
                "llm_role_token_limits": dict(config.llm_role_token_limits),
                "llm_role_cost_microusd_limits": dict(
                    config.llm_role_cost_microusd_limits
                ),
                "llm_role_seconds_limits": dict(config.llm_role_seconds_limits),
                "llm_role_backend_indices": {
                    role: list(indices)
                    for role, indices in config.llm_role_backend_indices.items()
                },
                "llm_max_retries": config.llm_max_retries,
                "llm_max_call_attempts": config.llm_max_call_attempts,
                "llm_fallback": config.llm_fallback,
                "llm_call_timeout_sec": config.llm_call_timeout_sec,
                "llm_max_response_chars": config.llm_max_response_chars,
                "prompt_max_chars": config.prompt_max_chars,
                "prompt_max_estimated_tokens": config.prompt_max_estimated_tokens,
                "llm_reward_accounted_roles": list(config.llm_reward_accounted_roles),
            },
            "reward_accounting_policy": state.get(
                "reward_accounting_policy",
                {
                    "policy": "configured_reward_accounted_roles_v1",
                    "reward_accounted_roles": ["mutation"],
                },
            ),
            "role_accounting": role_accounting,
            "role_scheduler_state": role_scheduler_state,
            "role_call_limits": role_call_limits,
            "role_backend_policy": copy.deepcopy(state.get("role_backend_policy", {})),
            "totals": _aggregate_llm_role_accounting(role_accounting),
            "scheduler_totals": _aggregate_llm_role_scheduler_state(
                role_scheduler_state
            ),
        }
    )
    return record


def _runtime_llm_provider_diagnostics(llm: object | None) -> dict:
    if llm is None:
        return {
            "schema": LLM_PROVIDER_DIAGNOSTICS_SCHEMA,
            "status": "not_initialized",
            "reason": "no_mutation_llm_was_constructed",
        }
    if not isinstance(llm, LLMEnsemble):
        return {
            "schema": LLM_PROVIDER_DIAGNOSTICS_SCHEMA,
            "status": "unavailable",
            "reason": "llm_is_not_llm_ensemble",
            "llm_type": _manifest_safe_type_name(llm),
        }
    try:
        summary = llm.provider_diagnostics_summary
    except Exception as exc:
        return {
            "schema": LLM_PROVIDER_DIAGNOSTICS_SCHEMA,
            "status": "invalid",
            "reason": "provider_diagnostics_summary_failed",
            "error_type": exc.__class__.__name__,
            "error": redact_sensitive_text(str(exc))[:_MAX_ABORT_MESSAGE_CHARS],
        }
    if isinstance(summary, dict):
        return summary
    return {
        "schema": LLM_PROVIDER_DIAGNOSTICS_SCHEMA,
        "status": "invalid",
        "reason": "provider_diagnostics_summary_not_mapping",
        "summary_type": _manifest_safe_type_name(summary),
    }


def _runtime_prompt_section_packing_coverage(config: Config) -> dict:
    roles = [
        _prompt_section_packing_role_record(
            config,
            role="mutation",
            prompt_builder="PromptSampler.build",
            section_packing_status="supported",
            section_packing_boundary="pre_llm_promptsampler_optional_section_packing",
            role_discovery="static_mutation_role",
        ),
        _prompt_section_packing_role_record(
            config,
            role="critique",
            prompt_builder="build_critique_prompt",
            section_packing_status="unsupported",
            section_packing_boundary="final_prompt_boundary_only",
            role_discovery="static_critique_role",
        ),
        _prompt_section_packing_role_record(
            config,
            role="feedback:*",
            prompt_builder="_build_feedback_prompt",
            section_packing_status="unsupported",
            section_packing_boundary="final_prompt_boundary_only",
            role_discovery="dynamic_feedback_role_names",
            token_counter_capability=None,
        ),
        _prompt_section_packing_role_record(
            config,
            role="meta_prompt",
            prompt_builder="_build_meta_prompt_mutation_request",
            section_packing_status="unsupported",
            section_packing_boundary="final_prompt_boundary_only",
            role_discovery="static_meta_prompt_role",
        ),
    ]
    ready_roles = [
        role["role"]
        for role in roles
        if role["section_packing_status"] == "supported"
        and role["provider_token_section_packing_ready"] is True
    ]
    missing_roles = [
        role["role"]
        for role in roles
        if role["section_packing_status"] != "supported"
        or role["provider_token_section_packing_ready"] is not True
    ]
    record = {
        "schema": PROMPT_SECTION_PACKING_COVERAGE_SCHEMA,
        "policy": "role_scoped_prompt_builder_section_packing_coverage_v1",
        "section_packing_roles": [
            role["role"]
            for role in roles
            if role["section_packing_status"] == "supported"
        ],
        "provider_token_section_packing_ready_roles": ready_roles,
        "provider_token_section_packing_missing_roles": missing_roles,
        "automatic_provider_token_section_packing_complete": False,
        "final_prompt_token_counting_boundary": (
            "LLMEnsemble.generate performs role-scoped final-prompt counting "
            "when all eligible backends share a local counter"
        ),
        "roles": roles,
        "limitations": [
            "non_mutation_prompt_builders_do_not_use_promptsampler_section_packing",
            "feedback_roles_are_dynamic_and_discovered_at_llm_generate_boundary",
            "provider_token_section_packing_is_not_complete_for_all_prompt_roles",
        ],
    }
    record["validation"] = validate_prompt_section_packing_coverage(record)
    return record


def _runtime_prompt_context_policy_coverage() -> dict:
    capabilities = validate_meta_prompt_context_policy_capabilities(
        _META_PROMPT_CONTEXT_POLICY_CAPABILITIES
    )
    sections = []
    all_fields: list[str] = []
    for section_name in _META_PROMPT_CONTEXT_POLICY_CAPABILITY_SECTIONS:
        fields = _context_policy_capability_fields(capabilities[section_name])
        all_fields.extend(fields)
        sections.append(
            {
                "name": section_name,
                "field_count": len(fields),
                "fields_sha256": hashlib.sha256(
                    ",".join(fields).encode("utf-8")
                ).hexdigest(),
            }
        )
    record = {
        "schema": PROMPT_CONTEXT_POLICY_COVERAGE_SCHEMA,
        "policy": "meta_prompt_visible_context_policy_surface_v1",
        "capabilities_schema": capabilities["schema"],
        "context_policy_schema": validate_prompt_context_policy({})["schema"],
        "tunable_field_count": len(all_fields),
        "tunable_fields_sha256": hashlib.sha256(
            ",".join(sorted(all_fields)).encode("utf-8")
        ).hexdigest(),
        "sections": sections,
        "meta_prompt_mutation_accepts_context_policy": True,
        "prompt_history_replay_validates_context_policy_hash": True,
        "alphaevolve_context_policy_complete": False,
        "unsupported_surfaces": [
            "retrieval_summarization_policy",
            "learned_or_external_semantic_ranking_policy",
            "deep_retrieval_debug_refinement_loop",
            "non_promptsampler_prompt_builder_section_policy",
            "semantic_source_selection_policy",
        ],
        "limitations": [
            "coverage_tracks_current_validated_policy_schema_not_full_alphaevolve_context_control",
            "retrieval_and_summarization_policy_remain_fixed_code_or_config_paths",
            "semantic_context_selection_is_not_meta_prompt_evolved",
        ],
    }
    record["validation"] = validate_prompt_context_policy_coverage(record)
    return record


def validate_prompt_context_policy_coverage(record: object) -> dict:
    """Validate meta-prompt-visible context-policy coverage without overclaiming."""
    issues: list[dict[str, str]] = []
    if not isinstance(record, Mapping):
        return {
            "schema": PROMPT_CONTEXT_POLICY_COVERAGE_VALIDATION_SCHEMA,
            "coverage_schema": None,
            "ok": False,
            "alphaevolve_context_policy_complete": False,
            "tunable_field_count": 0,
            "unsupported_surface_count": 0,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "prompt context-policy coverage must be an object",
                }
            ],
        }
    if record.get("schema") != PROMPT_CONTEXT_POLICY_COVERAGE_SCHEMA:
        issues.append(
            {
                "code": "invalid_schema",
                "message": "unsupported prompt context-policy coverage schema",
            }
        )
    if record.get("policy") != "meta_prompt_visible_context_policy_surface_v1":
        issues.append(
            {
                "code": "invalid_policy",
                "message": "unsupported prompt context-policy coverage policy",
            }
        )
    expected_capabilities = validate_meta_prompt_context_policy_capabilities(
        _META_PROMPT_CONTEXT_POLICY_CAPABILITIES
    )
    expected_fields: list[str] = []
    expected_sections = []
    for section_name in _META_PROMPT_CONTEXT_POLICY_CAPABILITY_SECTIONS:
        fields = _context_policy_capability_fields(expected_capabilities[section_name])
        expected_fields.extend(fields)
        expected_sections.append(
            {
                "name": section_name,
                "field_count": len(fields),
                "fields_sha256": hashlib.sha256(
                    ",".join(fields).encode("utf-8")
                ).hexdigest(),
            }
        )
    expected_hash = hashlib.sha256(
        ",".join(sorted(expected_fields)).encode("utf-8")
    ).hexdigest()
    if record.get("capabilities_schema") != META_PROMPT_CONTEXT_POLICY_CAPABILITIES_SCHEMA:
        issues.append(
            {
                "code": "capabilities_schema_mismatch",
                "message": "capabilities_schema must match meta-prompt capability schema",
            }
        )
    if record.get("context_policy_schema") != validate_prompt_context_policy({})["schema"]:
        issues.append(
            {
                "code": "context_policy_schema_mismatch",
                "message": "context_policy_schema must match prompt context policy schema",
            }
        )
    if record.get("tunable_field_count") != len(expected_fields):
        issues.append(
            {
                "code": "tunable_field_count_mismatch",
                "message": "tunable field count must match validated policy fields",
            }
        )
    if record.get("tunable_fields_sha256") != expected_hash:
        issues.append(
            {
                "code": "tunable_fields_hash_mismatch",
                "message": "tunable field hash must match validated policy fields",
            }
        )
    if record.get("sections") != expected_sections:
        issues.append(
            {
                "code": "sections_mismatch",
                "message": "sections must match current meta-prompt capability sections",
            }
        )
    if record.get("meta_prompt_mutation_accepts_context_policy") is not True:
        issues.append(
            {
                "code": "context_policy_mutation_not_marked_supported",
                "message": "coverage must record context_policy mutation support",
            }
        )
    if record.get("prompt_history_replay_validates_context_policy_hash") is not True:
        issues.append(
            {
                "code": "context_policy_replay_hash_not_marked_supported",
                "message": "coverage must record prompt history context-policy hash validation",
            }
        )
    if record.get("alphaevolve_context_policy_complete") is not False:
        issues.append(
            {
                "code": "context_policy_completion_overclaim",
                "message": "current context-policy coverage must not claim full AlphaEvolve completeness",
            }
        )
    unsupported = record.get("unsupported_surfaces")
    required_unsupported = {
        "retrieval_summarization_policy",
        "learned_or_external_semantic_ranking_policy",
        "deep_retrieval_debug_refinement_loop",
        "non_promptsampler_prompt_builder_section_policy",
        "semantic_source_selection_policy",
    }
    if not isinstance(unsupported, list) or not all(
        isinstance(item, str) for item in unsupported
    ):
        issues.append(
            {
                "code": "invalid_unsupported_surfaces",
                "message": "unsupported_surfaces must be a list of strings",
            }
        )
        unsupported_count = 0
    else:
        unsupported_count = len(unsupported)
        for item in sorted(required_unsupported - set(unsupported)):
            issues.append(
                {
                    "code": "missing_unsupported_surface",
                    "message": f"missing unsupported context-policy surface {item}",
                }
            )
    limitations = record.get("limitations")
    required_limitations = {
        "coverage_tracks_current_validated_policy_schema_not_full_alphaevolve_context_control",
        "retrieval_and_summarization_policy_remain_fixed_code_or_config_paths",
        "semantic_context_selection_is_not_meta_prompt_evolved",
    }
    if not isinstance(limitations, list) or not all(
        isinstance(item, str) for item in limitations
    ):
        issues.append(
            {
                "code": "invalid_limitations",
                "message": "limitations must be a list of strings",
            }
        )
    else:
        for item in sorted(required_limitations - set(limitations)):
            issues.append(
                {
                    "code": "missing_limitation",
                    "message": f"missing context-policy limitation {item}",
                }
            )
    return {
        "schema": PROMPT_CONTEXT_POLICY_COVERAGE_VALIDATION_SCHEMA,
        "coverage_schema": (
            record.get("schema") if isinstance(record.get("schema"), str) else None
        ),
        "ok": not issues,
        "alphaevolve_context_policy_complete": False,
        "tunable_field_count": (
            record.get("tunable_field_count")
            if isinstance(record.get("tunable_field_count"), int)
            and not isinstance(record.get("tunable_field_count"), bool)
            else 0
        ),
        "unsupported_surface_count": unsupported_count,
        "issues": issues,
    }


def _context_policy_capability_fields(value: str) -> list[str]:
    return [field for field in value.split(",") if field]


def _prompt_section_packing_role_record(
    config: Config,
    *,
    role: str,
    prompt_builder: str,
    section_packing_status: str,
    section_packing_boundary: str,
    role_discovery: str,
    token_counter_capability: dict | None | object = ...,
) -> dict:
    capability = token_counter_capability
    if capability is ...:
        _, capability = discover_prompt_token_counter(
            config.backends,
            role=role,
            role_backend_indices=config.llm_role_backend_indices,
        )
    provider_ready = (
        section_packing_status == "supported"
        and isinstance(capability, dict)
        and capability.get("status") == "ready"
    )
    return {
        "role": role,
        "prompt_builder": prompt_builder,
        "role_discovery": role_discovery,
        "section_packing_status": section_packing_status,
        "section_packing_boundary": section_packing_boundary,
        "provider_token_section_packing_ready": provider_ready,
        "final_prompt_token_counting": (
            "role_scoped_llm_generate_boundary"
            if role != "feedback:*"
            else "dynamic_feedback_role_llm_generate_boundary"
        ),
        "token_counter_capability": copy.deepcopy(capability),
    }


def validate_prompt_section_packing_coverage(record: object) -> dict:
    """Validate prompt section-packing role coverage without upgrading claims."""
    issues: list[dict[str, str]] = []
    if not isinstance(record, Mapping):
        return {
            "schema": PROMPT_SECTION_PACKING_COVERAGE_VALIDATION_SCHEMA,
            "coverage_schema": None,
            "ok": False,
            "automatic_provider_token_section_packing_complete": False,
            "section_packing_role_count": 0,
            "ready_role_count": 0,
            "missing_role_count": 0,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "prompt section-packing coverage must be an object",
                }
            ],
        }
    if record.get("schema") != PROMPT_SECTION_PACKING_COVERAGE_SCHEMA:
        issues.append(
            {
                "code": "invalid_schema",
                "message": "unsupported prompt section-packing coverage schema",
            }
        )
    if record.get("policy") != "role_scoped_prompt_builder_section_packing_coverage_v1":
        issues.append(
            {
                "code": "invalid_policy",
                "message": "unsupported prompt section-packing coverage policy",
            }
        )
    roles = _validate_prompt_section_packing_roles(record.get("roles"), issues)
    role_names = [role["role"] for role in roles]
    if role_names != ["mutation", "critique", "feedback:*", "meta_prompt"]:
        issues.append(
            {
                "code": "unexpected_role_coverage",
                "message": "coverage must enumerate mutation, critique, feedback:*, and meta_prompt",
            }
        )
    section_roles = [
        role["role"]
        for role in roles
        if role["section_packing_status"] == "supported"
    ]
    ready_roles = [
        role["role"]
        for role in roles
        if role["section_packing_status"] == "supported"
        and role["provider_token_section_packing_ready"] is True
    ]
    missing_roles = [
        role["role"]
        for role in roles
        if role["section_packing_status"] != "supported"
        or role["provider_token_section_packing_ready"] is not True
    ]
    if record.get("section_packing_roles") != section_roles:
        issues.append(
            {
                "code": "section_packing_roles_mismatch",
                "message": "section_packing_roles must match supported role records",
            }
        )
    if record.get("provider_token_section_packing_ready_roles") != ready_roles:
        issues.append(
            {
                "code": "ready_roles_mismatch",
                "message": "ready role list must match provider-ready section-packing records",
            }
        )
    if record.get("provider_token_section_packing_missing_roles") != missing_roles:
        issues.append(
            {
                "code": "missing_roles_mismatch",
                "message": "missing role list must match unsupported or non-ready records",
            }
        )
    if record.get("automatic_provider_token_section_packing_complete") is not False:
        issues.append(
            {
                "code": "section_packing_overclaim",
                "message": "current coverage must not claim complete provider-token section packing",
            }
        )
    limitations = record.get("limitations")
    required_limitations = {
        "non_mutation_prompt_builders_do_not_use_promptsampler_section_packing",
        "feedback_roles_are_dynamic_and_discovered_at_llm_generate_boundary",
        "provider_token_section_packing_is_not_complete_for_all_prompt_roles",
    }
    if not isinstance(limitations, list) or not all(
        isinstance(item, str) for item in limitations
    ):
        issues.append(
            {
                "code": "invalid_limitations",
                "message": "limitations must be a list of strings",
            }
        )
    else:
        for item in sorted(required_limitations - set(limitations)):
            issues.append(
                {
                    "code": "missing_limitation",
                    "message": f"missing prompt section-packing limitation {item}",
                }
            )
    return {
        "schema": PROMPT_SECTION_PACKING_COVERAGE_VALIDATION_SCHEMA,
        "coverage_schema": (
            record.get("schema") if isinstance(record.get("schema"), str) else None
        ),
        "ok": not issues,
        "automatic_provider_token_section_packing_complete": False,
        "section_packing_role_count": len(section_roles),
        "ready_role_count": len(ready_roles),
        "missing_role_count": len(missing_roles),
        "issues": issues,
    }


def _validate_prompt_section_packing_roles(
    value: object,
    issues: list[dict[str, str]],
) -> list[Mapping[str, object]]:
    if not isinstance(value, list):
        issues.append(
            {
                "code": "invalid_roles",
                "message": "roles must be a list",
            }
        )
        return []
    roles: list[Mapping[str, object]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            issues.append(
                {
                    "code": "invalid_role_record",
                    "message": f"roles[{index}] must be an object",
                }
            )
            continue
        for field in (
            "role",
            "prompt_builder",
            "role_discovery",
            "section_packing_status",
            "section_packing_boundary",
            "final_prompt_token_counting",
        ):
            if not isinstance(item.get(field), str) or not item.get(field):
                issues.append(
                    {
                        "code": "invalid_role_field",
                        "message": f"roles[{index}].{field} must be non-empty text",
                    }
                )
        if item.get("section_packing_status") not in {"supported", "unsupported"}:
            issues.append(
                {
                    "code": "invalid_section_packing_status",
                    "message": "section_packing_status must be supported or unsupported",
                }
            )
        if not isinstance(item.get("provider_token_section_packing_ready"), bool):
            issues.append(
                {
                    "code": "invalid_provider_ready",
                    "message": "provider_token_section_packing_ready must be boolean",
                }
            )
        if (
            item.get("section_packing_status") == "unsupported"
            and item.get("provider_token_section_packing_ready") is True
        ):
            issues.append(
                {
                    "code": "unsupported_role_ready_overclaim",
                    "message": "unsupported roles must not be provider section-packing ready",
                }
            )
        capability = item.get("token_counter_capability")
        if capability is not None and not isinstance(capability, Mapping):
            issues.append(
                {
                    "code": "invalid_token_counter_capability",
                    "message": "token_counter_capability must be an object or null",
                }
            )
        roles.append(item)
    return roles


def _runtime_llm_budget_report(
    config: Config,
    scheduler_record: dict,
    *,
    llm: object | None = None,
) -> dict:
    status = scheduler_record.get("status")
    if status != "snapshot":
        reason = scheduler_record.get("reason")
        return {
            "schema": LLM_BUDGET_REPORT_SCHEMA,
            "status": status if isinstance(status, str) else "unavailable",
            "policy": LLM_BUDGET_REPORT_POLICY,
            "paper_budget_ready": False,
            "reason": (
                reason
                if isinstance(reason, str)
                else "llm_scheduler_snapshot_unavailable"
            ),
        }

    state = scheduler_record["state"]
    role_accounting = state.get("role_accounting")
    if not isinstance(role_accounting, dict) or not role_accounting:
        return {
            "schema": LLM_BUDGET_REPORT_SCHEMA,
            "status": "unavailable",
            "policy": LLM_BUDGET_REPORT_POLICY,
            "paper_budget_ready": False,
            "reason": "no_llm_role_accounting_records",
        }

    adapter_attempts_by_role = _runtime_llm_budget_adapter_attempts_by_role(llm)
    report = {
        "schema": LLM_BUDGET_REPORT_SCHEMA,
        "status": LLM_BUDGET_REPORT_STATUS,
        "policy": LLM_BUDGET_REPORT_POLICY,
        "run_id": config.run_id,
        "paper_budget_ready": False,
        "role_budgets": [
            _runtime_llm_budget_role_budget(config, role, summary)
            for role, summary in sorted(role_accounting.items())
            if isinstance(summary, dict)
        ],
        "role_usage": [
            _runtime_llm_budget_role_usage(
                role,
                summary,
                adapter_attempts=adapter_attempts_by_role.get(role, []),
            )
            for role, summary in sorted(role_accounting.items())
            if isinstance(summary, dict)
        ],
        "resume_state": {
            "persisted": True,
            "restored": scheduler_record.get("resume_status")
            == _LLM_SCHEDULER_RESUME_STATUS_RESTORED,
            "state_sha256": hashlib.sha256(
                json.dumps(state, sort_keys=True, separators=(",", ":")).encode(
                    "utf-8"
                )
            ).hexdigest(),
        },
        "runtime_policy_note": (
            "limits are derived from configured logical-call caps and observed "
            "role usage; provider-attempt, token, configured-cost, and "
            "wall-clock limits are live stop criteria before the next LLM call"
        ),
    }
    validation = validate_llm_budget_report(report)
    report["validation"] = {
        "ok": validation.ok,
        "paper_budget_ready": validation.paper_budget_ready,
        "run_id": validation.run_id,
        "role_count": validation.role_count,
        "issues": [
            {"code": issue.code, "message": issue.message}
            for issue in validation.issues
        ],
    }
    return report


def _runtime_llm_budget_adapter_attempts_by_role(llm: object | None) -> dict[str, list[dict]]:
    if not isinstance(llm, LLMEnsemble):
        return {}
    try:
        call_history = llm.call_history
    except Exception:
        return {}
    attempts_by_role: dict[str, list[dict]] = {}
    if not isinstance(call_history, list):
        return attempts_by_role
    for record in call_history:
        if not isinstance(record, dict):
            continue
        adapter_retry = record.get("adapter_retry")
        if not isinstance(adapter_retry, dict):
            continue
        role = record.get("role")
        if not isinstance(role, str):
            continue
        attempts_record = _runtime_llm_budget_adapter_attempt(record, adapter_retry)
        if attempts_record is None:
            continue
        attempts_by_role.setdefault(role, []).append(attempts_record)
    return attempts_by_role


def _runtime_llm_budget_adapter_attempt(
    record: Mapping[str, object],
    adapter_retry: Mapping[str, object],
) -> dict | None:
    max_retries = _nonnegative_int_or_none(adapter_retry.get("max_retries"))
    attempts = _positive_int_or_none(adapter_retry.get("attempts"))
    failed_attempts = _nonnegative_int_or_none(adapter_retry.get("failed_attempts"))
    if max_retries is None or attempts is None or failed_attempts is None:
        return None
    backend = record.get("backend_name")
    if not isinstance(backend, str) or not backend.strip():
        backend_idx = _nonnegative_int_or_none(record.get("backend_idx"))
        backend = f"backend_{backend_idx if backend_idx is not None else 'unknown'}"
    attempt_record: dict[str, object] = {
        "backend": backend,
        "provider_max_retries": max_retries,
        "attempts": attempts,
        "failed_attempts": failed_attempts,
    }
    for field in ("id", "sequence_id", "backend_idx", "status"):
        value = record.get(field)
        if isinstance(value, (str, int)) and not isinstance(value, bool):
            target = "call_id" if field == "id" else field
            attempt_record[target] = value
    failures = adapter_retry.get("failures")
    if isinstance(failures, list):
        attempt_record["failures"] = copy.deepcopy(failures)
    return attempt_record


def _runtime_llm_budget_role_budget(
    config: Config,
    role: str,
    summary: Mapping[str, object],
) -> dict:
    calls = _nonnegative_int_summary(summary.get("calls"))
    retry_limit = calls * max(0, config.llm_max_call_attempts - 1)
    role_limit = _role_scope_limit(config.llm_role_call_limits, role)
    observed_adapter_attempts = _nonnegative_int_summary(
        summary.get("provider_internal_attempts")
    )
    observed_tokens = _nonnegative_int_summary(summary.get("total_tokens"))
    observed_cost_usd = _cost_usd_from_microusd(summary.get("cost_microusd"))
    observed_seconds = _nonnegative_number_summary(summary.get("wall_clock_seconds"))
    role_adapter_attempt_limit = _role_scope_limit(
        config.llm_role_provider_attempt_limits,
        role,
    )
    configured_adapter_attempt_limit = (
        role_adapter_attempt_limit
        if role_adapter_attempt_limit is not None
        else config.max_llm_provider_attempts
    )
    adapter_attempt_limit = (
        max(configured_adapter_attempt_limit, observed_adapter_attempts)
        if configured_adapter_attempt_limit is not None
        else observed_adapter_attempts
    )
    role_token_limit = _role_scope_limit(config.llm_role_token_limits, role)
    configured_token_limit = (
        role_token_limit if role_token_limit is not None else config.max_llm_tokens
    )
    token_limit = (
        max(configured_token_limit, observed_tokens)
        if configured_token_limit is not None
        else None
    )
    role_cost_microusd_limit = _role_scope_limit(
        config.llm_role_cost_microusd_limits,
        role,
    )
    configured_cost_microusd_limit = (
        role_cost_microusd_limit
        if role_cost_microusd_limit is not None
        else config.max_llm_cost_microusd
    )
    configured_cost_usd_limit = (
        _cost_usd_from_microusd(configured_cost_microusd_limit)
        if configured_cost_microusd_limit is not None
        else None
    )
    cost_limit_usd = (
        max(configured_cost_usd_limit, observed_cost_usd)
        if configured_cost_usd_limit is not None
        else None
    )
    role_seconds_limit = _role_scope_limit(config.llm_role_seconds_limits, role)
    configured_seconds_limit = (
        role_seconds_limit
        if role_seconds_limit is not None
        else config.max_llm_seconds
    )
    seconds_limit = (
        max(configured_seconds_limit, observed_seconds)
        if configured_seconds_limit is not None
        else None
    )
    record = {
        "role": role,
        "logical_call_limit": (
            role_limit
            if role_limit is not None
            else config.max_llm_calls
            if config.max_llm_calls is not None
            else calls
        ),
        "retry_attempt_limit": retry_limit,
        "adapter_attempt_limit": adapter_attempt_limit,
        "configured_adapter_attempt_limit": configured_adapter_attempt_limit,
        "configured_token_limit": configured_token_limit,
        "configured_cost_limit_usd": configured_cost_usd_limit,
        "configured_wall_clock_limit_seconds": configured_seconds_limit,
        "limit_source": {
            "logical_call_limit": (
                "config.llm_role_call_limits"
                if role_limit is not None
                else "config.max_llm_calls"
                if config.max_llm_calls is not None
                else "observed_role_calls"
            ),
            "retry_attempt_limit": "config.llm_max_call_attempts_times_observed_role_calls",
            "adapter_attempt_limit": (
                "config.llm_role_provider_attempt_limits_or_observed_inflight_overshoot"
                if role_adapter_attempt_limit is not None
                else "config.max_llm_provider_attempts_or_observed_inflight_overshoot"
                if config.max_llm_provider_attempts is not None
                else "observed_provider_internal_attempts"
            ),
            "token_limit": (
                "config.llm_role_token_limits_or_observed_inflight_overshoot"
                if role_token_limit is not None
                else "config.max_llm_tokens_or_observed_inflight_overshoot"
                if config.max_llm_tokens is not None
                else "not_configured"
            ),
            "cost_limit_usd": (
                "config.llm_role_cost_microusd_limits_or_observed_inflight_overshoot"
                if role_cost_microusd_limit is not None
                else "config.max_llm_cost_microusd_or_observed_inflight_overshoot"
                if config.max_llm_cost_microusd is not None
                else "not_configured"
            ),
            "wall_clock_limit_seconds": (
                "config.llm_role_seconds_limits_or_observed_inflight_overshoot"
                if role_seconds_limit is not None
                else "config.max_llm_seconds_or_observed_inflight_overshoot"
                if config.max_llm_seconds is not None
                else "not_configured"
            ),
        },
    }
    if configured_adapter_attempt_limit is not None:
        record["configured_adapter_attempt_limit"] = configured_adapter_attempt_limit
    if token_limit is not None and token_limit > 0:
        record["token_limit"] = token_limit
    if cost_limit_usd is not None and cost_limit_usd > 0.0:
        record["cost_limit_usd"] = cost_limit_usd
    if seconds_limit is not None and seconds_limit > 0.0:
        record["wall_clock_limit_seconds"] = seconds_limit
    return record


def _role_scope_limit(limits: Mapping[str, object], role: str) -> object | None:
    matches = []
    if role in limits:
        matches.append(limits[role])
    matches.extend(
        value
        for scope, value in limits.items()
        if isinstance(scope, str)
        and scope.endswith(":*")
        and role.startswith(scope[:-1])
    )
    if not matches:
        return None
    return min(matches)


def _runtime_llm_budget_role_usage(
    role: str,
    summary: Mapping[str, object],
    *,
    adapter_attempts: list[dict],
) -> dict:
    adapter_attempt_count = _nonnegative_int_summary(
        summary.get("provider_internal_attempts")
    )
    retained_attempt_count = sum(
        _nonnegative_int_summary(attempt.get("attempts"))
        for attempt in adapter_attempts
    )
    if adapter_attempts:
        adapter_attempt_policy = (
            "retained_call_history_provider_retry_details"
            if retained_attempt_count == adapter_attempt_count
            else "bounded_call_history_provider_retry_details"
        )
    else:
        adapter_attempt_policy = "aggregate_only_provider_attempt_details_not_retained"
    return {
        "role": role,
        "logical_calls": _nonnegative_int_summary(summary.get("calls")),
        "retry_attempts": _nonnegative_int_summary(
            summary.get("ensemble_retry_attempts")
        ),
        "adapter_attempt_count": adapter_attempt_count,
        "total_tokens": _nonnegative_int_summary(summary.get("total_tokens")),
        "cost_usd": _cost_usd_from_microusd(summary.get("cost_microusd")),
        "wall_clock_seconds": _nonnegative_number_summary(
            summary.get("wall_clock_seconds")
        ),
        "adapter_attempts": copy.deepcopy(adapter_attempts),
        "adapter_attempt_policy": adapter_attempt_policy,
        "retained_adapter_attempt_count": retained_attempt_count,
    }


def _nonnegative_int_summary(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
    return value


def _cost_usd_from_microusd(value: object) -> float:
    return round(_nonnegative_int_summary(value) / 1_000_000, 6)


def _nonnegative_number_summary(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0.0:
        return 0.0
    return numeric


def _nonnegative_int_or_none(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _positive_int_or_none(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        return None
    return value


def load_runtime_llm_scheduler_state_snapshot(manifest_path: str | Path) -> dict:
    try:
        manifest = load_strict_json_object(Path(manifest_path))
    except StrictJsonlError as exc:
        raise RuntimeLLMSchedulerStateError(str(exc)) from exc
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        raise RuntimeLLMSchedulerStateError("manifest runtime must be an object")
    if "llm_scheduler" not in runtime:
        raise RuntimeLLMSchedulerStateError(
            "manifest runtime missing llm_scheduler snapshot"
        )
    return validate_runtime_llm_scheduler_state_snapshot(runtime["llm_scheduler"])


def load_runtime_budget_state_snapshot(manifest_path: str | Path) -> dict:
    try:
        manifest = load_strict_json_object(Path(manifest_path))
    except StrictJsonlError as exc:
        raise RuntimeBudgetStateError(str(exc)) from exc
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        raise RuntimeBudgetStateError("manifest runtime must be an object")
    wall_clock = runtime.get("wall_clock")
    if isinstance(wall_clock, dict):
        wall_clock = {
            field: wall_clock[field]
            for field in (
                "schema",
                "started_at",
                "updated_at",
                "finished_at",
                "runtime_seconds_source",
                "clock",
                "monotonic_budget_clock",
                "resume_segments",
            )
            if field in wall_clock
        }
    snapshot = {
        "wall_clock": wall_clock,
        "limits": runtime.get("limits"),
        "consumed": runtime.get("consumed"),
        "stop_reason": runtime.get("stop_reason"),
    }
    try:
        return validate_restored_budget_snapshot(snapshot)
    except BudgetSnapshotError as exc:
        raise RuntimeBudgetStateError(str(exc)) from exc


def load_full_resume_bundle(
    manifest_path: str | Path,
    *,
    history_path: str | Path | None = None,
    controller_budget_events_path: str | Path | None = None,
) -> dict:
    """Load all currently compatible runtime restore surfaces from one manifest.

    This is a direct-call resume bundle for checked runtime state. It does not
    replay provider outputs, async controller queues, plugin-owned state, or
    validator subprocess state.
    """
    manifest = Path(manifest_path)
    history = Path(history_path) if history_path is not None else manifest.parent / "history.jsonl"
    controller_events_path = (
        Path(controller_budget_events_path)
        if controller_budget_events_path is not None
        else manifest.parent / "controller_budget_events.jsonl"
    )
    try:
        rng_snapshot = load_runtime_rng_state_snapshot(manifest)
        llm_scheduler_snapshot = load_runtime_llm_scheduler_state_snapshot(manifest)
        budget_snapshot = load_runtime_budget_state_snapshot(manifest)
        lineage_replay_policy = load_runtime_lineage_replay_policy_snapshot(manifest)
        archive_bundle = load_archive_restore_bundle(manifest, history)
        controller_events = _load_controller_budget_events_restore_stream(
            controller_events_path
        )
        controller_budget_state = validate_controller_budget_state(
            {
                "schema": CONTROLLER_BUDGET_STATE_SCHEMA,
                "snapshot": budget_snapshot,
                "events": controller_events,
            }
        )
        budget_snapshot = _replay_controller_budget_events_to_snapshot(
            controller_budget_state,
        )
    except (BudgetSnapshotError, StrictJsonlError, ValueError) as exc:
        message = redact_sensitive_text(str(exc))
        raise RuntimeFullResumeBundleError(
            f"full resume bundle restore failed: {message}"
        ) from exc

    evolve_kwargs = {
        "runtime_rng_state_snapshot": rng_snapshot,
        "runtime_llm_scheduler_state_snapshot": llm_scheduler_snapshot,
        "runtime_archive_state_snapshot": archive_bundle["archive_state_snapshot"],
        "runtime_archive_programs_by_id": archive_bundle["archive_programs_by_id"],
        "runtime_budget_state_snapshot": budget_snapshot,
    }
    bundle = {
        "schema": _FULL_RESUME_BUNDLE_SCHEMA,
        "restore_entrypoint": "evolve",
        "manifest_name": manifest.name,
        "history_name": history.name,
        "controller_budget_events_name": controller_events_path.name,
        "evolve_kwargs": evolve_kwargs,
        "runtime_rng_replay_boundary": copy.deepcopy(rng_snapshot["replay_boundary"]),
        "lineage_replay_policy": lineage_replay_policy,
        "controller_budget_state": controller_budget_state,
        "controller_budget_replay": {
            "status": "replayed_and_applied_to_evolve_budget_snapshot",
            "event_count": len(controller_budget_state["events"]),
            "replay_entrypoint": "apply_controller_budget_event",
            "runtime_seconds_policy": "manifest_snapshot_authoritative",
        },
        "unsupported_surfaces": list(_FULL_RESUME_UNSUPPORTED_SURFACES),
    }
    validation = validate_full_resume_bundle(bundle)
    if not validation["ok"]:
        issues = ",".join(issue["code"] for issue in validation["issues"][:5])
        raise RuntimeFullResumeBundleError(
            f"full resume bundle validation failed: {issues}"
        )
    bundle["bundle_validation"] = validation
    return bundle


def validate_full_resume_bundle(bundle: object) -> dict:
    """Validate the composed full-resume bundle without upgrading replay claims."""
    issues: list[dict[str, str]] = []
    if not isinstance(bundle, Mapping):
        return {
            "schema": FULL_RESUME_BUNDLE_VALIDATION_SCHEMA,
            "bundle_schema": None,
            "ok": False,
            "compatible_resume_ready": False,
            "full_replay_ready": False,
            "provider_output_replay_ready": False,
            "pending_work_resume_ready": False,
            "unsupported_surface_count": 0,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "full resume bundle must be an object",
                }
            ],
        }
    if bundle.get("schema") != _FULL_RESUME_BUNDLE_SCHEMA:
        issues.append(
            {
                "code": "invalid_schema",
                "message": "unsupported full resume bundle schema",
            }
        )
    if bundle.get("restore_entrypoint") != "evolve":
        issues.append(
            {
                "code": "invalid_restore_entrypoint",
                "message": "full resume bundle restore_entrypoint must be evolve",
            }
        )
    for field in ("manifest_name", "history_name", "controller_budget_events_name"):
        if not isinstance(bundle.get(field), str) or not bundle.get(field):
            issues.append(
                {
                    "code": f"invalid_{field}",
                    "message": f"{field} must be non-empty text",
                }
            )
    kwargs = bundle.get("evolve_kwargs")
    if not isinstance(kwargs, Mapping):
        issues.append(
            {
                "code": "invalid_evolve_kwargs",
                "message": "evolve_kwargs must be an object",
            }
        )
        kwargs = {}
    _validate_full_resume_bundle_kwargs(kwargs, issues)
    _validate_full_resume_bundle_boundaries(bundle, kwargs, issues)
    controller_event_count = _validate_full_resume_controller_state(bundle, issues)
    _validate_full_resume_unsupported_surfaces(bundle.get("unsupported_surfaces"), issues)
    return {
        "schema": FULL_RESUME_BUNDLE_VALIDATION_SCHEMA,
        "bundle_schema": bundle.get("schema"),
        "ok": not issues,
        "compatible_resume_ready": not issues,
        "full_replay_ready": False,
        "provider_output_replay_ready": False,
        "pending_work_resume_ready": False,
        "controller_event_count": controller_event_count,
        "unsupported_surface_count": len(bundle.get("unsupported_surfaces", []))
        if isinstance(bundle.get("unsupported_surfaces"), list)
        else 0,
        "issues": issues,
        "limitations": [
            "provider_outputs_not_replayed",
            "controller_pending_work_not_restored",
            "plugin_internal_state_not_restored",
            "validator_subprocess_state_not_restored",
            "ordered_migration_event_replay_not_restore_engine",
        ],
    }


def _validate_full_resume_bundle_kwargs(
    kwargs: Mapping[str, object],
    issues: list[dict[str, str]],
) -> None:
    expected = {
        "runtime_rng_state_snapshot",
        "runtime_llm_scheduler_state_snapshot",
        "runtime_archive_state_snapshot",
        "runtime_archive_programs_by_id",
        "runtime_budget_state_snapshot",
    }
    missing = sorted(expected - set(kwargs))
    if missing:
        issues.append(
            {
                "code": "missing_evolve_kwargs",
                "message": f"evolve_kwargs missing restore inputs: {missing}",
            }
        )
    unsupported = sorted(set(kwargs) - expected)
    if unsupported:
        issues.append(
            {
                "code": "unsupported_evolve_kwargs",
                "message": f"evolve_kwargs has unsupported fields: {unsupported}",
            }
        )
    _record_validation_issue(
        issues,
        "invalid_runtime_rng_state_snapshot",
        lambda: validate_runtime_rng_state_snapshot(
            kwargs.get("runtime_rng_state_snapshot")
        ),
    )
    _record_validation_issue(
        issues,
        "invalid_runtime_llm_scheduler_state_snapshot",
        lambda: validate_runtime_llm_scheduler_state_snapshot(
            kwargs.get("runtime_llm_scheduler_state_snapshot")
        ),
    )
    _record_validation_issue(
        issues,
        "invalid_runtime_budget_state_snapshot",
        lambda: validate_restored_budget_snapshot(
            kwargs.get("runtime_budget_state_snapshot")
        ),
    )
    archive_state = kwargs.get("runtime_archive_state_snapshot")
    if not isinstance(archive_state, Mapping):
        issues.append(
            {
                "code": "invalid_runtime_archive_state_snapshot",
                "message": "runtime_archive_state_snapshot must be an object",
            }
        )
    else:
        archive_contents = archive_state.get("archive_contents")
        if not isinstance(archive_contents, Mapping):
            issues.append(
                {
                    "code": "missing_archive_contents",
                    "message": "runtime archive state must include archive_contents",
                }
            )
        migration_replay = archive_state.get("migration_replay")
        if (
            isinstance(migration_replay, Mapping)
            and migration_replay.get("replay_engine_supported") is True
        ):
            issues.append(
                {
                    "code": "migration_replay_overclaim",
                    "message": "full resume bundle must not claim ordered migration replay support",
                }
            )
    programs = kwargs.get("runtime_archive_programs_by_id")
    if not isinstance(programs, Mapping):
        issues.append(
            {
                "code": "invalid_runtime_archive_programs_by_id",
                "message": "runtime_archive_programs_by_id must be a mapping",
            }
        )
    elif any(not isinstance(program, Program) for program in programs.values()):
        issues.append(
            {
                "code": "invalid_runtime_archive_program_record",
                "message": "runtime archive program restore map must contain Program objects",
            }
        )


def _validate_full_resume_bundle_boundaries(
    bundle: Mapping[str, object],
    kwargs: Mapping[str, object],
    issues: list[dict[str, str]],
) -> None:
    rng_snapshot = kwargs.get("runtime_rng_state_snapshot")
    rng_boundary = (
        rng_snapshot.get("replay_boundary")
        if isinstance(rng_snapshot, Mapping)
        else None
    )
    if bundle.get("runtime_rng_replay_boundary") != rng_boundary:
        issues.append(
            {
                "code": "runtime_rng_replay_boundary_mismatch",
                "message": "bundle runtime_rng_replay_boundary must match RNG snapshot",
            }
        )
    _record_validation_issue(
        issues,
        "invalid_lineage_replay_policy",
        lambda: validate_runtime_lineage_replay_policy(
            bundle.get("lineage_replay_policy")
        ),
    )
    lineage_policy = bundle.get("lineage_replay_policy")
    if isinstance(lineage_policy, Mapping):
        provider_boundary = lineage_policy.get("provider_boundary")
        if (
            not isinstance(provider_boundary, Mapping)
            or provider_boundary.get("provider_outputs_replayed") is not False
        ):
            issues.append(
                {
                    "code": "provider_output_replay_overclaim",
                    "message": "lineage replay policy must keep provider outputs outside replay",
                }
            )
        if lineage_policy.get("full_replay_ready") is not False:
            issues.append(
                {
                    "code": "full_replay_overclaim",
                    "message": "current full resume bundle is not full replay ready",
                }
            )


def _validate_full_resume_controller_state(
    bundle: Mapping[str, object],
    issues: list[dict[str, str]],
) -> int:
    controller_state = bundle.get("controller_budget_state")
    event_count = 0
    try:
        validated = validate_controller_budget_state(controller_state)
        event_count = len(validated["events"])
    except (BudgetSnapshotError, ValueError, TypeError) as exc:
        issues.append(
            {
                "code": "invalid_controller_budget_state",
                "message": redact_sensitive_text(str(exc)),
            }
        )
    replay = bundle.get("controller_budget_replay")
    if not isinstance(replay, Mapping):
        issues.append(
            {
                "code": "invalid_controller_budget_replay",
                "message": "controller_budget_replay must be an object",
            }
        )
        return event_count
    expected = {
        "status": "replayed_and_applied_to_evolve_budget_snapshot",
        "replay_entrypoint": "apply_controller_budget_event",
        "runtime_seconds_policy": "manifest_snapshot_authoritative",
    }
    for field, expected_value in expected.items():
        if replay.get(field) != expected_value:
            issues.append(
                {
                    "code": f"invalid_controller_budget_replay_{field}",
                    "message": f"controller_budget_replay.{field} is unsupported",
                }
            )
    if replay.get("event_count") != event_count:
        issues.append(
            {
                "code": "controller_budget_replay_event_count_mismatch",
                "message": "controller_budget_replay event_count must match state events",
            }
        )
    return event_count


def _validate_full_resume_unsupported_surfaces(
    surfaces: object,
    issues: list[dict[str, str]],
) -> None:
    if not isinstance(surfaces, list):
        issues.append(
            {
                "code": "invalid_unsupported_surfaces",
                "message": "unsupported_surfaces must be a list",
            }
        )
        return
    if surfaces != list(_FULL_RESUME_UNSUPPORTED_SURFACES):
        issues.append(
            {
                "code": "unsupported_surfaces_mismatch",
                "message": "unsupported_surfaces must preserve current replay boundaries",
            }
        )


def _record_validation_issue(
    issues: list[dict[str, str]],
    code: str,
    validator: Callable[[], object],
) -> None:
    try:
        validator()
    except (BudgetSnapshotError, RuntimeRngStateError, RuntimeLLMSchedulerStateError, RuntimeLineageReplayPolicyError, ValueError, TypeError) as exc:
        issues.append({"code": code, "message": redact_sensitive_text(str(exc))})


def _load_controller_budget_events_restore_stream(path: Path) -> list[dict]:
    events = list(
        iter_strict_jsonl_objects(
            Path(path),
            stream_name="controller_budget_events.jsonl",
        )
    )
    return validate_controller_budget_state(
        {
            "schema": CONTROLLER_BUDGET_STATE_SCHEMA,
            "snapshot": _minimal_controller_budget_snapshot_for_event_validation(),
            "events": events,
        }
    )["events"]


def _replay_controller_budget_events_to_snapshot(
    controller_budget_state: Mapping[str, object],
) -> dict:
    replay = validate_controller_budget_replay_state(dict(controller_budget_state))
    return replay["snapshot"]


def controller_state_artifact_inventory(
    manifest: object | str | Path,
    artifact_root: str | Path,
) -> dict:
    """Verify terminal controller-state event stream evidence under a root."""
    data, issues = _load_controller_state_inventory_manifest(manifest)
    root = Path(artifact_root)
    records: list[dict[str, object]] = []
    controller_state = _manifest_controller_state(data) if data is not None else None
    artifacts = _manifest_artifacts(data) if data is not None else {}
    if controller_state is None and data is not None:
        issues.append(
            {
                "code": "missing_controller_state",
                "message": "manifest runtime.history.controller_state must be an object",
            }
        )
    elif controller_state is not None:
        record = _controller_event_stream_inventory_record(
            controller_state.get("event_stream"),
            artifacts,
            root,
        )
        records.append(record)
    verified_count = sum(1 for record in records if record["status"] == "verified")
    missing_count = sum(1 for record in records if record["status"] == "missing_file")
    mismatch_count = sum(
        1
        for record in records
        if record["status"]
        in {
            "hash_mismatch",
            "bytes_mismatch",
            "event_count_mismatch",
            "last_event_mismatch",
            "artifact_record_mismatch",
        }
    )
    invalid_count = sum(
        1
        for record in records
        if record["status"] in {"invalid_artifact", "unsafe_path", "read_error"}
    )
    if not records and data is not None and not issues:
        issues.append(
            {
                "code": "empty_controller_state_inventory",
                "message": "no controller-state artifact records were available to verify",
            }
        )
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return {
        "schema": CONTROLLER_STATE_ARTIFACT_INVENTORY_SCHEMA,
        "manifest_schema": data.get("schema") if isinstance(data, dict) else None,
        "controller_state_schema": (
            controller_state.get("schema") if isinstance(controller_state, dict) else None
        ),
        "artifact_root_policy": "safe_relative_controller_artifact_paths_under_artifact_root",
        "artifact_root_name": root.name,
        "artifact_count": len(records),
        "verified_count": verified_count,
        "missing_count": missing_count,
        "mismatch_count": mismatch_count,
        "invalid_count": invalid_count,
        "records_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "ok": (
            not issues
            and bool(records)
            and verified_count == len(records)
            and missing_count == 0
            and mismatch_count == 0
            and invalid_count == 0
        ),
        "issues": issues,
        "artifacts": records,
    }


def validate_controller_state_snapshot(controller_state: object) -> dict:
    """Validate the terminal synchronous controller-state boundary."""
    record = _controller_state_validation_record(controller_state)
    issues = list(record["issues"])
    overclaim_count = (
        1
        if record["status"] == "overclaim"
        else 0
    )
    invalid_count = (
        1
        if record["status"] == "invalid_record"
        else 0
    )
    payload = json.dumps(record, sort_keys=True, separators=(",", ":"))
    return {
        "schema": CONTROLLER_STATE_VALIDATION_SCHEMA,
        "controller_state_schema": (
            controller_state.get("schema")
            if isinstance(controller_state, dict)
            else None
        ),
        "controller_model": record.get("controller_model"),
        "resume_scope": record.get("resume_scope"),
        "status": record["status"],
        "terminal_drained": record["terminal_drained"],
        "pending_work_count": record["pending_work_count"],
        "overclaim_count": overclaim_count,
        "invalid_count": invalid_count,
        "records_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "ok": record["status"] == "verified" and not issues,
        "issues": issues,
        "record": record,
    }


def _controller_state_validation_record(controller_state: object) -> dict:
    if not isinstance(controller_state, dict):
        return {
            "status": "invalid_record",
            "controller_model": None,
            "resume_scope": None,
            "terminal_drained": False,
            "pending_work_count": 0,
            "issues": ["invalid_controller_state"],
        }
    issues: list[str] = []
    if controller_state.get("schema") != "libreevolve.controller_state.v1":
        issues.append("controller_state_schema_mismatch")
    if controller_state.get("status") != "terminal_synchronous_controller_drained":
        issues.append("controller_state_status_not_terminal_drained")
    controller_model = controller_state.get("controller_model")
    if controller_model != "single_process_serial_loop":
        issues.append("controller_model_not_single_process_serial_loop")
    resume_scope = controller_state.get("resume_scope")
    if resume_scope != "terminal_drained_state_only":
        issues.append("resume_scope_overclaimed")
    pending = controller_state.get("pending_work")
    pending_count = _controller_pending_work_count(pending, issues)
    terminal_drained = pending_count == 0 and not any(
        issue == "invalid_pending_work"
        or issue == "missing_pending_work_fields"
        or issue == "unsupported_pending_work_fields"
        or issue.startswith("invalid_pending_work_")
        for issue in issues
    )
    terminal = controller_state.get("terminal")
    if not isinstance(terminal, dict):
        issues.append("invalid_terminal_controller_state")
    else:
        if not isinstance(terminal.get("stop_reason"), str) or not terminal.get(
            "stop_reason"
        ):
            issues.append("invalid_terminal_stop_reason")
        for field in ("generations_completed", "evaluations"):
            value = terminal.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                issues.append(f"invalid_terminal_{field}")
    event_stream = controller_state.get("event_stream")
    if not isinstance(event_stream, dict):
        issues.append("invalid_controller_event_stream")
    else:
        if event_stream.get("replay_scope") != "budget_counters_only":
            issues.append("event_stream_replay_scope_overclaimed")
        event_count = event_stream.get("event_count")
        if (
            isinstance(event_count, bool)
            or not isinstance(event_count, int)
            or event_count < 0
        ):
            issues.append("invalid_event_stream_event_count")
        status = event_stream.get("status")
        if status not in {"present", "absent"}:
            issues.append("invalid_event_stream_status")
    for field in (
        "async_resume_ready",
        "pending_work_resume_ready",
        "full_replay_ready",
        "provider_output_replay_ready",
    ):
        if controller_state.get(field) is True:
            issues.append(f"{field}_overclaimed")
    limitations = controller_state.get("limitations")
    if not isinstance(limitations, list) or not all(
        isinstance(item, str) for item in limitations
    ):
        issues.append("invalid_controller_state_limitations")
    else:
        required = {
            "synchronous_terminal_snapshot_not_async_queue_checkpoint",
            "no_mid_generation_resume_boundary",
            "provider_outputs_not_replayed",
        }
        missing = sorted(required - set(limitations))
        issues.extend(f"missing_limitation_{item}" for item in missing)
    overclaim_codes = {
        "resume_scope_overclaimed",
        "event_stream_replay_scope_overclaimed",
        "async_resume_ready_overclaimed",
        "pending_work_resume_ready_overclaimed",
        "full_replay_ready_overclaimed",
        "provider_output_replay_ready_overclaimed",
    }
    if any(issue in overclaim_codes for issue in issues):
        status = "overclaim"
    elif issues:
        status = "invalid_record"
    else:
        status = "verified"
    return {
        "status": status,
        "controller_model": controller_model,
        "resume_scope": resume_scope,
        "terminal_drained": terminal_drained,
        "pending_work_count": pending_count,
        "event_stream_status": (
            event_stream.get("status") if isinstance(event_stream, dict) else None
        ),
        "event_count": (
            event_stream.get("event_count") if isinstance(event_stream, dict) else None
        ),
        "issues": sorted(set(issues)),
    }


def _controller_pending_work_count(
    pending: object,
    issues: list[str],
) -> int:
    if not isinstance(pending, dict):
        issues.append("invalid_pending_work")
        return 0
    expected = {
        "queued_proposals",
        "running_proposals",
        "queued_evaluations",
        "running_evaluations",
        "in_flight_llm_calls",
        "pending_archive_admissions",
        "partially_completed_generation",
    }
    extra = set(pending) - expected
    missing = expected - set(pending)
    if extra:
        issues.append("unsupported_pending_work_fields")
    if missing:
        issues.append("missing_pending_work_fields")
    total = 0
    for field in sorted(expected - {"partially_completed_generation"}):
        value = pending.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            issues.append(f"invalid_pending_work_{field}")
            continue
        total += value
    partial = pending.get("partially_completed_generation")
    if not isinstance(partial, bool):
        issues.append("invalid_pending_work_partially_completed_generation")
    elif partial:
        total += 1
    if total:
        issues.append("controller_pending_work_not_drained")
    return total


def _load_controller_state_inventory_manifest(
    manifest: object | str | Path,
) -> tuple[dict | None, list[dict[str, str]]]:
    if isinstance(manifest, dict):
        return dict(manifest), []
    if isinstance(manifest, (str, Path)):
        try:
            data = load_strict_json_object(Path(manifest), source="manifest.json")
        except (StrictJsonlError, OSError, ValueError) as exc:
            return (
                None,
                [
                    {
                        "code": "read_error",
                        "message": f"failed to read controller-state manifest: {exc}",
                    }
                ],
            )
        if isinstance(data, dict):
            return data, []
    return (
        None,
        [
            {
                "code": "invalid_manifest",
                "message": "controller-state artifact inventory requires a manifest object",
            }
        ],
    )


def _manifest_controller_state(manifest: dict) -> dict | None:
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        return None
    history = runtime.get("history")
    if not isinstance(history, dict):
        return None
    controller_state = history.get("controller_state")
    return controller_state if isinstance(controller_state, dict) else None


def _manifest_artifacts(manifest: dict) -> dict:
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        return {}
    artifacts = runtime.get("artifacts")
    return artifacts if isinstance(artifacts, dict) else {}


def _controller_event_stream_inventory_record(
    event_stream: object,
    artifacts: Mapping[str, object],
    root: Path,
) -> dict[str, object]:
    if not isinstance(event_stream, dict):
        return {
            "kind": "controller_budget_events",
            "path": "",
            "status": "invalid_artifact",
            "issues": ["invalid_controller_event_stream"],
        }
    path = event_stream.get("path")
    record: dict[str, object] = {
        "kind": "controller_budget_events",
        "path": path if isinstance(path, str) else "",
        "expected_status": event_stream.get("status")
        if isinstance(event_stream.get("status"), str)
        else None,
        "expected_event_count": event_stream.get("event_count")
        if isinstance(event_stream.get("event_count"), int)
        and not isinstance(event_stream.get("event_count"), bool)
        else None,
        "expected_last_sequence": event_stream.get("last_sequence"),
        "expected_last_kind": event_stream.get("last_kind")
        if isinstance(event_stream.get("last_kind"), str)
        else None,
        "status": "verified",
        "issues": [],
    }
    path_obj = Path(path) if isinstance(path, str) else None
    if (
        path_obj is None
        or not path
        or path_obj.is_absolute()
        or path.startswith(("/", "\\"))
        or ".." in path_obj.parts
    ):
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_controller_event_stream_path")
        return record
    artifact_record = artifacts.get(path) if isinstance(path, str) else None
    if not isinstance(artifact_record, dict):
        record["status"] = "artifact_record_mismatch"
        record["issues"].append("missing_controller_event_artifact_record")
    try:
        resolved_root = root.resolve()
        resolved_path = (resolved_root / path_obj).resolve(strict=False)
    except OSError:
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_controller_event_stream_path")
        return record
    if not resolved_path.is_relative_to(resolved_root):
        record["status"] = "unsafe_path"
        record["issues"].append("controller_event_stream_path_outside_root")
        return record
    if not resolved_path.exists():
        record["status"] = "missing_file"
        record["issues"].append("missing_controller_event_stream_file")
        return record
    if not resolved_path.is_file() or resolved_path.is_symlink():
        record["status"] = "unsafe_path"
        record["issues"].append("controller_event_stream_path_not_regular_file")
        return record
    try:
        raw = resolved_path.read_bytes()
        events = list(
            iter_strict_jsonl_objects(
                resolved_path,
                stream_name="controller_budget_events.jsonl",
            )
        )
    except (OSError, StrictJsonlError) as exc:
        record["status"] = "read_error"
        record["issues"].append("controller_event_stream_read_error")
        record["error"] = redact_sensitive_text(str(exc))
        return record
    actual_sha = hashlib.sha256(raw).hexdigest()
    actual_bytes = len(raw)
    record["actual_sha256"] = actual_sha
    record["actual_bytes"] = actual_bytes
    record["actual_event_count"] = len(events)
    record["actual_last_sequence"] = events[-1].get("sequence") if events else None
    record["actual_last_kind"] = events[-1].get("kind") if events else None
    _compare_controller_artifact_record(record, artifact_record, actual_sha, actual_bytes)
    if record["expected_status"] not in {None, "present"}:
        if record["status"] == "verified":
            record["status"] = "artifact_record_mismatch"
        record["issues"].append("controller_event_stream_not_present")
    if (
        record["expected_event_count"] is not None
        and record["expected_event_count"] != len(events)
    ):
        if record["status"] == "verified":
            record["status"] = "event_count_mismatch"
        record["issues"].append("controller_event_count_mismatch")
    if record["expected_last_sequence"] != record["actual_last_sequence"]:
        if record["status"] == "verified":
            record["status"] = "last_event_mismatch"
        record["issues"].append("controller_last_sequence_mismatch")
    if (
        record["expected_last_kind"] is not None
        and record["expected_last_kind"] != record["actual_last_kind"]
    ):
        if record["status"] == "verified":
            record["status"] = "last_event_mismatch"
        record["issues"].append("controller_last_kind_mismatch")
    return record


def _compare_controller_artifact_record(
    record: dict[str, object],
    artifact_record: object,
    actual_sha: str,
    actual_bytes: int,
) -> None:
    if not isinstance(artifact_record, dict):
        return
    exists = artifact_record.get("exists")
    if exists is not True:
        record["status"] = "artifact_record_mismatch"
        record["issues"].append("controller_event_artifact_record_not_existing")
    expected_sha = artifact_record.get("sha256")
    if not isinstance(expected_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        if record["status"] == "verified":
            record["status"] = "hash_mismatch"
        record["issues"].append("invalid_controller_event_artifact_hash")
    elif expected_sha != actual_sha:
        if record["status"] == "verified":
            record["status"] = "hash_mismatch"
        record["issues"].append("controller_event_artifact_hash_mismatch")
    expected_bytes = artifact_record.get("bytes")
    if (
        isinstance(expected_bytes, bool)
        or not isinstance(expected_bytes, int)
        or expected_bytes <= 0
    ):
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("invalid_controller_event_artifact_bytes")
    elif expected_bytes != actual_bytes:
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("controller_event_artifact_bytes_mismatch")


def _minimal_controller_budget_snapshot_for_event_validation() -> dict:
    budget = RunBudget.from_config(Config(max_generations=0))
    return budget.snapshot()


def validate_runtime_llm_scheduler_state_snapshot(
    snapshot: object,
    *,
    backend_count: int | None = None,
) -> dict:
    if not isinstance(snapshot, dict):
        raise RuntimeLLMSchedulerStateError("LLM scheduler snapshot must be an object")
    required = {"status", "schema", "state", "restore_entrypoint", "resume_status"}
    missing = required - set(snapshot)
    if missing:
        raise RuntimeLLMSchedulerStateError(
            f"LLM scheduler snapshot missing fields: {sorted(missing)}"
        )
    unsupported = set(snapshot) - required
    if unsupported:
        raise RuntimeLLMSchedulerStateError(
            f"LLM scheduler snapshot has unsupported fields: {sorted(unsupported)}"
        )
    if snapshot.get("status") != "snapshot":
        raise RuntimeLLMSchedulerStateError(
            "LLM scheduler snapshot status must be snapshot"
        )
    if snapshot.get("schema") != "libreevolve.llm_scheduler_state.v1":
        raise RuntimeLLMSchedulerStateError("unsupported LLM scheduler snapshot schema")
    if snapshot.get("restore_entrypoint") != "LLMEnsemble.restore_scheduler_state":
        raise RuntimeLLMSchedulerStateError(
            "unsupported LLM scheduler restore entrypoint"
        )
    if snapshot.get("resume_status") not in _LLM_SCHEDULER_RESUME_STATUSES:
        raise RuntimeLLMSchedulerStateError(
            "unsupported LLM scheduler resume status"
        )
    state = copy.deepcopy(snapshot["state"])
    try:
        json.dumps(state, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise RuntimeLLMSchedulerStateError(
            "LLM scheduler state snapshot must be finite JSON"
        ) from exc
    if backend_count is not None:
        try:
            validate_scheduler_state_snapshot(state, backend_count)
        except ValueError as exc:
            raise RuntimeLLMSchedulerStateError(
                f"LLM scheduler state is not restorable: {redact_sensitive_text(str(exc))}"
            ) from exc
    return {
        "status": snapshot["status"],
        "schema": snapshot["schema"],
        "state": state,
        "restore_entrypoint": snapshot["restore_entrypoint"],
        "resume_status": snapshot["resume_status"],
    }


def restore_runtime_llm_scheduler_state_snapshot(
    llm: object,
    snapshot: object,
) -> dict:
    if not isinstance(llm, LLMEnsemble):
        raise RuntimeLLMSchedulerStateError(
            "LLM scheduler snapshot restore requires LLMEnsemble"
        )
    validated = validate_runtime_llm_scheduler_state_snapshot(
        snapshot,
        backend_count=len(llm.backends),
    )
    llm.restore_scheduler_state(validated["state"])
    return validated


def _restore_llm_scheduler_state_snapshot(
    llm: object,
    snapshot: Mapping[str, object],
) -> dict:
    return restore_runtime_llm_scheduler_state_snapshot(llm, snapshot)


def _runtime_provider_cancellation_policy(
    config: Config,
    llm_scheduler_record: Mapping[str, object] | None = None,
) -> dict:
    provider_timeout_rules = [
        _provider_timeout_policy_rule(role, config)
        for role in ("mutation", "critique", "feedback:*", "meta_prompt")
    ]
    ensemble_timeout_rules = [
        _ensemble_timeout_policy_rule(role, config)
        for role in ("mutation", "critique", "feedback:*", "meta_prompt")
    ]
    policy = {
        "schema": PROVIDER_CANCELLATION_POLICY_SCHEMA,
        "policy_id": "libreevolve.runtime_llm_timeout_policy.v1",
        "hard_cancel_ready": False,
        "configured_limits": {
            "llm_call_timeout_sec": config.llm_call_timeout_sec,
            "max_runtime_seconds": config.max_runtime_seconds,
            "backend_timeout_fields": "per-backend timeout_sec",
            "llm_role_failure_quarantine_after": dict(
                sorted(config.llm_role_failure_quarantine_after.items())
            ),
        },
        "role_scope": {
            "policy": "libreevolve.llm_timeout_role_scope.v1",
            "roles": ["mutation", "critique", "feedback:*", "meta_prompt"],
            "source": "loop_llm_generate_roles",
        },
        "rules": [
            *provider_timeout_rules,
            *ensemble_timeout_rules,
            {
                "id": "runtime_deadline",
                "kind": "runtime_deadline",
                "role": "*",
                "budget_actions": ["stop_run"],
                "artifact_required": True,
                "artifact_kinds": ["budget_stop_record"],
                "description": (
                    "Remaining max_runtime_seconds clamps deadline-aware ensemble "
                    "attempts before each LLM call starts."
                ),
            },
        ],
        "artifacts": [
            _policy_artifact_record("timeout_log", "llm_calls.jsonl"),
            _policy_artifact_record("quarantine_record", "llm_calls.jsonl"),
            _policy_artifact_record("budget_stop_record", "manifest.json"),
        ],
    }
    validation = validate_provider_cancellation_policy(policy)
    return {
        "status": "valid" if validation.ok else "invalid",
        "policy": policy,
        "observations": _runtime_provider_cancellation_observations(
            llm_scheduler_record
        ),
        "validation": {
            "ok": validation.ok,
            "hard_cancel_ready": validation.hard_cancel_ready,
            "policy_id": validation.policy_id,
            "rule_count": validation.rule_count,
            "issues": [
                {"code": issue.code, "message": issue.message}
                for issue in validation.issues
            ],
        },
    }


def _runtime_provider_cancellation_observations(
    llm_scheduler_record: Mapping[str, object] | None,
) -> dict:
    base = {
        "schema": "libreevolve.provider_cancellation_observations.v1",
        "source": "runtime.llm_scheduler",
    }
    if not isinstance(llm_scheduler_record, Mapping):
        return {
            **base,
            "status": "unavailable",
            "reason": "llm_scheduler_snapshot_missing",
        }
    status = llm_scheduler_record.get("status")
    if status != "snapshot":
        reason = llm_scheduler_record.get("reason")
        return {
            **base,
            "status": status if isinstance(status, str) else "unavailable",
            "reason": (
                reason
                if isinstance(reason, str)
                else "llm_scheduler_snapshot_unavailable"
            ),
        }
    state = llm_scheduler_record.get("state")
    if not isinstance(state, Mapping):
        return {
            **base,
            "status": "invalid",
            "reason": "llm_scheduler_state_missing",
        }
    role_accounting = state.get("role_accounting")
    if not isinstance(role_accounting, Mapping):
        role_accounting = {}
    timeout_failures_by_role: dict[str, int] = {}
    for raw_role, raw_accounting in role_accounting.items():
        if not isinstance(raw_role, str) or not isinstance(raw_accounting, Mapping):
            continue
        timeout_failures = raw_accounting.get("timeout_failures")
        if (
            isinstance(timeout_failures, int)
            and not isinstance(timeout_failures, bool)
            and timeout_failures > 0
        ):
            timeout_failures_by_role[raw_role] = timeout_failures
    quarantine_state = state.get("provider_failure_policy_state")
    quarantine_thresholds: dict[str, int] = {}
    quarantined_backends_by_role: dict[str, int] = {}
    total_quarantined_backends = 0
    if isinstance(quarantine_state, Mapping):
        raw_thresholds = quarantine_state.get("role_quarantine_after")
        if isinstance(raw_thresholds, Mapping):
            for role, threshold in raw_thresholds.items():
                if (
                    isinstance(role, str)
                    and isinstance(threshold, int)
                    and not isinstance(threshold, bool)
                    and threshold > 0
                ):
                    quarantine_thresholds[role] = threshold
        roles = quarantine_state.get("roles")
        if isinstance(roles, Mapping):
            for role, role_state in roles.items():
                if not isinstance(role, str) or not isinstance(role_state, Mapping):
                    continue
                backends = role_state.get("backends")
                if not isinstance(backends, list):
                    continue
                count = sum(
                    1
                    for item in backends
                    if isinstance(item, Mapping) and item.get("quarantined") is True
                )
                if count > 0:
                    quarantined_backends_by_role[role] = count
                    total_quarantined_backends += count
    return {
        **base,
        "status": "snapshot",
        "timeout_failures_total": sum(timeout_failures_by_role.values()),
        "timeout_failures_by_role": dict(sorted(timeout_failures_by_role.items())),
        "quarantine_thresholds": dict(sorted(quarantine_thresholds.items())),
        "quarantined_backend_count": total_quarantined_backends,
        "quarantined_backends_by_role": dict(
            sorted(quarantined_backends_by_role.items())
        ),
        "hard_cancel_runtime_enforcement": "unsupported",
        "timeout_stop_runtime_enforcement": "unsupported",
        "remaining_gap": (
            "timeout observations are audit evidence only; SDK hard "
            "cancellation handles and timeout-driven stop policies remain open"
        ),
    }


def _provider_timeout_policy_rule(role: str, config: Config) -> dict:
    suffix = _policy_role_suffix(role)
    quarantine_enabled = _timeout_quarantine_enabled(role, config)
    return {
        "id": f"provider_request_timeout_{suffix}",
        "kind": "provider_request_timeout",
        "role": role,
        "budget_actions": _timeout_budget_actions(quarantine_enabled),
        "artifact_required": True,
        "artifact_kinds": _timeout_artifact_kinds(quarantine_enabled),
        "description": (
            "Bundled provider request timeout_sec values are forwarded to "
            f"provider clients for {role} calls and failures enter normal "
            "retry/fallback telemetry plus configured role/backend quarantine "
            "when that role has llm_role_failure_quarantine_after."
        ),
    }


def _ensemble_timeout_policy_rule(role: str, config: Config) -> dict:
    suffix = _policy_role_suffix(role)
    quarantine_enabled = _timeout_quarantine_enabled(role, config)
    return {
        "id": f"ensemble_wait_deadline_{suffix}",
        "kind": "ensemble_wait_deadline",
        "role": role,
        "budget_actions": _timeout_budget_actions(quarantine_enabled),
        "artifact_required": True,
        "artifact_kinds": _timeout_artifact_kinds(quarantine_enabled),
        "description": (
            "llm_call_timeout_sec wraps each ensemble backend attempt for "
            f"{role} calls and records ProviderCallTimeoutError timeout telemetry "
            "plus configured role/backend quarantine when that role has "
            "llm_role_failure_quarantine_after."
        ),
    }


def _timeout_quarantine_enabled(role: str, config: Config) -> bool:
    thresholds = config.llm_role_failure_quarantine_after
    if role.endswith(":*"):
        prefix = role[:-1]
        return any(candidate.startswith(prefix) for candidate in thresholds)
    return role in thresholds


def _timeout_budget_actions(quarantine_enabled: bool) -> list[str]:
    actions = ["retry", "fallback"]
    if quarantine_enabled:
        actions.append("quarantine")
    return actions


def _timeout_artifact_kinds(quarantine_enabled: bool) -> list[str]:
    kinds = ["timeout_log"]
    if quarantine_enabled:
        kinds.append("quarantine_record")
    return kinds


def _policy_role_suffix(role: str) -> str:
    return role.replace(":", "_").replace("*", "all")


def _policy_artifact_record(kind: str, path: str) -> dict:
    payload = f"{kind}:{path}:runtime_provider_cancellation_policy"
    return {
        "kind": kind,
        "path": path,
        "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "bytes": len(payload.encode("utf-8")),
    }


def _aggregate_llm_role_accounting(
    role_accounting: Mapping[str, Mapping[str, int | float]],
) -> dict[str, int | float]:
    totals: dict[str, int | float] = {}
    for summary in role_accounting.values():
        for field, value in summary.items():
            totals[field] = totals.get(field, 0) + value
    return totals


def _aggregate_llm_role_scheduler_state(
    role_scheduler_state: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    totals: dict[str, object] = {
        "counts": [],
        "wins": [],
        "total": 0,
        "unrewarded_success_call_count": 0,
        "rewarded_call_count": 0,
    }
    for summary in role_scheduler_state.values():
        counts = summary.get("counts")
        if isinstance(counts, list):
            totals["counts"] = _sum_numeric_vectors(totals["counts"], counts, int)
        wins = summary.get("wins")
        if isinstance(wins, list):
            totals["wins"] = _sum_numeric_vectors(totals["wins"], wins, float)
        total = summary.get("total")
        if isinstance(total, int) and not isinstance(total, bool):
            totals["total"] = int(totals["total"]) + total
        unrewarded = summary.get("unrewarded_success_call_ids")
        if isinstance(unrewarded, list):
            totals["unrewarded_success_call_count"] = int(
                totals["unrewarded_success_call_count"]
            ) + sum(len(items) for items in unrewarded if isinstance(items, list))
        rewarded = summary.get("rewarded_call_ids")
        if isinstance(rewarded, list):
            totals["rewarded_call_count"] = int(totals["rewarded_call_count"]) + len(
                rewarded
            )
    return totals


def _sum_numeric_vectors(left: object, right: list, cast: type) -> list:
    base = list(left) if isinstance(left, list) else []
    if len(base) < len(right):
        base.extend([0] * (len(right) - len(base)))
    for index, value in enumerate(right):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        base[index] = cast(base[index] + value)
    return base


def _runtime_rng_state(
    rng: random.Random,
    seed: int,
    *,
    resume_status: str = _RNG_RESUME_STATUS_RESTORE_SUPPORTED,
) -> dict:
    if resume_status not in _RNG_RESUME_STATUSES:
        raise ValueError("unsupported random state resume status")
    state = _serialize_rng_state(rng.getstate())
    state_sha256 = _hash_rng_state_payload(state)
    return {
        "status": "snapshot",
        "schema": "python.random.mt19937.v1",
        "engine": "python.random.Random",
        "seed": seed,
        "state": state,
        "state_sha256": state_sha256,
        "restore_entrypoint": "random.Random.setstate",
        "resume_status": resume_status,
        "replay_boundary": _runtime_rng_replay_boundary(),
    }


def _runtime_rng_replay_boundary() -> dict:
    return {
        "schema": _RNG_REPLAY_BOUNDARY_SCHEMA,
        "owned_rng": "framework_run_random",
        "restored_by_runtime_rng_snapshot": True,
        "owned_surfaces": list(_RNG_REPLAY_OWNED_SURFACES),
        "external_surfaces": copy.deepcopy(_RNG_REPLAY_EXTERNAL_SURFACES),
        "provider_rng_policy": "provider_outputs_not_replayed_by_framework_rng",
        "plugin_rng_policy": "plugin_internal_randomness_not_replayed_by_framework_rng",
    }


def _runtime_lineage_replay_policy() -> dict:
    return {
        "schema": _LINEAGE_REPLAY_POLICY_SCHEMA,
        "policy": "deterministic_loop_ids_with_explicit_external_boundaries",
        "loop_created_program_ids": {
            "seed_candidates": "deterministic_seed_index_workspace_hash",
            "generated_candidates": (
                "deterministic_generation_loop_index_proposal_parent_prompt_"
                "mutation_workspace_hash"
            ),
            "direct_program_default": "uuid4_excluded_from_replay_contract",
        },
        "prompt_program_ids": {
            "configured_seed_templates": "deterministic_index_template_hash",
            "mutated_prompt_templates": (
                "deterministic_parent_mutation_generation_template_hash"
            ),
            "direct_prompt_program_default": "uuid4_excluded_from_replay_contract",
        },
        "llm_call_ids": {
            "policy": (
                "deterministic_ordered_stream_role_backend_attempt_prompt_hash"
            ),
            "provider_output_replay": "not_supported",
        },
        "provider_boundary": {
            "provider_outputs_replayed": False,
            "provider_nondeterminism": "remote_or_sdk_outputs_not_replayed",
            "call_ids_do_not_prove_same_provider_output": True,
        },
        "covered_restore_surfaces": [
            "runtime_rng_snapshot",
            "llm_scheduler_snapshot",
            "archive_cursor_and_contents_snapshot",
            "full_resume_bundle_for_compatible_runtime_surfaces",
            "prompt_history_replay",
        ],
        "excluded_surfaces": [
            "direct Program() uuid4 defaults",
            "direct PromptProgram() uuid4 defaults",
            "provider/model outputs",
            "controller pending work",
            "plugin internal randomness",
            "validator subprocess randomness",
        ],
        "full_replay_ready": False,
        "remaining_gap": [
            "provider output capture or replay exclusion in resumed trace",
            "controller and pending evaluation state",
            "end-to-end parent prompt call archive sampling replay test",
        ],
    }


def load_runtime_lineage_replay_policy_snapshot(manifest_path: str | Path) -> dict:
    """Load and validate runtime.lineage_replay_policy from manifest.json."""
    try:
        manifest = load_strict_json_object(Path(manifest_path), source="manifest.json")
    except StrictJsonlError as exc:
        raise RuntimeLineageReplayPolicyError(str(exc)) from exc
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        raise RuntimeLineageReplayPolicyError("manifest runtime must be an object")
    if "lineage_replay_policy" not in runtime:
        raise RuntimeLineageReplayPolicyError(
            "manifest runtime missing lineage_replay_policy"
        )
    return validate_runtime_lineage_replay_policy(runtime["lineage_replay_policy"])


def validate_runtime_lineage_replay_policy(policy: object) -> dict:
    """Validate the loop-owned lineage/provider replay boundary."""
    if not isinstance(policy, dict):
        raise RuntimeLineageReplayPolicyError(
            "runtime lineage_replay_policy must be an object"
        )
    required = set(_runtime_lineage_replay_policy())
    missing = required - set(policy)
    if missing:
        raise RuntimeLineageReplayPolicyError(
            f"runtime lineage_replay_policy missing fields: {sorted(missing)}"
        )
    unsupported = set(policy) - required
    if unsupported:
        raise RuntimeLineageReplayPolicyError(
            "runtime lineage_replay_policy has unsupported fields: "
            f"{sorted(unsupported)}"
        )
    expected = _runtime_lineage_replay_policy()
    for field in (
        "schema",
        "policy",
        "loop_created_program_ids",
        "prompt_program_ids",
        "llm_call_ids",
        "provider_boundary",
        "covered_restore_surfaces",
        "excluded_surfaces",
        "full_replay_ready",
        "remaining_gap",
    ):
        if policy[field] != expected[field]:
            raise RuntimeLineageReplayPolicyError(
                f"runtime lineage_replay_policy {field} changed or overclaims replay support"
            )
    return copy.deepcopy(expected)


def _serialize_rng_state(state: object) -> dict:
    if not isinstance(state, tuple) or len(state) != 3:
        raise ValueError("random state must be a 3-item tuple")
    version, internal_state, gauss_next = state
    if not isinstance(version, int):
        raise ValueError("random state version must be an integer")
    if not isinstance(internal_state, tuple):
        raise ValueError("random internal state must be a tuple")
    internal_values: list[int] = []
    for index, value in enumerate(internal_state):
        if not isinstance(value, int):
            raise ValueError(f"random internal state value {index} must be an integer")
        internal_values.append(value)
    if gauss_next is not None:
        if not isinstance(gauss_next, (int, float)) or not math.isfinite(
            float(gauss_next)
        ):
            raise ValueError("random gaussian cache must be finite or null")
        gauss_next = float(gauss_next)
    return {
        "version": version,
        "internal_state": internal_values,
        "gauss_next": gauss_next,
    }


def load_runtime_rng_state_snapshot(manifest_path: str | Path) -> dict:
    """Load and validate runtime.rng from a strict manifest.json file."""
    try:
        manifest = load_strict_json_object(Path(manifest_path), source="manifest.json")
    except StrictJsonlError as exc:
        raise RuntimeRngStateError(str(exc)) from exc
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        raise RuntimeRngStateError("manifest runtime must be an object")
    if "rng" not in runtime:
        raise RuntimeRngStateError("manifest runtime missing rng snapshot")
    return validate_runtime_rng_state_snapshot(runtime["rng"])


def validate_runtime_rng_state_snapshot(snapshot: object) -> dict:
    """Validate a runtime.rng snapshot before future resume/replay use."""
    if not isinstance(snapshot, dict):
        raise RuntimeRngStateError("random state snapshot must be an object")
    required = {
        "status",
        "schema",
        "engine",
        "seed",
        "state",
        "state_sha256",
        "restore_entrypoint",
        "resume_status",
    }
    missing = required - set(snapshot)
    if missing:
        raise RuntimeRngStateError(
            f"random state snapshot missing fields: {sorted(missing)}"
        )
    optional = {"replay_boundary"}
    unsupported = set(snapshot) - required - optional
    if unsupported:
        raise RuntimeRngStateError(
            f"random state snapshot has unsupported fields: {sorted(unsupported)}"
        )
    if snapshot.get("status") != "snapshot":
        raise RuntimeRngStateError("random state snapshot status must be snapshot")
    if snapshot.get("schema") != "python.random.mt19937.v1":
        raise RuntimeRngStateError("unsupported random state snapshot schema")
    if snapshot.get("engine") != "python.random.Random":
        raise RuntimeRngStateError("unsupported random state snapshot engine")
    if snapshot.get("restore_entrypoint") != "random.Random.setstate":
        raise RuntimeRngStateError("unsupported random state restore entrypoint")
    if snapshot.get("resume_status") not in _RNG_RESUME_STATUSES:
        raise RuntimeRngStateError("unsupported random state resume status")
    replay_boundary = (
        _validate_runtime_rng_replay_boundary(snapshot["replay_boundary"])
        if "replay_boundary" in snapshot
        else _runtime_rng_replay_boundary()
    )
    seed = snapshot.get("seed")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise RuntimeRngStateError("random state seed must be an integer")

    raw_state = snapshot.get("state")
    if not isinstance(raw_state, dict):
        raise RuntimeRngStateError("random state snapshot must include state object")
    recorded_hash = snapshot.get("state_sha256")
    if not _is_sha256_hex(recorded_hash):
        raise RuntimeRngStateError("random state snapshot must include state_sha256")
    if _hash_rng_state_payload(raw_state) != recorded_hash:
        raise RuntimeRngStateError("random state snapshot hash mismatch")

    version = raw_state.get("version")
    internal_state = raw_state.get("internal_state")
    gauss_next = raw_state.get("gauss_next")
    if version != 3:
        raise RuntimeRngStateError("random state version must be 3")
    if not isinstance(internal_state, list):
        raise RuntimeRngStateError("random internal state must be a list")
    restored_internal: list[int] = []
    for index, value in enumerate(internal_state):
        if isinstance(value, bool) or not isinstance(value, int):
            raise RuntimeRngStateError(
                f"random internal state value {index} must be an integer"
            )
        restored_internal.append(value)
    if gauss_next is not None:
        if not isinstance(gauss_next, (int, float)) or not math.isfinite(
            float(gauss_next)
        ):
            raise RuntimeRngStateError("random gaussian cache must be finite or null")
        gauss_next = float(gauss_next)
    try:
        random.Random().setstate((version, tuple(restored_internal), gauss_next))
    except ValueError as exc:
        raise RuntimeRngStateError(f"random state is not restorable: {exc}") from exc
    return {
        "status": snapshot["status"],
        "schema": snapshot["schema"],
        "engine": snapshot["engine"],
        "seed": seed,
        "state": {
            "version": version,
            "internal_state": list(restored_internal),
            "gauss_next": gauss_next,
        },
        "state_sha256": recorded_hash,
        "restore_entrypoint": snapshot["restore_entrypoint"],
        "resume_status": snapshot["resume_status"],
        "replay_boundary": replay_boundary,
    }


def _validate_runtime_rng_replay_boundary(value: object) -> dict:
    if not isinstance(value, dict):
        raise RuntimeRngStateError("random state replay_boundary must be an object")
    required = {
        "schema",
        "owned_rng",
        "restored_by_runtime_rng_snapshot",
        "owned_surfaces",
        "external_surfaces",
        "provider_rng_policy",
        "plugin_rng_policy",
    }
    missing = required - set(value)
    if missing:
        raise RuntimeRngStateError(
            f"random state replay_boundary missing fields: {sorted(missing)}"
        )
    unsupported = set(value) - required
    if unsupported:
        raise RuntimeRngStateError(
            f"random state replay_boundary has unsupported fields: {sorted(unsupported)}"
        )
    if value["schema"] != _RNG_REPLAY_BOUNDARY_SCHEMA:
        raise RuntimeRngStateError("random state replay_boundary schema is unsupported")
    if value["owned_rng"] != "framework_run_random":
        raise RuntimeRngStateError("random state replay_boundary owned_rng is unsupported")
    if value["restored_by_runtime_rng_snapshot"] is not True:
        raise RuntimeRngStateError(
            "random state replay_boundary must restore the framework RNG"
        )
    owned_surfaces = _validate_rng_boundary_string_list(
        value["owned_surfaces"],
        "owned_surfaces",
    )
    if owned_surfaces != _RNG_REPLAY_OWNED_SURFACES:
        raise RuntimeRngStateError("random state replay_boundary owned_surfaces changed")
    external_surfaces = _validate_rng_external_surfaces(value["external_surfaces"])
    provider_policy = _validate_rng_boundary_text(
        value["provider_rng_policy"],
        "provider_rng_policy",
    )
    plugin_policy = _validate_rng_boundary_text(
        value["plugin_rng_policy"],
        "plugin_rng_policy",
    )
    return {
        "schema": value["schema"],
        "owned_rng": value["owned_rng"],
        "restored_by_runtime_rng_snapshot": True,
        "owned_surfaces": owned_surfaces,
        "external_surfaces": external_surfaces,
        "provider_rng_policy": provider_policy,
        "plugin_rng_policy": plugin_policy,
    }


def _validate_rng_boundary_string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list):
        raise RuntimeRngStateError(f"random state replay_boundary {field} must be a list")
    restored = []
    for index, item in enumerate(value):
        restored.append(
            _validate_rng_boundary_text(item, f"{field}[{index}]")
        )
    return restored


def _validate_rng_external_surfaces(value: object) -> list[dict]:
    if not isinstance(value, list):
        raise RuntimeRngStateError(
            "random state replay_boundary external_surfaces must be a list"
        )
    restored = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise RuntimeRngStateError(
                "random state replay_boundary external_surfaces"
                f"[{index}] must be an object"
            )
        required = {"surface", "restored_by_runtime_rng", "boundary"}
        missing = required - set(item)
        if missing:
            raise RuntimeRngStateError(
                "random state replay_boundary external_surfaces"
                f"[{index}] missing fields: {sorted(missing)}"
            )
        unsupported = set(item) - required
        if unsupported:
            raise RuntimeRngStateError(
                "random state replay_boundary external_surfaces"
                f"[{index}] has unsupported fields: {sorted(unsupported)}"
            )
        if item["restored_by_runtime_rng"] is not False:
            raise RuntimeRngStateError(
                "random state replay_boundary external surfaces must not be "
                "claimed as restored"
            )
        restored.append(
            {
                "surface": _validate_rng_boundary_text(
                    item["surface"],
                    f"external_surfaces[{index}].surface",
                ),
                "restored_by_runtime_rng": False,
                "boundary": _validate_rng_boundary_text(
                    item["boundary"],
                    f"external_surfaces[{index}].boundary",
                ),
            }
        )
    expected = copy.deepcopy(_RNG_REPLAY_EXTERNAL_SURFACES)
    if restored != expected:
        raise RuntimeRngStateError("random state replay_boundary external_surfaces changed")
    return restored


def _validate_rng_boundary_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise RuntimeRngStateError(
            f"random state replay_boundary {field} must be non-empty text"
        )
    if redact_sensitive_text(value) != value:
        raise RuntimeRngStateError(
            f"random state replay_boundary {field} must not contain secrets"
        )
    if len(value) > 160:
        raise RuntimeRngStateError(
            f"random state replay_boundary {field} is too long"
        )
    return value


def restore_runtime_rng_state_snapshot(snapshot: object) -> random.Random:
    validated = validate_runtime_rng_state_snapshot(snapshot)
    state = validated["state"]

    restored = random.Random()
    restored.setstate(
        (
            state["version"],
            tuple(state["internal_state"]),
            state["gauss_next"],
        )
    )
    return restored


def _restore_rng_state_snapshot(snapshot: Mapping[str, object]) -> random.Random:
    return restore_runtime_rng_state_snapshot(snapshot)


def _is_sha256_hex(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _hash_rng_state_payload(state: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(state, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
            "utf-8"
        )
    ).hexdigest()


def _manifest_safe_type_name(value: object) -> str:
    name = value.__class__.__name__
    redacted = redact_sensitive_text(name)
    if redacted and redacted == name:
        return redacted[:160]
    return "object"


def _runtime_artifact_pointers(run_dir: Path) -> dict:
    artifacts: dict[str, dict] = {}
    resolved_run_dir = _resolve_path_for_scope(run_dir)
    for name in (
        "history.jsonl",
        "failure_history.jsonl",
        "archive_events.jsonl",
        "history_invalid.jsonl",
        "failure_history_invalid.jsonl",
        "archive_events_invalid.jsonl",
        "controller_budget_events.jsonl",
        "controller_budget_events_invalid.jsonl",
        "llm_calls.jsonl",
        "llm_calls_invalid.jsonl",
        "prompt_history.jsonl",
        "prompt_history_invalid.jsonl",
        "manifest_invalid.jsonl",
        "evaluator_artifacts",
        "plugin_artifacts",
        "best.py",
        "best_workspace",
    ):
        path = run_dir / name
        artifacts[name] = _runtime_artifact_pointer(path, name, resolved_run_dir)
    return artifacts


def _runtime_artifact_pointer(path: Path, name: str, resolved_run_dir: Path) -> dict:
    record: dict[str, object] = {
        "path": name,
        "exists": None,
        "present": None,
        "is_symlink": None,
        "is_junction": None,
        "broken_link": False,
    }
    try:
        stat_result = path.lstat()
        record["present"] = True
    except FileNotFoundError:
        record["exists"] = False
        record["present"] = False
        record["is_symlink"] = False
        record["is_junction"] = False
        return record
    except OSError as exc:
        record["exists"] = None
        _append_artifact_error(record, "lstat", exc)
        return record

    is_symlink = _safe_artifact_predicate(record, "is_symlink", path.is_symlink)
    is_junction = _safe_artifact_predicate(record, "is_junction", lambda: _path_is_junction(path))
    link_like = bool(is_symlink) or bool(is_junction)
    record["is_symlink"] = is_symlink
    record["is_junction"] = is_junction

    if link_like:
        record["kind"] = "link"
        exists = _safe_artifact_predicate(record, "exists", path.exists)
        record["exists"] = exists
        record["broken_link"] = exists is False
        _attach_artifact_target_scope(record, path, resolved_run_dir)
        return record

    record["exists"] = True
    record["broken_link"] = False
    if stat_module.S_ISREG(stat_result.st_mode):
        record["kind"] = "file"
        record["bytes"] = stat_result.st_size
        try:
            raw = path.read_bytes()
        except OSError as exc:
            _append_artifact_error(record, "read", exc)
        else:
            record["sha256"] = hashlib.sha256(raw).hexdigest()
            record["hash_scope"] = "file_bytes"
    elif stat_module.S_ISDIR(stat_result.st_mode):
        record["kind"] = "directory"
        record.update(_runtime_artifact_tree_hash(path))
    else:
        record["kind"] = "other"
    return record


def _runtime_artifact_tree_hash(path: Path) -> dict:
    digest = hashlib.sha256()
    file_count = 0
    skipped_link_count = 0
    try:
        entries = sorted(path.rglob("*"), key=lambda item: item.as_posix())
    except OSError as exc:
        return {
            "tree_hash_status": "listing_error",
            "inspection_errors": [
                {
                    "operation": "tree_listing",
                    "error_type": exc.__class__.__name__,
                    "message": _bounded_redacted_text(
                        str(exc),
                        _MAX_ARTIFACT_ERROR_CHARS,
                    ),
                }
            ],
        }
    for entry in entries:
        try:
            is_link_like = entry.is_symlink() or _path_is_junction(entry)
        except OSError as exc:
            return {
                "tree_hash_status": "stat_error",
                "inspection_errors": [
                    {
                        "operation": "tree_stat",
                        "error_type": exc.__class__.__name__,
                        "message": _bounded_redacted_text(
                            str(exc),
                            _MAX_ARTIFACT_ERROR_CHARS,
                        ),
                    }
                ],
            }
        if is_link_like:
            skipped_link_count += 1
            continue
        try:
            if not entry.is_file():
                continue
            rel = entry.relative_to(path).as_posix()
            raw = entry.read_bytes()
        except OSError as exc:
            return {
                "tree_hash_status": "read_error",
                "inspection_errors": [
                    {
                        "operation": "tree_read",
                        "error_type": exc.__class__.__name__,
                        "message": _bounded_redacted_text(
                            str(exc),
                            _MAX_ARTIFACT_ERROR_CHARS,
                        ),
                    }
                ],
            }
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(raw).hexdigest().encode("ascii"))
        digest.update(b"\0")
        file_count += 1
    return {
        "tree_hash_status": "ok",
        "tree_hash": digest.hexdigest(),
        "tree_hash_scope": "relative_file_paths_and_sha256",
        "file_count": file_count,
        "skipped_link_count": skipped_link_count,
    }


def _path_is_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction()) if callable(is_junction) else False


def _safe_artifact_predicate(record: dict, field: str, predicate) -> bool | None:
    try:
        return bool(predicate())
    except OSError as exc:
        _append_artifact_error(record, field, exc)
        return None


def _attach_artifact_target_scope(record: dict, path: Path, resolved_run_dir: Path) -> None:
    try:
        if record.get("is_symlink"):
            raw_target = str(path.readlink())
            record["link_target_hash"] = hashlib.sha256(
                raw_target.encode("utf-8", errors="replace")
            ).hexdigest()
    except OSError as exc:
        _append_artifact_error(record, "readlink", exc)
    try:
        resolved_target = path.resolve(strict=True)
    except OSError as exc:
        record["target_scope"] = "unresolved"
        record["target_within_run_dir"] = None
        _append_artifact_error(record, "resolve", exc)
        return
    target_text = str(resolved_target)
    record["target_resolved_hash"] = hashlib.sha256(
        target_text.encode("utf-8", errors="replace")
    ).hexdigest()
    within_run = _path_within(resolved_target, resolved_run_dir)
    record["target_within_run_dir"] = within_run
    record["target_scope"] = "within_run_dir" if within_run else "outside_run_dir"
    record["target_path_redacted"] = True


def _resolve_path_for_scope(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError:
        return path.absolute()


def _path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _problem_config_source(problem: Problem) -> dict:
    source = getattr(problem, "config_source", None)
    if isinstance(source, dict):
        return dict(source)
    return {"path": "config.yaml", "status": "not_loaded"}


def _problem_dotenv_source(problem: Problem) -> dict | None:
    source = getattr(problem, "dotenv_source", None)
    if isinstance(source, dict):
        return dict(source)
    return None


def _append_artifact_error(record: dict, operation: str, exc: OSError) -> None:
    errors = record.setdefault("inspection_errors", [])
    if not isinstance(errors, list):
        errors = []
        record["inspection_errors"] = errors
    errors.append(
        {
            "operation": operation,
            "error_type": exc.__class__.__name__,
            "message": _bounded_redacted_text(str(exc), _MAX_ARTIFACT_ERROR_CHARS),
        }
    )


def _bounded_redacted_text(text: str, max_chars: int) -> str:
    redacted = redact_sensitive_text(text)
    if len(redacted) <= max_chars:
        return redacted
    suffix = "...<truncated>"
    if max_chars <= len(suffix):
        return redacted[:max_chars]
    return redacted[: max_chars - len(suffix)] + suffix


def _bounded_redacted_plugin_context_text(
    text: str,
    max_chars: int,
    *,
    truncation: str,
) -> str:
    if truncation == "head":
        return _bounded_redacted_text(text, max_chars)
    redacted = redact_sensitive_text(text)
    if len(redacted) <= max_chars:
        return redacted
    if max_chars <= 0:
        return ""
    head_chars = (max_chars + 1) // 2
    tail_chars = max_chars - head_chars
    if tail_chars <= 0:
        return redacted[:head_chars]
    return redacted[:head_chars] + redacted[-tail_chars:]


def _runtime_history_summary(db: ProgramDatabase, run_dir: Path, budget: RunBudget) -> dict:
    history_exists = (run_dir / "history.jsonl").exists()
    programs = db.all_programs()
    programs_logged = len(programs)
    archive_state = db.archive_state_snapshot()
    paper_metric_contract = _paper_evaluator_metric_contract_report(
        db,
        programs,
    )
    summary = {
        "programs_logged": programs_logged,
        "history_partially_written": history_exists,
        "no_candidates_evaluated": budget.evaluations == 0 and programs_logged == 0,
        "objective_frontier": db.objective_frontier_snapshot(),
        "objective_metric_leaders": db.objective_metric_leaders_snapshot(),
        "objective_metric_archives": db.objective_metric_archives_snapshot(),
        "score_index": db.score_index_snapshot(),
        "lineage_index": db.lineage_index_snapshot(),
        "descriptor_index": db.descriptor_index_snapshot(),
        "feedback_index": db.feedback_index_snapshot(),
        "resurfacing_index": db.resurfacing_index_snapshot(),
        "failure_index": db.failure_index_snapshot(),
        "hypothesis_index": db.hypothesis_index_snapshot(),
        "artifact_index": db.artifact_index_snapshot(),
        "paper_evaluator_metric_contract": paper_metric_contract,
        "paper_metric_table_export": _paper_metric_table_export_report(
            paper_metric_contract
        ),
        "task_spec_artifact_resolution_report": (
            _task_spec_artifact_resolution_report(
                db.startup_manifest_snapshot(),
                run_dir,
                programs,
                paper_metric_contract,
            )
        ),
        "initial_program_idea_provenance_report": (
            _initial_program_idea_provenance_report(
                db.startup_manifest_snapshot(),
                programs,
            )
        ),
        "candidate_abstraction_choice_report": (
            _candidate_abstraction_choice_report(
                db.startup_manifest_snapshot(),
                programs,
            )
        ),
        "marker_spelling_provenance_report": (
            _marker_spelling_provenance_report()
        ),
        "existing_codebase_integration_report": (
            _existing_codebase_integration_report(
                db.startup_manifest_snapshot(),
                programs,
            )
        ),
        "alphaevolve_process_exhibit_report": (
            _alphaevolve_process_exhibit_report(run_dir, programs)
        ),
        "evaluator_oracle_registry": _evaluator_oracle_registry_report(
            db,
            programs,
        ),
        "embedded_evaluator_entrypoint_report": (
            _embedded_evaluator_entrypoint_report(programs)
        ),
        "evaluation_cascade_report": _evaluation_cascade_report(programs),
        "evaluator_workload_report": _evaluator_workload_report(programs),
        "proposal_lifecycle_report": _proposal_lifecycle_report(db, programs),
        "hypothesis_branch_report": _hypothesis_branch_report(db, programs),
        "archive_state": archive_state,
        "archive_event_replay_audit": validate_archive_event_replay_audit(
            archive_event_replay_audit(
                run_dir / "archive_events.jsonl",
                archive_state,
            )
        ),
        "controller_state": _runtime_controller_state(run_dir, budget),
    }
    if summary["no_candidates_evaluated"]:
        absence_reason = _no_candidate_absence_reason(budget)
        summary["candidate_absence_reason"] = absence_reason
        if not history_exists:
            summary["history_absent_reason"] = absence_reason
    return summary


def _marker_spelling_provenance_report() -> dict:
    canonical_probe = _marker_spelling_parser_probe(
        "# EVOLVE-BLOCK-START solve\nx = 1\n# EVOLVE-BLOCK-END\n"
    )
    space_variant_probe = _marker_spelling_parser_probe(
        "# EVOLVE-BLOCK START solve\nx = 1\n# EVOLVE-BLOCK-END\n"
    )
    records = [
        {
            "record_id": "alphaevolve_section_2_1_page_4_start",
            "paper": "2506.13131__AlphaEvolve.pdf",
            "local_pdf_page": 4,
            "source_location": "Section 2.1 API prose",
            "marker_text": "# EVOLVE-BLOCK-START",
            "marker_role": "start",
            "source_surface": "section_prose",
            "provisional_classification": "canonical_marker_spelling",
            "local_parser_probe": canonical_probe,
            "local_support": "supported",
            "source_artifact": _marker_source_artifact_placeholder(),
        },
        {
            "record_id": "alphaevolve_section_2_1_page_4_end",
            "paper": "2506.13131__AlphaEvolve.pdf",
            "local_pdf_page": 4,
            "source_location": "Section 2.1 API prose",
            "marker_text": "# EVOLVE-BLOCK-END",
            "marker_role": "end",
            "source_surface": "section_prose",
            "provisional_classification": "canonical_marker_spelling",
            "local_parser_probe": canonical_probe,
            "local_support": "supported",
            "source_artifact": _marker_source_artifact_placeholder(),
        },
        {
            "record_id": "alphaevolve_figure_3a_page_6_space_start",
            "paper": "2506.13131__AlphaEvolve.pdf",
            "local_pdf_page": 6,
            "source_location": "Figure 3(a) extracted/rendered marker text",
            "marker_text": "# EVOLVE-BLOCK START",
            "marker_role": "start",
            "source_surface": "figure_text_extraction",
            "provisional_classification": (
                "figure_text_variant_or_extraction_uncertainty"
            ),
            "local_parser_probe": space_variant_probe,
            "local_support": "unsupported_current_parser",
            "source_artifact": _marker_source_artifact_placeholder(),
        },
        {
            "record_id": "alphaevolve_figure_3a_page_6_hyphenated_start",
            "paper": "2506.13131__AlphaEvolve.pdf",
            "local_pdf_page": 6,
            "source_location": "Figure 3(a) extracted/rendered marker text",
            "marker_text": "# EVOLVE-BLOCK-START",
            "marker_role": "start",
            "source_surface": "figure_text_extraction",
            "provisional_classification": "canonical_marker_spelling_in_figure",
            "local_parser_probe": canonical_probe,
            "local_support": "supported",
            "source_artifact": _marker_source_artifact_placeholder(),
        },
    ]
    report = {
        "schema": "libreevolve.marker_spelling_provenance_report.v1",
        "source": "alphaevolve_paper_source_locations_and_local_parser_probe",
        "canonical_start_marker": "# EVOLVE-BLOCK-START",
        "canonical_end_marker": "# EVOLVE-BLOCK-END",
        "record_count": len(records),
        "records": records,
        "compatibility_decision": {
            "policy": "canonical_hyphenated_markers_only",
            "space_variant_supported": False,
            "space_variant_probe_error": space_variant_probe["error"],
            "compatibility_mode": "not_configured",
            "documentation_policy": (
                "document Figure 3 space spelling as source variant or extraction "
                "uncertainty, not as supported parser syntax"
            ),
        },
        "claim_ready": False,
        "claim_readiness": {
            "source_locations_recorded": True,
            "parser_probe_recorded": True,
            "compatibility_decision_recorded": True,
            "source_artifact_hashes_attached": False,
            "source_screenshots_attached": False,
            "final_variant_classification": False,
            "remaining_gap": [
                "source_pdf_excerpt_or_screenshot_hashes",
                "exact_figure_3_text_artifact",
                "final_classification_as_rendered_text_ocr_or_paper_typo",
                "optional_space_variant_compatibility_mode_if_intended",
            ],
        },
    }
    report["validation"] = validate_marker_spelling_provenance_report(report)
    return report


def _marker_spelling_parser_probe(code: str) -> dict:
    error = validate_evolve_blocks(code)
    blocks = extract_evolve_blocks(code) if error is None else []
    return {
        "sample_sha256": hashlib.sha256(code.encode("utf-8")).hexdigest(),
        "accepted": error is None,
        "error": error,
        "block_count": len(blocks),
        "block_names": [block.name for block in blocks],
    }


def _marker_source_artifact_placeholder() -> dict:
    return {
        "status": "not_attached",
        "artifact_path": None,
        "sha256": None,
        "reason": "paper source screenshot_or_exact_excerpt_not_generated_in_this_report",
    }


def _initial_program_idea_provenance_report(
    startup_manifest: Mapping[str, object],
    programs: list[Program],
) -> dict:
    problem = (
        startup_manifest.get("problem")
        if isinstance(startup_manifest.get("problem"), Mapping)
        else {}
    )
    seed_sources = (
        problem.get("seed_sources")
        if isinstance(problem.get("seed_sources"), list)
        else []
    )
    seed_programs = [
        program
        for program in programs
        if isinstance(program.metadata, Mapping)
        and program.metadata.get("candidate_type") == "seed"
    ]
    seed_programs_by_index = {
        program.metadata.get("seed_index"): program
        for program in seed_programs
        if isinstance(program.metadata.get("seed_index"), int)
        and not isinstance(program.metadata.get("seed_index"), bool)
    }
    records = [
        _initial_program_idea_record(index, source, seed_programs_by_index.get(index))
        for index, source in enumerate(seed_sources)
        if isinstance(source, Mapping)
    ]
    retained_records = records[:50]
    annotated_count = sum(
        1 for record in retained_records if record["idea_metadata_present"]
    )
    origin_counts: dict[str, int] = {}
    for record in retained_records:
        origin = record["seed_idea_origin"]
        origin_counts[origin] = origin_counts.get(origin, 0) + 1
    report = {
        "schema": "libreevolve.initial_program_idea_provenance_report.v1",
        "source": "seed_source_metadata_and_generation_zero_history",
        "seed_source_count": len(seed_sources),
        "seed_program_count": len(seed_programs),
        "record_count": len(retained_records),
        "annotated_seed_count": annotated_count,
        "unknown_origin_count": origin_counts.get("unknown", 0),
        "origin_counts": origin_counts,
        "records": retained_records,
        "records_limit": 50,
        "records_truncated": len(records) > 50,
        "metadata_contract": {
            "manifest_path": "problem.seed_sources",
            "optional_fields": [
                "seed_variant_id",
                "seed_idea_origin",
                "seed_idea_label",
                "seed_idea_summary",
                "seed_contribution_roles",
                "seed_prior_technique",
                "seed_background_refs",
            ],
            "allowed_idea_origins": [
                "unknown",
                "simple_baseline",
                "random_baseline",
                "researcher_idea",
                "prior_art_derived",
                "collaboration_enhanced",
            ],
        },
        "claim_ready": False,
        "claim_readiness": {
            "seed_source_identity_recorded": bool(seed_sources),
            "generation_zero_history_linked": len(seed_programs) == len(records),
            "idea_origin_metadata_present": annotated_count == len(records)
            and len(records) > 0,
            "human_or_background_contribution_labels": all(
                bool(record["seed_contribution_roles"]) for record in records
            )
            and len(records) > 0,
            "seed_variant_ids_recorded": all(
                isinstance(record.get("seed_variant_id"), str)
                for record in records
            )
            and len(records) > 0,
            "evaluator_metric_linkage": all(
                bool(record["runtime"].get("metric_names")) for record in records
            )
            and len(records) > 0,
            "equal_budget_seed_variant_results": False,
            "alphaevolve_human_seeded_benchmark_parity": False,
            "remaining_gap": [
                "seed_variant_result_table",
                "equal_budget_simple_random_researcher_seed_comparison",
                "matrix_and_constructive_math_seed_variant_reports",
                "human_contribution_review_or_signoff",
                "prompt_context_to_seed_idea_linkage",
            ],
        },
    }
    report["validation"] = validate_initial_program_idea_provenance_report(report)
    return report


def _initial_program_idea_record(
    index: int,
    source: Mapping[str, object],
    program: Program | None,
) -> dict:
    origin = source.get("seed_idea_origin")
    if not isinstance(origin, str):
        origin = "unknown"
    roles = source.get("seed_contribution_roles")
    if not isinstance(roles, list):
        roles = []
    background_refs = source.get("seed_background_refs")
    if not isinstance(background_refs, list):
        background_refs = []
    idea_fields = [
        "seed_variant_id",
        "seed_idea_origin",
        "seed_idea_label",
        "seed_idea_summary",
        "seed_contribution_roles",
        "seed_prior_technique",
        "seed_background_refs",
    ]
    runtime = {
        "program_id": None,
        "workspace_sha256": None,
        "metric_names": [],
        "fitness": None,
        "evaluator_validity": None,
        "history_linked": False,
    }
    if program is not None:
        evaluation = (
            program.evaluation
            if isinstance(program.evaluation, Mapping)
            else {}
        )
        runtime = {
            "program_id": program.id,
            "workspace_sha256": _workspace_sha256(program.workspace()),
            "metric_names": sorted(
                name for name in program.metrics if name != "is_valid"
            ),
            "fitness": program.fitness,
            "evaluator_validity": evaluation.get("is_valid"),
            "history_linked": True,
        }
    return {
        "seed_index": source.get("seed_index", index),
        "seed_source_kind": source.get("seed_source_kind"),
        "seed_source_path": source.get("seed_source_path"),
        "primary_file": source.get("primary_file"),
        "seed_variant_id": source.get("seed_variant_id"),
        "seed_idea_origin": origin,
        "seed_idea_label": source.get("seed_idea_label"),
        "seed_idea_summary_present": isinstance(source.get("seed_idea_summary"), str),
        "seed_contribution_roles": roles,
        "seed_prior_technique": source.get("seed_prior_technique"),
        "seed_background_refs": background_refs,
        "idea_metadata_present": any(field in source for field in idea_fields),
        "runtime": runtime,
        "equal_budget_variant_evidence": "not_recorded",
    }


def validate_initial_program_idea_provenance_report(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.initial_program_idea_provenance_report.v1",
            "ok": False,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "initial-program idea provenance report must be an object",
                }
            ],
        }
    required = {
        "schema",
        "source",
        "seed_source_count",
        "seed_program_count",
        "record_count",
        "annotated_seed_count",
        "unknown_origin_count",
        "origin_counts",
        "records",
        "metadata_contract",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append(
            {
                "code": "missing_fields",
                "message": f"initial-program idea report missing fields: {sorted(missing)}",
            }
        )
    if report.get("schema") != "libreevolve.initial_program_idea_provenance_report.v1":
        issues.append(
            {
                "code": "invalid_schema",
                "message": "unsupported initial-program idea report schema",
            }
        )
    if report.get("source") != "seed_source_metadata_and_generation_zero_history":
        issues.append(
            {
                "code": "invalid_source",
                "message": "unsupported initial-program idea report source",
            }
        )
    records = report.get("records")
    if not isinstance(records, list):
        issues.append({"code": "invalid_records", "message": "records must be a list"})
        records = []
    _validate_report_count(report, "record_count", len(records), issues)
    annotated_count = 0
    unknown_count = 0
    origin_counts: dict[str, int] = {}
    allowed_origins = {
        "unknown",
        "simple_baseline",
        "random_baseline",
        "researcher_idea",
        "prior_art_derived",
        "collaboration_enhanced",
    }
    allowed_roles = {
        "human_seed_author",
        "researcher_idea",
        "background_knowledge",
        "prior_art",
        "collaborator_feedback",
        "automated_baseline_generator",
    }
    for record in records:
        if not isinstance(record, Mapping):
            issues.append(
                {"code": "invalid_record", "message": "records must be objects"}
            )
            continue
        seed_index = record.get("seed_index")
        if not isinstance(seed_index, int) or isinstance(seed_index, bool) or seed_index < 0:
            issues.append(
                {
                    "code": "invalid_seed_index",
                    "message": "seed_index must be a non-negative integer",
                }
            )
        origin = record.get("seed_idea_origin")
        if origin not in allowed_origins:
            issues.append(
                {
                    "code": "invalid_seed_idea_origin",
                    "message": "seed_idea_origin is unsupported",
                }
            )
        else:
            origin_counts[origin] = origin_counts.get(origin, 0) + 1
            if origin == "unknown":
                unknown_count += 1
        if record.get("idea_metadata_present") is True:
            annotated_count += 1
        roles = record.get("seed_contribution_roles")
        if not isinstance(roles, list):
            issues.append(
                {
                    "code": "invalid_seed_contribution_roles",
                    "message": "seed_contribution_roles must be a list",
                }
            )
        else:
            for role in roles:
                if role not in allowed_roles:
                    issues.append(
                        {
                            "code": "invalid_seed_contribution_role",
                            "message": "seed contribution role is unsupported",
                        }
                    )
        runtime = record.get("runtime")
        if not isinstance(runtime, Mapping):
            issues.append(
                {"code": "invalid_runtime_link", "message": "runtime must be an object"}
            )
        else:
            workspace_hash = runtime.get("workspace_sha256")
            if workspace_hash is not None and not _is_sha256_hex(workspace_hash):
                issues.append(
                    {
                        "code": "invalid_workspace_hash",
                        "message": "runtime workspace hash must be sha256 hex",
                    }
                )
            metric_names = runtime.get("metric_names")
            if not isinstance(metric_names, list) or not all(
                isinstance(item, str) for item in metric_names
            ):
                issues.append(
                    {
                        "code": "invalid_metric_names",
                        "message": "runtime metric_names must be a list of strings",
                    }
                )
        if record.get("equal_budget_variant_evidence") != "not_recorded":
            issues.append(
                {
                    "code": "equal_budget_variant_overclaim",
                    "message": "equal-budget seed-variant evidence must remain not_recorded",
                }
            )
    _validate_report_count(report, "annotated_seed_count", annotated_count, issues)
    _validate_report_count(report, "unknown_origin_count", unknown_count, issues)
    if report.get("origin_counts") != origin_counts:
        issues.append(
            {
                "code": "origin_counts_mismatch",
                "message": "origin_counts must match records",
            }
        )
    contract = report.get("metadata_contract")
    if not isinstance(contract, Mapping):
        issues.append(
            {
                "code": "invalid_metadata_contract",
                "message": "metadata_contract must be an object",
            }
        )
    elif contract.get("manifest_path") != "problem.seed_sources":
        issues.append(
            {
                "code": "invalid_metadata_manifest_path",
                "message": "metadata contract must point at problem.seed_sources",
            }
        )
    readiness = report.get("claim_readiness")
    if not isinstance(readiness, Mapping):
        issues.append(
            {
                "code": "invalid_claim_readiness",
                "message": "claim_readiness must be an object",
            }
        )
    else:
        if readiness.get("equal_budget_seed_variant_results") is not False:
            issues.append(
                {
                    "code": "equal_budget_results_overclaim",
                    "message": "equal-budget seed-variant results must remain false",
                }
            )
        if readiness.get("alphaevolve_human_seeded_benchmark_parity") is not False:
            issues.append(
                {
                    "code": "human_seeded_parity_overclaim",
                    "message": "AlphaEvolve human-seeded benchmark parity must remain false",
                }
            )
    if report.get("claim_ready") is not False:
        issues.append(
            {
                "code": "claim_ready_overclaim",
                "message": "initial-program idea report must not claim full parity",
            }
        )
    return {
        "schema": "libreevolve.initial_program_idea_provenance_report.v1",
        "ok": not issues,
        "issues": issues,
    }


def _candidate_abstraction_choice_report(
    startup_manifest: Mapping[str, object],
    programs: list[Program],
) -> dict:
    policies = (
        startup_manifest.get("policies")
        if isinstance(startup_manifest.get("policies"), Mapping)
        else {}
    )
    candidate_policy = (
        policies.get("candidate_language")
        if isinstance(policies.get("candidate_language"), Mapping)
        else {}
    )
    policy_validation = validate_candidate_language_policy(candidate_policy)
    runtime_records = [_candidate_abstraction_runtime_record(program) for program in programs]
    python_file_count = sum(record["python_file_count"] for record in runtime_records)
    non_python_text_file_count = sum(
        record["non_python_text_file_count"] for record in runtime_records
    )
    static_member_count = sum(record["static_member_count"] for record in runtime_records)
    report = {
        "schema": "libreevolve.candidate_abstraction_choice_report.v1",
        "source": "candidate_language_policy_and_runtime_workspaces",
        "selected_abstraction": "code_file_set",
        "selected_representation": {
            "manifest_path": "policies.candidate_language",
            "policy": candidate_policy.get("policy"),
            "candidate_representation": candidate_policy.get(
                "candidate_representation"
            ),
            "primary_language": candidate_policy.get("primary_language"),
            "language_runner_ready": candidate_policy.get("language_runner_ready"),
            "policy_validation": policy_validation,
        },
        "serializer_runner_linkage": {
            "workspace_serializer": "CandidateWorkspace.to_dict",
            "workspace_materializer": "best_workspace_and_evaluator_temp_workspace",
            "mutation_applier": "apply_workspace_mutation",
            "validator_runner": (
                candidate_policy.get("runner_policy", {}).get("validator_runner")
                if isinstance(candidate_policy.get("runner_policy"), Mapping)
                else None
            ),
            "problem_defined_serializer_hooks": "unsupported",
            "problem_defined_runner_hooks": "unsupported",
        },
        "runtime_candidate_shape": {
            "program_count": len(programs),
            "workspace_program_count": len(runtime_records),
            "python_file_count": python_file_count,
            "non_python_text_file_count": non_python_text_file_count,
            "static_member_count": static_member_count,
            "program_record_count": min(len(runtime_records), 50),
            "program_records_limit": 50,
            "program_records_truncated": len(runtime_records) > 50,
            "program_records": runtime_records[:50],
        },
        "abstraction_options": [
            {
                "option": "direct_solution",
                "local_status": "supported_as_python_file_or_workspace",
                "selection_status": "selected_current_default",
                "bias_evidence": "not_recorded",
                "equal_budget_benchmark": "not_recorded",
            },
            {
                "option": "constructor_function",
                "local_status": "not_distinguished_from_python_workspace",
                "selection_status": "unsupported_as_typed_abstraction",
                "bias_evidence": "not_recorded",
                "equal_budget_benchmark": "not_recorded",
            },
            {
                "option": "bespoke_search_algorithm",
                "local_status": "not_distinguished_from_python_workspace",
                "selection_status": "unsupported_as_typed_abstraction",
                "bias_evidence": "not_recorded",
                "equal_budget_benchmark": "not_recorded",
            },
            {
                "option": "coevolved_solution_and_search",
                "local_status": "unsupported",
                "selection_status": "unsupported_as_paired_representation",
                "bias_evidence": "not_recorded",
                "equal_budget_benchmark": "not_recorded",
            },
        ],
        "abstraction_rationale": {
            "status": "not_recorded",
            "problem_metadata_field": "not_configured",
            "selected_abstraction_reason": None,
            "alternative_abstraction_reasoning": [],
        },
        "bias_assessment": {
            "symmetry_structure_assumptions_recorded": False,
            "constructor_symmetry_bias_assessed": False,
            "search_algorithm_non_symmetric_bias_assessed": False,
            "problem_structure_labels": [],
            "equal_budget_comparison_ready": False,
        },
        "claim_ready": False,
        "claim_readiness": {
            "candidate_language_policy_validated": policy_validation.get("ok") is True,
            "selected_abstraction_recorded": True,
            "serializer_runner_linkage_recorded": True,
            "unsupported_alternatives_diagnosed": True,
            "abstraction_rationale_recorded": False,
            "symmetry_structure_assumptions_recorded": False,
            "paired_solution_search_representation": False,
            "equal_budget_benchmark_comparison": False,
            "alphaevolve_abstraction_selection_fidelity": False,
            "remaining_gap": [
                "abstraction_rationale_problem_metadata",
                "symmetry_structure_assumption_labels",
                "problem_defined_candidate_abstraction_hooks",
                "paired_solution_search_representation_support",
                "equal_budget_direct_constructor_search_comparisons",
                "benchmark_reports_for_abstraction_bias",
            ],
        },
    }
    report["validation"] = validate_candidate_abstraction_choice_report(report)
    return report


def _candidate_abstraction_runtime_record(program: Program) -> dict:
    workspace = program.workspace()
    paths = sorted(workspace.files)
    python_paths = [path for path in paths if path.endswith(".py")]
    return {
        "program_id": program.id,
        "generation": program.generation,
        "candidate_type": program.metadata.get("candidate_type"),
        "primary_file": workspace.primary_file,
        "workspace_sha256": _workspace_sha256(workspace),
        "file_count": len(paths),
        "python_file_count": len(python_paths),
        "non_python_text_file_count": len(paths) - len(python_paths),
        "static_member_count": len(workspace.static_files),
        "representational_role": "direct_solution_code_workspace",
    }


def validate_candidate_abstraction_choice_report(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.candidate_abstraction_choice_report.v1",
            "ok": False,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "candidate abstraction choice report must be an object",
                }
            ],
        }
    required = {
        "schema",
        "source",
        "selected_abstraction",
        "selected_representation",
        "serializer_runner_linkage",
        "runtime_candidate_shape",
        "abstraction_options",
        "abstraction_rationale",
        "bias_assessment",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append(
            {
                "code": "missing_fields",
                "message": f"candidate abstraction report missing fields: {sorted(missing)}",
            }
        )
    if report.get("schema") != "libreevolve.candidate_abstraction_choice_report.v1":
        issues.append(
            {
                "code": "invalid_schema",
                "message": "unsupported candidate abstraction report schema",
            }
        )
    if report.get("source") != "candidate_language_policy_and_runtime_workspaces":
        issues.append(
            {
                "code": "invalid_source",
                "message": "unsupported candidate abstraction report source",
            }
        )
    if report.get("selected_abstraction") != "code_file_set":
        issues.append(
            {
                "code": "invalid_selected_abstraction",
                "message": "selected abstraction must remain the code-file-set boundary",
            }
        )
    selected = report.get("selected_representation")
    if not isinstance(selected, Mapping):
        issues.append(
            {
                "code": "invalid_selected_representation",
                "message": "selected_representation must be an object",
            }
        )
    else:
        if selected.get("policy") != "python_primary_text_workspace_v1":
            issues.append(
                {
                    "code": "invalid_candidate_policy",
                    "message": "candidate policy must be python_primary_text_workspace_v1",
                }
            )
        if (
            selected.get("candidate_representation")
            != "bounded_utf8_text_workspace_with_typed_static_members"
        ):
            issues.append(
                {
                    "code": "invalid_candidate_representation",
                    "message": "candidate representation must be the bounded workspace",
                }
            )
        if selected.get("primary_language") != "python":
            issues.append(
                {
                    "code": "invalid_primary_language",
                    "message": "primary language must remain python",
                }
            )
        validation = selected.get("policy_validation")
        if not isinstance(validation, Mapping) or validation.get("ok") is not True:
            issues.append(
                {
                    "code": "candidate_policy_validation_failed",
                    "message": "selected candidate-language policy must validate",
                }
            )
        if selected.get("language_runner_ready") is not False:
            issues.append(
                {
                    "code": "language_runner_ready_overclaim",
                    "message": "language_runner_ready must remain false",
                }
            )
    linkage = report.get("serializer_runner_linkage")
    if not isinstance(linkage, Mapping):
        issues.append(
            {
                "code": "invalid_serializer_runner_linkage",
                "message": "serializer_runner_linkage must be an object",
            }
        )
    else:
        if linkage.get("problem_defined_serializer_hooks") != "unsupported":
            issues.append(
                {
                    "code": "serializer_hook_overclaim",
                    "message": "problem-defined serializer hooks must remain unsupported",
                }
            )
        if linkage.get("problem_defined_runner_hooks") != "unsupported":
            issues.append(
                {
                    "code": "runner_hook_overclaim",
                    "message": "problem-defined runner hooks must remain unsupported",
                }
            )
    shape = report.get("runtime_candidate_shape")
    if not isinstance(shape, Mapping):
        issues.append(
            {
                "code": "invalid_runtime_candidate_shape",
                "message": "runtime_candidate_shape must be an object",
            }
        )
        records = []
    else:
        records = shape.get("program_records")
        if not isinstance(records, list):
            issues.append(
                {
                    "code": "invalid_program_records",
                    "message": "runtime program_records must be a list",
                }
            )
            records = []
        _validate_report_count(shape, "program_record_count", len(records), issues)
        if not isinstance(shape.get("program_count"), int) or isinstance(
            shape.get("program_count"), bool
        ):
            issues.append(
                {"code": "invalid_program_count", "message": "program_count must be int"}
            )
        if not isinstance(shape.get("workspace_program_count"), int) or isinstance(
            shape.get("workspace_program_count"), bool
        ):
            issues.append(
                {
                    "code": "invalid_workspace_program_count",
                    "message": "workspace_program_count must be int",
                }
            )
        if (
            isinstance(shape.get("program_count"), int)
            and isinstance(shape.get("workspace_program_count"), int)
            and shape.get("workspace_program_count") != shape.get("program_count")
        ):
            issues.append(
                {
                    "code": "workspace_program_count_mismatch",
                    "message": "all current Program rows should expose workspaces",
                }
            )
        for count_field in (
            "python_file_count",
            "non_python_text_file_count",
            "static_member_count",
        ):
            if not isinstance(shape.get(count_field), int) or isinstance(
                shape.get(count_field), bool
            ):
                issues.append(
                    {
                        "code": f"invalid_{count_field}",
                        "message": f"{count_field} must be an integer",
                    }
                )
        for record in records:
            if not isinstance(record, Mapping):
                issues.append(
                    {
                        "code": "invalid_program_record",
                        "message": "program records must be objects",
                    }
                )
                continue
            if not _is_sha256_hex(record.get("workspace_sha256")):
                issues.append(
                    {
                        "code": "invalid_workspace_hash",
                        "message": "workspace_sha256 must be sha256 hex",
                    }
                )
            if record.get("representational_role") != "direct_solution_code_workspace":
                issues.append(
                    {
                        "code": "invalid_representational_role",
                        "message": "runtime records must remain direct code workspaces",
                    }
                )
    options = report.get("abstraction_options")
    if not isinstance(options, list):
        issues.append(
            {
                "code": "invalid_abstraction_options",
                "message": "abstraction_options must be a list",
            }
        )
        options = []
    option_names = {
        option.get("option") for option in options if isinstance(option, Mapping)
    }
    required_options = {
        "direct_solution",
        "constructor_function",
        "bespoke_search_algorithm",
        "coevolved_solution_and_search",
    }
    missing_options = required_options - option_names
    if missing_options:
        issues.append(
            {
                "code": "missing_abstraction_options",
                "message": f"abstraction options missing: {sorted(missing_options)}",
            }
        )
    for option in options:
        if not isinstance(option, Mapping):
            issues.append(
                {
                    "code": "invalid_abstraction_option",
                    "message": "abstraction option entries must be objects",
                }
            )
            continue
        if option.get("option") != "direct_solution" and option.get(
            "equal_budget_benchmark"
        ) != "not_recorded":
            issues.append(
                {
                    "code": "benchmark_overclaim",
                    "message": "alternative abstraction benchmarks are not recorded yet",
                }
            )
    rationale = report.get("abstraction_rationale")
    if not isinstance(rationale, Mapping):
        issues.append(
            {
                "code": "invalid_abstraction_rationale",
                "message": "abstraction_rationale must be an object",
            }
        )
    elif rationale.get("status") != "not_recorded":
        issues.append(
            {
                "code": "abstraction_rationale_overclaim",
                "message": "abstraction rationale must remain not_recorded",
            }
        )
    bias = report.get("bias_assessment")
    if not isinstance(bias, Mapping):
        issues.append(
            {
                "code": "invalid_bias_assessment",
                "message": "bias_assessment must be an object",
            }
        )
    else:
        for field in (
            "symmetry_structure_assumptions_recorded",
            "constructor_symmetry_bias_assessed",
            "search_algorithm_non_symmetric_bias_assessed",
            "equal_budget_comparison_ready",
        ):
            if bias.get(field) is not False:
                issues.append(
                    {
                        "code": f"{field}_overclaim",
                        "message": f"{field} must remain false",
                    }
                )
    readiness = report.get("claim_readiness")
    if not isinstance(readiness, Mapping):
        issues.append(
            {
                "code": "invalid_claim_readiness",
                "message": "claim_readiness must be an object",
            }
        )
    else:
        if readiness.get("alphaevolve_abstraction_selection_fidelity") is not False:
            issues.append(
                {
                    "code": "abstraction_selection_fidelity_overclaim",
                    "message": "AlphaEvolve abstraction-selection fidelity must remain false",
                }
            )
        if readiness.get("equal_budget_benchmark_comparison") is not False:
            issues.append(
                {
                    "code": "equal_budget_benchmark_overclaim",
                    "message": "equal-budget abstraction comparison must remain false",
                }
            )
    if report.get("claim_ready") is not False:
        issues.append(
            {
                "code": "claim_ready_overclaim",
                "message": "candidate abstraction report must not claim full fidelity",
            }
        )
    return {
        "schema": "libreevolve.candidate_abstraction_choice_report.v1",
        "ok": not issues,
        "issues": issues,
    }


def validate_marker_spelling_provenance_report(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.marker_spelling_provenance_report.v1",
            "ok": False,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "marker spelling provenance report must be an object",
                }
            ],
        }
    required = {
        "schema",
        "source",
        "canonical_start_marker",
        "canonical_end_marker",
        "record_count",
        "records",
        "compatibility_decision",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append({"code": "missing_fields", "message": f"marker spelling report missing fields: {sorted(missing)}"})
    if report.get("schema") != "libreevolve.marker_spelling_provenance_report.v1":
        issues.append({"code": "invalid_schema", "message": "unsupported marker spelling report schema"})
    if report.get("source") != "alphaevolve_paper_source_locations_and_local_parser_probe":
        issues.append({"code": "invalid_source", "message": "unsupported marker spelling report source"})
    if report.get("canonical_start_marker") != "# EVOLVE-BLOCK-START":
        issues.append({"code": "invalid_start_marker", "message": "canonical start marker changed"})
    if report.get("canonical_end_marker") != "# EVOLVE-BLOCK-END":
        issues.append({"code": "invalid_end_marker", "message": "canonical end marker changed"})
    records = report.get("records")
    if not isinstance(records, list):
        issues.append({"code": "invalid_records", "message": "records must be a list"})
        records = []
    _validate_report_count(report, "record_count", len(records), issues)
    marker_texts = set()
    for record in records:
        if not isinstance(record, Mapping):
            issues.append({"code": "invalid_record", "message": "marker records must be objects"})
            continue
        marker_text = record.get("marker_text")
        if isinstance(marker_text, str):
            marker_texts.add(marker_text)
        else:
            issues.append({"code": "invalid_marker_text", "message": "marker_text must be text"})
        if record.get("marker_role") not in {"start", "end"}:
            issues.append({"code": "invalid_marker_role", "message": "marker_role must be start or end"})
        if not isinstance(record.get("local_pdf_page"), int) or isinstance(record.get("local_pdf_page"), bool):
            issues.append({"code": "invalid_pdf_page", "message": "local_pdf_page must be an int"})
        probe = record.get("local_parser_probe")
        if not isinstance(probe, Mapping):
            issues.append({"code": "invalid_parser_probe", "message": "local_parser_probe must be an object"})
        else:
            if not _is_sha256_hex(probe.get("sample_sha256")):
                issues.append({"code": "invalid_probe_hash", "message": "parser probe sample hash must be sha256"})
            if not isinstance(probe.get("accepted"), bool):
                issues.append({"code": "invalid_probe_accepted", "message": "parser probe accepted must be boolean"})
            if not isinstance(probe.get("block_count"), int) or isinstance(probe.get("block_count"), bool):
                issues.append({"code": "invalid_probe_block_count", "message": "parser probe block_count must be int"})
        artifact = record.get("source_artifact")
        if not isinstance(artifact, Mapping):
            issues.append({"code": "invalid_source_artifact", "message": "source_artifact must be an object"})
        elif artifact.get("status") != "not_attached":
            issues.append({"code": "source_artifact_overclaim", "message": "source artifact must remain not_attached"})
    if "# EVOLVE-BLOCK START" not in marker_texts:
        issues.append({"code": "missing_space_variant", "message": "space variant marker record is required"})
    if "# EVOLVE-BLOCK-START" not in marker_texts:
        issues.append({"code": "missing_canonical_variant", "message": "canonical marker record is required"})
    decision = report.get("compatibility_decision")
    if not isinstance(decision, Mapping):
        issues.append({"code": "invalid_compatibility_decision", "message": "compatibility_decision must be an object"})
    else:
        if decision.get("policy") != "canonical_hyphenated_markers_only":
            issues.append({"code": "invalid_compatibility_policy", "message": "compatibility policy must remain canonical-only"})
        if decision.get("space_variant_supported") is not False:
            issues.append({"code": "space_variant_support_overclaim", "message": "space variant support must remain false"})
        if decision.get("space_variant_probe_error") != "orphan_end":
            issues.append({"code": "invalid_space_variant_probe", "message": "space variant probe should fail as orphan_end"})
    readiness = report.get("claim_readiness")
    if not isinstance(readiness, Mapping):
        issues.append({"code": "invalid_claim_readiness", "message": "claim_readiness must be an object"})
    else:
        if readiness.get("source_artifact_hashes_attached") is not False:
            issues.append({"code": "source_hash_overclaim", "message": "source artifact hashes must remain false"})
        if readiness.get("final_variant_classification") is not False:
            issues.append({"code": "variant_classification_overclaim", "message": "final variant classification must remain false"})
    if report.get("claim_ready") is not False:
        issues.append({"code": "claim_ready_overclaim", "message": "marker spelling report must not claim full source parity"})
    return {
        "schema": "libreevolve.marker_spelling_provenance_report.v1",
        "ok": not issues,
        "issues": issues,
    }


def _existing_codebase_integration_report(
    startup_manifest: Mapping[str, object],
    programs: list[Program],
) -> dict:
    seed_sources = _existing_codebase_seed_sources(startup_manifest)
    program_records = [
        record
        for program in programs
        if (record := _existing_codebase_program_record(program)) is not None
    ]
    marked_file_count = sum(record["marked_python_file_count"] for record in program_records)
    evolved_block_count = sum(record["evolved_block_count"] for record in program_records)
    unmarked_file_count = sum(record["unmarked_file_count"] for record in program_records)
    report = {
        "schema": "libreevolve.existing_codebase_integration_report.v1",
        "source": "runtime_candidate_workspaces_and_seed_sources",
        "seed_source_count": len(seed_sources),
        "seed_sources": seed_sources[:50],
        "seed_sources_truncated": len(seed_sources) > 50,
        "program_count": len(programs),
        "workspace_program_count": len(program_records),
        "marked_python_file_count": marked_file_count,
        "evolved_block_count": evolved_block_count,
        "unmarked_file_count": unmarked_file_count,
        "program_records": program_records[:50],
        "program_records_limit": 50,
        "program_records_truncated": len(program_records) > 50,
        "marker_contract": {
            "language": "python",
            "start_marker": "# EVOLVE-BLOCK-START",
            "end_marker": "# EVOLVE-BLOCK-END",
            "marker_grammar": "python_comment_exact_token_optional_manifest_safe_name",
            "unsupported_marker_policy": "non_python_marker_like_syntax_rejected",
            "skeleton_hash_policy": "sha256_python_file_with_evolved_block_content_placeholders",
        },
        "integration_boundary": {
            "original_codebase_identity": "not_recorded",
            "marker_added_diff_summary": "not_recorded",
            "setup_change_counts": "not_recorded",
            "upstream_release_artifact_identity": "not_recorded",
            "evaluator_entrypoint_continuity": (
                "startup_evaluator_sources_present"
                if seed_sources
                else "not_recorded"
            ),
        },
        "claim_ready": False,
        "claim_readiness": {
            "marker_span_inventory": evolved_block_count > 0,
            "skeleton_hashes_recorded": marked_file_count > 0,
            "unmarked_file_inventory": unmarked_file_count > 0,
            "original_codebase_identity": False,
            "marker_only_setup_diff": False,
            "paper_faithful_existing_codebase_integration": False,
            "remaining_gap": [
                "original_codebase_or_release_artifact_id",
                "pre_marker_source_hashes",
                "marker_added_setup_diff_summary",
                "evaluator_call_path_before_after_marker_insertion",
                "setup_change_counts",
                "codebase_scale_fixture_with_upstream_identity",
            ],
        },
    }
    report["validation"] = validate_existing_codebase_integration_report(report)
    return report


def _existing_codebase_seed_sources(
    startup_manifest: Mapping[str, object],
) -> list[dict]:
    problem = (
        startup_manifest.get("problem")
        if isinstance(startup_manifest.get("problem"), Mapping)
        else {}
    )
    seed_sources = (
        problem.get("seed_sources")
        if isinstance(problem.get("seed_sources"), list)
        else []
    )
    records = []
    for source in seed_sources:
        if not isinstance(source, Mapping):
            continue
        record = {
            "id": source.get("id"),
            "kind": source.get("kind"),
            "path": source.get("path") or source.get("relative_path"),
            "sha256": source.get("sha256"),
            "workspace": source.get("workspace") is True,
        }
        records.append({key: value for key, value in record.items() if value is not None})
    return records


def _existing_codebase_program_record(program: Program) -> dict | None:
    workspace = program.workspace()
    marked_files = []
    unmarked_files = []
    for path, content in sorted(workspace.files.items()):
        if not path.endswith(".py"):
            unmarked_files.append(_unmarked_file_record(path, content))
            continue
        marker_error = validate_evolve_blocks(content)
        if marker_error is not None:
            continue
        blocks = extract_evolve_blocks(content)
        if blocks:
            marked_files.append(_marked_file_record(path, content, blocks))
        else:
            unmarked_files.append(_unmarked_file_record(path, content))
    if not marked_files and not unmarked_files:
        return None
    evolved_block_count = sum(file["block_count"] for file in marked_files)
    return {
        "program_id": program.id,
        "generation": program.generation,
        "primary_file": workspace.primary_file,
        "file_count": len(workspace.files),
        "static_file_count": len(workspace.static_files),
        "workspace_sha256": _workspace_sha256(workspace),
        "marked_python_file_count": len(marked_files),
        "evolved_block_count": evolved_block_count,
        "unmarked_file_count": len(unmarked_files),
        "marked_files": marked_files[:25],
        "marked_files_truncated": len(marked_files) > 25,
        "unmarked_files": unmarked_files[:25],
        "unmarked_files_truncated": len(unmarked_files) > 25,
        "integration_evidence": (
            "runtime_workspace_marker_inventory_not_upstream_setup_diff"
        ),
    }


def _marked_file_record(path: str, content: str, blocks: list) -> dict:
    skeleton = _evolve_block_skeleton_text(content, blocks)
    return {
        "path": path,
        "language": "python",
        "marker_grammar": "canonical_python_comment",
        "file_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "skeleton_sha256": hashlib.sha256(skeleton.encode("utf-8")).hexdigest(),
        "block_count": len(blocks),
        "blocks": [
            _evolve_block_span_record(path, content, block, index)
            for index, block in enumerate(blocks)
        ],
    }


def _evolve_block_span_record(path: str, content: str, block: object, index: int) -> dict:
    name = getattr(block, "name", "") or f"block_{index}"
    span_key = f"{path}:{name}:{index}:{getattr(block, 'start', 0)}:{getattr(block, 'end', 0)}"
    block_content = getattr(block, "content", "")
    return {
        "span_id": hashlib.sha256(span_key.encode("utf-8")).hexdigest()[:24],
        "name": name,
        "index": index,
        "start_line": _line_number_for_offset(content, getattr(block, "start", 0)),
        "content_start_line": _line_number_for_offset(
            content,
            getattr(block, "content_start", 0),
        ),
        "content_end_line": _line_number_for_offset(
            content,
            getattr(block, "content_end", 0),
        ),
        "end_line": _line_number_for_offset(content, getattr(block, "end", 0)),
        "content_sha256": hashlib.sha256(block_content.encode("utf-8")).hexdigest(),
        "score_linked": False,
    }


def _evolve_block_skeleton_text(content: str, blocks: list) -> str:
    pieces = []
    cursor = 0
    for index, block in enumerate(sorted(blocks, key=lambda item: item.content_start)):
        pieces.append(content[cursor:block.content_start])
        pieces.append(f"<EVOLVE_BLOCK_CONTENT:{getattr(block, 'name', '')}:{index}>")
        cursor = block.content_end
    pieces.append(content[cursor:])
    return "".join(pieces)


def _line_number_for_offset(content: str, offset: int) -> int:
    safe_offset = max(0, min(len(content), offset))
    return content.count("\n", 0, safe_offset) + 1


def _unmarked_file_record(path: str, content: str) -> dict:
    return {
        "path": path,
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "bytes": len(content.encode("utf-8")),
    }


def validate_existing_codebase_integration_report(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.existing_codebase_integration_report.v1",
            "ok": False,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "existing-codebase integration report must be an object",
                }
            ],
        }
    required = {
        "schema",
        "source",
        "seed_source_count",
        "seed_sources",
        "program_count",
        "workspace_program_count",
        "marked_python_file_count",
        "evolved_block_count",
        "unmarked_file_count",
        "program_records",
        "marker_contract",
        "integration_boundary",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append({"code": "missing_fields", "message": f"integration report missing fields: {sorted(missing)}"})
    if report.get("schema") != "libreevolve.existing_codebase_integration_report.v1":
        issues.append({"code": "invalid_schema", "message": "unsupported integration report schema"})
    if report.get("source") != "runtime_candidate_workspaces_and_seed_sources":
        issues.append({"code": "invalid_source", "message": "unsupported integration report source"})
    seed_sources = report.get("seed_sources")
    if not isinstance(seed_sources, list):
        issues.append({"code": "invalid_seed_sources", "message": "seed_sources must be a list"})
        seed_sources = []
    _validate_report_count(report, "seed_source_count", len(seed_sources), issues)
    records = report.get("program_records")
    if not isinstance(records, list):
        issues.append({"code": "invalid_program_records", "message": "program_records must be a list"})
        records = []
    marked_count = 0
    block_count = 0
    unmarked_count = 0
    for record in records:
        if not isinstance(record, Mapping):
            issues.append({"code": "invalid_program_record", "message": "program records must be objects"})
            continue
        if not isinstance(record.get("program_id"), str) or not record.get("program_id"):
            issues.append({"code": "invalid_program_id", "message": "program_id must be non-empty text"})
        if not _is_sha256_hex(record.get("workspace_sha256")):
            issues.append({"code": "invalid_workspace_hash", "message": "workspace_sha256 must be sha256 hex"})
        marked_files = record.get("marked_files")
        if not isinstance(marked_files, list):
            issues.append({"code": "invalid_marked_files", "message": "marked_files must be a list"})
            marked_files = []
        unmarked_files = record.get("unmarked_files")
        if not isinstance(unmarked_files, list):
            issues.append({"code": "invalid_unmarked_files", "message": "unmarked_files must be a list"})
            unmarked_files = []
        marked_count += int(record.get("marked_python_file_count", 0)) if isinstance(record.get("marked_python_file_count"), int) else 0
        block_count += int(record.get("evolved_block_count", 0)) if isinstance(record.get("evolved_block_count"), int) else 0
        unmarked_count += int(record.get("unmarked_file_count", 0)) if isinstance(record.get("unmarked_file_count"), int) else 0
        for file_record in marked_files:
            if not isinstance(file_record, Mapping):
                issues.append({"code": "invalid_marked_file", "message": "marked file records must be objects"})
                continue
            if not _is_sha256_hex(file_record.get("file_sha256")):
                issues.append({"code": "invalid_file_hash", "message": "marked file hash must be sha256 hex"})
            if not _is_sha256_hex(file_record.get("skeleton_sha256")):
                issues.append({"code": "invalid_skeleton_hash", "message": "skeleton hash must be sha256 hex"})
            blocks = file_record.get("blocks")
            if not isinstance(blocks, list):
                issues.append({"code": "invalid_blocks", "message": "blocks must be a list"})
                continue
            if file_record.get("block_count") != len(blocks):
                issues.append({"code": "block_count_mismatch", "message": "block_count must match blocks length"})
            for block in blocks:
                if not isinstance(block, Mapping):
                    issues.append({"code": "invalid_block", "message": "block records must be objects"})
                    continue
                if not isinstance(block.get("span_id"), str) or len(block.get("span_id", "")) != 24:
                    issues.append({"code": "invalid_span_id", "message": "span_id must be a stable 24-char id"})
                if not _is_sha256_hex(block.get("content_sha256")):
                    issues.append({"code": "invalid_block_content_hash", "message": "block content hash must be sha256 hex"})
                if block.get("score_linked") is not False:
                    issues.append({"code": "score_link_overclaim", "message": "block score linkage must remain false"})
    _validate_report_count(report, "workspace_program_count", len(records), issues)
    _validate_report_count(report, "marked_python_file_count", marked_count, issues)
    _validate_report_count(report, "evolved_block_count", block_count, issues)
    _validate_report_count(report, "unmarked_file_count", unmarked_count, issues)
    contract = report.get("marker_contract")
    if not isinstance(contract, Mapping):
        issues.append({"code": "invalid_marker_contract", "message": "marker_contract must be an object"})
    elif contract.get("start_marker") != "# EVOLVE-BLOCK-START" or contract.get("end_marker") != "# EVOLVE-BLOCK-END":
        issues.append({"code": "invalid_marker_contract", "message": "marker contract must use canonical markers"})
    boundary = report.get("integration_boundary")
    if not isinstance(boundary, Mapping):
        issues.append({"code": "invalid_integration_boundary", "message": "integration_boundary must be an object"})
    elif boundary.get("original_codebase_identity") != "not_recorded":
        issues.append({"code": "codebase_identity_overclaim", "message": "original codebase identity must remain not_recorded"})
    readiness = report.get("claim_readiness")
    if not isinstance(readiness, Mapping):
        issues.append({"code": "invalid_claim_readiness", "message": "claim_readiness must be an object"})
    else:
        if readiness.get("paper_faithful_existing_codebase_integration") is not False:
            issues.append({"code": "integration_parity_overclaim", "message": "paper-faithful integration must remain false"})
        if readiness.get("marker_only_setup_diff") is not False:
            issues.append({"code": "marker_diff_overclaim", "message": "marker-only setup diff must remain false"})
    if report.get("claim_ready") is not False:
        issues.append({"code": "claim_ready_overclaim", "message": "existing-codebase integration report must not claim full parity"})
    return {
        "schema": "libreevolve.existing_codebase_integration_report.v1",
        "ok": not issues,
        "issues": issues,
    }


def _task_spec_artifact_resolution_report(
    startup_manifest: Mapping[str, object],
    run_dir: Path,
    programs: list[Program],
    paper_metric_contract: Mapping[str, object],
) -> dict:
    task_spec = (
        startup_manifest.get("task_specification")
        if isinstance(startup_manifest.get("task_specification"), Mapping)
        else {}
    )
    fields = task_spec.get("fields") if isinstance(task_spec.get("fields"), Mapping) else {}
    field_resolutions = [
        _task_spec_field_resolution(
            name,
            field if isinstance(field, Mapping) else {},
            startup_manifest,
            run_dir,
            programs,
            paper_metric_contract,
        )
        for name, field in sorted(fields.items())
        if isinstance(name, str)
    ]
    manifest_path_count = sum(
        len(record["manifest_path_resolutions"]) for record in field_resolutions
    )
    manifest_path_resolved_count = sum(
        1
        for record in field_resolutions
        for path in record["manifest_path_resolutions"]
        if path.get("resolved") is True
    )
    artifact_link_count = sum(
        len(record["runtime_artifact_resolutions"]) for record in field_resolutions
    )
    artifact_present_count = sum(
        1
        for record in field_resolutions
        for artifact in record["runtime_artifact_resolutions"]
        if artifact.get("present") is True
    )
    report = {
        "schema": "libreevolve.task_spec_artifact_resolution_report.v1",
        "source": "startup_task_specification_and_runtime_artifacts",
        "task_spec_schema": task_spec.get("schema"),
        "task_spec_id": task_spec.get("task_spec_id"),
        "task_spec_validation_ok": (
            task_spec.get("validation", {}).get("ok") is True
            if isinstance(task_spec.get("validation"), Mapping)
            else False
        ),
        "field_count": len(field_resolutions),
        "field_resolutions": field_resolutions,
        "manifest_path_count": manifest_path_count,
        "manifest_path_resolved_count": manifest_path_resolved_count,
        "artifact_link_count": artifact_link_count,
        "artifact_present_count": artifact_present_count,
        "program_count": len(programs),
        "seed_program_count": sum(1 for program in programs if program.generation == 0),
        "generated_program_count": sum(1 for program in programs if program.generation > 0),
        "claim_ready": False,
        "claim_readiness": {
            "startup_bundle_validated": (
                task_spec.get("validation", {}).get("ok") is True
                if isinstance(task_spec.get("validation"), Mapping)
                else False
            ),
            "manifest_paths_resolved": manifest_path_count > 0
            and manifest_path_count == manifest_path_resolved_count,
            "runtime_artifact_cross_links": artifact_link_count > 0,
            "artifact_links_all_present": artifact_link_count > 0
            and artifact_link_count == artifact_present_count,
            "full_alphaevolve_task_spec_parity": False,
            "remaining_gap": [
                "evolvable_component_span_ids",
                "score_field_to_candidate_path_links",
                "embedded_only_problem_definitions",
                "standalone_task_spec_report_examples",
                "deep_id_resolution_into_prompt_evaluator_candidate_history",
            ],
        },
    }
    report["validation"] = validate_task_spec_artifact_resolution_report(report)
    return report


def _task_spec_field_resolution(
    name: str,
    field: Mapping[str, object],
    startup_manifest: Mapping[str, object],
    run_dir: Path,
    programs: list[Program],
    paper_metric_contract: Mapping[str, object],
) -> dict:
    manifest_paths = _task_spec_manifest_paths(field)
    artifact_paths = _task_spec_artifact_paths_for_field(name)
    runtime_artifacts = [
        _task_spec_artifact_record(run_dir, path, _task_spec_artifact_role(name, path))
        for path in artifact_paths
    ]
    record = {
        "field": name,
        "field_status": field.get("status"),
        "manifest_path_resolutions": [
            _task_spec_manifest_path_record(startup_manifest, path)
            for path in manifest_paths
        ],
        "runtime_artifact_resolutions": runtime_artifacts,
        "reference_summary": _task_spec_reference_summary(
            name,
            field,
            programs,
            paper_metric_contract,
        ),
        "resolution_status": "partial_runtime_cross_link",
        "unresolved_gap": _task_spec_field_gap(name),
    }
    if all(path.get("resolved") is True for path in record["manifest_path_resolutions"]):
        if runtime_artifacts:
            record["resolution_status"] = "manifest_paths_resolved_with_runtime_links"
        else:
            record["resolution_status"] = "manifest_paths_resolved_only"
    return record


def _task_spec_manifest_paths(field: Mapping[str, object]) -> list[str]:
    paths = []
    for key in (
        "manifest_path",
        "role_routing_manifest_path",
        "context_policy_manifest_path",
    ):
        value = field.get(key)
        if isinstance(value, str) and value:
            paths.append(value)
    return paths


def _task_spec_artifact_paths_for_field(field_name: str) -> list[str]:
    return {
        "initial_programs": ["manifest.json", "history.jsonl"],
        "evaluation_code": [
            "manifest.json",
            "history.jsonl",
            "failure_history.jsonl",
            "evaluator_artifacts",
        ],
        "prompt_template_and_config": [
            "manifest.json",
            "prompt_history.jsonl",
        ],
        "llm_ensemble": [
            "manifest.json",
            "llm_calls.jsonl",
            "controller_budget_events.jsonl",
        ],
        "background_knowledge": [
            "manifest.json",
            "prompt_history.jsonl",
        ],
        "candidate_representation": [
            "manifest.json",
            "history.jsonl",
            "best.py",
            "best_workspace",
        ],
        "objective_metrics": [
            "manifest.json",
            "history.jsonl",
        ],
    }.get(field_name, ["manifest.json"])


def _task_spec_artifact_role(field_name: str, path: str) -> str:
    return f"{field_name}:{path}"


def _task_spec_artifact_record(run_dir: Path, path_name: str, role: str) -> dict:
    if path_name == "manifest.json":
        pointer = {
            "path": path_name,
            "present": (run_dir / path_name).exists(),
            "kind": "file",
            "hash_scope": "final_manifest_self_reference_deferred",
        }
    else:
        pointer = _runtime_artifact_pointer(
            run_dir / path_name,
            path_name,
            _resolve_path_for_scope(run_dir),
        )
    record = {
        "path": path_name,
        "role": role,
        "present": pointer.get("present") is True,
        "kind": pointer.get("kind"),
    }
    if _is_sha256_hex(pointer.get("sha256")):
        record["sha256"] = pointer["sha256"]
        record["hash_scope"] = pointer.get("hash_scope")
    elif _is_sha256_hex(pointer.get("tree_hash")):
        record["tree_hash"] = pointer["tree_hash"]
        record["hash_scope"] = pointer.get("tree_hash_scope")
    elif isinstance(pointer.get("hash_scope"), str):
        record["hash_scope"] = pointer["hash_scope"]
    if isinstance(pointer.get("bytes"), int):
        record["bytes"] = pointer["bytes"]
    return record


def _task_spec_manifest_path_record(
    manifest: Mapping[str, object],
    path: str,
) -> dict:
    resolved, value = _resolve_manifest_path(manifest, path)
    record = {
        "path": path,
        "resolved": resolved,
        "value_type": _task_spec_value_type(value) if resolved else None,
    }
    if resolved:
        count = _task_spec_value_count(value)
        if count is not None:
            record["value_count"] = count
    return record


def _resolve_manifest_path(manifest: Mapping[str, object], path: str) -> tuple[bool, object]:
    current: object = manifest
    for part in path.split("."):
        if isinstance(current, Mapping) and part in current:
            current = current[part]
            continue
        return False, None
    return True, current


def _task_spec_value_type(value: object) -> str:
    if isinstance(value, Mapping):
        return "object"
    if isinstance(value, list):
        return "list"
    if isinstance(value, str):
        return "string"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"
    if value is None:
        return "null"
    return "other"


def _task_spec_value_count(value: object) -> int | None:
    if isinstance(value, (Mapping, list)):
        return len(value)
    return None


def _task_spec_reference_summary(
    name: str,
    field: Mapping[str, object],
    programs: list[Program],
    paper_metric_contract: Mapping[str, object],
) -> dict:
    if name == "initial_programs":
        return {
            "startup_reference_count": int(field.get("count", 0))
            if isinstance(field.get("count"), int)
            and not isinstance(field.get("count"), bool)
            else 0,
            "seed_program_ids": [
                program.id for program in programs if program.generation == 0
            ][:50],
        }
    if name == "evaluation_code":
        return {
            "entrypoint_count": int(field.get("entrypoint_count", 0))
            if isinstance(field.get("entrypoint_count"), int)
            and not isinstance(field.get("entrypoint_count"), bool)
            else 0,
            "embedded_candidate_evaluate": field.get("embedded_candidate_evaluate")
            is True,
            "evaluated_program_count": sum(
                1
                for program in programs
                if isinstance(program.evaluation, Mapping) and program.evaluation
            ),
        }
    if name == "prompt_template_and_config":
        return {
            "variant_count": int(field.get("variant_count", 0))
            if isinstance(field.get("variant_count"), int)
            and not isinstance(field.get("variant_count"), bool)
            else 0,
        }
    if name == "llm_ensemble":
        return {
            "backend_count": int(field.get("backend_count", 0))
            if isinstance(field.get("backend_count"), int)
            and not isinstance(field.get("backend_count"), bool)
            else 0,
        }
    if name == "background_knowledge":
        return {
            "context_source_count": int(field.get("context_source_count", 0))
            if isinstance(field.get("context_source_count"), int)
            and not isinstance(field.get("context_source_count"), bool)
            else 0,
        }
    if name == "candidate_representation":
        return {
            "policy": field.get("policy"),
            "primary_language": field.get("primary_language"),
            "program_count": len(programs),
        }
    if name == "objective_metrics":
        return {
            "primary_metric": field.get("primary_metric"),
            "metric_count": field.get("metric_count"),
            "paper_metric_count": paper_metric_contract.get("paper_metric_count"),
            "paper_metric_names": paper_metric_contract.get("paper_metric_names", []),
        }
    return {}


def _task_spec_field_gap(field_name: str) -> list[str]:
    common = {
        "initial_programs": [
            "evolvable_component_span_ids",
            "seed_idea_variant_result_tables",
        ],
        "evaluation_code": [
            "score_field_to_candidate_path_links",
            "embedded_only_problem_definitions",
        ],
        "prompt_template_and_config": [
            "prompt_template_to_rendered_prompt_lineage",
            "standalone_task_spec_report_examples",
        ],
        "llm_ensemble": [
            "live_provider_model_registry_validation",
            "role_specific_scheduler_ownership",
        ],
        "background_knowledge": [
            "semantic_source_selection_evidence",
            "expert_formulation_provenance",
        ],
        "candidate_representation": [
            "problem_defined_candidate_abstraction_hooks",
            "arbitrary_language_build_runner_specs",
        ],
        "objective_metrics": [
            "cross_run_metric_contract_diff",
            "score_field_to_evolved_block_mapping",
        ],
    }
    return common.get(field_name, ["deep_runtime_artifact_resolution"])


def validate_task_spec_artifact_resolution_report(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.task_spec_artifact_resolution_report.v1",
            "ok": False,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "task spec artifact resolution report must be an object",
                }
            ],
        }
    required = {
        "schema",
        "source",
        "task_spec_schema",
        "task_spec_id",
        "task_spec_validation_ok",
        "field_count",
        "field_resolutions",
        "manifest_path_count",
        "manifest_path_resolved_count",
        "artifact_link_count",
        "artifact_present_count",
        "program_count",
        "seed_program_count",
        "generated_program_count",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append(
            {
                "code": "missing_fields",
                "message": f"task spec artifact resolution missing fields: {sorted(missing)}",
            }
        )
    if report.get("schema") != "libreevolve.task_spec_artifact_resolution_report.v1":
        issues.append({"code": "invalid_schema", "message": "unsupported task spec artifact resolution schema"})
    if report.get("source") != "startup_task_specification_and_runtime_artifacts":
        issues.append({"code": "invalid_source", "message": "unsupported task spec artifact resolution source"})
    if report.get("task_spec_schema") != "libreevolve.alphaevolve_task_specification_bundle.v1":
        issues.append({"code": "invalid_task_spec_schema", "message": "task_spec_schema must reference the startup task-spec bundle"})
    if not _is_sha256_hex(report.get("task_spec_id")):
        issues.append({"code": "invalid_task_spec_id", "message": "task_spec_id must be a sha256 hex id"})
    if report.get("task_spec_validation_ok") is not True:
        issues.append({"code": "invalid_task_spec_validation", "message": "startup task-spec validation must be ok"})
    fields = report.get("field_resolutions")
    if not isinstance(fields, list):
        issues.append({"code": "invalid_field_resolutions", "message": "field_resolutions must be a list"})
        fields = []
    expected_fields = {
        "initial_programs",
        "evaluation_code",
        "prompt_template_and_config",
        "llm_ensemble",
        "background_knowledge",
        "candidate_representation",
        "objective_metrics",
    }
    field_names = {
        field.get("field")
        for field in fields
        if isinstance(field, Mapping)
    }
    if field_names != expected_fields:
        issues.append({"code": "invalid_field_set", "message": "field_resolutions must cover all task-spec fields"})
    manifest_path_count = 0
    manifest_path_resolved_count = 0
    artifact_link_count = 0
    artifact_present_count = 0
    for field in fields:
        if not isinstance(field, Mapping):
            issues.append({"code": "invalid_field_resolution", "message": "field resolution records must be objects"})
            continue
        if field.get("field_status") not in {"present", "missing", "omitted", "unsupported", "partial"}:
            issues.append({"code": "invalid_field_status", "message": "field_status is unsupported"})
        paths = field.get("manifest_path_resolutions")
        if not isinstance(paths, list) or not paths:
            issues.append({"code": "invalid_manifest_path_resolutions", "message": "each field must resolve manifest paths"})
            paths = []
        manifest_path_count += len(paths)
        for path in paths:
            if not isinstance(path, Mapping):
                issues.append({"code": "invalid_manifest_path_record", "message": "manifest path records must be objects"})
                continue
            if not isinstance(path.get("path"), str) or not path.get("path"):
                issues.append({"code": "invalid_manifest_path", "message": "manifest path must be non-empty text"})
            if path.get("resolved") is True:
                manifest_path_resolved_count += 1
            elif path.get("resolved") is not False:
                issues.append({"code": "invalid_manifest_resolved_flag", "message": "manifest resolved flag must be boolean"})
        artifacts = field.get("runtime_artifact_resolutions")
        if not isinstance(artifacts, list):
            issues.append({"code": "invalid_artifact_resolutions", "message": "runtime artifact resolutions must be a list"})
            artifacts = []
        artifact_link_count += len(artifacts)
        for artifact in artifacts:
            if not isinstance(artifact, Mapping):
                issues.append({"code": "invalid_artifact_resolution", "message": "artifact resolution records must be objects"})
                continue
            if not isinstance(artifact.get("path"), str) or not artifact.get("path"):
                issues.append({"code": "invalid_artifact_path", "message": "artifact path must be non-empty text"})
            if not isinstance(artifact.get("role"), str) or not artifact.get("role"):
                issues.append({"code": "invalid_artifact_role", "message": "artifact role must be non-empty text"})
            if artifact.get("present") is True:
                artifact_present_count += 1
            elif artifact.get("present") is not False:
                issues.append({"code": "invalid_artifact_present", "message": "artifact present must be boolean"})
        if not isinstance(field.get("reference_summary"), Mapping):
            issues.append({"code": "invalid_reference_summary", "message": "reference_summary must be an object"})
        gaps = field.get("unresolved_gap")
        if not isinstance(gaps, list) or not all(isinstance(gap, str) and gap for gap in gaps):
            issues.append({"code": "invalid_unresolved_gap", "message": "unresolved_gap must be a list of labels"})
    _validate_report_count(report, "field_count", len(fields), issues)
    _validate_report_count(report, "manifest_path_count", manifest_path_count, issues)
    _validate_report_count(
        report,
        "manifest_path_resolved_count",
        manifest_path_resolved_count,
        issues,
    )
    _validate_report_count(report, "artifact_link_count", artifact_link_count, issues)
    _validate_report_count(report, "artifact_present_count", artifact_present_count, issues)
    program_count = report.get("program_count")
    seed_count = report.get("seed_program_count")
    generated_count = report.get("generated_program_count")
    if all(
        isinstance(value, int) and not isinstance(value, bool) and value >= 0
        for value in (program_count, seed_count, generated_count)
    ):
        if program_count != seed_count + generated_count:
            issues.append({"code": "program_count_mismatch", "message": "program counts must balance"})
    else:
        issues.append({"code": "invalid_program_counts", "message": "program counts must be non-negative integers"})
    readiness = report.get("claim_readiness")
    if not isinstance(readiness, Mapping):
        issues.append({"code": "invalid_claim_readiness", "message": "claim_readiness must be an object"})
    else:
        if readiness.get("full_alphaevolve_task_spec_parity") is not False:
            issues.append({"code": "task_spec_parity_overclaim", "message": "full AlphaEvolve task-spec parity must remain false"})
    if report.get("claim_ready") is not False:
        issues.append({"code": "claim_ready_overclaim", "message": "task spec artifact resolution must not claim full parity"})
    return {
        "schema": "libreevolve.task_spec_artifact_resolution_report.v1",
        "ok": not issues,
        "issues": issues,
    }


def _validate_report_count(
    report: Mapping[str, object],
    field: str,
    expected: int,
    issues: list[dict],
) -> None:
    value = report.get(field)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        issues.append({"code": f"invalid_{field}", "message": f"{field} must be a non-negative integer"})
    elif value != expected:
        issues.append({"code": f"{field}_mismatch", "message": f"{field} does not match report records"})


def _alphaevolve_process_exhibit_report(run_dir: Path, programs: list[Program]) -> dict:
    artifacts = _process_exhibit_artifact_evidence(run_dir)
    artifact_paths = [artifact["path"] for artifact in artifacts]
    figure_1_nodes = [
        _process_node(
            "fig1.human_problem_inputs",
            "human-defined problem inputs",
            "Problem, Config, task_specification",
            "partial",
            ["manifest.json"],
        ),
        _process_node(
            "fig1.llm_ensemble",
            "LLM ensemble",
            "LLMEnsemble, build_llm, backend routing",
            "implemented_sync",
            ["llm_calls.jsonl", "manifest.json"],
        ),
        _process_node(
            "fig1.prompt_sampler",
            "prompt sampler",
            "PromptSampler.build",
            "implemented_sync",
            ["prompt_history.jsonl"],
        ),
        _process_node(
            "fig1.evaluator_pool",
            "evaluator pool",
            "CascadeEvaluator and local subprocess validators",
            "partial",
            ["history.jsonl", "evaluator_artifacts"],
        ),
        _process_node(
            "fig1.program_database",
            "program database",
            "ProgramDatabase, MAP-Elites archives, history streams",
            "implemented_sync",
            ["history.jsonl", "archive_events.jsonl"],
        ),
        _process_node(
            "fig1.improved_solution",
            "improved solution",
            "best.py and best_workspace exports",
            "partial",
            ["best.py", "best_workspace"],
        ),
    ]
    figure_1_edges = [
        _process_edge("fig1.human_problem_inputs", "fig1.llm_ensemble", "configured_problem_context"),
        _process_edge("fig1.human_problem_inputs", "fig1.evaluator_pool", "configured_evaluation_contract"),
        _process_edge("fig1.program_database", "fig1.prompt_sampler", "parent_and_inspiration_selection"),
        _process_edge("fig1.prompt_sampler", "fig1.llm_ensemble", "rendered_prompt"),
        _process_edge("fig1.llm_ensemble", "fig1.evaluator_pool", "proposed_candidate"),
        _process_edge("fig1.evaluator_pool", "fig1.program_database", "scores_feedback_and_admission"),
        _process_edge("fig1.program_database", "fig1.improved_solution", "best_valid_export"),
    ]
    figure_2_steps = [
        _process_step(
            "fig2.step_1_sample",
            "database.sample()",
            "ProgramDatabase.sample, sample_diverse, prompt-program selection",
            "implemented_sync",
            ["history.jsonl", "prompt_history.jsonl"],
        ),
        _process_step(
            "fig2.step_2_build_prompt",
            "prompt_sampler.build(...)",
            "PromptSampler.build",
            "implemented_sync",
            ["prompt_history.jsonl"],
        ),
        _process_step(
            "fig2.step_3_generate",
            "llm.generate(...)",
            "_generate_with_budget and LLMEnsemble.generate",
            "implemented_sync",
            ["llm_calls.jsonl", "controller_budget_events.jsonl"],
        ),
        _process_step(
            "fig2.step_4_apply_diff",
            "apply_diff(...)",
            "apply_workspace_mutation",
            "implemented_sync",
            ["history.jsonl", "failure_history.jsonl"],
        ),
        _process_step(
            "fig2.step_5_execute_evaluator",
            "evaluator.execute(...)",
            "CascadeEvaluator.evaluate",
            "partial",
            ["history.jsonl", "evaluator_artifacts"],
        ),
        _process_step(
            "fig2.step_6_add_database",
            "database.add(...)",
            "ProgramDatabase.admit and ProgramDatabase.log",
            "implemented_sync",
            ["history.jsonl", "archive_events.jsonl"],
        ),
    ]
    figure_2_nodes = [
        _process_node(
            "fig2.initial_program",
            "initial program",
            "problem.initial_programs and seed workspaces",
            "implemented_sync",
            ["history.jsonl", "manifest.json"],
        ),
        _process_node(
            "fig2.prompt",
            "prompt",
            "PromptSampler rendered mutation prompt",
            "implemented_sync",
            ["prompt_history.jsonl"],
        ),
        _process_node(
            "fig2.proposal",
            "proposal",
            "LLM SEARCH/REPLACE or full-workspace candidate proposal",
            "implemented_sync",
            ["llm_calls.jsonl", "history.jsonl", "failure_history.jsonl"],
        ),
        _process_node(
            "fig2.evaluation",
            "evaluation",
            "CascadeEvaluator local evaluator result",
            "partial",
            ["history.jsonl", "evaluator_artifacts"],
        ),
        _process_node(
            "fig2.database",
            "database",
            "ProgramDatabase search state and MAP-Elites archive",
            "implemented_sync",
            ["history.jsonl", "archive_events.jsonl"],
        ),
    ]
    figure_2_edges = [
        _process_edge("fig2.database", "fig2.prompt", "sampled_context"),
        _process_edge("fig2.prompt", "fig2.proposal", "llm_generation_request"),
        _process_edge("fig2.proposal", "fig2.evaluation", "candidate_after_diff_application"),
        _process_edge("fig2.evaluation", "fig2.database", "validity_score_feedback"),
        _process_edge("fig2.database", "fig2.database", "iterative_archive_update"),
    ]
    figures = [
        {
            "figure_id": "alphaevolve_figure_1",
            "source": "2506.13131__AlphaEvolve.pdf",
            "local_pdf_page": 3,
            "role": "high_level_process_overview",
            "caption_location": "figure_caption_on_local_pdf_page_3",
            "nodes": figure_1_nodes,
            "edges": figure_1_edges,
            "rendered_artifact": _process_rendered_artifact_placeholder(
                "alphaevolve_figure_1"
            ),
        },
        {
            "figure_id": "alphaevolve_figure_2",
            "source": "2506.13131__AlphaEvolve.pdf",
            "local_pdf_page": 4,
            "role": "expanded_controller_loop",
            "caption_location": "figure_caption_and_displayed_pseudocode_on_local_pdf_page_4",
            "nodes": figure_2_nodes,
            "edges": figure_2_edges,
            "pseudocode_steps": figure_2_steps,
            "rendered_artifact": _process_rendered_artifact_placeholder(
                "alphaevolve_figure_2"
            ),
        },
    ]
    report = {
        "schema": "libreevolve.alphaevolve_process_exhibit_report.v1",
        "source": "runtime_history_static_figure_mapping",
        "runtime_scope": "single_completed_run",
        "controller_model": "single_process_serial_loop",
        "program_count": len(programs),
        "figures": figures,
        "figure_count": len(figures),
        "node_count": sum(len(figure.get("nodes", [])) for figure in figures),
        "edge_count": sum(len(figure.get("edges", [])) for figure in figures),
        "pseudocode_step_count": len(figure_2_steps),
        "artifact_evidence": artifacts,
        "artifact_evidence_paths": artifact_paths,
        "claim_ready": False,
        "claim_readiness": {
            "stable_figure_ids": True,
            "node_edge_component_mappings": True,
            "figure_2_pseudocode_step_mappings": True,
            "artifact_path_cross_links": True,
            "rendered_diagram_artifacts": False,
            "exact_diagram_text_reproduction": False,
            "full_alphaevolve_process_parity": False,
            "remaining_gap": [
                "rendered_process_diagram_artifacts_and_hashes",
                "exact_diagram_text_or_accessibility_export",
                "async_controller_sampler_evaluator_topology",
                "independent_evaluator_pool_parallelism",
                "artifact_level_step_validation_against_each_stream",
            ],
        },
    }
    report["validation"] = validate_alphaevolve_process_exhibit_report(report)
    return report


def _process_node(
    node_id: str,
    label: str,
    local_component: str,
    status: str,
    evidence_paths: list[str],
) -> dict:
    return {
        "node_id": node_id,
        "label": label,
        "local_component": local_component,
        "status": status,
        "evidence_paths": evidence_paths,
    }


def _process_edge(from_node: str, to_node: str, relationship: str) -> dict:
    return {
        "from": from_node,
        "to": to_node,
        "relationship": relationship,
    }


def _process_step(
    step_id: str,
    displayed_call: str,
    local_component: str,
    status: str,
    evidence_paths: list[str],
) -> dict:
    return {
        "step_id": step_id,
        "displayed_call": displayed_call,
        "local_component": local_component,
        "status": status,
        "evidence_paths": evidence_paths,
    }


def _process_rendered_artifact_placeholder(figure_id: str) -> dict:
    return {
        "figure_id": figure_id,
        "status": "not_generated",
        "path": None,
        "sha256": None,
        "reason": "source figure is mapped as manifest metadata only in this slice",
    }


def _process_exhibit_artifact_evidence(run_dir: Path) -> list[dict]:
    artifact_roles = {
        "manifest.json": ["run_manifest", "task_specification", "runtime_history"],
        "history.jsonl": ["candidate_history", "database_add", "evaluation_results"],
        "failure_history.jsonl": ["rejected_candidates", "diff_or_evaluation_failures"],
        "archive_events.jsonl": ["program_database_archive_events"],
        "controller_budget_events.jsonl": ["controller_budget_events"],
        "llm_calls.jsonl": ["llm_generation_calls"],
        "prompt_history.jsonl": ["prompt_sampler_outputs"],
        "evaluator_artifacts": ["evaluator_copy_out"],
        "best.py": ["improved_solution_export"],
        "best_workspace": ["improved_solution_workspace_export"],
    }
    resolved_run_dir = _resolve_path_for_scope(run_dir)
    records = []
    for path_name, roles in artifact_roles.items():
        if path_name == "manifest.json":
            pointer = {
                "path": path_name,
                "present": (run_dir / path_name).exists(),
                "kind": "file",
                "hash_scope": "final_manifest_self_reference_deferred",
            }
        else:
            pointer = _runtime_artifact_pointer(
                run_dir / path_name,
                path_name,
                resolved_run_dir,
            )
        record = {
            "path": path_name,
            "roles": roles,
            "present": pointer.get("present") is True,
            "kind": pointer.get("kind"),
        }
        if _is_sha256_hex(pointer.get("sha256")):
            record["sha256"] = pointer["sha256"]
            record["hash_scope"] = pointer.get("hash_scope")
        elif pointer.get("hash_scope") == "final_manifest_self_reference_deferred":
            record["hash_scope"] = pointer["hash_scope"]
        if isinstance(pointer.get("bytes"), int):
            record["bytes"] = pointer["bytes"]
        if _is_sha256_hex(pointer.get("tree_hash")):
            record["tree_hash"] = pointer["tree_hash"]
            record["hash_scope"] = pointer.get("tree_hash_scope")
        records.append(record)
    return records


def validate_alphaevolve_process_exhibit_report(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.alphaevolve_process_exhibit_report.v1",
            "ok": False,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "process exhibit report must be an object",
                }
            ],
        }
    required = {
        "schema",
        "source",
        "runtime_scope",
        "controller_model",
        "figures",
        "figure_count",
        "node_count",
        "edge_count",
        "pseudocode_step_count",
        "artifact_evidence",
        "artifact_evidence_paths",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append(
            {
                "code": "missing_fields",
                "message": f"process exhibit report missing fields: {sorted(missing)}",
            }
        )
    if report.get("schema") != "libreevolve.alphaevolve_process_exhibit_report.v1":
        issues.append({"code": "invalid_schema", "message": "unsupported process exhibit report schema"})
    if report.get("source") != "runtime_history_static_figure_mapping":
        issues.append({"code": "invalid_source", "message": "unsupported process exhibit report source"})
    if report.get("runtime_scope") != "single_completed_run":
        issues.append({"code": "invalid_runtime_scope", "message": "runtime_scope must be single_completed_run"})
    if report.get("controller_model") != "single_process_serial_loop":
        issues.append({"code": "invalid_controller_model", "message": "controller model must match current runtime boundary"})

    figures = report.get("figures")
    if not isinstance(figures, list):
        issues.append({"code": "invalid_figures", "message": "figures must be a list"})
        figures = []
    figure_ids = {
        figure.get("figure_id")
        for figure in figures
        if isinstance(figure, Mapping)
    }
    expected_ids = {"alphaevolve_figure_1", "alphaevolve_figure_2"}
    if figure_ids != expected_ids:
        issues.append({"code": "invalid_figure_ids", "message": "figure ids must cover AlphaEvolve figures 1 and 2"})
    nodes_seen: set[str] = set()
    edge_count = 0
    step_count = 0
    for figure_index, figure in enumerate(figures):
        if not isinstance(figure, Mapping):
            issues.append({"code": "invalid_figure", "message": f"figure {figure_index} must be an object"})
            continue
        if not isinstance(figure.get("local_pdf_page"), int) or isinstance(figure.get("local_pdf_page"), bool):
            issues.append({"code": "invalid_source_page", "message": f"figure {figure_index} local_pdf_page must be an int"})
        nodes = figure.get("nodes")
        if not isinstance(nodes, list) or not nodes:
            issues.append({"code": "invalid_nodes", "message": f"figure {figure_index} must include nodes"})
            nodes = []
        for node in nodes:
            if not isinstance(node, Mapping):
                issues.append({"code": "invalid_node", "message": "node records must be objects"})
                continue
            node_id = node.get("node_id")
            if not isinstance(node_id, str) or not node_id:
                issues.append({"code": "invalid_node_id", "message": "node_id must be non-empty text"})
                continue
            nodes_seen.add(node_id)
            _validate_process_status(node.get("status"), issues, "node")
            _validate_process_evidence_paths(node.get("evidence_paths"), issues, "node")
        edges = figure.get("edges")
        if not isinstance(edges, list) or not edges:
            issues.append({"code": "invalid_edges", "message": f"figure {figure_index} must include edges"})
            edges = []
        edge_count += len(edges)
        for edge in edges:
            if not isinstance(edge, Mapping):
                issues.append({"code": "invalid_edge", "message": "edge records must be objects"})
                continue
            if not isinstance(edge.get("from"), str) or not isinstance(edge.get("to"), str):
                issues.append({"code": "invalid_edge_endpoint", "message": "edge endpoints must be node ids"})
            if not isinstance(edge.get("relationship"), str) or not edge.get("relationship"):
                issues.append({"code": "invalid_edge_relationship", "message": "edge relationship must be non-empty text"})
        steps = figure.get("pseudocode_steps", [])
        if steps:
            if not isinstance(steps, list):
                issues.append({"code": "invalid_steps", "message": "pseudocode_steps must be a list"})
                steps = []
            step_count += len(steps)
            for step in steps:
                if not isinstance(step, Mapping):
                    issues.append({"code": "invalid_step", "message": "pseudocode step records must be objects"})
                    continue
                if not isinstance(step.get("step_id"), str) or not step.get("step_id"):
                    issues.append({"code": "invalid_step_id", "message": "step_id must be non-empty text"})
                if not isinstance(step.get("displayed_call"), str) or not step.get("displayed_call"):
                    issues.append({"code": "invalid_displayed_call", "message": "displayed_call must be non-empty text"})
                _validate_process_status(step.get("status"), issues, "step")
                _validate_process_evidence_paths(step.get("evidence_paths"), issues, "step")
        rendered = figure.get("rendered_artifact")
        if not isinstance(rendered, Mapping):
            issues.append({"code": "invalid_rendered_artifact", "message": "rendered_artifact must be an object"})
        elif rendered.get("status") != "not_generated":
            issues.append({"code": "rendered_artifact_overclaim", "message": "rendered figure artifacts are not generated by this report"})

    if isinstance(report.get("figure_count"), int) and not isinstance(report.get("figure_count"), bool):
        if report["figure_count"] != len(figures):
            issues.append({"code": "figure_count_mismatch", "message": "figure_count must match figures length"})
    else:
        issues.append({"code": "invalid_figure_count", "message": "figure_count must be an integer"})
    if isinstance(report.get("node_count"), int) and not isinstance(report.get("node_count"), bool):
        if report["node_count"] != len(nodes_seen):
            issues.append({"code": "node_count_mismatch", "message": "node_count must match unique node ids"})
    else:
        issues.append({"code": "invalid_node_count", "message": "node_count must be an integer"})
    if isinstance(report.get("edge_count"), int) and not isinstance(report.get("edge_count"), bool):
        if report["edge_count"] != edge_count:
            issues.append({"code": "edge_count_mismatch", "message": "edge_count must match edge records"})
    else:
        issues.append({"code": "invalid_edge_count", "message": "edge_count must be an integer"})
    if isinstance(report.get("pseudocode_step_count"), int) and not isinstance(report.get("pseudocode_step_count"), bool):
        if report["pseudocode_step_count"] != step_count:
            issues.append({"code": "step_count_mismatch", "message": "pseudocode_step_count must match step records"})
    else:
        issues.append({"code": "invalid_step_count", "message": "pseudocode_step_count must be an integer"})

    artifacts = report.get("artifact_evidence")
    artifact_paths = report.get("artifact_evidence_paths")
    if not isinstance(artifacts, list):
        issues.append({"code": "invalid_artifact_evidence", "message": "artifact_evidence must be a list"})
        artifacts = []
    if not isinstance(artifact_paths, list) or not all(isinstance(path, str) for path in artifact_paths):
        issues.append({"code": "invalid_artifact_paths", "message": "artifact_evidence_paths must be text paths"})
        artifact_paths = []
    if [artifact.get("path") for artifact in artifacts if isinstance(artifact, Mapping)] != artifact_paths:
        issues.append({"code": "artifact_path_mismatch", "message": "artifact_evidence_paths must match artifact records"})
    for artifact in artifacts:
        if not isinstance(artifact, Mapping):
            issues.append({"code": "invalid_artifact", "message": "artifact records must be objects"})
            continue
        if not isinstance(artifact.get("path"), str) or not artifact.get("path"):
            issues.append({"code": "invalid_artifact_path", "message": "artifact path must be non-empty text"})
        roles = artifact.get("roles")
        if not isinstance(roles, list) or not all(isinstance(role, str) and role for role in roles):
            issues.append({"code": "invalid_artifact_roles", "message": "artifact roles must be non-empty text"})
        if not isinstance(artifact.get("present"), bool):
            issues.append({"code": "invalid_artifact_present", "message": "artifact present must be boolean"})
    readiness = report.get("claim_readiness")
    if not isinstance(readiness, Mapping):
        issues.append({"code": "invalid_claim_readiness", "message": "claim_readiness must be an object"})
    else:
        if readiness.get("rendered_diagram_artifacts") is not False:
            issues.append({"code": "rendered_diagram_overclaim", "message": "rendered diagram artifacts must remain false"})
        if readiness.get("full_alphaevolve_process_parity") is not False:
            issues.append({"code": "process_parity_overclaim", "message": "full AlphaEvolve process parity must remain false"})
    if report.get("claim_ready") is not False:
        issues.append({"code": "claim_ready_overclaim", "message": "process exhibit report must not claim full process-diagram parity"})
    return {
        "schema": "libreevolve.alphaevolve_process_exhibit_report.v1",
        "ok": not issues,
        "issues": issues,
    }


def _validate_process_status(value: object, issues: list[dict], owner: str) -> None:
    if value not in {"implemented_sync", "partial", "unsupported", "not_applicable"}:
        issues.append({"code": "invalid_process_status", "message": f"{owner} status is unsupported"})


def _validate_process_evidence_paths(value: object, issues: list[dict], owner: str) -> None:
    if not isinstance(value, list) or not all(isinstance(path, str) and path for path in value):
        issues.append({"code": "invalid_process_evidence_paths", "message": f"{owner} evidence_paths must be non-empty text"})


def _evaluation_cascade_report(programs: list[Program]) -> dict:
    stages: dict[str, dict] = {}
    configured_candidate_count = 0
    main_test_exposure_count = 0
    stop_reasons: dict[str, int] = {}
    for program in programs:
        evaluation = program.evaluation if isinstance(program.evaluation, dict) else {}
        metadata = evaluation.get("metadata") if isinstance(evaluation.get("metadata"), dict) else {}
        configured = metadata.get("configured_stage_results")
        if not isinstance(configured, list):
            continue
        configured_candidate_count += 1
        if configured and isinstance(configured[-1], dict) and configured[-1].get("passed") is True:
            main_test_exposure_count += 1
        stopped_at = metadata.get("stopped_at")
        for stage_index, raw_stage in enumerate(configured):
            if not isinstance(raw_stage, dict):
                continue
            name = str(raw_stage.get("name", f"stage_{stage_index}"))
            stage = stages.setdefault(
                name,
                {
                    "name": name,
                    "stage_index": raw_stage.get("stage_index", stage_index),
                    "entered": 0,
                    "passed": 0,
                    "failed": 0,
                    "threshold_failed": 0,
                    "local_invalid": 0,
                    "sample_count": 0,
                    "retry_attempts": 0,
                    "subprocess_attempts": 0,
                    "timeout_count": 0,
                    "elapsed_sec": 0.0,
                    "candidate_ids": [],
                    "failure_reasons": {},
                    "thresholds": {
                        "fitness": raw_stage.get("threshold"),
                        "metric_thresholds": raw_stage.get("metric_thresholds", []),
                        "artifact_output_checks": raw_stage.get("artifact_output_checks", []),
                    },
                },
            )
            stage["entered"] += 1
            stage["candidate_ids"].append(program.id)
            if raw_stage.get("passed") is True:
                stage["passed"] += 1
            else:
                stage["failed"] += 1
                reason = str(
                    raw_stage.get("stop_reason")
                    or raw_stage.get("error")
                    or "stage_threshold_not_met"
                )
                stage["failure_reasons"][reason] = stage["failure_reasons"].get(reason, 0) + 1
                stop_reasons[reason] = stop_reasons.get(reason, 0) + 1
            if raw_stage.get("threshold_passed") is False:
                stage["threshold_failed"] += 1
            if raw_stage.get("local_valid") is False:
                stage["local_invalid"] += 1
            accounting = evaluation_accounting(raw_stage)
            stage["sample_count"] += int(accounting.get("configured_stage_samples", 0))
            stage["retry_attempts"] += int(accounting.get("retry_attempts", 0))
            stage["subprocess_attempts"] += int(accounting.get("subprocess_attempts", 0))
            stage["timeout_count"] += int(accounting.get("timeout_count", 0))
            elapsed = raw_stage.get("elapsed_sec")
            if isinstance(elapsed, (int, float)) and not isinstance(elapsed, bool):
                stage["elapsed_sec"] += float(elapsed)
        if isinstance(stopped_at, str):
            stop_reasons.setdefault(f"stopped_at:{stopped_at}", 0)
            stop_reasons[f"stopped_at:{stopped_at}"] += 1
    ordered_stages = [
        _finalize_cascade_stage_record(record)
        for record in sorted(stages.values(), key=lambda item: (item["stage_index"], item["name"]))
    ]
    report = {
        "schema": "libreevolve.evaluation_cascade_report.v1",
        "source": "runtime_history_configured_stage_results",
        "configured_candidate_count": configured_candidate_count,
        "stage_count": len(ordered_stages),
        "stages": ordered_stages,
        "main_test_exposure_count": main_test_exposure_count,
        "early_prune_count": max(0, configured_candidate_count - main_test_exposure_count),
        "stop_reasons": dict(sorted(stop_reasons.items())),
        "claim_ready": False,
        "claim_readiness": {
            "alphaevolve_cascade_efficiency": False,
            "reason": (
                "stage promotion and attrition counts exist, but difficulty/scale "
                "rationale and evaluator test-set identities are not yet complete"
            ),
            "remaining_gap": [
                "stage_difficulty_or_scale_labels",
                "evaluator_test_set_hashes",
                "main_test_denominator_policy",
                "cost_savings_counterfactual",
            ],
        },
    }
    report["validation"] = validate_evaluation_cascade_report(report)
    return report


def _paper_evaluator_metric_contract_report(
    db: ProgramDatabase,
    programs: list[Program],
) -> dict:
    objective_schema = db.objective_schema_snapshot()
    metrics = objective_schema.get("metrics", [])
    metric_records = [
        _paper_metric_contract_metric_record(metric, programs)
        for metric in metrics
        if isinstance(metric, Mapping)
    ]
    paper_metric_names = [
        record["name"] for record in metric_records if record["paper_metric"] is True
    ]
    excluded_declared_metrics = [
        {
            "name": record["name"],
            "source": record["source"],
            "reason": f"declared_metric_source_{record['source']}_not_evaluator",
        }
        for record in metric_records
        if record["paper_metric"] is False
    ]
    validity_gate = _paper_metric_validity_gate(programs)
    attachments = _paper_metric_attachment_exclusions(programs)
    report = {
        "schema": "libreevolve.paper_evaluator_metric_contract.v1",
        "source": "objective_schema_and_runtime_history",
        "primary_metric": objective_schema.get("primary_metric"),
        "declared_metric_names": [record["name"] for record in metric_records],
        "paper_metric_names": paper_metric_names,
        "excluded_declared_metrics": excluded_declared_metrics,
        "metric_count": len(metric_records),
        "paper_metric_count": len(paper_metric_names),
        "metrics": metric_records,
        "validity_gate": validity_gate,
        "excluded_reserved_fields": [
            {
                "field": "is_valid",
                "reason": "local_validity_gate_not_scored_metric",
            },
            {
                "field": "outputs",
                "reason": "non_scalar_program_output_attachment",
            },
            {
                "field": "program_output",
                "reason": "non_scalar_program_output_attachment",
            },
            {
                "field": "feedback_adjusted_fitness",
                "reason": "local_feedback_composition_not_evaluator_scalar_metric",
            },
            {
                "field": "llm_feedback",
                "reason": "post_evaluator_feedback_records_not_evaluator_scalar_metric",
            },
        ],
        "non_scalar_attachment_summary": attachments,
        "feedback_metric_exclusion_policy": (
            "metrics_yaml_source_feedback_plugin_or_final_fitness_are_not_paper_evaluator_metrics"
        ),
        "normalization_policy": (
            "declared_evaluator_metrics_are_transformed_to_higher_is_better_normalized_unit_scores"
        ),
        "claim_ready": True,
        "claim_readiness": {
            "alphaevolve_scalar_metric_boundary": True,
            "remaining_gap": [
                "cross_run_metric_contract_diff_report",
            ],
        },
    }
    report["validation"] = validate_paper_evaluator_metric_contract(report)
    return report


def _paper_metric_contract_metric_record(
    metric: Mapping[str, object],
    programs: list[Program],
) -> dict:
    name = str(metric.get("name"))
    source = str(metric.get("source", "evaluator"))
    direction = str(metric.get("direction", "maximize"))
    bounds = metric.get("bounds")
    lo = float(bounds[0]) if isinstance(bounds, list) and len(bounds) == 2 else 0.0
    hi = float(bounds[1]) if isinstance(bounds, list) and len(bounds) == 2 else 1.0
    observed, observed_count, missing_count, non_numeric_count = _paper_metric_observed_values(
        name,
        direction,
        lo,
        hi,
        programs,
    )
    return {
        "name": name,
        "source": source,
        "paper_metric": source == "evaluator",
        "primary": metric.get("primary") is True,
        "direction": direction,
        "bounds": [lo, hi],
        "weight": float(metric.get("weight", 1.0)),
        "maximize_transform": (
            "raw_value" if direction == "maximize" else "upper_bound_minus_raw_value"
        ),
        "normalized_transform": (
            "(raw_value - lower_bound) / (upper_bound - lower_bound)"
            if direction == "maximize"
            else "(upper_bound - raw_value) / (upper_bound - lower_bound)"
        ),
        "raw_value_source": f"Program.metrics.{name}",
        "normalized_value_source": f"Program.metadata.normalized_metrics.{name}",
        "observed_count": observed_count,
        "missing_count": missing_count,
        "non_numeric_count": non_numeric_count,
        "observed_values": observed,
        "observed_values_limit": 25,
    }


def _paper_metric_observed_values(
    name: str,
    direction: str,
    lo: float,
    hi: float,
    programs: list[Program],
) -> tuple[list[dict], int, int, int]:
    observed: list[dict] = []
    missing_count = 0
    non_numeric_count = 0
    for program in programs:
        if name not in program.metrics:
            missing_count += 1
            continue
        value = program.metrics[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            non_numeric_count += 1
            continue
        numeric = float(value)
        if not math.isfinite(numeric):
            non_numeric_count += 1
            continue
        normalized = _paper_metric_normalized_value(program, name, direction, lo, hi)
        observed.append(
            {
                "program_id": program.id,
                "raw_value": numeric,
                "maximized_value": numeric if direction == "maximize" else hi - numeric,
                "normalized_value": normalized,
                "is_valid": _paper_metric_program_is_valid(program),
            }
        )
    return observed[:25], len(observed), missing_count, non_numeric_count


def _paper_metric_normalized_value(
    program: Program,
    name: str,
    direction: str,
    lo: float,
    hi: float,
) -> float | None:
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    normalized_metrics = metadata.get("normalized_metrics")
    if isinstance(normalized_metrics, dict):
        value = normalized_metrics.get(name)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            numeric = float(value)
            if math.isfinite(numeric):
                return numeric
    value = program.metrics.get(name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    numeric = float(value)
    if not math.isfinite(numeric):
        return None
    rng = hi - lo
    if rng == 0:
        return 0.5
    if direction == "minimize":
        normalized = (hi - numeric) / rng
    else:
        normalized = (numeric - lo) / rng
    return max(0.0, min(1.0, normalized))


def _paper_metric_program_is_valid(program: Program) -> bool | None:
    evaluation = program.evaluation if isinstance(program.evaluation, dict) else {}
    value = evaluation.get("is_valid")
    if isinstance(value, bool):
        return value
    metrics_value = program.metrics.get("is_valid")
    return metrics_value if isinstance(metrics_value, bool) else None


def _paper_metric_validity_gate(programs: list[Program]) -> dict:
    true_count = 0
    false_count = 0
    missing_count = 0
    for program in programs:
        value = _paper_metric_program_is_valid(program)
        if value is True:
            true_count += 1
        elif value is False:
            false_count += 1
        else:
            missing_count += 1
    return {
        "field": "is_valid",
        "sources": ["evaluation.is_valid", "Program.metrics.is_valid"],
        "scored_metric": False,
        "valid_true_count": true_count,
        "valid_false_count": false_count,
        "missing_count": missing_count,
        "admission_policy": "validity_gate_before_program_database_admission",
    }


def _paper_metric_attachment_exclusions(programs: list[Program]) -> dict:
    program_output_count = 0
    llm_feedback_count = 0
    feedback_adjusted_fitness_count = 0
    for program in programs:
        evaluation = program.evaluation if isinstance(program.evaluation, dict) else {}
        metadata = evaluation.get("metadata") if isinstance(evaluation.get("metadata"), dict) else {}
        if isinstance(metadata.get("program_outputs"), dict):
            program_output_count += 1
        if isinstance(metadata.get("llm_feedback"), list) and metadata["llm_feedback"]:
            llm_feedback_count += 1
        if "feedback_adjusted_fitness" in metadata:
            feedback_adjusted_fitness_count += 1
    return {
        "program_output_attachment_count": program_output_count,
        "llm_feedback_record_count": llm_feedback_count,
        "feedback_adjusted_fitness_count": feedback_adjusted_fitness_count,
        "scored_metric": False,
    }


_PAPER_METRIC_TABLE_COLUMNS = [
    "metric_name",
    "program_id",
    "is_valid",
    "primary",
    "direction",
    "raw_value",
    "raw_display",
    "maximized_value",
    "maximized_display",
    "normalized_value",
    "normalized_display",
]


def _paper_metric_table_export_report(contract: Mapping[str, object]) -> dict:
    rows: list[dict] = []
    metrics = contract.get("metrics") if isinstance(contract.get("metrics"), list) else []
    for metric in metrics:
        if not isinstance(metric, Mapping) or metric.get("paper_metric") is not True:
            continue
        rows.extend(_paper_metric_table_rows(metric))
    display_policy = {
        "schema": "libreevolve.paper_metric_table_display_policy.v1",
        "raw_value_format": "significant_digits",
        "raw_value_significant_digits": 12,
        "maximized_value_format": "significant_digits",
        "maximized_value_significant_digits": 12,
        "normalized_value_format": "fixed_decimal_places",
        "normalized_value_decimal_places": 6,
        "rounding": "python_format_half_even_for_binary_float",
        "missing_value": "",
        "boolean_format": "json_lowercase",
    }
    table_payload = {
        "columns": list(_PAPER_METRIC_TABLE_COLUMNS),
        "rows": rows,
    }
    report = {
        "schema": "libreevolve.paper_metric_table_export.v1",
        "source": "runtime.history.paper_evaluator_metric_contract",
        "contract_schema": contract.get("schema"),
        "primary_metric": contract.get("primary_metric"),
        "paper_metric_names": list(contract.get("paper_metric_names", []))
        if isinstance(contract.get("paper_metric_names"), list)
        else [],
        "excluded_declared_metrics": copy.deepcopy(
            contract.get("excluded_declared_metrics", [])
        )
        if isinstance(contract.get("excluded_declared_metrics"), list)
        else [],
        "columns": list(_PAPER_METRIC_TABLE_COLUMNS),
        "row_count": len(rows),
        "rows": rows,
        "rows_limit": 250,
        "rows_truncated": False,
        "display_policy": display_policy,
        "export_formats": {
            "manifest_json_rows": True,
            "csv_header_order": list(_PAPER_METRIC_TABLE_COLUMNS),
            "external_file_written": False,
        },
        "table_sha256": hashlib.sha256(
            json.dumps(table_payload, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest(),
        "claim_ready": True,
        "claim_readiness": {
            "single_run_paper_metric_table": True,
            "cross_run_metric_contract_diff": False,
            "remaining_gap": ["cross_run_metric_contract_diff_report"],
        },
    }
    if len(rows) > report["rows_limit"]:
        report["rows"] = rows[: report["rows_limit"]]
        report["rows_truncated"] = True
    report["validation"] = validate_paper_metric_table_export(report)
    return report


def _paper_metric_table_rows(metric: Mapping[str, object]) -> list[dict]:
    name = str(metric.get("name"))
    direction = str(metric.get("direction", "maximize"))
    primary = metric.get("primary") is True
    rows = []
    observed_values = (
        metric.get("observed_values")
        if isinstance(metric.get("observed_values"), list)
        else []
    )
    for observed in observed_values:
        if not isinstance(observed, Mapping):
            continue
        raw_value = _paper_metric_table_number(observed.get("raw_value"))
        maximized_value = _paper_metric_table_number(observed.get("maximized_value"))
        normalized_value = _paper_metric_table_number(observed.get("normalized_value"))
        rows.append(
            {
                "metric_name": name,
                "program_id": observed.get("program_id"),
                "is_valid": observed.get("is_valid"),
                "primary": primary,
                "direction": direction,
                "raw_value": raw_value,
                "raw_display": _paper_metric_display_significant(raw_value, 12),
                "maximized_value": maximized_value,
                "maximized_display": _paper_metric_display_significant(
                    maximized_value,
                    12,
                ),
                "normalized_value": normalized_value,
                "normalized_display": _paper_metric_display_fixed(
                    normalized_value,
                    6,
                ),
            }
        )
    return rows


def _paper_metric_table_number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    numeric = float(value)
    if not math.isfinite(numeric):
        return None
    return numeric


def _paper_metric_display_significant(value: float | None, digits: int) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}g}"


def _paper_metric_display_fixed(value: float | None, places: int) -> str:
    if value is None:
        return ""
    return f"{value:.{places}f}"


def validate_paper_metric_table_export(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.paper_metric_table_export.v1",
            "ok": False,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "paper metric table export must be an object",
                }
            ],
        }
    required = {
        "schema",
        "source",
        "contract_schema",
        "primary_metric",
        "paper_metric_names",
        "excluded_declared_metrics",
        "columns",
        "row_count",
        "rows",
        "rows_limit",
        "rows_truncated",
        "display_policy",
        "export_formats",
        "table_sha256",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append({"code": "missing_fields", "message": f"paper metric table export missing fields: {sorted(missing)}"})
    if report.get("schema") != "libreevolve.paper_metric_table_export.v1":
        issues.append({"code": "invalid_schema", "message": "paper metric table export schema is unsupported"})
    if report.get("source") != "runtime.history.paper_evaluator_metric_contract":
        issues.append({"code": "invalid_source", "message": "paper metric table export source is unsupported"})
    if report.get("contract_schema") != "libreevolve.paper_evaluator_metric_contract.v1":
        issues.append({"code": "invalid_contract_schema", "message": "paper metric table export must consume the evaluator metric contract"})
    columns = report.get("columns")
    if columns != _PAPER_METRIC_TABLE_COLUMNS:
        issues.append({"code": "invalid_columns", "message": "paper metric table columns are not stable"})
    rows = report.get("rows")
    if not isinstance(rows, list):
        issues.append({"code": "invalid_rows", "message": "paper metric table rows must be a list"})
        rows = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            issues.append({"code": "invalid_row", "message": f"paper metric table row {index} must be an object"})
            continue
        missing_columns = set(_PAPER_METRIC_TABLE_COLUMNS) - set(row)
        if missing_columns:
            issues.append({"code": "missing_row_columns", "message": f"paper metric table row {index} missing columns: {sorted(missing_columns)}"})
        if not isinstance(row.get("metric_name"), str) or not row.get("metric_name"):
            issues.append({"code": "invalid_metric_name", "message": f"paper metric table row {index} metric_name is invalid"})
        if not isinstance(row.get("program_id"), str) or not row.get("program_id"):
            issues.append({"code": "invalid_program_id", "message": f"paper metric table row {index} program_id is invalid"})
        if row.get("direction") not in {"maximize", "minimize"}:
            issues.append({"code": "invalid_direction", "message": f"paper metric table row {index} direction is invalid"})
        for field in ("raw_value", "maximized_value"):
            value = row.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                issues.append({"code": f"invalid_{field}", "message": f"paper metric table row {index} {field} must be finite"})
        normalized = row.get("normalized_value")
        if normalized is not None and (
            isinstance(normalized, bool)
            or not isinstance(normalized, (int, float))
            or not math.isfinite(float(normalized))
            or not 0.0 <= float(normalized) <= 1.0
        ):
            issues.append({"code": "invalid_normalized_value", "message": f"paper metric table row {index} normalized_value must be in [0, 1] or null"})
        if row.get("raw_display") != _paper_metric_display_significant(_paper_metric_table_number(row.get("raw_value")), 12):
            issues.append({"code": "invalid_raw_display", "message": f"paper metric table row {index} raw_display does not match policy"})
        if row.get("maximized_display") != _paper_metric_display_significant(_paper_metric_table_number(row.get("maximized_value")), 12):
            issues.append({"code": "invalid_maximized_display", "message": f"paper metric table row {index} maximized_display does not match policy"})
        if row.get("normalized_display") != _paper_metric_display_fixed(_paper_metric_table_number(row.get("normalized_value")), 6):
            issues.append({"code": "invalid_normalized_display", "message": f"paper metric table row {index} normalized_display does not match policy"})
    if isinstance(report.get("row_count"), int) and not isinstance(report.get("row_count"), bool):
        if report.get("rows_truncated") is not True and report["row_count"] != len(rows):
            issues.append({"code": "invalid_row_count", "message": "row_count must match rows when not truncated"})
    else:
        issues.append({"code": "invalid_row_count", "message": "row_count must be an integer"})
    if not isinstance(report.get("display_policy"), dict):
        issues.append({"code": "invalid_display_policy", "message": "display_policy must be an object"})
    if not isinstance(report.get("export_formats"), dict):
        issues.append({"code": "invalid_export_formats", "message": "export_formats must be an object"})
    table_sha = report.get("table_sha256")
    if not isinstance(table_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", table_sha):
        issues.append({"code": "invalid_table_sha256", "message": "table_sha256 must be a SHA-256 hex digest"})
    elif report.get("rows_truncated") is not True and columns == _PAPER_METRIC_TABLE_COLUMNS:
        expected_sha = hashlib.sha256(
            json.dumps(
                {"columns": columns, "rows": rows},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if table_sha != expected_sha:
            issues.append({"code": "table_sha256_mismatch", "message": "table_sha256 must match stable column/row payload"})
    readiness = report.get("claim_readiness")
    if not isinstance(readiness, dict):
        issues.append({"code": "invalid_claim_readiness", "message": "claim_readiness must be an object"})
    elif readiness.get("cross_run_metric_contract_diff") is not False:
        issues.append({"code": "cross_run_overclaim", "message": "cross-run metric contract diff must remain false until implemented"})
    return {
        "schema": "libreevolve.paper_metric_table_export.v1",
        "ok": not issues,
        "issues": issues,
    }


def validate_paper_evaluator_metric_contract(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.paper_evaluator_metric_contract.v1",
            "ok": False,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "paper evaluator metric contract must be an object",
                }
            ],
        }
    required = {
        "schema",
        "source",
        "primary_metric",
        "declared_metric_names",
        "paper_metric_names",
        "excluded_declared_metrics",
        "metric_count",
        "paper_metric_count",
        "metrics",
        "validity_gate",
        "excluded_reserved_fields",
        "non_scalar_attachment_summary",
        "feedback_metric_exclusion_policy",
        "normalization_policy",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append({"code": "missing_fields", "message": f"metric contract missing fields: {sorted(missing)}"})
    if report.get("schema") != "libreevolve.paper_evaluator_metric_contract.v1":
        issues.append({"code": "invalid_schema", "message": "metric contract schema is unsupported"})
    if report.get("source") != "objective_schema_and_runtime_history":
        issues.append({"code": "invalid_source", "message": "metric contract source is unsupported"})
    metrics = report.get("metrics")
    if not isinstance(metrics, list):
        issues.append({"code": "invalid_metrics", "message": "metrics must be a list"})
        metrics = []
    declared_names: list[str] = []
    paper_names: list[str] = []
    for index, metric in enumerate(metrics):
        if not isinstance(metric, dict):
            issues.append({"code": "invalid_metric", "message": f"metric {index} must be an object"})
            continue
        name = metric.get("name")
        if not isinstance(name, str) or not name:
            issues.append({"code": "invalid_metric_name", "message": f"metric {index} name is invalid"})
            continue
        declared_names.append(name)
        if name in {"is_valid", "outputs", "program_output", "feedback_adjusted_fitness"}:
            issues.append({"code": "reserved_metric_name", "message": f"reserved field {name} must not be a paper metric"})
        if metric.get("paper_metric") is True:
            paper_names.append(name)
            if metric.get("source") != "evaluator":
                issues.append({"code": "invalid_paper_metric_source", "message": f"paper metric {name} is not evaluator-sourced"})
        elif metric.get("source") == "evaluator":
            issues.append({"code": "evaluator_metric_not_paper_metric", "message": f"evaluator metric {name} must be paper-facing"})
        if metric.get("direction") not in {"maximize", "minimize"}:
            issues.append({"code": "invalid_direction", "message": f"metric {name} direction is invalid"})
        bounds = metric.get("bounds")
        if (
            not isinstance(bounds, list)
            or len(bounds) != 2
            or any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in bounds)
            or not float(bounds[0]) < float(bounds[1])
        ):
            issues.append({"code": "invalid_bounds", "message": f"metric {name} bounds are invalid"})
        observed = metric.get("observed_values")
        if not isinstance(observed, list):
            issues.append({"code": "invalid_observed_values", "message": f"metric {name} observed_values must be a list"})
        else:
            for value_index, observed_value in enumerate(observed):
                if not isinstance(observed_value, dict):
                    issues.append({"code": "invalid_observed_value", "message": f"metric {name} observed value {value_index} must be an object"})
                    continue
                for field in ("raw_value", "maximized_value"):
                    value = observed_value.get(field)
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                        issues.append({"code": "invalid_observed_number", "message": f"metric {name} observed {field} must be finite"})
                normalized = observed_value.get("normalized_value")
                if normalized is not None and (
                    isinstance(normalized, bool)
                    or not isinstance(normalized, (int, float))
                    or not math.isfinite(float(normalized))
                    or not 0.0 <= float(normalized) <= 1.0
                ):
                    issues.append({"code": "invalid_normalized_value", "message": f"metric {name} normalized value must be in [0, 1]"})
    if report.get("declared_metric_names") != declared_names:
        issues.append({"code": "invalid_declared_names", "message": "declared_metric_names must match metrics order"})
    if report.get("paper_metric_names") != paper_names:
        issues.append({"code": "invalid_paper_names", "message": "paper_metric_names must match evaluator-sourced metrics"})
    if report.get("metric_count") != len(metrics):
        issues.append({"code": "invalid_metric_count", "message": "metric_count must match metrics length"})
    if report.get("paper_metric_count") != len(paper_names):
        issues.append({"code": "invalid_paper_metric_count", "message": "paper_metric_count must match paper_metric_names length"})
    validity_gate = report.get("validity_gate")
    if not isinstance(validity_gate, dict) or validity_gate.get("scored_metric") is not False:
        issues.append({"code": "invalid_validity_gate", "message": "is_valid must be documented as a non-scored gate"})
    reserved_fields = report.get("excluded_reserved_fields")
    if not isinstance(reserved_fields, list):
        issues.append({"code": "invalid_reserved_fields", "message": "excluded_reserved_fields must be a list"})
    else:
        excluded = {field.get("field") for field in reserved_fields if isinstance(field, dict)}
        for field in ("is_valid", "outputs", "program_output", "feedback_adjusted_fitness", "llm_feedback"):
            if field not in excluded:
                issues.append({"code": "missing_reserved_exclusion", "message": f"{field} exclusion is missing"})
    return {
        "schema": "libreevolve.paper_evaluator_metric_contract.v1",
        "ok": not issues,
        "issues": issues,
    }


def _evaluator_oracle_registry_report(
    db: ProgramDatabase,
    programs: list[Program],
) -> dict:
    manifest = db.startup_manifest_snapshot()
    config = manifest.get("config") if isinstance(manifest.get("config"), Mapping) else {}
    problem = manifest.get("problem") if isinstance(manifest.get("problem"), Mapping) else {}
    objective_schema = db.objective_schema_snapshot()
    eval_stages = config.get("eval_stages") if isinstance(config.get("eval_stages"), list) else []
    evaluator_sources = (
        problem.get("evaluator_sources")
        if isinstance(problem.get("evaluator_sources"), list)
        else []
    )
    llm_feedback = (
        config.get("llm_feedback")
        if isinstance(config.get("llm_feedback"), list)
        else []
    )
    oracles = _evaluator_oracle_records(
        eval_stages,
        evaluator_sources,
        llm_feedback,
        objective_schema,
    )
    report = {
        "schema": "libreevolve.evaluator_oracle_registry.v1",
        "source": "startup_manifest_and_runtime_history",
        "oracle_count": len(oracles),
        "oracles": oracles,
        "metric_ownership": _evaluator_oracle_metric_ownership(
            objective_schema,
            llm_feedback,
            "configured_evaluator_cascade" if eval_stages else "evaluator:default",
        ),
        "merge_policy": _evaluator_oracle_merge_policy(config),
        "runtime_summary": _evaluator_oracle_runtime_summary(programs),
        "prompt_feedback_linkage": {
            "stage_feedback": "evaluation.stages_and_configured_stage_results_rendered_by_prompt_sampler",
            "llm_feedback": "evaluation.metadata.llm_feedback_and_llm_feedback_stages",
            "failure_memory": "failure_history_records_can_render_evaluator_and_stage_summaries",
        },
        "claim_ready": False,
        "claim_readiness": {
            "independent_multi_evaluator_oracle_composition": False,
            "reason": (
                "evaluator and feedback oracle identities are registered, but "
                "LibreEvolve still uses one local cascade evaluator plus "
                "post-hoc synchronous feedback graders rather than a general "
                "independent multi-oracle arbitration contract"
            ),
            "remaining_gap": [
                "oracle_authority_configuration",
                "cross_oracle_conflict_resolution_policy",
                "per_oracle_sufficiency_for_benchmark_claims",
                "independent_reference_checker_or_statistical_test_oracles",
            ],
        },
    }
    report["validation"] = validate_evaluator_oracle_registry(report)
    return report


def _evaluator_oracle_records(
    eval_stages: list,
    evaluator_sources: list,
    llm_feedback: list,
    objective_schema: dict,
) -> list[dict]:
    records: list[dict] = []
    if eval_stages:
        source_by_stage = _evaluator_source_by_stage(evaluator_sources)
        for index, raw_stage in enumerate(eval_stages):
            if not isinstance(raw_stage, Mapping):
                continue
            name = str(raw_stage.get("name", f"stage_{index}"))
            mode = str(raw_stage.get("mode", "external_validator"))
            source = source_by_stage.get((index, name), {})
            records.append(
                {
                    "oracle_id": f"stage:{name}",
                    "oracle_type": (
                        "candidate_embedded_evaluator"
                        if mode == "embedded_evaluate"
                        else "deterministic_validator"
                    ),
                    "role": "configured_cascade_stage",
                    "authority": "candidate_validity_and_metric_gate",
                    "stage_name": name,
                    "stage_index": index,
                    "input_schema": (
                        "candidate_primary_module.evaluate(eval_inputs)"
                        if mode == "embedded_evaluate"
                        else "evaluate(code, workspace_path, stage)"
                    ),
                    "output_schema": "declared_metrics_plus_boolean_is_valid",
                    "metric_ownership": _evaluator_owned_metric_names(objective_schema),
                    "failure_policy": (
                        "stage_failure_or_threshold_failure_stops_candidate_cascade"
                    ),
                    "prompt_feedback_linkage": "configured_stage_results_and_stage_summaries",
                    "source": _evaluator_oracle_source_ref(source),
                }
            )
    else:
        source = _default_evaluator_source(evaluator_sources)
        records.append(
            {
                "oracle_id": "evaluator:default",
                "oracle_type": "deterministic_validator",
                "role": "default_problem_validator",
                "authority": "candidate_validity_and_metric_gate",
                "input_schema": "evaluate(code)_or_evaluate(code, workspace_path)",
                "output_schema": "declared_metrics_plus_boolean_is_valid",
                "metric_ownership": _evaluator_owned_metric_names(objective_schema),
                "failure_policy": "invalid_evaluation_blocks_database_admission",
                "prompt_feedback_linkage": "evaluation_stages_and_execution_summary",
                "source": _evaluator_oracle_source_ref(source),
            }
        )
    for index, raw_grader in enumerate(llm_feedback):
        if not isinstance(raw_grader, Mapping):
            continue
        name = str(raw_grader.get("name", f"feedback_{index}"))
        metric = raw_grader.get("metric")
        records.append(
            {
                "oracle_id": f"llm_feedback:{name}",
                "oracle_type": "llm_judge",
                "role": "post_evaluator_feedback_grader",
                "authority": (
                    "feedback_metric_and_optional_fitness_composition_not_primary_validity_gate"
                ),
                "input_schema": "candidate_workspace_plus_task_and_evaluator_feedback_prompt",
                "output_schema": "finite_score_and_optional_feedback_text",
                "metric_ownership": [metric] if isinstance(metric, str) else [],
                "failure_policy": str(raw_grader.get("failure_policy", "discard")),
                "prompt_feedback_linkage": "evaluation.metadata.llm_feedback",
                "source": {
                    "configured_feedback_index": index,
                    "metric": metric,
                    "objective_metric": raw_grader.get("objective_metric") is True,
                },
            }
        )
    return records


def _evaluator_source_by_stage(evaluator_sources: list) -> dict[tuple[int, str], Mapping[str, object]]:
    by_stage: dict[tuple[int, str], Mapping[str, object]] = {}
    for source in evaluator_sources:
        if not isinstance(source, Mapping):
            continue
        if source.get("role") != "stage":
            continue
        stage_index = source.get("stage_index")
        stage_name = source.get("stage_name")
        if (
            isinstance(stage_index, int)
            and not isinstance(stage_index, bool)
            and isinstance(stage_name, str)
        ):
            by_stage[(stage_index, stage_name)] = source
    return by_stage


def _default_evaluator_source(evaluator_sources: list) -> Mapping[str, object]:
    for source in evaluator_sources:
        if isinstance(source, Mapping) and source.get("role") == "default":
            return source
    return {}


def _evaluator_oracle_source_ref(source: Mapping[str, object]) -> dict:
    if not source:
        return {"status": "not_available"}
    return {
        "role": source.get("role"),
        "stage_name": source.get("stage_name"),
        "stage_index": source.get("stage_index"),
        "relative_path": source.get("relative_path"),
        "sha256": source.get("sha256"),
        "source_type": source.get("source_type"),
    }


def _evaluator_owned_metric_names(objective_schema: Mapping[str, object]) -> list[str]:
    metrics = objective_schema.get("metrics")
    if not isinstance(metrics, list):
        return []
    names = [
        metric.get("name")
        for metric in metrics
        if isinstance(metric, Mapping) and metric.get("source", "evaluator") == "evaluator"
    ]
    return [name for name in names if isinstance(name, str)]


def _evaluator_oracle_metric_ownership(
    objective_schema: Mapping[str, object],
    llm_feedback: list,
    evaluator_oracle_id: str,
) -> list[dict]:
    feedback_by_metric = {
        grader.get("metric"): str(grader.get("name", f"feedback_{index}"))
        for index, grader in enumerate(llm_feedback)
        if isinstance(grader, Mapping) and isinstance(grader.get("metric"), str)
    }
    ownership: list[dict] = []
    metrics = objective_schema.get("metrics")
    if not isinstance(metrics, list):
        return ownership
    for metric in metrics:
        if not isinstance(metric, Mapping) or not isinstance(metric.get("name"), str):
            continue
        name = metric["name"]
        source = str(metric.get("source", "evaluator"))
        if source == "evaluator":
            oracle_id = evaluator_oracle_id
        elif source == "feedback":
            oracle_id = f"llm_feedback:{feedback_by_metric.get(name, '<unmatched>')}"
        else:
            oracle_id = f"{source}:not_registered_evaluator_oracle"
        ownership.append(
            {
                "metric": name,
                "source": source,
                "primary": metric.get("primary") is True,
                "oracle_id": oracle_id,
                "paper_evaluator_metric": source == "evaluator",
            }
        )
    return ownership


def _evaluator_oracle_merge_policy(config: Mapping[str, object]) -> dict:
    eval_stages = config.get("eval_stages") if isinstance(config.get("eval_stages"), list) else []
    llm_feedback = config.get("llm_feedback") if isinstance(config.get("llm_feedback"), list) else []
    return {
        "schema": "libreevolve.evaluator_oracle_merge_policy.v1",
        "evaluator_policy": (
            "configured_stage_cascade_in_order"
            if eval_stages
            else "single_default_validator"
        ),
        "stage_stop_policy": "first_failed_stage_stops_candidate",
        "validity_policy": "evaluator_is_valid_and_thresholds_gate_admission",
        "llm_feedback_policy": (
            "synchronous_post_evaluator_feedback_graders"
            if llm_feedback
            else "not_configured"
        ),
        "feedback_aggregation_policy": "weighted_delta_after_evaluator_validity",
        "conflict_policy": (
            "no_general_cross_oracle_conflict_arbitration_beyond_configured_order"
        ),
    }


def _evaluator_oracle_runtime_summary(programs: list[Program]) -> dict:
    evaluated_program_count = 0
    valid_count = 0
    invalid_count = 0
    configured_stage_record_count = 0
    llm_feedback_record_count = 0
    for program in programs:
        evaluation = program.evaluation if isinstance(program.evaluation, dict) else {}
        if not evaluation:
            continue
        evaluated_program_count += 1
        if evaluation.get("is_valid") is True:
            valid_count += 1
        elif evaluation.get("is_valid") is False:
            invalid_count += 1
        metadata = evaluation.get("metadata") if isinstance(evaluation.get("metadata"), dict) else {}
        configured = metadata.get("configured_stage_results")
        if isinstance(configured, list):
            configured_stage_record_count += sum(1 for item in configured if isinstance(item, dict))
        feedback = metadata.get("llm_feedback")
        if isinstance(feedback, list):
            llm_feedback_record_count += sum(1 for item in feedback if isinstance(item, dict))
    return {
        "evaluated_program_count": evaluated_program_count,
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "configured_stage_record_count": configured_stage_record_count,
        "llm_feedback_record_count": llm_feedback_record_count,
    }


def _embedded_evaluator_entrypoint_report(programs: list[Program]) -> dict:
    records = []
    external_candidate_count = 0
    embedded_candidate_count = 0
    for program in programs:
        evaluation = program.evaluation if isinstance(program.evaluation, dict) else {}
        metadata = (
            evaluation.get("metadata")
            if isinstance(evaluation.get("metadata"), Mapping)
            else {}
        )
        mode = metadata.get("evaluator_mode")
        if mode == "embedded_evaluate":
            embedded_candidate_count += 1
            records.append(_embedded_entrypoint_record(program, metadata))
        elif mode == "external_validator":
            external_candidate_count += 1
        configured = metadata.get("configured_stage_results")
        if isinstance(configured, list):
            for stage in configured:
                if not isinstance(stage, Mapping):
                    continue
                stage_metadata = (
                    stage.get("metadata")
                    if isinstance(stage.get("metadata"), Mapping)
                    else {}
                )
                if stage_metadata.get("evaluator_mode") == "embedded_evaluate":
                    records.append(
                        _embedded_entrypoint_record(
                            program,
                            stage_metadata,
                            stage_result=stage,
                        )
                    )
    records = _dedupe_embedded_entrypoint_records(records)
    report = {
        "schema": "libreevolve.embedded_evaluator_entrypoint_report.v1",
        "source": "runtime_history_evaluation_metadata",
        "embedded_candidate_count": embedded_candidate_count,
        "external_validator_candidate_count": external_candidate_count,
        "embedded_entrypoint_count": len(records),
        "records": records[:50],
        "records_limit": 50,
        "records_truncated": len(records) > 50,
        "entrypoint_contract": {
            "mode": "embedded_evaluate",
            "callable": "evaluate",
            "signature": "evaluate(eval_inputs)",
            "eval_inputs_policy": "json_safe_config_data_hashed_not_retained",
            "dependency_policy": "candidate_primary_module_embedded_evaluate_v1",
            "input_schema": "candidate_primary_module.evaluate(eval_inputs)",
            "output_schema": "declared_metrics_plus_boolean_is_valid",
        },
        "claim_ready": False,
        "claim_readiness": {
            "candidate_owned_evaluate_entrypoint": bool(records),
            "embedded_only_problem_definition": False,
            "evolved_block_to_score_path_mapping": False,
            "remaining_gap": [
                "load_problem_without_external_validate_py",
                "skeleton_to_evolved_block_invocation_trace",
                "score_field_to_evolved_code_path_mapping",
                "stronger_callable_isolation_or_build_policy",
            ],
        },
    }
    report["validation"] = validate_embedded_evaluator_entrypoint_report(report)
    return report


def _embedded_entrypoint_record(
    program: Program,
    metadata: Mapping[str, object],
    *,
    stage_result: Mapping[str, object] | None = None,
) -> dict:
    candidate = (
        metadata.get("candidate_evaluator")
        if isinstance(metadata.get("candidate_evaluator"), Mapping)
        else {}
    )
    stage = metadata.get("stage") if isinstance(metadata.get("stage"), Mapping) else {}
    dependency = (
        metadata.get("evaluator_dependency_policy")
        if isinstance(metadata.get("evaluator_dependency_policy"), Mapping)
        else {}
    )
    record = {
        "program_id": program.id,
        "generation": program.generation,
        "stage_name": stage.get("name") or (
            stage_result.get("name") if isinstance(stage_result, Mapping) else None
        ),
        "stage_index": stage.get("stage_index"),
        "evaluator_mode": "embedded_evaluate",
        "entrypoint": candidate.get("entrypoint"),
        "callable": candidate.get("callable"),
        "signature": candidate.get("signature"),
        "eval_inputs": copy.deepcopy(candidate.get("eval_inputs"))
        if isinstance(candidate.get("eval_inputs"), Mapping)
        else {},
        "dependency_policy": {
            key: dependency.get(key)
            for key in (
                "policy",
                "allowed_scope",
                "problem_local_dependency_policy",
                "outside_problem_policy",
            )
            if key in dependency
        },
        "passed": stage_result.get("passed")
        if isinstance(stage_result, Mapping)
        else program.evaluation.get("is_valid"),
        "score": _paper_metric_table_number(
            stage_result.get("score") if isinstance(stage_result, Mapping) else program.fitness
        ),
        "metric_names": _embedded_entrypoint_metric_names(
            stage_result.get("metrics")
            if isinstance(stage_result, Mapping)
            else program.metrics
        ),
        "validator_boundary": "temporary_local_subprocess",
        "raw_eval_inputs_retained": (
            candidate.get("eval_inputs", {}).get("retained")
            if isinstance(candidate.get("eval_inputs"), Mapping)
            else None
        ),
    }
    return {key: value for key, value in record.items() if value is not None}


def _embedded_entrypoint_metric_names(metrics: object) -> list[str]:
    if not isinstance(metrics, Mapping):
        return []
    return sorted(
        name
        for name, value in metrics.items()
        if isinstance(name, str)
        and name != "is_valid"
        and isinstance(value, (int, float))
        and not isinstance(value, bool)
    )


def _dedupe_embedded_entrypoint_records(records: list[dict]) -> list[dict]:
    deduped = []
    seen = set()
    for record in records:
        key = (
            record.get("program_id"),
            record.get("stage_name"),
            record.get("stage_index"),
            record.get("entrypoint"),
            record.get("signature"),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    deduped.sort(
        key=lambda item: (
            int(item.get("generation", 0))
            if isinstance(item.get("generation"), int)
            and not isinstance(item.get("generation"), bool)
            else 0,
            str(item.get("program_id", "")),
            str(item.get("stage_name", "")),
        )
    )
    return deduped


def validate_embedded_evaluator_entrypoint_report(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.embedded_evaluator_entrypoint_report.v1",
            "ok": False,
            "issues": [
                {"code": "invalid_shape", "message": "embedded evaluator entrypoint report must be an object"}
            ],
        }
    required = {
        "schema",
        "source",
        "embedded_candidate_count",
        "external_validator_candidate_count",
        "embedded_entrypoint_count",
        "records",
        "records_limit",
        "records_truncated",
        "entrypoint_contract",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append({"code": "missing_fields", "message": f"embedded evaluator entrypoint report missing fields: {sorted(missing)}"})
    if report.get("schema") != "libreevolve.embedded_evaluator_entrypoint_report.v1":
        issues.append({"code": "invalid_schema", "message": "embedded evaluator entrypoint report schema is unsupported"})
    if report.get("source") != "runtime_history_evaluation_metadata":
        issues.append({"code": "invalid_source", "message": "embedded evaluator entrypoint report source is unsupported"})
    records = report.get("records")
    if not isinstance(records, list):
        issues.append({"code": "invalid_records", "message": "records must be a list"})
        records = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append({"code": "invalid_record", "message": f"record {index} must be an object"})
            continue
        if not isinstance(record.get("program_id"), str) or not record.get("program_id"):
            issues.append({"code": "invalid_program_id", "message": f"record {index} program_id is invalid"})
        if record.get("evaluator_mode") != "embedded_evaluate":
            issues.append({"code": "invalid_evaluator_mode", "message": f"record {index} evaluator_mode must be embedded_evaluate"})
        if record.get("callable") != "evaluate":
            issues.append({"code": "invalid_callable", "message": f"record {index} callable must be evaluate"})
        if record.get("signature") != "evaluate(eval_inputs)":
            issues.append({"code": "invalid_signature", "message": f"record {index} signature must be evaluate(eval_inputs)"})
        eval_inputs = record.get("eval_inputs")
        if not isinstance(eval_inputs, dict) or eval_inputs.get("schema") != "libreevolve.eval_inputs_provenance.v1":
            issues.append({"code": "invalid_eval_inputs", "message": f"record {index} eval_inputs provenance is invalid"})
        elif eval_inputs.get("retained") is not False:
            issues.append({"code": "eval_inputs_retention_overclaim", "message": f"record {index} eval inputs must remain hashed/not retained"})
        dependency = record.get("dependency_policy")
        if not isinstance(dependency, dict) or dependency.get("policy") != "candidate_primary_module_embedded_evaluate_v1":
            issues.append({"code": "invalid_dependency_policy", "message": f"record {index} dependency policy is invalid"})
        if not isinstance(record.get("metric_names"), list):
            issues.append({"code": "invalid_metric_names", "message": f"record {index} metric_names must be a list"})
    if report.get("records_truncated") is not True:
        if report.get("embedded_entrypoint_count") != len(records):
            issues.append({"code": "invalid_entrypoint_count", "message": "embedded_entrypoint_count must match records when not truncated"})
    for field in ("embedded_candidate_count", "external_validator_candidate_count"):
        value = report.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            issues.append({"code": f"invalid_{field}", "message": f"{field} must be a non-negative integer"})
    contract = report.get("entrypoint_contract")
    if not isinstance(contract, dict) or contract.get("signature") != "evaluate(eval_inputs)":
        issues.append({"code": "invalid_entrypoint_contract", "message": "entrypoint contract must describe evaluate(eval_inputs)"})
    if report.get("claim_ready") is not False:
        issues.append({"code": "claim_ready_overclaim", "message": "embedded evaluator report must not claim full Figure 3 parity"})
    readiness = report.get("claim_readiness")
    if not isinstance(readiness, dict):
        issues.append({"code": "invalid_claim_readiness", "message": "claim_readiness must be an object"})
    elif readiness.get("embedded_only_problem_definition") is not False:
        issues.append({"code": "embedded_only_overclaim", "message": "embedded-only problem definition must remain false"})
    return {
        "schema": "libreevolve.embedded_evaluator_entrypoint_report.v1",
        "ok": not issues,
        "issues": issues,
    }


def validate_evaluator_oracle_registry(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.evaluator_oracle_registry.v1",
            "ok": False,
            "issues": [
                {"code": "invalid_shape", "message": "oracle registry must be an object"}
            ],
        }
    required = {
        "schema",
        "source",
        "oracle_count",
        "oracles",
        "metric_ownership",
        "merge_policy",
        "runtime_summary",
        "prompt_feedback_linkage",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append({"code": "missing_fields", "message": f"oracle registry missing fields: {sorted(missing)}"})
    if report.get("schema") != "libreevolve.evaluator_oracle_registry.v1":
        issues.append({"code": "invalid_schema", "message": "oracle registry schema is unsupported"})
    if report.get("source") != "startup_manifest_and_runtime_history":
        issues.append({"code": "invalid_source", "message": "oracle registry source is unsupported"})
    oracles = report.get("oracles")
    if not isinstance(oracles, list):
        issues.append({"code": "invalid_oracles", "message": "oracles must be a list"})
        oracles = []
    allowed_types = {
        "deterministic_validator",
        "candidate_embedded_evaluator",
        "statistical_test",
        "reference_checker",
        "llm_judge",
    }
    seen_ids: set[str] = set()
    for index, oracle in enumerate(oracles):
        if not isinstance(oracle, dict):
            issues.append({"code": "invalid_oracle", "message": f"oracle {index} must be an object"})
            continue
        oracle_id = oracle.get("oracle_id")
        if not isinstance(oracle_id, str) or not oracle_id:
            issues.append({"code": "invalid_oracle_id", "message": f"oracle {index} id is invalid"})
        elif oracle_id in seen_ids:
            issues.append({"code": "duplicate_oracle_id", "message": f"oracle id {oracle_id!r} is duplicated"})
        else:
            seen_ids.add(oracle_id)
        if oracle.get("oracle_type") not in allowed_types:
            issues.append({"code": "invalid_oracle_type", "message": f"oracle {index} type is invalid"})
        for field in ("role", "authority", "input_schema", "output_schema", "failure_policy", "prompt_feedback_linkage"):
            if not isinstance(oracle.get(field), str) or not oracle.get(field):
                issues.append({"code": "invalid_oracle_field", "message": f"oracle {index} {field} must be a non-empty string"})
        if not isinstance(oracle.get("metric_ownership"), list):
            issues.append({"code": "invalid_oracle_metric_ownership", "message": f"oracle {index} metric ownership must be a list"})
    if report.get("oracle_count") != len(oracles):
        issues.append({"code": "invalid_oracle_count", "message": "oracle_count must match oracles length"})
    ownership = report.get("metric_ownership")
    if not isinstance(ownership, list):
        issues.append({"code": "invalid_metric_ownership", "message": "metric_ownership must be a list"})
    else:
        for index, item in enumerate(ownership):
            if not isinstance(item, dict) or not isinstance(item.get("metric"), str):
                issues.append({"code": "invalid_metric_owner", "message": f"metric ownership {index} is invalid"})
            elif not isinstance(item.get("oracle_id"), str) or not item.get("oracle_id"):
                issues.append({"code": "invalid_metric_owner_oracle", "message": f"metric ownership {index} oracle_id is invalid"})
    merge_policy = report.get("merge_policy")
    if not isinstance(merge_policy, dict) or merge_policy.get("schema") != "libreevolve.evaluator_oracle_merge_policy.v1":
        issues.append({"code": "invalid_merge_policy", "message": "merge_policy is invalid"})
    if not isinstance(report.get("runtime_summary"), dict):
        issues.append({"code": "invalid_runtime_summary", "message": "runtime_summary must be an object"})
    return {
        "schema": "libreevolve.evaluator_oracle_registry.v1",
        "ok": not issues,
        "issues": issues,
    }


def _evaluator_workload_report(programs: list[Program]) -> dict:
    stages: dict[str, dict] = {}
    workload_type_counts: dict[str, int] = {}
    configured_candidate_count = 0
    for program in programs:
        evaluation = program.evaluation if isinstance(program.evaluation, dict) else {}
        metadata = evaluation.get("metadata") if isinstance(evaluation.get("metadata"), dict) else {}
        configured = metadata.get("configured_stage_results")
        if not isinstance(configured, list):
            continue
        configured_candidate_count += 1
        for stage_index, raw_stage in enumerate(configured):
            if not isinstance(raw_stage, dict):
                continue
            name = str(raw_stage.get("name", f"stage_{stage_index}"))
            workload = _configured_stage_workload(raw_stage)
            workload_type = str(workload.get("type", "simple_check"))
            declared = bool(workload.get("declared"))
            workload_type_counts[workload_type] = workload_type_counts.get(workload_type, 0) + 1
            key = f"{raw_stage.get('stage_index', stage_index)}:{name}"
            stage = stages.setdefault(
                key,
                {
                    "name": name,
                    "stage_index": raw_stage.get("stage_index", stage_index),
                    "workload_type": workload_type,
                    "declaration_source": workload["source"],
                    "declared": declared,
                    "candidate_count": 0,
                    "passed": 0,
                    "failed": 0,
                    "datasets": workload.get("datasets", []),
                    "budget": workload.get("budget", {}),
                    "checkpoint_policy": workload.get("checkpoint_policy", "not_declared"),
                    "score_fields": workload.get("score_fields", []),
                    "artifact_policy": workload.get("artifact_policy", "not_declared"),
                    "seed_count": workload.get("seed_count", 0),
                    "sample_count": 0,
                    "retry_attempts": 0,
                    "subprocess_attempts": 0,
                    "timeout_count": 0,
                    "candidate_ids": [],
                },
            )
            stage["candidate_count"] += 1
            stage["candidate_ids"].append(program.id)
            if raw_stage.get("passed") is True:
                stage["passed"] += 1
            else:
                stage["failed"] += 1
            accounting = evaluation_accounting(raw_stage)
            stage["sample_count"] += int(accounting.get("configured_stage_samples", 0))
            stage["retry_attempts"] += int(accounting.get("retry_attempts", 0))
            stage["subprocess_attempts"] += int(accounting.get("subprocess_attempts", 0))
            stage["timeout_count"] += int(accounting.get("timeout_count", 0))
    ordered_stages = [
        _finalize_workload_stage_record(record)
        for record in sorted(stages.values(), key=lambda item: (item["stage_index"], item["name"]))
    ]
    declared_workload_stage_count = sum(1 for stage in ordered_stages if stage["declared"])
    report = {
        "schema": "libreevolve.evaluator_workload_report.v1",
        "source": "runtime_history_configured_stage_results",
        "configured_candidate_count": configured_candidate_count,
        "stage_count": len(ordered_stages),
        "declared_workload_stage_count": declared_workload_stage_count,
        "workload_type_counts": dict(sorted(workload_type_counts.items())),
        "stages": ordered_stages,
        "claim_ready": False,
        "claim_readiness": {
            "alphaevolve_inner_search_or_ml_training": False,
            "reason": (
                "stage workload metadata is preserved and aggregated, but "
                "LibreEvolve does not yet enforce workload-specific protocol "
                "execution, artifact completeness, or statistical linkage"
            ),
            "remaining_gap": [
                "dataset_and_split_hash_enforcement",
                "training_or_inner_search_protocol_runner",
                "checkpoint_artifact_completeness_checks",
                "score_field_to_artifact_validation",
                "stochastic_re_evaluation_policy",
            ],
        },
    }
    report["validation"] = validate_evaluator_workload_report(report)
    return report


def _proposal_lifecycle_report(
    db: ProgramDatabase,
    programs: list[Program],
) -> dict:
    generated_programs = [
        program
        for program in programs
        if isinstance(program.metadata, dict)
        and program.metadata.get("candidate_type") == "generated"
    ]
    failure_records = db.failure_records_snapshot()
    generated_failures = [
        record
        for record in failure_records
        if isinstance(record, dict)
        and record.get("record_type", "generated") == "generated"
    ]
    failure_by_program_id = {
        record["program_id"]: record
        for record in generated_failures
        if isinstance(record.get("program_id"), str)
    }
    generated_program_ids = {program.id for program in generated_programs}
    lifecycle_records = [
        _proposal_lifecycle_history_record(
            program,
            failure_by_program_id.get(program.id),
        )
        for program in generated_programs
    ] + [
        _proposal_lifecycle_failure_record(record)
        for record in generated_failures
        if record.get("program_id") not in generated_program_ids
    ]
    lifecycle_records.sort(key=_proposal_lifecycle_sort_key)
    accepted_invalid_count = sum(
        1
        for record in lifecycle_records
        if record.get("lifecycle_status") == "accepted_history"
        and record.get("evaluator_is_valid") is not True
    )
    accepted_generated_count = sum(
        1
        for record in lifecycle_records
        if record.get("lifecycle_status") == "accepted_history"
    )
    rejected_generated_count = sum(
        1
        for record in lifecycle_records
        if str(record.get("lifecycle_status", "")).startswith("rejected_")
    )
    evaluation_filtered_count = sum(
        1 for record in lifecycle_records if record.get("execution_filtered") is True
    )
    report = {
        "schema": "libreevolve.proposal_lifecycle_report.v1",
        "source": "history_and_failure_history_records",
        "generated_candidate_count": len(lifecycle_records),
        "accepted_generated_count": accepted_generated_count,
        "rejected_generated_count": rejected_generated_count,
        "execution_filtered_count": evaluation_filtered_count,
        "diff_or_parse_error_count": sum(
            1 for record in lifecycle_records if record.get("diff_error") is not None
        ),
        "invalid_evaluation_count": sum(
            1 for record in lifecycle_records if record.get("evaluator_is_valid") is False
        ),
        "archive_rejected_count": sum(
            1
            for record in lifecycle_records
            if record.get("admission", {}).get("admitted") is False
        ),
        "accepted_invalid_count": accepted_invalid_count,
        "rejection_reasons": _proposal_lifecycle_rejection_reasons(lifecycle_records),
        "records": lifecycle_records[:50],
        "records_truncated": len(lifecycle_records) > 50,
        "feedback_reuse": {
            "failure_record_count": len(failure_records),
            "generated_failure_record_count": len(generated_failures),
            "failure_memory_context_count": len(db.retrieval_failure_context),
            "failure_memory_policy": (
                "bounded_recent_failure_records_rendered_by_prompt_sampler_when_available"
            ),
            "failure_index_source": "runtime.history.failure_index",
            "queryable_failure_fingerprints": True,
        },
        "false_acceptance_review": {
            "status": "not_independently_reviewed",
            "accepted_invalid_count": accepted_invalid_count,
            "policy": (
                "history admission requires evaluator is_valid true before archive "
                "retention, but no independent false-acceptance audit is run"
            ),
        },
        "false_rejection_review": {
            "status": "not_independently_reviewed",
            "policy": (
                "rejected candidates are persisted with bounded diagnostics, but "
                "LibreEvolve does not rerun them through a stronger adjudicator"
            ),
        },
        "claim_ready": False,
        "claim_readiness": {
            "execution_grounded_incorrect_suggestion_filtering": True,
            "independent_false_acceptance_rate": False,
            "independent_false_rejection_rate": False,
            "remaining_gap": [
                "independent_rejudge_of_rejected_candidates",
                "cross_run_proposal_lifecycle_table",
                "audited_false_acceptance_and_false_rejection_rates",
                "semantic_failed_proposal_retrieval_beyond_bounded_recent_memory",
            ],
        },
    }
    report["validation"] = validate_proposal_lifecycle_report(report)
    return report


def _proposal_lifecycle_history_record(
    program: Program,
    failure_record: Mapping[str, object] | None = None,
) -> dict:
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    evaluation = program.evaluation if isinstance(program.evaluation, dict) else {}
    admission = (
        metadata.get("archive_admission")
        if isinstance(metadata.get("archive_admission"), dict)
        else {}
    )
    admitted = admission.get("admitted") is True
    diff_error = (
        _proposal_lifecycle_text(failure_record.get("diff_error"), 500)
        if isinstance(failure_record, Mapping)
        else None
    )
    evaluator_error = _proposal_lifecycle_text(evaluation.get("error"), 500)
    rejection_reason = (
        _proposal_lifecycle_text(
            failure_record.get("admission_reason")
            or failure_record.get("diff_error")
            or failure_record.get("error"),
            500,
        )
        if isinstance(failure_record, Mapping)
        else _proposal_lifecycle_text(admission.get("reason"), 500)
    )
    execution_filtered = (
        not admitted
        and (
            diff_error is not None
            or evaluation.get("is_valid") is False
            or admission.get("reason") == "invalid_evaluation"
        )
    )
    record = {
        "proposal_id": program.id,
        "parent_id": program.parent_id,
        "generation": program.generation,
        "proposal_batch": _proposal_lifecycle_batch(metadata.get("proposal_batch")),
        "lifecycle_status": (
            "accepted_history" if admitted else "rejected_history"
        ),
        "evaluator_is_valid": evaluation.get("is_valid"),
        "score": _proposal_lifecycle_number(program.fitness),
        "diff_error": diff_error,
        "evaluator_error": evaluator_error,
        "execution_filtered": execution_filtered,
        "admission": _proposal_lifecycle_admission(admission),
        "llm": _proposal_lifecycle_llm_summary(
            metadata.get("llm_calls"),
            metadata.get("backend_idx"),
        ),
        "mutation": _proposal_lifecycle_mutation_summary(
            metadata.get("diff"),
            mutation_mode=metadata.get("mutation_mode"),
        ),
        "proposal_metadata": _proposal_lifecycle_proposal_metadata(
            metadata.get("proposal")
        ),
    }
    if not admitted:
        record["rejection_reason"] = rejection_reason
        record["failure_record_linked"] = isinstance(failure_record, Mapping)
    return record


def _proposal_lifecycle_failure_record(record: dict) -> dict:
    archive_admission = (
        record.get("archive_admission")
        if isinstance(record.get("archive_admission"), dict)
        else {}
    )
    diff_error = _proposal_lifecycle_text(record.get("diff_error"), 500)
    evaluator_error = _proposal_lifecycle_text(record.get("error"), 500)
    is_valid = record.get("is_valid")
    admitted = archive_admission.get("admitted")
    execution_filtered = (
        diff_error is not None
        or is_valid is False
        or record.get("admission_reason") == "invalid_evaluation"
    )
    return {
        "proposal_id": record.get("program_id"),
        "parent_id": record.get("parent_id"),
        "generation": record.get("generation"),
        "proposal_batch": {},
        "lifecycle_status": "rejected_failure_history",
        "evaluator_is_valid": is_valid if isinstance(is_valid, bool) else None,
        "score": _proposal_lifecycle_number(record.get("score")),
        "diff_error": diff_error,
        "evaluator_error": evaluator_error,
        "execution_filtered": execution_filtered,
        "rejection_reason": _proposal_lifecycle_text(
            record.get("admission_reason") or diff_error or evaluator_error,
            500,
        ),
        "admission": _proposal_lifecycle_admission(archive_admission),
        "llm": _proposal_lifecycle_llm_from_failure(record.get("llm")),
        "mutation": _proposal_lifecycle_failure_mutation(record),
        "proposal_metadata": {"captured": False, "fields": []},
    }


def _proposal_lifecycle_batch(value: object) -> dict:
    if not isinstance(value, Mapping):
        return {}
    result: dict = {}
    for field in (
        "policy",
        "proposal_index",
        "proposal_number",
        "proposals_per_generation",
        "loop_proposal_index",
    ):
        item = value.get(field)
        if isinstance(item, (str, int)) and not isinstance(item, bool):
            result[field] = item
    return result


def _proposal_lifecycle_admission(value: Mapping[str, object]) -> dict:
    if not isinstance(value, Mapping):
        return {}
    result: dict = {}
    for field in (
        "admitted",
        "reason",
        "evaluation_is_valid",
        "cell_admitted",
        "elite_retained",
        "search_state_changed",
        "sampling_eligible",
    ):
        item = value.get(field)
        if isinstance(item, (str, bool)):
            result[field] = item
    return result


def _proposal_lifecycle_llm_summary(
    calls: object,
    backend_idx: object = None,
) -> dict:
    summary: dict = {}
    if isinstance(backend_idx, int) and not isinstance(backend_idx, bool):
        summary["backend_idx"] = backend_idx
    if isinstance(calls, list):
        call_records = [
            call_summary
            for call in calls[:5]
            if (call_summary := _proposal_lifecycle_call_summary(call))
        ]
        if call_records:
            summary["calls"] = call_records
            summary["call_count"] = len(calls)
            summary["calls_truncated"] = len(calls) > len(call_records)
    return summary


def _proposal_lifecycle_llm_from_failure(value: object) -> dict:
    if not isinstance(value, Mapping):
        return {}
    summary: dict = {}
    backend_idx = value.get("backend_idx")
    if isinstance(backend_idx, int) and not isinstance(backend_idx, bool):
        summary["backend_idx"] = backend_idx
    calls = value.get("calls")
    if isinstance(calls, list):
        summary["calls"] = [
            call_summary
            for call in calls[:5]
            if (call_summary := _proposal_lifecycle_call_summary(call))
        ]
        call_count = value.get("call_count")
        summary["call_count"] = (
            call_count
            if isinstance(call_count, int) and not isinstance(call_count, bool)
            else len(summary["calls"])
        )
        summary["calls_truncated"] = value.get("calls_truncated") is True
    return summary


def _proposal_lifecycle_call_summary(call: object) -> dict:
    if not isinstance(call, Mapping):
        return {}
    summary: dict = {}
    for field in (
        "id",
        "call_id",
        "role",
        "backend",
        "backend_name",
        "provider",
        "model",
        "status",
        "finish_reason",
        "error",
        "provider_failure_category",
    ):
        value = _proposal_lifecycle_text(call.get(field), 160)
        if value is not None:
            summary[field] = value
    for field in (
        "backend_idx",
        "attempt_index",
        "provider_attempts",
        "prompt_chars",
        "output_chars",
        "total_tokens",
        "cost_microusd",
    ):
        value = call.get(field)
        if isinstance(value, int) and not isinstance(value, bool):
            summary[field] = value
    return summary


def _proposal_lifecycle_mutation_summary(
    value: object,
    *,
    mutation_mode: object = None,
) -> dict:
    summary = {
        "payload_text": isinstance(value, str),
        "payload_type": type(value).__name__,
    }
    if isinstance(mutation_mode, str):
        summary["mutation_mode"] = mutation_mode
    if isinstance(value, str):
        summary["sha256"] = hashlib.sha256(
            value.encode("utf-8", errors="replace")
        ).hexdigest()
        summary["chars"] = len(value)
    return summary


def _proposal_lifecycle_failure_mutation(record: Mapping[str, object]) -> dict:
    summary = {
        "payload_text": record.get("mutation_payload_text"),
        "payload_type": record.get("mutation_payload_type"),
        "sha256": record.get("mutation_sha256"),
        "truncated": record.get("mutation_truncated") is True,
        "source": "failure_history_bounded_mutation_payload",
    }
    return {key: value for key, value in summary.items() if value is not None}


def _proposal_lifecycle_proposal_metadata(value: object) -> dict:
    if not isinstance(value, Mapping):
        return {"captured": False, "fields": []}
    fields = sorted(key for key in value if isinstance(key, str))
    return {
        "captured": bool(fields),
        "fields": fields,
        "text_field_hashes": {
            key: hashlib.sha256(
                str(value[key]).encode("utf-8", errors="replace")
            ).hexdigest()
            for key in fields
            if isinstance(value.get(key), str)
        },
    }


def _proposal_lifecycle_number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(float(value)):
        return None
    return float(value)


def _proposal_lifecycle_text(value: object, max_chars: int) -> str | None:
    if not isinstance(value, str):
        return None
    redacted = redact_sensitive_text(value)
    if len(redacted) <= max_chars:
        return redacted
    if max_chars <= 3:
        return redacted[:max_chars]
    return redacted[: max_chars - 3] + "..."


def _proposal_lifecycle_sort_key(record: dict) -> tuple:
    generation = record.get("generation")
    if not isinstance(generation, int) or isinstance(generation, bool):
        generation = 10**9
    batch = record.get("proposal_batch") if isinstance(record.get("proposal_batch"), dict) else {}
    loop_index = batch.get("loop_proposal_index")
    if not isinstance(loop_index, int) or isinstance(loop_index, bool):
        loop_index = 10**9
    proposal_id = record.get("proposal_id") if isinstance(record.get("proposal_id"), str) else ""
    return generation, loop_index, proposal_id


def _proposal_lifecycle_rejection_reasons(records: list[dict]) -> dict:
    reasons: dict[str, int] = {}
    for record in records:
        if not str(record.get("lifecycle_status", "")).startswith("rejected_"):
            continue
        reason = record.get("rejection_reason")
        if not isinstance(reason, str) or not reason:
            reason = "unknown"
        reasons[reason] = reasons.get(reason, 0) + 1
    return dict(sorted(reasons.items()))


def validate_proposal_lifecycle_report(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.proposal_lifecycle_report.v1",
            "ok": False,
            "issues": [
                {"code": "invalid_shape", "message": "proposal lifecycle report must be an object"}
            ],
        }
    required = {
        "schema",
        "source",
        "generated_candidate_count",
        "accepted_generated_count",
        "rejected_generated_count",
        "execution_filtered_count",
        "diff_or_parse_error_count",
        "invalid_evaluation_count",
        "archive_rejected_count",
        "accepted_invalid_count",
        "rejection_reasons",
        "records",
        "records_truncated",
        "feedback_reuse",
        "false_acceptance_review",
        "false_rejection_review",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append({"code": "missing_fields", "message": f"proposal lifecycle report missing fields: {sorted(missing)}"})
    if report.get("schema") != "libreevolve.proposal_lifecycle_report.v1":
        issues.append({"code": "invalid_schema", "message": "proposal lifecycle report schema is unsupported"})
    if report.get("source") != "history_and_failure_history_records":
        issues.append({"code": "invalid_source", "message": "proposal lifecycle report source is unsupported"})
    records = report.get("records")
    if not isinstance(records, list):
        issues.append({"code": "invalid_records", "message": "records must be a list"})
        records = []
    accepted = 0
    rejected = 0
    execution_filtered = 0
    diff_errors = 0
    invalid_eval = 0
    archive_rejected = 0
    accepted_invalid = 0
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append({"code": "invalid_record", "message": f"record {index} must be an object"})
            continue
        if not isinstance(record.get("proposal_id"), str) or not record.get("proposal_id"):
            issues.append({"code": "invalid_proposal_id", "message": f"record {index} proposal_id is invalid"})
        status = record.get("lifecycle_status")
        if status == "accepted_history":
            accepted += 1
            if record.get("evaluator_is_valid") is not True:
                accepted_invalid += 1
        elif status in {"rejected_history", "rejected_failure_history"}:
            rejected += 1
        else:
            issues.append({"code": "invalid_lifecycle_status", "message": f"record {index} lifecycle_status is invalid"})
        if record.get("execution_filtered") is True:
            execution_filtered += 1
        if record.get("diff_error") is not None:
            diff_errors += 1
        if record.get("evaluator_is_valid") is False:
            invalid_eval += 1
        admission = record.get("admission")
        if isinstance(admission, dict) and admission.get("admitted") is False:
            archive_rejected += 1
        if not isinstance(record.get("mutation"), dict):
            issues.append({"code": "invalid_mutation_summary", "message": f"record {index} mutation summary is invalid"})
        if not isinstance(record.get("llm"), dict):
            issues.append({"code": "invalid_llm_summary", "message": f"record {index} llm summary is invalid"})
    truncated = report.get("records_truncated") is True
    if not truncated:
        expected = accepted + rejected
        if report.get("generated_candidate_count") != expected:
            issues.append({"code": "invalid_generated_count", "message": "generated_candidate_count must match record count"})
        if report.get("accepted_generated_count") != accepted:
            issues.append({"code": "invalid_accepted_count", "message": "accepted_generated_count must match records"})
        if report.get("rejected_generated_count") != rejected:
            issues.append({"code": "invalid_rejected_count", "message": "rejected_generated_count must match records"})
        if report.get("execution_filtered_count") != execution_filtered:
            issues.append({"code": "invalid_filtered_count", "message": "execution_filtered_count must match records"})
        if report.get("diff_or_parse_error_count") != diff_errors:
            issues.append({"code": "invalid_diff_error_count", "message": "diff_or_parse_error_count must match records"})
        if report.get("invalid_evaluation_count") != invalid_eval:
            issues.append({"code": "invalid_evaluation_count", "message": "invalid_evaluation_count must match records"})
        if report.get("archive_rejected_count") != archive_rejected:
            issues.append({"code": "invalid_archive_rejected_count", "message": "archive_rejected_count must match records"})
        if report.get("accepted_invalid_count") != accepted_invalid:
            issues.append({"code": "invalid_accepted_invalid_count", "message": "accepted_invalid_count must match records"})
    if report.get("accepted_invalid_count") not in (0, accepted_invalid):
        issues.append({"code": "accepted_invalid_overclaim", "message": "accepted invalid count is inconsistent"})
    if not isinstance(report.get("feedback_reuse"), dict):
        issues.append({"code": "invalid_feedback_reuse", "message": "feedback_reuse must be an object"})
    if report.get("claim_ready") is not False:
        issues.append({"code": "invalid_claim_ready", "message": "proposal lifecycle report must not claim independent audit readiness"})
    return {
        "schema": "libreevolve.proposal_lifecycle_report.v1",
        "ok": not issues,
        "issues": issues,
    }


def _hypothesis_branch_report(
    db: ProgramDatabase,
    programs: list[Program],
) -> dict:
    failure_records = db.failure_records_snapshot()
    failure_by_id = {
        record["program_id"]: record
        for record in failure_records
        if isinstance(record, Mapping)
        and record.get("record_type", "generated") == "generated"
        and isinstance(record.get("program_id"), str)
    }
    branches: dict[str, dict] = {}
    for program in programs:
        metadata = program.metadata if isinstance(program.metadata, dict) else {}
        if metadata.get("candidate_type") != "generated":
            continue
        proposal = metadata.get("proposal")
        if not isinstance(proposal, Mapping):
            continue
        branch = _hypothesis_branch_record_for_proposal(proposal)
        if branch is None:
            continue
        branch_record = branches.setdefault(branch["branch_id"], branch)
        _hypothesis_branch_add_program(
            branch_record,
            program,
            failure_by_id.get(program.id),
        )
    finalized = [
        _finalize_hypothesis_branch_record(record)
        for record in branches.values()
    ]
    finalized.sort(key=_hypothesis_branch_sort_key)
    abandonment_count = sum(
        1 for branch in finalized if branch["branch_status"] == "abandoned_evidence"
    )
    report = {
        "schema": "libreevolve.hypothesis_branch_report.v1",
        "source": "history_failure_history_and_proposal_metadata",
        "branch_count": len(finalized),
        "abandoned_branch_count": abandonment_count,
        "active_or_validated_branch_count": sum(
            1
            for branch in finalized
            if branch["branch_status"] == "active_or_validated"
        ),
        "branches": finalized[:50],
        "branches_limit": 50,
        "branches_truncated": len(finalized) > 50,
        "failure_memory_linkage": {
            "failure_record_count": len(failure_records),
            "failure_memory_context_count": len(db.retrieval_failure_context),
            "hypothesis_context_count": len(db.retrieval_hypothesis_context),
            "failure_memory_policy": (
                "bounded_recent_failure_records_rendered_by_prompt_sampler_when_available"
            ),
            "hypothesis_context_policy": (
                "bounded_recent_valid_proposal_hypothesis_context_when_available"
            ),
        },
        "backtracking_policy": {
            "controller_suppression": "not_configured",
            "fallback_target_policy": "inferred_parent_or_alternative_branch_only",
            "resumed_search_outcome_policy": (
                "observed_later_accepted_different_branch_not_causal_proof"
            ),
        },
        "claim_ready": False,
        "claim_readiness": {
            "branch_level_abandonment_evidence": abandonment_count > 0,
            "controller_backtracking_decision": False,
            "redirected_sampling_proof": False,
            "remaining_gap": [
                "explicit_branch_state_machine",
                "controller_suppression_or_retry_policy",
                "fallback_target_selection_event",
                "causal_redirected_sampling_evidence",
                "cross_run_hypothesis_branch_table",
            ],
        },
    }
    report["validation"] = validate_hypothesis_branch_report(report)
    return report


def _hypothesis_branch_record_for_proposal(proposal: Mapping[str, object]) -> dict | None:
    text: dict[str, str] = {}
    for field in ("idea", "hypothesis", "rationale"):
        value = proposal.get(field)
        if isinstance(value, str) and value.strip():
            text[field] = redact_sensitive_text(value.strip())
    if not text:
        return None
    key_payload = json.dumps(text, sort_keys=True, separators=(",", ":"))
    branch_id = "hypothesis-" + hashlib.sha256(
        key_payload.encode("utf-8")
    ).hexdigest()[:16]
    return {
        "branch_id": branch_id,
        "proposal_fields": {
            field: _hypothesis_branch_text_summary(value)
            for field, value in text.items()
        },
        "candidate_ids": [],
        "accepted_candidate_ids": [],
        "rejected_candidate_ids": [],
        "execution_filtered_candidate_ids": [],
        "parent_ids": [],
        "generations": [],
        "rejection_reasons": {},
        "evaluator_errors": {},
        "cascade_stop_reasons": {},
    }


def _hypothesis_branch_text_summary(value: str) -> dict:
    return {
        "policy": "bounded_redacted_branch_text_v1",
        "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "chars": len(value),
        "preview": value[:200],
        "preview_chars": min(len(value), 200),
        "truncated": len(value) > 200,
    }


def _hypothesis_branch_add_program(
    branch: dict,
    program: Program,
    failure_record: Mapping[str, object] | None,
) -> None:
    branch["candidate_ids"].append(program.id)
    if program.parent_id is not None:
        branch["parent_ids"].append(program.parent_id)
    branch["generations"].append(program.generation)
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    admission = (
        metadata.get("archive_admission")
        if isinstance(metadata.get("archive_admission"), Mapping)
        else {}
    )
    evaluation = program.evaluation if isinstance(program.evaluation, dict) else {}
    admitted = admission.get("admitted") is True
    if admitted:
        branch["accepted_candidate_ids"].append(program.id)
    else:
        branch["rejected_candidate_ids"].append(program.id)
    execution_filtered = (
        not admitted
        and (
            evaluation.get("is_valid") is False
            or admission.get("reason") == "invalid_evaluation"
            or (
                isinstance(failure_record, Mapping)
                and isinstance(failure_record.get("diff_error"), str)
            )
        )
    )
    if execution_filtered:
        branch["execution_filtered_candidate_ids"].append(program.id)
    reason = None
    if not admitted:
        if isinstance(failure_record, Mapping):
            reason = failure_record.get("admission_reason") or failure_record.get(
                "diff_error"
            )
        reason = reason or admission.get("reason") or "rejected"
        reason = str(reason)
        branch["rejection_reasons"][reason] = branch["rejection_reasons"].get(reason, 0) + 1
    error = evaluation.get("error")
    if isinstance(error, str) and error:
        branch["evaluator_errors"][error] = branch["evaluator_errors"].get(error, 0) + 1
    eval_metadata = (
        evaluation.get("metadata")
        if isinstance(evaluation.get("metadata"), Mapping)
        else {}
    )
    stopped_at = eval_metadata.get("stopped_at")
    if isinstance(stopped_at, str) and stopped_at:
        key = f"stopped_at:{stopped_at}"
        branch["cascade_stop_reasons"][key] = (
            branch["cascade_stop_reasons"].get(key, 0) + 1
        )


def _finalize_hypothesis_branch_record(branch: dict) -> dict:
    candidate_ids = _unique_preserve_order(branch["candidate_ids"])
    accepted_ids = _unique_preserve_order(branch["accepted_candidate_ids"])
    rejected_ids = _unique_preserve_order(branch["rejected_candidate_ids"])
    filtered_ids = _unique_preserve_order(branch["execution_filtered_candidate_ids"])
    parent_ids = _unique_preserve_order(branch["parent_ids"])
    generations = [
        generation
        for generation in branch["generations"]
        if isinstance(generation, int) and not isinstance(generation, bool)
    ]
    rejected_count = len(rejected_ids)
    accepted_count = len(accepted_ids)
    if rejected_count and not accepted_count:
        status = "abandoned_evidence"
        abandonment_reason = (
            "all_observed_candidates_rejected_or_execution_filtered"
            if len(filtered_ids) == rejected_count
            else "all_observed_candidates_rejected"
        )
    elif accepted_count:
        status = "active_or_validated"
        abandonment_reason = None
    else:
        status = "insufficient_evidence"
        abandonment_reason = None
    fallback_target = {
        "type": "parent_program",
        "candidate_ids": parent_ids[:5],
        "policy": "inferred_from_rejected_candidate_parent_ids",
    } if rejected_count else {
        "type": "not_applicable",
        "candidate_ids": [],
        "policy": "no_rejected_candidates",
    }
    return {
        "branch_id": branch["branch_id"],
        "proposal_fields": branch["proposal_fields"],
        "branch_status": status,
        "abandonment_reason": abandonment_reason,
        "candidate_count": len(candidate_ids),
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "execution_filtered_count": len(filtered_ids),
        "candidate_ids": candidate_ids[:25],
        "candidate_ids_truncated": len(candidate_ids) > 25,
        "accepted_candidate_ids": accepted_ids[:25],
        "rejected_candidate_ids": rejected_ids[:25],
        "execution_filtered_candidate_ids": filtered_ids[:25],
        "generation_span": [
            min(generations) if generations else None,
            max(generations) if generations else None,
        ],
        "parent_ids": parent_ids[:10],
        "parent_ids_truncated": len(parent_ids) > 10,
        "rejection_reasons": dict(sorted(branch["rejection_reasons"].items())),
        "evaluator_errors": dict(sorted(branch["evaluator_errors"].items())),
        "cascade_stop_reasons": dict(sorted(branch["cascade_stop_reasons"].items())),
        "fallback_target": fallback_target,
        "suppression_policy": "not_configured",
        "retry_policy": "normal_parent_sampling_can_retry_until_budget_or_archive_state_changes",
        "resumed_search_outcome": {
            "status": "not_causally_tracked",
            "policy": "manifest_report_observes_branch_outcomes_without_controller_redirect_events",
        },
    }


def _unique_preserve_order(values: list) -> list:
    result = []
    seen = set()
    for value in values:
        if not isinstance(value, str) or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _hypothesis_branch_sort_key(branch: dict) -> tuple:
    status_rank = 0 if branch.get("branch_status") == "abandoned_evidence" else 1
    return (
        status_rank,
        -int(branch.get("rejected_count", 0)),
        -int(branch.get("candidate_count", 0)),
        str(branch.get("branch_id", "")),
    )


def validate_hypothesis_branch_report(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.hypothesis_branch_report.v1",
            "ok": False,
            "issues": [
                {"code": "invalid_shape", "message": "hypothesis branch report must be an object"}
            ],
        }
    required = {
        "schema",
        "source",
        "branch_count",
        "abandoned_branch_count",
        "active_or_validated_branch_count",
        "branches",
        "branches_limit",
        "branches_truncated",
        "failure_memory_linkage",
        "backtracking_policy",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append({"code": "missing_fields", "message": f"hypothesis branch report missing fields: {sorted(missing)}"})
    if report.get("schema") != "libreevolve.hypothesis_branch_report.v1":
        issues.append({"code": "invalid_schema", "message": "hypothesis branch report schema is unsupported"})
    if report.get("source") != "history_failure_history_and_proposal_metadata":
        issues.append({"code": "invalid_source", "message": "hypothesis branch report source is unsupported"})
    branches = report.get("branches")
    if not isinstance(branches, list):
        issues.append({"code": "invalid_branches", "message": "branches must be a list"})
        branches = []
    abandoned = 0
    active = 0
    for index, branch in enumerate(branches):
        if not isinstance(branch, dict):
            issues.append({"code": "invalid_branch", "message": f"branch {index} must be an object"})
            continue
        branch_id = branch.get("branch_id")
        if not isinstance(branch_id, str) or not re.fullmatch(r"hypothesis-[0-9a-f]{16}", branch_id):
            issues.append({"code": "invalid_branch_id", "message": f"branch {index} id is invalid"})
        status = branch.get("branch_status")
        if status == "abandoned_evidence":
            abandoned += 1
        elif status == "active_or_validated":
            active += 1
        elif status != "insufficient_evidence":
            issues.append({"code": "invalid_branch_status", "message": f"branch {index} status is invalid"})
        candidate_count = branch.get("candidate_count")
        accepted_count = branch.get("accepted_count")
        rejected_count = branch.get("rejected_count")
        filtered_count = branch.get("execution_filtered_count")
        for field, value in (
            ("candidate_count", candidate_count),
            ("accepted_count", accepted_count),
            ("rejected_count", rejected_count),
            ("execution_filtered_count", filtered_count),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                issues.append({"code": f"invalid_{field}", "message": f"branch {index} {field} must be a non-negative integer"})
        if (
            isinstance(candidate_count, int)
            and isinstance(accepted_count, int)
            and isinstance(rejected_count, int)
            and candidate_count != accepted_count + rejected_count
        ):
            issues.append({"code": "invalid_branch_counts", "message": f"branch {index} accepted/rejected counts must add to candidate_count"})
        if isinstance(filtered_count, int) and isinstance(rejected_count, int) and filtered_count > rejected_count:
            issues.append({"code": "invalid_filtered_count", "message": f"branch {index} filtered count cannot exceed rejected count"})
        if not isinstance(branch.get("proposal_fields"), dict) or not branch["proposal_fields"]:
            issues.append({"code": "invalid_proposal_fields", "message": f"branch {index} must include proposal fields"})
        if not isinstance(branch.get("fallback_target"), dict):
            issues.append({"code": "invalid_fallback_target", "message": f"branch {index} fallback target must be an object"})
    if report.get("branches_truncated") is not True:
        if report.get("branch_count") != len(branches):
            issues.append({"code": "invalid_branch_count", "message": "branch_count must match branches when not truncated"})
        if report.get("abandoned_branch_count") != abandoned:
            issues.append({"code": "invalid_abandoned_count", "message": "abandoned_branch_count must match branches"})
        if report.get("active_or_validated_branch_count") != active:
            issues.append({"code": "invalid_active_count", "message": "active_or_validated_branch_count must match branches"})
    if not isinstance(report.get("failure_memory_linkage"), dict):
        issues.append({"code": "invalid_failure_memory_linkage", "message": "failure_memory_linkage must be an object"})
    policy = report.get("backtracking_policy")
    if not isinstance(policy, dict):
        issues.append({"code": "invalid_backtracking_policy", "message": "backtracking_policy must be an object"})
    elif policy.get("controller_suppression") != "not_configured":
        issues.append({"code": "controller_backtracking_overclaim", "message": "controller suppression must remain not_configured until implemented"})
    if report.get("claim_ready") is not False:
        issues.append({"code": "claim_ready_overclaim", "message": "hypothesis branch report must not claim AlphaEvolve backtracking parity"})
    readiness = report.get("claim_readiness")
    if not isinstance(readiness, dict):
        issues.append({"code": "invalid_claim_readiness", "message": "claim_readiness must be an object"})
    elif readiness.get("controller_backtracking_decision") is not False:
        issues.append({"code": "controller_decision_overclaim", "message": "controller backtracking decision must remain false"})
    return {
        "schema": "libreevolve.hypothesis_branch_report.v1",
        "ok": not issues,
        "issues": issues,
    }


def _configured_stage_workload(raw_stage: dict) -> dict:
    metadata = raw_stage.get("metadata") if isinstance(raw_stage.get("metadata"), dict) else {}
    stage = metadata.get("stage") if isinstance(metadata.get("stage"), dict) else {}
    workload = stage.get("workload") if isinstance(stage.get("workload"), dict) else None
    source = "stage.workload"
    if workload is None:
        config = stage.get("config") if isinstance(stage.get("config"), dict) else {}
        workload = config.get("workload") if isinstance(config.get("workload"), dict) else None
        source = "stage.config.workload"
    config = stage.get("config") if isinstance(stage.get("config"), dict) else {}
    if workload is None:
        workload = {"type": "simple_check"}
        source = "implicit_simple_check"
    return {
        "type": workload.get("type", "simple_check"),
        "source": source,
        "declared": source != "implicit_simple_check",
        "datasets": copy.deepcopy(workload.get("datasets", []))
        if isinstance(workload.get("datasets"), list)
        else [],
        "budget": copy.deepcopy(workload.get("budget", {}))
        if isinstance(workload.get("budget"), dict)
        else {},
        "checkpoint_policy": workload.get("checkpoint_policy", "not_declared"),
        "score_fields": list(workload.get("score_fields", []))
        if isinstance(workload.get("score_fields"), list)
        else [],
        "artifact_policy": workload.get("artifact_policy", "not_declared"),
        "seed_count": len(config.get("seeds", [])) if isinstance(config.get("seeds"), list) else 0,
    }


def _finalize_workload_stage_record(record: dict) -> dict:
    finalized = dict(record)
    finalized["candidate_ids"] = finalized["candidate_ids"][:50]
    finalized["candidate_ids_truncated"] = finalized["candidate_count"] > len(
        finalized["candidate_ids"]
    )
    return finalized


def validate_evaluator_workload_report(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.evaluator_workload_report.v1",
            "ok": False,
            "issues": [
                {"code": "invalid_shape", "message": "workload report must be an object"}
            ],
        }
    required = {
        "schema",
        "source",
        "configured_candidate_count",
        "stage_count",
        "declared_workload_stage_count",
        "workload_type_counts",
        "stages",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append({"code": "missing_fields", "message": f"workload report missing fields: {sorted(missing)}"})
    if report.get("schema") != "libreevolve.evaluator_workload_report.v1":
        issues.append({"code": "invalid_schema", "message": "workload report schema is unsupported"})
    if report.get("source") != "runtime_history_configured_stage_results":
        issues.append({"code": "invalid_source", "message": "workload report source is unsupported"})
    stages = report.get("stages")
    if not isinstance(stages, list):
        issues.append({"code": "invalid_stages", "message": "workload report stages must be a list"})
        stages = []
    allowed_types = {"simple_check", "inner_search", "ml_training", "custom"}
    counted = 0
    declared = 0
    type_counts: dict[str, int] = {}
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            issues.append({"code": "invalid_stage", "message": f"workload stage {index} must be an object"})
            continue
        for field in ("name", "stage_index", "workload_type", "candidate_count", "passed", "failed"):
            if field not in stage:
                issues.append({"code": "missing_stage_field", "message": f"workload stage {index} missing {field}"})
        workload_type = stage.get("workload_type")
        if workload_type not in allowed_types:
            issues.append({"code": "invalid_workload_type", "message": f"workload stage {index} has invalid type"})
        candidate_count = stage.get("candidate_count")
        if isinstance(candidate_count, int) and not isinstance(candidate_count, bool):
            counted += candidate_count
            type_counts[str(workload_type)] = type_counts.get(str(workload_type), 0) + candidate_count
            passed = stage.get("passed")
            failed = stage.get("failed")
            if (
                isinstance(passed, int)
                and not isinstance(passed, bool)
                and isinstance(failed, int)
                and not isinstance(failed, bool)
                and candidate_count != passed + failed
            ):
                issues.append({"code": "invalid_stage_counts", "message": f"workload stage {index} counts do not add up"})
        else:
            issues.append({"code": "invalid_candidate_count", "message": f"workload stage {index} candidate_count must be int"})
        if stage.get("declared") is True:
            declared += 1
        if not isinstance(stage.get("datasets"), list):
            issues.append({"code": "invalid_datasets", "message": f"workload stage {index} datasets must be a list"})
        if not isinstance(stage.get("budget"), dict):
            issues.append({"code": "invalid_budget", "message": f"workload stage {index} budget must be an object"})
        if not isinstance(stage.get("score_fields"), list):
            issues.append({"code": "invalid_score_fields", "message": f"workload stage {index} score_fields must be a list"})
    if isinstance(report.get("stage_count"), int) and not isinstance(report.get("stage_count"), bool):
        if report["stage_count"] != len(stages):
            issues.append({"code": "invalid_stage_count", "message": "stage_count must equal stages length"})
    else:
        issues.append({"code": "invalid_stage_count", "message": "stage_count must be an int"})
    declared_reported = report.get("declared_workload_stage_count")
    if isinstance(declared_reported, int) and not isinstance(declared_reported, bool):
        if declared_reported != declared:
            issues.append({"code": "invalid_declared_count", "message": "declared workload count mismatch"})
    else:
        issues.append({"code": "invalid_declared_count", "message": "declared workload count must be an int"})
    if isinstance(report.get("workload_type_counts"), dict):
        if report["workload_type_counts"] != dict(sorted(type_counts.items())):
            issues.append({"code": "invalid_type_counts", "message": "workload type counts mismatch"})
    else:
        issues.append({"code": "invalid_type_counts", "message": "workload_type_counts must be an object"})
    return {
        "schema": "libreevolve.evaluator_workload_report.v1",
        "ok": not issues,
        "issues": issues,
    }


def _finalize_cascade_stage_record(record: dict) -> dict:
    finalized = dict(record)
    finalized["candidate_count"] = finalized.pop("entered")
    finalized["promotion_rate"] = (
        finalized["passed"] / finalized["candidate_count"]
        if finalized["candidate_count"]
        else None
    )
    finalized["failure_reasons"] = dict(sorted(finalized["failure_reasons"].items()))
    finalized["candidate_ids"] = finalized["candidate_ids"][:50]
    finalized["candidate_ids_truncated"] = finalized["candidate_count"] > len(
        finalized["candidate_ids"]
    )
    finalized["elapsed_sec"] = round(finalized["elapsed_sec"], 9)
    return finalized


def validate_evaluation_cascade_report(report: object) -> dict:
    issues: list[dict] = []
    if not isinstance(report, dict):
        return {
            "schema": "libreevolve.evaluation_cascade_report.v1",
            "ok": False,
            "issues": [{"code": "invalid_shape", "message": "cascade report must be an object"}],
        }
    required = {
        "schema",
        "source",
        "configured_candidate_count",
        "stage_count",
        "stages",
        "main_test_exposure_count",
        "early_prune_count",
        "stop_reasons",
        "claim_ready",
        "claim_readiness",
    }
    missing = required - set(report)
    if missing:
        issues.append({"code": "missing_fields", "message": f"cascade report missing fields: {sorted(missing)}"})
    if report.get("schema") != "libreevolve.evaluation_cascade_report.v1":
        issues.append({"code": "invalid_schema", "message": "cascade report schema is unsupported"})
    if report.get("source") != "runtime_history_configured_stage_results":
        issues.append({"code": "invalid_source", "message": "cascade report source is unsupported"})
    stages = report.get("stages")
    if not isinstance(stages, list):
        issues.append({"code": "invalid_stages", "message": "cascade report stages must be a list"})
        stages = []
    if isinstance(report.get("stage_count"), int) and not isinstance(report.get("stage_count"), bool):
        if report["stage_count"] != len(stages):
            issues.append({"code": "stage_count_mismatch", "message": "stage_count must match stages length"})
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            issues.append({"code": "invalid_stage", "message": "cascade stage records must be objects"})
            continue
        for key in ("candidate_count", "passed", "failed"):
            value = stage.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                issues.append({"code": "invalid_stage_count", "message": f"stage {index} {key} must be a non-negative integer"})
        if (
            isinstance(stage.get("candidate_count"), int)
            and isinstance(stage.get("passed"), int)
            and isinstance(stage.get("failed"), int)
            and stage["candidate_count"] != stage["passed"] + stage["failed"]
        ):
            issues.append({"code": "stage_count_inconsistent", "message": f"stage {index} counts must balance"})
    configured = report.get("configured_candidate_count")
    exposure = report.get("main_test_exposure_count")
    early = report.get("early_prune_count")
    if all(isinstance(value, int) and not isinstance(value, bool) for value in (configured, exposure, early)):
        if configured < 0 or exposure < 0 or early < 0 or configured != exposure + early:
            issues.append({"code": "candidate_count_inconsistent", "message": "configured candidate counts must balance"})
    else:
        issues.append({"code": "invalid_candidate_counts", "message": "candidate counts must be non-negative integers"})
    readiness = report.get("claim_readiness")
    if not isinstance(readiness, dict):
        issues.append({"code": "invalid_claim_readiness", "message": "claim_readiness must be an object"})
    if report.get("claim_ready") is not False:
        issues.append({"code": "claim_ready_overclaimed", "message": "current cascade report must not claim AlphaEvolve readiness"})
    return {
        "schema": "libreevolve.evaluation_cascade_report.v1",
        "ok": not issues,
        "issues": issues,
    }


def _runtime_controller_state(run_dir: Path, budget: RunBudget) -> dict:
    event_stream = _controller_budget_event_stream_summary(
        run_dir / "controller_budget_events.jsonl"
    )
    state = {
        "schema": "libreevolve.controller_state.v1",
        "status": "terminal_synchronous_controller_drained",
        "controller_model": "single_process_serial_loop",
        "resume_scope": "terminal_drained_state_only",
        "pending_work": {
            "queued_proposals": 0,
            "running_proposals": 0,
            "queued_evaluations": 0,
            "running_evaluations": 0,
            "in_flight_llm_calls": 0,
            "pending_archive_admissions": 0,
            "partially_completed_generation": False,
        },
        "terminal": {
            "stop_reason": budget.stop_reason,
            "generations_completed": budget.generations_completed,
            "evaluations": budget.evaluations,
        },
        "event_stream": event_stream,
        "limitations": [
            "synchronous_terminal_snapshot_not_async_queue_checkpoint",
            "no_mid_generation_resume_boundary",
            "provider_outputs_not_replayed",
            "plugin_internal_pending_work_reported_separately",
        ],
    }
    state["validation"] = validate_controller_state_snapshot(state)
    return state


def _controller_budget_event_stream_summary(path: Path) -> dict:
    if not path.exists():
        return {
            "path": path.name,
            "status": "absent",
            "event_count": 0,
            "last_sequence": None,
            "last_kind": None,
            "replay_scope": "budget_counters_only",
        }
    event_count = 0
    last_sequence = None
    last_kind = None
    for event in iter_strict_jsonl_objects(
        path,
        stream_name="controller_budget_events.jsonl",
    ):
        event_count += 1
        last_sequence = event.get("sequence")
        last_kind = event.get("kind")
    return {
        "path": path.name,
        "status": "present",
        "event_count": event_count,
        "last_sequence": last_sequence,
        "last_kind": last_kind,
        "replay_scope": "budget_counters_only",
    }


def _no_candidate_absence_reason(budget: RunBudget) -> str:
    if budget.stop_reason in {
        "max_evaluations",
        "max_evaluator_seconds",
        "max_evaluator_subprocess_attempts",
        "max_evaluator_stage_samples",
        "max_evaluator_retry_attempts",
        "max_evaluator_timeouts",
        "max_evaluator_sample_budget_exhaustions",
        "max_evaluator_stage_budget_exhaustions",
        "max_runtime_seconds",
    }:
        return f"{budget.stop_reason}_before_seed_evaluation"
    if budget.stop_reason == "aborted":
        return "aborted_before_evaluation"
    if budget.stop_reason:
        return f"{budget.stop_reason}_before_evaluation"
    return "no_evaluations_recorded"


def _phase_role(phase: str) -> str | None:
    if "llm_mutation" in phase:
        return "mutation"
    if "llm_critique" in phase:
        return "critique"
    if "llm_feedback" in phase:
        return "feedback"
    if "llm_meta_prompt" in phase:
        return "meta_prompt"
    if "candidate_evaluation" in phase or "seed_evaluation" in phase:
        return "evaluation"
    if "plugin_" in phase:
        return "plugin"
    if "manifest" in phase or "finalization" in phase:
        return "manifest"
    return None


def _validate_problem_for_evolve(problem: Problem, config: Config) -> None:
    validate_direct_task_description(problem.task_description)
    if not problem.initial_programs and not problem.initial_workspaces:
        raise ValueError("Problem must provide at least one initial program or workspace")
    _validate_initial_workspaces_for_evolve(problem, config)
    _validate_inline_seed_programs_for_evolve(problem, config)
    validate_direct_context_files(problem.context_files)


def _validate_initial_workspaces_for_evolve(problem: Problem, config: Config) -> None:
    if not problem.initial_workspaces:
        return
    if not isinstance(problem.initial_workspaces, list):
        raise ValueError(
            "Problem initial_workspaces must be a list of CandidateWorkspace "
            "objects or workspace records"
        )
    normalized_workspaces: list[CandidateWorkspace] = []
    for index, workspace in enumerate(problem.initial_workspaces):
        try:
            normalized = _normalize_direct_initial_workspace(workspace)
            _validate_workspace_size_for_config(normalized, config)
            _validate_workspace_evolve_blocks(index, normalized)
        except ValueError as exc:
            raise ValueError(
                f"Problem initial_workspaces[{index}] is invalid: {exc}"
            ) from exc
        normalized_workspaces.append(normalized)
    problem.initial_workspaces = normalized_workspaces


def _normalize_direct_initial_workspace(workspace: object) -> CandidateWorkspace:
    if isinstance(workspace, CandidateWorkspace):
        return CandidateWorkspace(
            files=dict(workspace.files),
            primary_file=workspace.primary_file,
            allowed_reserved_paths=workspace.allowed_reserved_paths,
            static_files=workspace.static_files,
        )
    if isinstance(workspace, Mapping):
        return CandidateWorkspace.from_dict(dict(workspace))
    raise ValueError("expected CandidateWorkspace or workspace record mapping")


def _validate_workspace_size_for_config(workspace: CandidateWorkspace, config: Config) -> dict:
    return validate_candidate_workspace_limits(
        workspace.files,
        static_files=workspace.static_files,
        max_files=config.max_candidate_workspace_files,
        max_file_chars=config.max_candidate_file_chars,
        max_total_chars=config.max_candidate_total_chars,
        max_static_file_bytes=config.max_candidate_static_file_bytes,
        max_total_static_bytes=config.max_candidate_total_static_bytes,
    )


def _validate_workspace_evolve_blocks(
    index: int, workspace: CandidateWorkspace
) -> None:
    for path, content in workspace.files.items():
        marker_error = validate_evolve_blocks(content)
        if marker_error is not None:
            raise ValueError(
                f"initial_workspaces[{index}].files[{path!r}] has malformed "
                f"evolve-block markers: {marker_error}"
            )


def _validate_inline_seed_programs_for_evolve(problem: Problem, config: Config) -> None:
    if problem.initial_workspaces:
        return
    if not isinstance(problem.initial_programs, list):
        raise ValueError("Problem initial_programs must be a list of seed program strings")
    for index, code in enumerate(problem.initial_programs):
        if not isinstance(code, str):
            raise ValueError(
                f"Problem initial_programs[{index}] must be a seed program string"
            )
        if len(code) > _MAX_DIRECT_INLINE_SEED_CHARS:
            raise ValueError(
                f"Problem initial_programs[{index}] must be at most "
                f"{_MAX_DIRECT_INLINE_SEED_CHARS} characters"
            )
        try:
            code.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError(
                f"Problem initial_programs[{index}] must be UTF-8 encodable"
            ) from exc
        _validate_workspace_size_for_config(CandidateWorkspace.from_code(code), config)
        marker_error = validate_evolve_blocks(code)
        if marker_error is not None:
            raise ValueError(
                f"Problem initial_programs[{index}] has malformed evolve-block "
                f"markers: {marker_error}"
            )


def _validate_plugins_for_evolve(
    plugins: list[object],
    *,
    mutation_capable: bool,
) -> None:
    for index, plugin in enumerate(plugins):
        if isinstance(plugin, PluginBase):
            continue
        identity = _plugin_identity(plugin, index)
        known_hooks = {
            name: getattr(plugin, name, None)
            for name in (
                "on_generation_start",
                "build_extra_context",
                "prompt_context_metadata",
                "on_evaluated",
                "on_generation_end",
                "run_artifacts_metadata",
            )
        }
        non_callable = [
            name for name, value in known_hooks.items()
            if value is not None and not callable(value)
        ]
        if non_callable:
            raise ValueError(
                "Invalid plugin instance "
                f"{identity['instance_id']}: plugin hook(s) must be callable: "
                + ", ".join(sorted(non_callable))
            )
        callable_hooks = {name for name, value in known_hooks.items() if callable(value)}
        required_hooks = (
            {
                "on_generation_start",
                "build_extra_context",
                "on_evaluated",
                "on_generation_end",
            }
            if mutation_capable
            else {"run_artifacts_metadata"}
        )
        missing = sorted(required_hooks - callable_hooks)
        if not missing:
            continue
        if callable_hooks and not mutation_capable:
            continue
        raise ValueError(
            "Invalid plugin instance "
            f"{identity['instance_id']}: expected PluginBase or callable hook protocol; "
            "missing " + ", ".join(missing)
        )


def _seed_workspace_entries(problem: Problem) -> list[tuple[CandidateWorkspace, dict]]:
    if problem.initial_workspaces:
        sources = problem.initial_workspace_sources or []
        return [
            (workspace, _normalize_seed_source(index, sources[index] if index < len(sources) else None))
            for index, workspace in enumerate(problem.initial_workspaces)
        ]
    return [
        (
            CandidateWorkspace.from_code(code),
            {
                "seed_index": index,
                "seed_source_kind": "inline",
            },
        )
        for index, code in enumerate(problem.initial_programs)
    ]


def _deterministic_seed_candidate_id(index: int, workspace: CandidateWorkspace) -> str:
    digest = _workspace_sha256(workspace)[:16]
    return f"candidate-seed-{index}-{digest}"


def _deterministic_generated_candidate_id(
    *,
    generation: int,
    loop_generation_index: int,
    proposal_index: int,
    parent_id: str,
    prompt_program_id: str,
    mutation_text: object,
    workspace: CandidateWorkspace,
) -> str:
    mutation_text_for_hash = _candidate_id_mutation_text(mutation_text)
    payload = {
        "generation": generation,
        "loop_generation_index": loop_generation_index,
        "proposal_index": proposal_index,
        "parent_id": parent_id,
        "prompt_program_id": prompt_program_id,
        "mutation_sha256": hashlib.sha256(
            mutation_text_for_hash.encode("utf-8", errors="replace")
        ).hexdigest(),
        "workspace_sha256": _workspace_sha256(workspace),
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"candidate-gen-{generation}-{loop_generation_index}-p{proposal_index}-{digest}"


def _candidate_id_mutation_text(value: object) -> str:
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return repr(value)


def _workspace_sha256(workspace: CandidateWorkspace) -> str:
    payload = {
        "primary_file": workspace.primary_file,
        "files": [[path, workspace.files[path]] for path in sorted(workspace.files)],
        "static_files": [dict(item) for item in workspace.static_files],
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _problem_seed_sources(problem: Problem) -> list[dict]:
    if problem.initial_workspaces:
        sources = problem.initial_workspace_sources or []
        return [
            _normalize_seed_source(index, sources[index] if index < len(sources) else None)
            for index, _workspace in enumerate(problem.initial_workspaces)
        ]
    return [
        {
            "seed_index": index,
            "seed_source_kind": "inline",
        }
        for index, _code in enumerate(problem.initial_programs)
    ]


def _problem_seed_skipped(problem: Problem) -> list[dict]:
    return list(getattr(problem, "initial_workspace_skipped", []) or [])


def _problem_seed_policy(problem: Problem) -> dict:
    return dict(getattr(problem, "initial_workspace_policy", {}) or {})


def _problem_retrieval_query_context(problem: Problem) -> dict:
    context = {
        "task_description": problem.task_description,
        "context_files": dict(getattr(problem, "context_files", {}) or {}),
    }
    local_papers = getattr(problem, "local_papers", None)
    if local_papers is None:
        local_papers = _local_paper_query_context_rows()
    if local_papers:
        context["local_papers"] = local_papers
    return context


def _local_paper_query_context_rows(root: Path | None = None) -> list[dict]:
    root_path = root or Path(__file__).resolve().parents[2]
    manifest_path = root_path / "papers" / "download_manifest.json"
    try:
        raw_rows = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    if not isinstance(raw_rows, list):
        return []
    rows: list[dict] = []
    for raw_row in raw_rows:
        if not isinstance(raw_row, Mapping):
            continue
        row: dict[str, object] = {}
        for key in ("id", "title", "url", "file", "sha256"):
            value = raw_row.get(key)
            if isinstance(value, str) and value:
                row[key] = value
        value = raw_row.get("ok")
        if isinstance(value, bool):
            row["ok"] = value
        value = raw_row.get("bytes")
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            row["bytes"] = value
        if row.get("id") or row.get("title"):
            rows.append(row)
        if len(rows) >= 25:
            break
    return rows


def _normalize_seed_source(index: int, source: dict | None) -> dict:
    return validate_seed_source_record(index, source)


def _build_plugin_context(
    plugins: list[PluginBase],
    parent: Program,
    inspirations: list[Program],
    *,
    config: Config,
    generation: int | None = None,
    phase: str | None = None,
    context_policy: Mapping[str, object] | None = None,
) -> tuple[str, list[dict]]:
    context_entries: list[dict] = []
    records: list[dict] = []
    inspiration_ids = [program.id for program in inspirations]
    prompt_context_policy = validate_prompt_context_policy(context_policy)
    plugin_context_max_chars_by_label = prompt_context_policy[
        "plugin_context_max_chars_by_label"
    ]
    plugin_context_max_chars = prompt_context_policy["plugin_context_max_chars"]
    plugin_context_truncation = prompt_context_policy["plugin_context_truncation"]
    plugin_context_order = prompt_context_policy["plugin_context_order"]
    plugin_context_required_terms = prompt_context_policy[
        "plugin_context_required_terms"
    ]
    plugin_context_excluded_terms = prompt_context_policy[
        "plugin_context_excluded_terms"
    ]
    plugin_context_ranking_terms = prompt_context_policy[
        "plugin_context_ranking_terms"
    ]
    plugin_context_limit = prompt_context_policy["plugin_context_limit"]
    if prompt_context_policy["plugin_context_enabled"] is False:
        return "", [
            _skipped_plugin_context_record(
                plugin,
                index,
                parent=parent,
                inspiration_ids=inspiration_ids,
                config=config,
            )
            for index, plugin in enumerate(plugins)
        ]
    plugin_context_allowlist = set(prompt_context_policy["plugin_context_allowlist"])
    plugin_context_excluded_labels = set(
        prompt_context_policy["plugin_context_excluded_labels"]
    )
    for index, plugin in enumerate(plugins):
        if plugin_context_excluded_labels and _plugin_context_matches_labels(
            plugin,
            index,
            plugin_context_excluded_labels,
        ):
            records.append(
                _skipped_plugin_context_record(
                    plugin,
                    index,
                    parent=parent,
                    inspiration_ids=inspiration_ids,
                    config=config,
                    reason="excluded_by_prompt_context_labels",
                    plugin_context_enabled=True,
                    plugin_context_excluded_labels=sorted(
                        plugin_context_excluded_labels
                    ),
                )
            )
            continue
        if plugin_context_allowlist and not _plugin_context_is_allowlisted(
            plugin, index, plugin_context_allowlist
        ):
            records.append(
                _skipped_plugin_context_record(
                    plugin,
                    index,
                    parent=parent,
                    inspiration_ids=inspiration_ids,
                    config=config,
                    reason="not_selected_by_prompt_context_allowlist",
                    plugin_context_enabled=True,
                    plugin_context_allowlist=sorted(plugin_context_allowlist),
                )
            )
            continue
        rendered = _call_plugin_hook(
            plugin,
            index,
            "build_extra_context",
            parent,
            inspirations,
            generation=generation,
            phase=phase,
            hook_policy="fatal_run_abort",
            parent_id=parent.id,
        )
        if rendered is None:
            text = ""
        elif isinstance(rendered, str):
            text = rendered
        else:
            exc = ValueError(
                f"plugin_context[{index}].build_extra_context must return text or None"
            )
            _annotate_plugin_failure(
                exc,
                plugin,
                index,
                "build_extra_context",
                generation=generation,
                phase=phase,
                hook_policy="fatal_run_abort",
                parent_id=parent.id,
            )
            raise exc
        redacted_text = redact_sensitive_text(text) if text else ""
        policy_max_chars = _plugin_context_policy_max_chars(
            plugin,
            index,
            plugin_context_max_chars_by_label,
        )
        effective_max_chars = min(
            cap
            for cap in (
                _MAX_PLUGIN_CONTEXT_CHARS,
                plugin_context_max_chars,
                policy_max_chars,
            )
            if cap is not None
        )
        safe_text = (
            _bounded_redacted_plugin_context_text(
                text,
                effective_max_chars,
                truncation=plugin_context_truncation,
            )
            if text and effective_max_chars > 0
            else ""
        )
        term_policy = _plugin_context_term_policy(
            safe_text,
            required_terms=plugin_context_required_terms,
            excluded_terms=plugin_context_excluded_terms,
        )
        prompt_visible_text = safe_text if term_policy["selected"] else ""
        prompt_context_text = (
            _render_plugin_context_section(index, plugin, prompt_visible_text)
            if prompt_visible_text
            else ""
        )
        if prompt_context_text:
            prompt_context_text = redact_sensitive_text(prompt_context_text)
        prompt_context_truncated = len(safe_text) < len(redacted_text) if text else False
        retained_context = _retained_plugin_context_text(
            plugin=plugin,
            index=index,
            original_text=text,
            prompt_context_text=prompt_context_text,
            prompt_context_truncated=prompt_context_truncated,
            mode=config.plugin_context_retention_mode,
        )
        record = {
            **_plugin_identity(plugin, index),
            "plugin_spec": _plugin_spec_record(
                plugin, index, config, list(config.plugins)
            ),
            "parent_id": parent.id,
            "inspiration_ids": inspiration_ids,
            "chars": retained_context["stored_chars"],
            "original_chars": len(text),
            "max_chars": effective_max_chars,
            "default_max_chars": _MAX_PLUGIN_CONTEXT_CHARS,
            "policy_global_max_chars": plugin_context_max_chars,
            "policy_max_chars": policy_max_chars,
            "policy_truncation": plugin_context_truncation,
            "context_redacted": redacted_text != text,
            "context_truncated": retained_context["truncated"],
            "prompt_context_chars": len(prompt_context_text),
            "prompt_context_truncated": prompt_context_truncated,
            "prompt_context_content_policy": {
                "schema": "libreevolve.plugin_context_content_policy.v1",
                "max_chars": effective_max_chars,
                "truncation": plugin_context_truncation,
                "selection_policy": (
                    "all_redacted_plugin_context_text"
                    if len(redacted_text) <= effective_max_chars
                    else f"{plugin_context_truncation}_chars_after_redaction"
                ),
            },
            "sha256": retained_context["sha256"] or "",
            "context_retention": {
                key: value
                for key, value in retained_context.items()
                if key != "text"
            },
            "emitted": bool(prompt_visible_text.strip()),
            "context_visibility": _plugin_context_visibility(
                prompt_visible_text,
                term_policy,
            ),
            "metadata_visibility": "none",
        }
        if term_policy["policy"] != "none":
            record["prompt_context_term_policy"] = term_policy
        if retained_context["text"]:
            record["context"] = retained_context["text"]
        if prompt_context_text:
            order_position = _plugin_context_order_position(
                plugin,
                index,
                plugin_context_order,
            )
            order_source = (
                "prompt_context_policy"
                if order_position is not None
                else "config_plugin_order_append"
            )
            record["prompt_context_order"] = {
                "policy": "plugin_context_order_v1",
                "source": order_source,
                "position": order_position,
                "configured_order": list(plugin_context_order),
            }
            context_entries.append(
                {
                    "text": prompt_context_text,
                    "content": prompt_visible_text,
                    "plugin_index": index,
                    "order_position": order_position,
                    "record": record,
                }
            )
        plugin_metadata = _call_optional_plugin_hook(
            plugin,
            index,
            "prompt_context_metadata",
            generation=generation,
            phase=phase,
            hook_policy="fatal_run_abort",
            parent_id=parent.id,
        )
        if plugin_metadata is None:
            pass
        elif not isinstance(plugin_metadata, dict):
            exc = ValueError(
                "prompt_context_metadata must return a mapping, an empty mapping, or None"
            )
            _annotate_plugin_failure(
                exc,
                plugin,
                index,
                "prompt_context_metadata",
                generation=generation,
                phase=phase,
                hook_policy="fatal_run_abort",
                parent_id=parent.id,
            )
            raise exc
        elif plugin_metadata:
            try:
                plugin_metadata = _validate_plugin_metadata(
                    f"plugin_context[{index}].metadata",
                    plugin_metadata,
                )
            except ValueError as exc:
                _annotate_plugin_failure(
                    exc,
                    plugin,
                    index,
                    "prompt_context_metadata",
                    generation=generation,
                    phase=phase,
                    hook_policy="fatal_run_abort",
                    parent_id=parent.id,
                )
                raise
            record["metadata"] = plugin_metadata
            record["metadata_visibility"] = (
                "prompt_visible_context" if record["emitted"] else "provenance_only"
            )
        records.append(record)
    ordered_entries = sorted(
        context_entries,
        key=lambda entry: (
            1 if entry["order_position"] is None else 0,
            entry["order_position"] if entry["order_position"] is not None else 0,
            entry["plugin_index"],
        ),
    )
    if plugin_context_ranking_terms:
        ordered_entries = _rank_plugin_context_entries_by_terms(
            ordered_entries,
            ranking_terms=plugin_context_ranking_terms,
        )
    if plugin_context_limit is None:
        selected_entries = ordered_entries
        omitted_entries: list[dict] = []
    else:
        selected_entries = ordered_entries[:plugin_context_limit]
        omitted_entries = ordered_entries[plugin_context_limit:]
        _apply_plugin_context_limit_policy(
            selected_entries,
            omitted_entries,
            source_limit=plugin_context_limit,
        )
    ordered_contexts = [
        entry["text"]
        for entry in selected_entries
    ]
    return "\n".join(ordered_contexts), records


def _skipped_plugin_context_record(
    plugin: PluginBase,
    index: int,
    *,
    parent: Program,
    inspiration_ids: list[str],
    config: Config,
    reason: str = "disabled_by_prompt_context_policy",
    plugin_context_enabled: bool = False,
    plugin_context_allowlist: list[str] | None = None,
    plugin_context_excluded_labels: list[str] | None = None,
) -> dict:
    retention_policy = reason
    policy = {
        "schema": "libreevolve.plugin_context_policy.v1",
        "plugin_context_enabled": plugin_context_enabled,
        "source": "prompt_context_policy",
    }
    if plugin_context_allowlist is not None:
        policy["plugin_context_allowlist"] = list(plugin_context_allowlist)
        policy["selected"] = False
    if plugin_context_excluded_labels is not None:
        policy["plugin_context_excluded_labels"] = list(
            plugin_context_excluded_labels
        )
        policy["selected"] = False
    return {
        **_plugin_identity(plugin, index),
        "plugin_spec": _plugin_spec_record(
            plugin,
            index,
            config,
            list(config.plugins),
        ),
        "parent_id": parent.id,
        "inspiration_ids": list(inspiration_ids),
        "chars": 0,
        "original_chars": 0,
        "max_chars": _MAX_PLUGIN_CONTEXT_CHARS,
        "context_redacted": False,
        "context_truncated": False,
        "prompt_context_chars": 0,
        "prompt_context_truncated": False,
        "sha256": "",
        "context_retention": {
            "sha256": None,
            "chars": 0,
            "stored_chars": 0,
            "redacted": False,
            "truncated": False,
            "retention_mode": config.plugin_context_retention_mode,
            "retention_policy": retention_policy,
        },
        "emitted": False,
        "context_visibility": reason,
        "metadata_visibility": "none",
        "prompt_context_policy": policy,
    }


def _plugin_context_is_allowlisted(
    plugin: PluginBase,
    index: int,
    allowlist: set[str],
) -> bool:
    return _plugin_context_matches_labels(plugin, index, allowlist)


def _plugin_context_matches_labels(
    plugin: PluginBase,
    index: int,
    labels_to_match: set[str],
) -> bool:
    identity = _plugin_identity(plugin, index)
    labels = {
        identity["plugin"],
        identity["module"],
        identity["class"],
        identity["instance_id"],
    }
    return any(label in labels_to_match for label in labels if isinstance(label, str))


def _plugin_context_order_position(
    plugin: PluginBase,
    index: int,
    ordered_labels: list[str],
) -> int | None:
    if not ordered_labels:
        return None
    identity = _plugin_identity(plugin, index)
    labels = {
        identity["plugin"],
        identity["module"],
        identity["class"],
        identity["instance_id"],
    }
    for position, label in enumerate(ordered_labels):
        if any(candidate == label for candidate in labels if isinstance(candidate, str)):
            return position
    return None


def _plugin_context_policy_max_chars(
    plugin: PluginBase,
    index: int,
    caps_by_label: Mapping[str, int],
) -> int | None:
    if not caps_by_label:
        return None
    identity = _plugin_identity(plugin, index)
    labels = {
        identity["plugin"],
        identity["module"],
        identity["class"],
        identity["instance_id"],
    }
    matches = [
        caps_by_label[label]
        for label in labels
        if isinstance(label, str) and label in caps_by_label
    ]
    return min(matches) if matches else None


def _rank_plugin_context_entries_by_terms(
    entries: list[dict],
    *,
    ranking_terms: list[str],
) -> list[dict]:
    ranked = []
    for original_rank, entry in enumerate(entries, start=1):
        source_terms = {
            match.group(0).lower()
            for match in re.finditer(r"[A-Za-z0-9_]{3,}", str(entry["content"]))
        }
        score = sum(1 for term in ranking_terms if term in source_terms)
        ranked.append((score, original_rank, entry))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    selected_sources = []
    for rank, (score, original_rank, entry) in enumerate(ranked, start=1):
        record = entry["record"]
        record["prompt_context_ranking_policy"] = {
            "schema": "libreevolve.plugin_context_ranking_policy.v1",
            "ranking_policy": "term_overlap_plugin_context_v1",
            "ranking_terms": list(ranking_terms),
            "ranking_terms_sha256": hashlib.sha256(
                " ".join(ranking_terms).encode("utf-8")
            ).hexdigest(),
            "ranking_term_count": len(ranking_terms),
            "candidate_count": len(entries),
            "rank": rank,
            "score": score,
            "previous_rank": original_rank,
        }
        selected_sources.append(
            {
                "plugin_index": int(entry["plugin_index"]),
                "rank": rank,
                "score": score,
                "previous_rank": original_rank,
            }
        )
    ranking_sha256 = hashlib.sha256(
        json.dumps(
            selected_sources,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    for _, _, entry in ranked:
        entry["record"]["prompt_context_ranking_policy"][
            "ranking_sha256"
        ] = ranking_sha256
    return [entry for _, _, entry in ranked]


def _apply_plugin_context_limit_policy(
    selected_entries: list[dict],
    omitted_entries: list[dict],
    *,
    source_limit: int,
) -> None:
    selected_indices = [int(entry["plugin_index"]) for entry in selected_entries]
    omitted_indices = [int(entry["plugin_index"]) for entry in omitted_entries]
    selection_sha256 = hashlib.sha256(
        json.dumps(
            {
                "source_limit": source_limit,
                "selected_plugin_indices": selected_indices,
                "omitted_plugin_indices": omitted_indices,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    for position, entry in enumerate(selected_entries, start=1):
        record = entry["record"]
        record["prompt_context_limit_policy"] = {
            "schema": "libreevolve.plugin_context_limit_policy.v1",
            "source_limit": source_limit,
            "pre_limit_selected_count": len(selected_entries) + len(omitted_entries),
            "selected_count": len(selected_entries),
            "omitted_count": len(omitted_entries),
            "selected": True,
            "rank": position,
            "selection_sha256": selection_sha256,
        }
    for position, entry in enumerate(omitted_entries, start=len(selected_entries) + 1):
        record = entry["record"]
        record["pre_limit_prompt_context_chars"] = record["prompt_context_chars"]
        record["prompt_context_chars"] = 0
        record["emitted"] = False
        record["context_visibility"] = "not_selected_by_prompt_context_limit"
        if record.get("metadata_visibility") == "prompt_visible_context":
            record["metadata_visibility"] = "provenance_only"
        record["prompt_context_limit_policy"] = {
            "schema": "libreevolve.plugin_context_limit_policy.v1",
            "source_limit": source_limit,
            "pre_limit_selected_count": len(selected_entries) + len(omitted_entries),
            "selected_count": len(selected_entries),
            "omitted_count": len(omitted_entries),
            "selected": False,
            "rank": position,
            "selection_sha256": selection_sha256,
        }


def _plugin_context_term_policy(
    text: str,
    *,
    required_terms: list[str],
    excluded_terms: list[str],
) -> dict:
    terms = {
        match.group(0).lower()
        for match in re.finditer(r"[A-Za-z0-9_]{3,}", text)
    }
    required = set(required_terms)
    excluded = set(excluded_terms)
    missing_required = sorted(required - terms)
    matched_excluded = sorted(excluded.intersection(terms))
    selected = not missing_required and not matched_excluded
    return {
        "schema": "libreevolve.plugin_context_term_policy.v1",
        "policy": (
            "required_excluded_terms_v1"
            if required or excluded
            else "none"
        ),
        "required_terms": list(required_terms),
        "excluded_terms": list(excluded_terms),
        "matched_required_count": len(required) - len(missing_required),
        "missing_required_terms": missing_required,
        "matched_excluded_terms": matched_excluded,
        "selected": selected,
        "selection_sha256": hashlib.sha256(
            json.dumps(
                {
                    "required_terms": list(required_terms),
                    "excluded_terms": list(excluded_terms),
                    "missing_required_terms": missing_required,
                    "matched_excluded_terms": matched_excluded,
                    "selected": selected,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
    }


def _plugin_context_visibility(prompt_visible_text: str, term_policy: dict) -> str:
    if prompt_visible_text.strip():
        return "prompt_visible"
    if term_policy["policy"] != "none" and not term_policy["selected"]:
        return "not_selected_by_prompt_context_terms"
    return "not_prompt_visible"


def _render_plugin_context_section(index: int, plugin: PluginBase, text: str) -> str:
    identity = _plugin_identity(plugin, index)
    plugin_name = identity["plugin"] or "Plugin"
    module = identity["module"] or "unknown"
    return "\n".join(
        [
            "[PLUGIN CONTEXT]",
            f"Plugin: {plugin_name}",
            f"Module: {module}",
            f"Index: {index}",
            f"Content-Characters: {len(text)}",
            "Content-JSON:",
            json.dumps(text),
        ]
    )


def _plugin_identity(plugin: object, index: int) -> dict:
    return plugin_identity_record(plugin, index)


def _validate_plugin_metadata(path: str, value: object) -> object:
    item_counter = {"count": 0}
    sanitized = _validate_plugin_metadata_value(
        path,
        value,
        item_counter,
        depth=0,
    )
    json_chars = len(
        json.dumps(
            sanitized,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    if json_chars > _MAX_PLUGIN_METADATA_JSON_CHARS:
        raise ValueError(
            f"{path} metadata JSON exceeds {_MAX_PLUGIN_METADATA_JSON_CHARS} chars"
        )
    return sanitized


def _validate_plugin_metadata_value(
    path: str,
    value: object,
    item_counter: dict[str, int],
    *,
    depth: int,
) -> object:
    if depth > _MAX_PLUGIN_METADATA_DEPTH:
        raise ValueError(
            f"{path} metadata nesting exceeds {_MAX_PLUGIN_METADATA_DEPTH} levels"
        )
    item_counter["count"] += 1
    if item_counter["count"] > _MAX_PLUGIN_METADATA_ITEMS:
        raise ValueError(
            f"{path} metadata item count exceeds {_MAX_PLUGIN_METADATA_ITEMS}"
        )
    if isinstance(value, dict):
        sanitized: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} keys must be strings")
            if _has_unicode_format_control(key):
                raise ValueError(f"{path}.{key!r} must be a display-safe metadata label")
            safe_key = _safe_plugin_metadata_key(key)
            if safe_key in sanitized:
                safe_key = _plugin_metadata_key_with_hash(key, key)
            sanitized[safe_key] = _validate_plugin_metadata_value(
                f"{path}.{safe_key}",
                item,
                item_counter,
                depth=depth + 1,
            )
        return sanitized
    if isinstance(value, list):
        return [
            _validate_plugin_metadata_value(
                f"{path}[{index}]",
                item,
                item_counter,
                depth=depth + 1,
            )
            for index, item in enumerate(value)
        ]
    if isinstance(value, str):
        if len(value) > _MAX_PLUGIN_METADATA_STRING_CHARS:
            raise ValueError(f"{path} metadata value exceeds {_MAX_PLUGIN_METADATA_STRING_CHARS} chars")
        if _has_unicode_format_control(value):
            raise ValueError(f"{path} must be a display-safe metadata value")
        return redact_sensitive_text(value)
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path} metadata value must be finite")
        return value
    raise ValueError(f"{path} metadata value must be JSON-safe")


def _safe_plugin_metadata_key(key: str) -> str:
    redacted = redact_sensitive_text(key)
    if redacted != key and (
        redact_sensitive_text(redacted) != redacted
        or _has_secret_label_word(key)
    ):
        redacted = "redacted_metadata_key"
    bounded = _bounded_plugin_metadata_key(redacted)
    if bounded != key:
        return _plugin_metadata_key_with_hash(bounded, key)
    return bounded


def _bounded_plugin_metadata_key(key: str) -> str:
    if len(key) <= _MAX_PLUGIN_METADATA_KEY_CHARS:
        return key
    suffix = "...<truncated>"
    return key[: _MAX_PLUGIN_METADATA_KEY_CHARS - len(suffix)] + suffix


def _has_secret_label_word(value: str) -> bool:
    normalized = value.lower().replace("-", "_")
    return any(
        word in normalized
        for word in ("api_key", "apikey", "token", "secret", "password")
    )


def _plugin_metadata_key_with_hash(label: str, hash_source: str) -> str:
    digest = hashlib.sha256(hash_source.encode("utf-8")).hexdigest()[:12]
    suffix = f"#sha256:{digest}"
    base_limit = max(1, _MAX_PLUGIN_METADATA_KEY_CHARS - len(suffix))
    base = label if len(label) <= base_limit else label[:base_limit]
    return base + suffix


def _has_unicode_format_control(value: str) -> bool:
    return any(unicodedata.category(ch) == "Cf" for ch in value)


_RETRIEVAL_EVIDENCE_LIMITATIONS = (
    "bounded_redacted_payload_artifacts_not_unbounded_raw_payloads",
    "lexical_grounding_not_semantic_verification",
    "query_overlap_not_learned_semantic_ranking",
    "transport_status_without_tls_certificate_chain_replay",
    "retrieval_context_is_untrusted_non_authoritative_prompt_evidence",
)
_RETRIEVAL_EVIDENCE_OVERCLAIM_FIELDS = {
    "raw_provider_payload_retained": "raw_provider_payload_overclaim",
    "raw_source_payload_retained": "raw_source_payload_overclaim",
    "semantic_source_verification_ready": "semantic_source_verification_overclaim",
    "learned_ranking_ready": "learned_ranking_overclaim",
    "tls_decision_replay_ready": "tls_decision_replay_overclaim",
    "full_retrieval_replay_ready": "full_retrieval_replay_overclaim",
}
_RETRIEVAL_EVIDENCE_COUNT_FIELDS = (
    "event_count",
    "ok_event_count",
    "empty_event_count",
    "error_event_count",
    "source_count",
    "transport_policy_count",
    "payload_artifact_policy_count",
    "payload_artifact_reference_count",
    "stored_payload_artifact_count",
    "source_content_snapshot_count",
    "source_content_trust_policy_count",
    "replayable_source_count",
    "source_grounding_policy_count",
    "lexically_grounded_source_count",
    "source_ranking_provenance_count",
    "evidence_boundary_policy_count",
    "context_audit_policy_count",
    "bounded_context_audit_ready_count",
)


def _non_negative_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
    return value


def _count_retrieval_sources(event: Mapping[str, object]) -> int:
    sources = event.get("sources")
    if not isinstance(sources, list):
        return 0
    return sum(1 for source in sources if isinstance(source, dict))


def _count_source_content_snapshots(event: Mapping[str, object]) -> int:
    sources = event.get("sources")
    if not isinstance(sources, list):
        return 0
    return sum(
        1
        for source in sources
        if isinstance(source, dict)
        and isinstance(source.get("content_snapshot"), dict)
    )


def _retrieval_evidence_coverage(events: list[dict]) -> dict:
    event_count = len(events)
    ok_event_count = sum(1 for event in events if event.get("status") == "ok")
    empty_event_count = sum(1 for event in events if event.get("status") == "empty")
    error_event_count = sum(1 for event in events if event.get("status") == "error")
    source_count = sum(_count_retrieval_sources(event) for event in events)
    payload_artifact_policy_count = sum(
        1 for event in events if isinstance(event.get("payload_artifact_policy"), dict)
    )
    payload_artifact_reference_count = sum(
        len(event.get("payload_artifacts"))
        for event in events
        if isinstance(event.get("payload_artifacts"), list)
    )
    stored_payload_artifact_count = sum(
        _non_negative_int(event["payload_artifact_policy"].get("stored_artifacts"))
        for event in events
        if isinstance(event.get("payload_artifact_policy"), dict)
    )
    source_content_snapshot_count = sum(
        _count_source_content_snapshots(event) for event in events
    )
    source_content_trust_policy_count = sum(
        1
        for event in events
        if isinstance(event.get("source_content_trust_policy"), dict)
    )
    replayable_source_count = sum(
        _non_negative_int(
            event["source_content_trust_policy"].get("replayable_source_count")
        )
        for event in events
        if isinstance(event.get("source_content_trust_policy"), dict)
    )
    source_grounding_policy_count = sum(
        1 for event in events if isinstance(event.get("source_grounding_policy"), dict)
    )
    lexically_grounded_source_count = sum(
        _non_negative_int(
            event["source_grounding_policy"].get("lexically_grounded_source_count")
        )
        for event in events
        if isinstance(event.get("source_grounding_policy"), dict)
    )
    source_ranking_provenance_count = sum(
        1 for event in events if isinstance(event.get("source_ranking"), dict)
    )
    evidence_boundary_policy_count = sum(
        1
        for event in events
        if isinstance(event.get("evidence_boundary_policy"), dict)
    )
    context_audit_policy_count = sum(
        1 for event in events if isinstance(event.get("context_audit_policy"), dict)
    )
    bounded_context_audit_ready_count = sum(
        1
        for event in events
        if isinstance(event.get("context_audit_policy"), dict)
        and event["context_audit_policy"].get("bounded_context_audit_ready") is True
    )
    transport_policy_count = sum(
        1 for event in events if isinstance(event.get("transport_policy"), dict)
    )
    if bounded_context_audit_ready_count or replayable_source_count:
        status = "bounded_replay_evidence"
    elif (
        transport_policy_count
        or source_content_trust_policy_count
        or source_content_snapshot_count
        or source_ranking_provenance_count
        or payload_artifact_policy_count
    ):
        status = "bounded_metadata_or_snapshot_evidence"
    else:
        status = "event_count_only"
    record = {
        "schema": RETRIEVAL_EVIDENCE_COVERAGE_SCHEMA,
        "status": status,
        "event_count": event_count,
        "ok_event_count": ok_event_count,
        "empty_event_count": empty_event_count,
        "error_event_count": error_event_count,
        "source_count": source_count,
        "transport_policy_count": transport_policy_count,
        "payload_artifact_policy_count": payload_artifact_policy_count,
        "payload_artifact_reference_count": payload_artifact_reference_count,
        "stored_payload_artifact_count": stored_payload_artifact_count,
        "source_content_snapshot_count": source_content_snapshot_count,
        "source_content_trust_policy_count": source_content_trust_policy_count,
        "replayable_source_count": replayable_source_count,
        "source_grounding_policy_count": source_grounding_policy_count,
        "lexically_grounded_source_count": lexically_grounded_source_count,
        "source_ranking_provenance_count": source_ranking_provenance_count,
        "evidence_boundary_policy_count": evidence_boundary_policy_count,
        "context_audit_policy_count": context_audit_policy_count,
        "bounded_context_audit_ready_count": bounded_context_audit_ready_count,
        "raw_provider_payload_retained": False,
        "raw_source_payload_retained": False,
        "semantic_source_verification_ready": False,
        "learned_ranking_ready": False,
        "tls_decision_replay_ready": False,
        "full_retrieval_replay_ready": False,
        "limitations": list(_RETRIEVAL_EVIDENCE_LIMITATIONS),
    }
    record["validation"] = validate_retrieval_evidence_coverage(record)
    return record


def validate_retrieval_evidence_coverage(record: object) -> dict:
    """Validate run-level retrieval evidence coverage without overclaiming replay."""
    issues: list[dict[str, str]] = []
    if not isinstance(record, dict):
        return {
            "schema": RETRIEVAL_EVIDENCE_COVERAGE_VALIDATION_SCHEMA,
            "ok": False,
            "coverage_schema": None,
            "event_count": 0,
            "source_count": 0,
            "issues": [
                {
                    "code": "invalid_record",
                    "message": "retrieval evidence coverage must be an object",
                }
            ],
        }
    if record.get("schema") != RETRIEVAL_EVIDENCE_COVERAGE_SCHEMA:
        issues.append(
            {
                "code": "schema_mismatch",
                "message": "retrieval evidence coverage schema is unsupported",
            }
        )
    for field in _RETRIEVAL_EVIDENCE_COUNT_FIELDS:
        value = record.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            issues.append(
                {
                    "code": f"invalid_{field}",
                    "message": f"{field} must be a non-negative integer",
                }
            )
    for field, code in _RETRIEVAL_EVIDENCE_OVERCLAIM_FIELDS.items():
        value = record.get(field)
        if value is not False:
            issues.append(
                {
                    "code": code,
                    "message": f"{field} must remain false until evidence is retained",
                }
            )
    limitations = record.get("limitations")
    if not isinstance(limitations, list):
        limitations = []
        issues.append(
            {
                "code": "invalid_limitations",
                "message": "limitations must list the evidence boundary",
            }
        )
    missing = [
        limitation
        for limitation in _RETRIEVAL_EVIDENCE_LIMITATIONS
        if limitation not in limitations
    ]
    for limitation in missing:
        issues.append(
            {
                "code": "missing_limitation",
                "message": f"missing limitation: {limitation}",
            }
        )
    return {
        "schema": RETRIEVAL_EVIDENCE_COVERAGE_VALIDATION_SCHEMA,
        "ok": not issues,
        "coverage_schema": record.get("schema"),
        "event_count": _non_negative_int(record.get("event_count")),
        "source_count": _non_negative_int(record.get("source_count")),
        "issues": issues,
    }


def _retrieval_manifest_summary(programs: list[Program]) -> dict:
    events: dict[tuple, dict] = {}
    by_plugin: dict[str, dict] = {}
    coverage_events: list[dict] = []
    for program in programs:
        metadata = program.metadata if isinstance(program.metadata, dict) else {}
        plugin_context = metadata.get("plugin_context")
        if not isinstance(plugin_context, list):
            continue
        for context_record in plugin_context:
            if not isinstance(context_record, dict):
                continue
            plugin_name = str(context_record.get("plugin") or "unknown")
            plugin_meta = context_record.get("metadata")
            if not isinstance(plugin_meta, dict):
                continue
            retrieval_events = plugin_meta.get("retrieval_events")
            if not isinstance(retrieval_events, list):
                continue
            for event in retrieval_events:
                if not isinstance(event, dict):
                    continue
                event_key = (
                    plugin_name,
                    event.get("query"),
                    event.get("timestamp"),
                    event.get("status"),
                    event.get("synthesis_sha256"),
                    event.get("error"),
                )
                if event_key in events:
                    continue
                summary = {
                    "plugin": plugin_name,
                    "provider": event.get("provider"),
                    "query": event.get("query"),
                    "query_policy": event.get("query_policy"),
                    "query_inputs": event.get("query_inputs"),
                    "generation": event.get("generation"),
                    "status": event.get("status"),
                    "timestamp": event.get("timestamp"),
                    "result_chars": event.get("result_chars", 0),
                    "synthesis_sha256": event.get("synthesis_sha256", ""),
                    "source_count": len(event.get("sources", []))
                    if isinstance(event.get("sources"), list)
                    else 0,
                }
                for key in ("trust_policy", "prompt_boundary", "authoritative"):
                    if key in event:
                        summary[key] = event.get(key)
                if isinstance(event.get("cache"), dict):
                    summary["cache"] = event.get("cache")
                if isinstance(event.get("source_metadata"), dict):
                    summary["source_metadata"] = event.get("source_metadata")
                if event.get("error"):
                    summary["error"] = event.get("error")
                if event.get("error_type"):
                    summary["error_type"] = event.get("error_type")
                for evidence_key in (
                    "transport_policy",
                    "payload_artifact_policy",
                    "source_ranking",
                    "source_grounding_policy",
                    "source_content_trust_policy",
                    "evidence_boundary_policy",
                    "context_audit_policy",
                ):
                    value = event.get(evidence_key)
                    if isinstance(value, dict):
                        summary[evidence_key] = value
                transport = event.get("transport")
                if isinstance(transport, dict):
                    transport_summary: dict = {
                        "authenticated_transport": bool(
                            transport.get("authenticated_transport")
                        ),
                    }
                    for key in (
                        "status_code",
                        "payload_bytes",
                        "payload_observed_bytes",
                        "payload_limit_bytes",
                        "payload_truncated",
                        "oversized_response",
                        "payload_sha256",
                    ):
                        if key in transport:
                            transport_summary[key] = transport.get(key)
                    request = transport.get("request")
                    if isinstance(request, dict):
                        transport_summary["request_scheme"] = request.get("scheme")
                        transport_summary["request_host"] = request.get("host")
                    final = transport.get("final")
                    if isinstance(final, dict):
                        transport_summary["final_scheme"] = final.get("scheme")
                        transport_summary["final_host"] = final.get("host")
                    if "redirected" in transport:
                        transport_summary["redirected"] = bool(transport.get("redirected"))
                    summary["transport"] = transport_summary
                events[event_key] = summary
                coverage_events.append(event)
                plugin_summary = by_plugin.setdefault(
                    plugin_name,
                    {
                        "events": 0,
                        "ok": 0,
                        "empty": 0,
                        "error": 0,
                        "sources": 0,
                    },
                )
                plugin_summary["events"] += 1
                if event.get("status") in ("ok", "empty", "error"):
                    plugin_summary[str(event.get("status"))] += 1
                plugin_summary["sources"] += summary["source_count"]
    if not events:
        return {}
    return {
        "events": len(events),
        "by_plugin": by_plugin,
        "event_summaries": list(events.values())[-20:],
        "evidence_coverage": _retrieval_evidence_coverage(coverage_events),
    }


def _plugin_artifact_manifest(
    plugins: list[PluginBase],
    *,
    errors: str = "raise",
) -> tuple[list[dict], list[dict]]:
    artifacts = []
    failures = []
    for index, plugin in enumerate(plugins):
        try:
            metadata = _call_optional_plugin_hook(
                plugin,
                index,
                "run_artifacts_metadata",
                phase="normal_finalization",
                hook_policy="fatal_run_abort",
            )
        except Exception as exc:
            if errors != "record":
                raise
            failures.append(_plugin_artifact_failure_manifest(plugin, index, exc))
            continue
        if metadata is None:
            continue
        if not isinstance(metadata, dict):
            exc = ValueError(
                "run_artifacts_metadata must return a mapping, an empty mapping, or None"
            )
            _annotate_plugin_failure(
                exc,
                plugin,
                index,
                "run_artifacts_metadata",
                generation=None,
                phase="normal_finalization",
                hook_policy="fatal_run_abort",
            )
            if errors != "record":
                raise exc
            failures.append(_plugin_artifact_failure_manifest(plugin, index, exc))
            continue
        if metadata:
            try:
                metadata = _validate_plugin_metadata(
                    f"plugin_artifacts[{plugin.__class__.__name__}]",
                    metadata,
                )
            except ValueError as exc:
                _annotate_plugin_failure(
                    exc,
                    plugin,
                    index,
                    "run_artifacts_metadata",
                    generation=None,
                    phase="normal_finalization",
                    hook_policy="fatal_run_abort",
                )
                if errors != "record":
                    raise
                failures.append(_plugin_artifact_failure_manifest(plugin, index, exc))
                continue
            artifacts.append(_plugin_artifact_record(plugin, index, metadata))
    return artifacts, failures


def _plugin_artifact_record(plugin: PluginBase, index: int, metadata: dict) -> dict:
    return {
        **_plugin_identity(plugin, index),
        "metadata": metadata,
    }


def _plugin_artifact_failure_manifest(
    plugin: PluginBase,
    index: int,
    exc: Exception,
) -> dict:
    return {
        **_plugin_identity(plugin, index),
        "hook": "run_artifacts_metadata",
        "policy": "recorded_during_abort_finalization",
        "continued": False,
        "exception_type": exc.__class__.__name__,
        **_aborted_exception_manifest(exc),
    }


def _seed_post_processing_policy() -> dict:
    return {
        "policy": "raw_evaluator_baseline",
        "llm_feedback": "not_applied",
        "plugin_score_composition": "not_applied",
    }


def _apply_plugin_scores(
    program: Program,
    initial_score: float,
    plugins: list[PluginBase],
    *,
    generation: int | None = None,
    phase: str | None = None,
) -> float:
    score = initial_score
    composition = {
        "evaluator_fitness": program.evaluation.get("fitness") if program.evaluation else None,
        "initial_fitness": initial_score,
        "final_fitness": initial_score,
        "diverged_from_evaluation": False,
        "plugins": [],
    }
    feedback_adjusted = program.metrics.get("feedback_adjusted_fitness")
    if feedback_adjusted is not None:
        composition["feedback_adjusted_fitness"] = feedback_adjusted

    for index, plugin in enumerate(plugins):
        before = score
        before_metrics = dict(program.metrics)
        before_metadata = copy.deepcopy(program.metadata)
        record = {
            **_plugin_identity(plugin, index),
            "before": before,
            "after": before,
            "delta": 0.0,
            "metrics_added": [],
            "metrics_changed": [],
            "metadata_added": [],
            "metadata_changed": [],
            "accepted": False,
            "error": None,
        }
        proposed = _call_plugin_hook(
            plugin,
            index,
            "on_evaluated",
            program,
            score,
            generation=generation,
            phase=phase,
            hook_policy="fatal_run_abort",
            parent_id=program.parent_id,
            candidate_id=program.id,
        )
        if isinstance(proposed, bool) or not isinstance(proposed, (int, float)):
            record["error"] = "invalid_plugin_score"
        elif not math.isfinite(float(proposed)):
            record["error"] = "non_finite_plugin_score"
        else:
            score = float(proposed)
            record["after"] = score
            record["delta"] = score - before
            record["accepted"] = True
        try:
            after_metrics = validate_program_metrics(program.metrics)
            program.metrics = after_metrics
        except ValueError as exc:
            program.metrics = before_metrics
            after_metrics = before_metrics
            score = before
            record["after"] = before
            record["delta"] = 0.0
            record["accepted"] = False
            record["error"] = "invalid_plugin_metrics"
            record["message"] = _bounded_redacted_text(
                str(exc),
                _MAX_PLUGIN_SIDE_EFFECT_ERROR_CHARS,
            )
        try:
            after_metadata = validate_program_metadata(
                program.metadata,
                label="Plugin-updated program metadata",
            )
            program.metadata = after_metadata
        except ValueError as exc:
            program.metrics = before_metrics
            program.metadata = before_metadata
            after_metrics = before_metrics
            after_metadata = before_metadata
            score = before
            record["after"] = before
            record["delta"] = 0.0
            record["accepted"] = False
            record["error"] = "invalid_plugin_metadata"
            record["message"] = _bounded_redacted_text(
                str(exc),
                _MAX_PLUGIN_SIDE_EFFECT_ERROR_CHARS,
            )
        record["metrics_added"] = sorted(set(after_metrics) - set(before_metrics))
        record["metrics_changed"] = sorted(
            key
            for key in set(after_metrics) & set(before_metrics)
            if after_metrics[key] != before_metrics[key]
        )
        record["metadata_added"] = sorted(set(after_metadata) - set(before_metadata))
        record["metadata_changed"] = sorted(
            key
            for key in set(after_metadata) & set(before_metadata)
            if after_metadata[key] != before_metadata[key]
        )
        composition["plugins"].append(record)
        program.fitness = score

    composition["final_fitness"] = score
    evaluation_fitness = composition["evaluator_fitness"]
    composition["diverged_from_evaluation"] = (
        isinstance(evaluation_fitness, (int, float))
        and math.isfinite(float(evaluation_fitness))
        and score != float(evaluation_fitness)
    )
    program.metadata = dict(program.metadata)
    program.metadata["score_composition"] = composition
    program.fitness = score
    return score


def _annotate_metric_policy(program: Program, problem: Problem) -> None:
    normalized: dict[str, float] = {}
    weights: dict[str, float] = {}
    for metric in problem.metrics:
        name = metric.get("name")
        if not isinstance(name, str):
            continue
        if metric.get("source") == "final_fitness":
            value = program.fitness
            if not (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
            ):
                program.metrics[name] = float(value)
        elif name in program.metrics:
            value = program.metrics[name]
        else:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        numeric = float(value)
        if not math.isfinite(numeric):
            continue
        normalized[name] = problem.normalize_metric(name, numeric)
        raw_weight = metric.get("weight", 1.0)
        if (
            isinstance(raw_weight, (int, float))
            and not isinstance(raw_weight, bool)
            and math.isfinite(float(raw_weight))
            and float(raw_weight) >= 0.0
        ):
            weights[name] = float(raw_weight)
        else:
            weights[name] = 1.0
    if not normalized:
        return
    total_weight = sum(weights.get(name, 1.0) for name in normalized)
    uses_non_default_weights = any(
        weights.get(name, 1.0) != 1.0 for name in normalized
    )
    if total_weight > 0.0 and uses_non_default_weights:
        selection_score = (
            sum(normalized[name] * weights.get(name, 1.0) for name in normalized)
            / total_weight
        )
        policy_type = "weighted_normalized_declared_metrics"
    elif total_weight > 0.0:
        selection_score = sum(normalized.values()) / len(normalized)
        policy_type = "mean_normalized_declared_metrics"
    else:
        selection_score = sum(normalized.values()) / len(normalized)
        policy_type = "mean_normalized_declared_metrics_zero_weight_fallback"
    program.metadata = dict(program.metadata)
    program.metadata["normalized_metrics"] = normalized
    program.metadata["selection_score"] = selection_score
    program.metadata["selection_policy"] = {
        "type": policy_type,
        "metrics": list(normalized),
        "primary_metric": problem.primary_metric,
    }
    if policy_type == "weighted_normalized_declared_metrics":
        program.metadata["selection_policy"]["weights"] = {
            name: weights[name]
            for name in normalized
        }


def _last_llm_call(llm) -> dict | None:
    call = getattr(llm, "last_call", None)
    return dict(call) if isinstance(call, dict) else None


def _generate_with_budget(
    llm,
    budget: RunBudget,
    prompt: str,
    *,
    role: str,
    budget_event_sink: Callable[[dict], dict] | None = None,
) -> tuple[str, int]:
    reason = budget.check_before_llm_call(role=role)
    if reason is not None:
        raise RuntimeError(f"LLM call budget exhausted before {role}: {reason}")
    remaining_runtime_sec = budget.remaining_runtime_seconds()
    if remaining_runtime_sec is not None and remaining_runtime_sec <= 0.0:
        raise RuntimeError(f"LLM call budget exhausted before {role}: max_runtime_seconds")
    call_count_before = _llm_call_count(llm)
    original_max_call_attempts = None
    remaining_llm_calls = _remaining_llm_call_budget(budget)
    if isinstance(llm, LLMEnsemble) and remaining_llm_calls is not None:
        original_max_call_attempts = llm.max_call_attempts
        llm.max_call_attempts = min(original_max_call_attempts, remaining_llm_calls)
    try:
        return _generate_with_runtime_deadline(
            llm,
            prompt,
            role=role,
            remaining_runtime_sec=remaining_runtime_sec,
        )
    finally:
        call_span = _llm_call_span(llm, call_count_before)
        if original_max_call_attempts is not None:
            llm.max_call_attempts = original_max_call_attempts
        call_delta = _llm_call_attempt_delta(llm, call_count_before)
        for _ in range(call_delta):
            budget.record_llm_call()
        budget.record_llm_provider_attempts(
            _llm_provider_attempt_delta(call_span),
            role=role,
        )
        budget.record_llm_tokens(_llm_token_delta(call_span), role=role)
        budget.record_llm_cost_microusd(
            _llm_cost_microusd_delta(call_span),
            role=role,
        )
        budget.record_llm_seconds(_llm_seconds_delta(call_span), role=role)
        _emit_llm_budget_events(
            call_span,
            role=role,
            fallback_call_count=call_delta,
            sink=budget_event_sink,
        )


def _remaining_llm_call_budget(budget: RunBudget) -> int | None:
    if budget.max_llm_calls is None:
        return None
    return max(1, budget.max_llm_calls - budget.llm_calls)


def _llm_call_attempt_delta(llm, call_count_before: int | None) -> int:
    call_count_after = _llm_call_count(llm)
    if (
        isinstance(call_count_before, int)
        and isinstance(call_count_after, int)
        and call_count_after >= call_count_before
    ):
        return max(1, call_count_after - call_count_before)
    return 1


def _llm_provider_attempt_delta(call_span: list[dict]) -> int:
    attempts = 0
    retained_records = 0
    for record in call_span:
        if not isinstance(record, dict):
            continue
        retained_records += 1
        attempts += _llm_provider_attempts_for_record(record)
    return attempts if retained_records else 0


def _llm_provider_attempts_for_record(record: dict) -> int:
    adapter_retry = record.get("adapter_retry")
    if isinstance(adapter_retry, dict):
        raw_attempts = adapter_retry.get("attempts")
        if (
            isinstance(raw_attempts, int)
            and not isinstance(raw_attempts, bool)
            and raw_attempts > 0
        ):
            return raw_attempts
    return 1


def _llm_token_delta(call_span: list[dict]) -> int:
    tokens = 0
    for record in call_span:
        if not isinstance(record, dict):
            continue
        tokens += _llm_tokens_for_record(record)
    return tokens


def _llm_tokens_for_record(record: dict) -> int:
    usage = record.get("usage")
    if not isinstance(usage, dict):
        return 0
    total_tokens = usage.get("total_tokens")
    if (
        isinstance(total_tokens, int)
        and not isinstance(total_tokens, bool)
        and total_tokens > 0
    ):
        return total_tokens
    return 0


def _llm_cost_microusd_delta(call_span: list[dict]) -> int:
    cost_microusd = 0
    for record in call_span:
        if not isinstance(record, dict):
            continue
        cost_microusd += _llm_cost_microusd_for_record(record)
    return cost_microusd


def _llm_cost_microusd_for_record(record: dict) -> int:
    cost_estimate = record.get("cost_estimate")
    if not isinstance(cost_estimate, dict):
        return 0
    raw_cost = cost_estimate.get("cost_microusd")
    if isinstance(raw_cost, int) and not isinstance(raw_cost, bool) and raw_cost > 0:
        return raw_cost
    return 0


def _llm_seconds_delta(call_span: list[dict]) -> float:
    seconds = 0.0
    for record in call_span:
        if not isinstance(record, dict):
            continue
        seconds += _llm_seconds_for_record(record)
    return seconds


def _llm_seconds_for_record(record: dict) -> float:
    raw_latency = record.get("latency_sec")
    if isinstance(raw_latency, bool) or not isinstance(raw_latency, (int, float)):
        return 0.0
    latency = float(raw_latency)
    if math.isfinite(latency) and latency > 0.0:
        return latency
    return 0.0


def _emit_llm_budget_events(
    call_span: list[dict],
    *,
    role: str,
    fallback_call_count: int,
    sink: Callable[[dict], dict] | None,
) -> None:
    if sink is None:
        return
    emitted = 0
    for record in call_span:
        if not isinstance(record, dict):
            continue
        sink(_llm_budget_event_for_record(record, role=role))
        emitted += 1
    for _ in range(max(0, fallback_call_count - emitted)):
        sink({"kind": "llm_call", "role": role})


def _llm_budget_event_for_record(record: dict, *, role: str) -> dict:
    event: dict[str, object] = {"kind": "llm_call", "role": role}
    provider_attempts = _llm_provider_attempts_for_record(record)
    if provider_attempts:
        event["provider_attempts"] = provider_attempts
    tokens = _llm_tokens_for_record(record)
    if tokens:
        event["tokens"] = tokens
    cost_microusd = _llm_cost_microusd_for_record(record)
    if cost_microusd:
        event["cost_microusd"] = cost_microusd
    seconds = _llm_seconds_for_record(record)
    if seconds:
        event["seconds"] = seconds
    return event


def _is_llm_budget_exhaustion(exc: BaseException) -> bool:
    return isinstance(exc, RuntimeError) and str(exc).startswith(
        "LLM call budget exhausted before "
    )


def _generate_with_runtime_deadline(
    llm,
    prompt: str,
    *,
    role: str,
    remaining_runtime_sec: float | None,
) -> tuple[str, int]:
    if (
        remaining_runtime_sec is None
        or "call_timeout_sec" not in getattr(llm, "__dict__", {})
    ):
        return llm.generate(prompt, role=role)
    original_timeout = getattr(llm, "call_timeout_sec")
    effective_timeout = remaining_runtime_sec
    if original_timeout is not None:
        effective_timeout = min(float(original_timeout), remaining_runtime_sec)
    setattr(llm, "call_timeout_sec", effective_timeout)
    try:
        return llm.generate(prompt, role=role)
    finally:
        setattr(llm, "call_timeout_sec", original_timeout)


class _BudgetedLLMProxy:
    def __init__(
        self,
        llm,
        budget: RunBudget,
        *,
        budget_event_sink: Callable[[dict], dict] | None = None,
    ):
        self._llm = llm
        self._budget = budget
        self._budget_event_sink = budget_event_sink

    def generate(self, prompt: str, role: str):
        return _generate_with_budget(
            self._llm,
            self._budget,
            prompt,
            role=role,
            budget_event_sink=self._budget_event_sink,
        )

    def __getattr__(self, name: str):
        return getattr(self._llm, name)


def _skipped_llm_budget_record(
    *,
    role: str,
    stop_reason: str | None,
    budget: RunBudget,
) -> dict:
    return {
        "status": "skipped",
        "role": role,
        "skip_reason": stop_reason or "max_llm_calls",
        "budget": budget.snapshot(),
    }


def _llm_call_count(llm) -> int | None:
    retention = getattr(llm, "call_history_retention", None)
    if isinstance(retention, dict):
        total = retention.get("total_records")
        if isinstance(total, int) and not isinstance(total, bool) and total >= 0:
            return total
    history = getattr(llm, "call_history", None)
    return len(history) if isinstance(history, list) else None


def _llm_call_span(llm, start: int | None) -> list[dict]:
    if start is None:
        return []
    history = getattr(llm, "call_history", None)
    if not isinstance(history, list) or start < 0:
        return []
    retention = getattr(llm, "call_history_retention", None)
    dropped = 0
    if isinstance(retention, dict):
        raw_dropped = retention.get("dropped_records")
        if isinstance(raw_dropped, int) and not isinstance(raw_dropped, bool) and raw_dropped >= 0:
            dropped = raw_dropped
    retained_start = max(0, start - dropped)
    if retained_start > len(history):
        return []
    return [dict(call) for call in history[retained_start:] if isinstance(call, dict)]


def _filter_inspirations_by_policy(
    inspirations: list[Program],
    sample_metadata: dict,
    *,
    required_metric: str | None,
    excluded_metrics: list[str] | tuple[str, ...] | None = None,
    fitness_threshold: dict | None = None,
    metric_thresholds: dict,
    metric_ranking: dict | None,
    requested_count: int,
    pool_requested_count: int,
) -> tuple[list[Program], dict]:
    excluded_metric_set = set(excluded_metrics or [])
    required_matching = [
        program
        for program in inspirations
        if required_metric is None
        or (isinstance(program.metrics, dict) and required_metric in program.metrics)
    ]
    excluded_metric_matching = [
        program
        for program in required_matching
        if not _program_has_excluded_inspiration_metric(program, excluded_metric_set)
    ]
    fitness_matching = [
        program
        for program in excluded_metric_matching
        if _program_matches_inspiration_fitness_threshold(
            program,
            fitness_threshold,
        )
    ]
    threshold_matching = [
        program
        for program in fitness_matching
        if _program_matches_inspiration_metric_thresholds(program, metric_thresholds)
    ]
    ranked = _rank_inspirations_by_metric(threshold_matching, metric_ranking)
    selected = ranked[:requested_count]
    selected_ids = {program.id for program in selected}
    filtered_out = [
        program
        for program in inspirations
        if program.id not in selected_ids
    ]
    metadata = dict(sample_metadata)
    metadata["requested_count"] = requested_count
    metadata["selected_count"] = len(selected)
    metadata["selected_program_ids"] = [program.id for program in selected]
    metadata["pre_filter_selected_count"] = len(inspirations)
    metadata["pool_requested_count"] = pool_requested_count
    if required_metric is not None:
        metadata["inspiration_required_metric"] = required_metric
        metadata["inspiration_required_metric_policy"] = "metric_present_filter_v1"
        metadata["required_metric_matching_count"] = len(required_matching)
    if excluded_metric_set:
        metadata["inspiration_excluded_metrics"] = sorted(excluded_metric_set)
        metadata["inspiration_excluded_metrics_policy"] = "metric_absence_filter_v1"
        metadata["excluded_metric_matching_count"] = len(excluded_metric_matching)
    if fitness_threshold is not None:
        metadata["inspiration_fitness_threshold"] = dict(fitness_threshold)
        metadata["inspiration_fitness_threshold_policy"] = (
            "fitness_value_threshold_filter_v1"
        )
        metadata["fitness_threshold_matching_count"] = len(fitness_matching)
    if metric_thresholds:
        metadata["inspiration_metric_thresholds"] = {
            name: dict(thresholds)
            for name, thresholds in metric_thresholds.items()
        }
        metadata["inspiration_metric_threshold_policy"] = (
            "metric_value_threshold_filter_v1"
        )
        metadata["metric_threshold_matching_count"] = len(threshold_matching)
    if metric_ranking is not None:
        metadata["inspiration_metric_ranking"] = dict(metric_ranking)
        metadata["inspiration_metric_ranking_policy"] = "metric_value_sort_v1"
        metadata["metric_ranking_candidate_count"] = len(ranked)
    metadata["inspiration_filter_filtered_count"] = len(filtered_out)
    metadata["inspiration_filter_filtered_program_ids"] = [
        program.id for program in filtered_out[:20]
    ]
    if "target_metrics" in metadata and isinstance(metadata["target_metrics"], list):
        metadata["target_metrics"] = [
            item
            for item in metadata["target_metrics"]
            if isinstance(item, dict) and item.get("program_id") in selected_ids
        ]
    return selected, metadata


def _program_has_excluded_inspiration_metric(
    program: Program,
    excluded_metrics: set[str],
) -> bool:
    if not excluded_metrics:
        return False
    metrics = program.metrics if isinstance(program.metrics, dict) else {}
    return any(metric in metrics for metric in excluded_metrics)


def _program_matches_inspiration_fitness_threshold(
    program: Program,
    fitness_threshold: dict | None,
) -> bool:
    if fitness_threshold is None:
        return True
    if (
        isinstance(program.fitness, bool)
        or not isinstance(program.fitness, (int, float))
        or not math.isfinite(float(program.fitness))
    ):
        return False
    fitness = float(program.fitness)
    minimum = fitness_threshold.get("min")
    maximum = fitness_threshold.get("max")
    if minimum is not None and fitness < float(minimum):
        return False
    if maximum is not None and fitness > float(maximum):
        return False
    return True


def _program_matches_inspiration_metric_thresholds(
    program: Program,
    metric_thresholds: dict,
) -> bool:
    if not metric_thresholds:
        return True
    metrics = program.metrics if isinstance(program.metrics, dict) else {}
    for metric, bounds in metric_thresholds.items():
        value = metrics.get(metric)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        number = float(value)
        if not math.isfinite(number):
            return False
        minimum = bounds.get("min") if isinstance(bounds, dict) else None
        maximum = bounds.get("max") if isinstance(bounds, dict) else None
        if minimum is not None and number < minimum:
            return False
        if maximum is not None and number > maximum:
            return False
    return True


def _rank_inspirations_by_metric(
    inspirations: list[Program],
    metric_ranking: dict | None,
) -> list[Program]:
    if metric_ranking is None:
        return inspirations
    metric = metric_ranking["metric"]
    direction = metric_ranking["direction"]
    sortable: list[tuple[float, int, Program]] = []
    unsortable: list[tuple[int, Program]] = []
    for index, program in enumerate(inspirations):
        metrics = program.metrics if isinstance(program.metrics, dict) else {}
        value = metrics.get(metric)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            unsortable.append((index, program))
            continue
        number = float(value)
        if not math.isfinite(number):
            unsortable.append((index, program))
            continue
        sortable.append((number, index, program))
    reverse = direction == "maximize"
    ranked = [
        program
        for _, _, program in sorted(
            sortable,
            key=lambda item: (item[0], -item[1] if reverse else item[1]),
            reverse=reverse,
        )
    ]
    ranked.extend(program for _, program in unsortable)
    return ranked


def _build_meta_prompt_mutation_request(
    prompt_program,
    prompt_db: PromptDatabase,
    program: Program,
    parent: Program,
    prompt_reward: float,
    recent_failures: list[dict],
    config: Config,
) -> tuple[str, dict]:
    context_policy_capabilities = validate_meta_prompt_context_policy_capabilities(
        _META_PROMPT_CONTEXT_POLICY_CAPABILITIES
    )
    evidence = {
        "reward_policy": {
            "mode": config.prompt_reward_mode,
            "bounds": [
                float(config.prompt_reward_bounds[0]),
                float(config.prompt_reward_bounds[1]),
            ],
        },
        "latest_candidate": _candidate_evidence(program, parent, prompt_reward),
        "selected_prompt": _prompt_program_evidence(prompt_program, selected=True),
        "context_policy_capabilities": context_policy_capabilities,
        "prompt_program_summaries": [
            _prompt_program_evidence(candidate, selected=candidate.id == prompt_program.id)
            for candidate in sorted(
                prompt_db.all(),
                key=lambda item: (item.mean_reward, item.uses, item.id),
                reverse=True,
            )[:5]
        ],
        "recent_failures": [_failure_evidence(failure) for failure in recent_failures[-3:]],
    }
    raw_context = json.dumps(evidence, indent=2)
    redacted_context = redact_sensitive_text(raw_context)
    truncated = len(redacted_context) > _MAX_META_PROMPT_CONTEXT_CHARS
    if truncated:
        redacted_context = (
            redacted_context[: _MAX_META_PROMPT_CONTEXT_CHARS - 15] + "...<truncated>"
        )
    retained_evidence = _retained_meta_prompt_evidence(
        raw_context=raw_context,
        prompt_context=redacted_context,
        prompt_context_truncated=truncated,
        mode=config.meta_prompt_evidence_retention_mode,
    )
    context_hash = (
        hashlib.sha256(redacted_context.encode("utf-8")).hexdigest()
        if retained_evidence["sha256"] is not None
        else None
    )
    safe_template, template_metadata = _meta_prompt_template_preview(
        prompt_program.template
    )
    context_metadata = {
        "schema": "meta_prompt_mutation_context_v1",
        "sha256": context_hash,
        "chars": (
            len(redacted_context) if retained_evidence["chars"] is not None else None
        ),
        "truncated": truncated if retained_evidence["chars"] is not None else False,
        "sections": [
            "reward_policy",
            "latest_candidate",
            "selected_prompt",
            "context_policy_capabilities",
            "prompt_program_summaries",
            "recent_failures",
        ],
        "selected_prompt_id": prompt_program.id,
        "latest_program_id": program.id,
        "latest_parent_id": parent.id,
        "current_template": template_metadata,
        "evidence_retention": {
            key: value for key, value in retained_evidence.items() if key != "text"
        },
    }
    if retained_evidence["text"] is not None:
        context_metadata["evidence"] = retained_evidence["text"]
    current_fields = sorted(prompt_template_fields(prompt_program.template))
    mutation_prompt = (
        "Improve this LibreEvolve prompt template for future code evolution. "
        "Use the bounded prompt-performance evidence to improve search behavior. "
        "Keep all existing Python format placeholders intact. You may also tune "
        "the structured context_policy.disabled_sections list and "
        "context_policy.section_priorities map to change optional context "
        "rendering and prompt-packing priorities, plus "
        "context_policy.mutation_instruction_variant with one of default, "
        "minimal, or exploratory, context_policy."
        "mutation_instruction_include_example to keep or remove the built-in "
        "mutation-format example, context_policy.proposal_metadata_enabled "
        "to override whether proposal metadata instructions and parsing are "
        "enabled for this prompt arm, and context_policy.feedback_sections to "
        "choose which evaluator/LLM-feedback subsections are rendered, plus "
        "context_policy.llm_feedback_fields to choose LLM-grader feedback "
        "fields, context_policy.llm_feedback_max_chars_by_field to cap "
        "LLM-grader feedback fields independently, "
        "context_policy.proposal_fields to choose proposal-metadata "
        "fields, context_policy.proposal_max_chars_by_field to cap "
        "proposal-metadata fields independently, "
        "context_policy.stage_summary_fields to choose stage-summary "
        "fields, context_policy.stage_summary_max_chars_by_field to cap "
        "stage-summary fields independently, "
        "context_policy.execution_output_fields to choose execution-output "
        "fields, context_policy.execution_output_max_chars_by_field to cap "
        "stdout/stderr/error text independently, context_policy.sample_retry_fields to choose sample/retry "
        "diagnostic fields, context_policy.sample_retry_max_chars_by_field to cap "
        "sample/retry diagnostic text independently, "
        "context_policy.program_output_fields to choose program-output "
        "fields, and context_policy.program_output_max_chars_by_field to cap "
        "program-output text fields independently, "
        "context_policy.validator_artifact_fields to choose validator-artifact "
        "fields, context_policy.validator_artifact_max_chars_by_field to cap "
        "validator-artifact text fields independently, "
        "context_policy.validator_artifact_content_fields to choose "
        "nested artifact-content fields, context_policy."
        "validator_artifact_content_mode and validator_artifact_content_max_bytes/"
        "max_chars to choose artifact-content rendering policy, and context_policy."
        "validator_skipped_artifact_fields to choose skipped-artifact fields, "
        "context_policy.validator_skipped_artifact_max_chars_by_field to cap "
        "skipped-artifact text fields independently, "
        "and context_policy.validator_diagnostic_groups to choose validator "
        "diagnostic groups, plus context_policy.validator_metadata_keys "
        "to choose safe validator metadata-summary keys, context_policy."
        "validator_metadata_limit to cap validator metadata-summary item count, "
        "context_policy."
        "validator_metadata_max_chars_by_key to cap validator metadata-summary "
        "values by key, and context_policy."
        "syntax_error_fields to choose syntax-error diagnostic fields, plus "
        "context_policy.syntax_error_max_chars_by_field to cap syntax-error "
        "diagnostic text fields independently, plus "
        "context_policy.metric_bound_fields to choose metric-bound diagnostic "
        "fields, context_policy.metric_bound_max_chars_by_field to cap "
        "metric-bound diagnostic text fields independently, and context_policy."
        "configured_stage_check_fields to choose "
        "configured-stage diagnostic fields, context_policy."
        "configured_stage_check_max_chars_by_field to cap configured-stage "
        "diagnostic text fields independently, context_policy.stage_metric_threshold_fields "
        "to choose nested stage metric-threshold fields, context_policy."
        "stage_metric_threshold_max_chars_by_field to cap nested stage "
        "metric-threshold text fields independently, context_policy."
        "artifact_output_check_fields to choose nested artifact-output check "
        "fields, context_policy.artifact_output_check_max_chars_by_field to "
        "cap nested artifact-output check text fields independently, plus "
        "context_policy."
        "malformed_metric_fields to choose malformed-metric diagnostic fields, "
        "context_policy.malformed_metric_max_chars_by_field to cap "
        "malformed-metric diagnostic text fields independently. "
        "context_policy.metric_aggregation_fields may choose "
        "metric-aggregation diagnostic fields. context_policy."
        "metric_aggregation_max_chars_by_field may cap metric-aggregation "
        "diagnostic text fields independently. context_policy."
        "execution_diagnostic_groups may choose execution-diagnostic subgroups. "
        "context_policy.validator_boundary_fields may choose validator-boundary diagnostic "
        "fields, context_policy.validator_boundary_max_chars_by_field may cap "
        "validator-boundary diagnostic text fields independently, context_policy."
        "validator_resource_limit_fields may choose "
        "nested validator resource-limit fields, context_policy."
        "validator_resource_limit_max_chars_by_field may cap nested validator "
        "resource-limit text fields independently, and context_policy."
        "validator_stdin_fields may choose "
        "validator-stdin diagnostic fields, while context_policy."
        "validator_stdin_max_chars_by_field may cap validator-stdin "
        "diagnostic text fields independently. context_policy."
        "diagnostic_output_fields may choose diagnostic-output fields. "
        "context_policy.diagnostic_output_max_chars_by_field may cap "
        "diagnostic-output text fields independently. "
        "context_policy.timeout_cleanup_fields may choose timeout-cleanup "
        "diagnostic fields, and context_policy."
        "timeout_cleanup_max_chars_by_field may cap timeout-cleanup "
        "diagnostic text fields independently. "
        "When "
        "stochastic prompt-format markers are configured, context_policy."
        "prompt_format_weights may override their alternative weights, and "
        "context_policy.context_source_paths may select local context paths to "
        "render, context_policy.context_source_max_chars may cap rendered local "
        "context source text, context_policy.context_source_limit may cap how many "
        "ordered local context sources render after path selection and ranking, "
        "context_policy.context_source_required_terms may require loaded local "
        "context sources to contain all listed safe terms before ranking, "
        "context_policy.context_source_excluded_terms may omit loaded local "
        "context sources containing any listed safe terms before ranking, "
        "context_policy.context_source_ranking_terms may provide explicit safe "
        "terms for deterministic local context-source ranking, "
        "context_policy.context_source_truncation may choose "
        "head or head_tail truncation, context_policy.context_source_order_policy "
        "may keep path order or rank selected context sources by deterministic "
        "task-term overlap, and context_policy.recent_failure_limit may cap rendered "
        "recent failure-memory records, context_policy."
        "recent_failure_selection_policy may choose recent, oldest, "
        "lowest_score, or highest_repetition retained failure-memory records, "
        "context_policy."
        "recent_failure_required_errors may filter retained failure-memory "
        "records by exact safe error or diff_error labels, context_policy."
        "recent_failure_excluded_errors may exclude retained failure-memory "
        "records by exact safe error or diff_error labels, context_policy."
        "recent_failure_required_changed_files may filter retained "
        "failure-memory records by exact safe changed file paths, context_policy."
        "recent_failure_excluded_changed_files may exclude retained "
        "failure-memory records by exact safe changed file paths, context_policy."
        "recent_failure_required_stage_names may filter retained "
        "failure-memory records by exact safe evaluation stage names, "
        "context_policy.recent_failure_excluded_stage_names may exclude retained "
        "failure-memory records by exact safe evaluation stage names, context_policy."
        "recent_failure_required_terms may require retained failure-memory "
        "records to contain all listed safe terms, context_policy."
        "recent_failure_excluded_terms may omit retained failure-memory records "
        "containing any listed safe terms, context_policy."
        "recent_failure_repetition_threshold may filter retained "
        "failure-memory records by repetition_count min/max bounds, context_policy."
        "recent_failure_score_threshold may filter retained failure-memory "
        "records by finite score min/max bounds, context_policy."
        "recent_failure_max_chars_by_field may cap recent failure-memory "
        "fields independently, and context_policy.inspiration_limit "
        "may cap rendered selected inspirations, context_policy."
        "inspiration_sample_count may choose how many inspirations are sampled "
        "upstream before plugin context and prompt rendering, context_policy."
        "inspiration_required_metric may filter upstream inspirations to "
        "programs carrying a safe metric name before plugin context and prompt "
        "rendering, context_policy.inspiration_excluded_metrics may filter out "
        "upstream inspirations carrying any listed safe metric names, "
        "context_policy.inspiration_fitness_threshold may filter upstream "
        "inspirations by finite fitness min/max bounds, "
        "context_policy.inspiration_metric_thresholds may filter "
        "upstream inspirations to programs whose numeric metric values meet "
        "safe min/max thresholds before plugin context and prompt rendering, "
        "context_policy.evaluator_path_fields may select prompt-visible "
        "validator path provenance and "
        "context_policy.evaluator_path_max_chars_by_field may cap those "
        "path fields, "
        "context_policy.evaluator_dependency_fields may select prompt-visible "
        "validator dependency-policy provenance and "
        "context_policy.evaluator_dependency_max_chars_by_field may cap those "
        "dependency fields, "
        "context_policy.evaluator_stage_fields may select prompt-visible "
        "validator stage-context provenance and "
        "context_policy.evaluator_stage_max_chars_by_field may cap those "
        "stage fields, "
        "context_policy.evaluator_workspace_fields may select prompt-visible "
        "evaluated workspace provenance and "
        "context_policy.evaluator_workspace_max_chars_by_field may cap those "
        "workspace fields, "
        "context_policy.validator_budget_fields may select prompt-visible "
        "stage/sample budget diagnostics and "
        "context_policy.validator_budget_max_chars_by_field may cap those "
        "budget fields, context_policy.validator_env_fields may select "
        "prompt-visible validator environment diagnostics and "
        "context_policy.validator_env_max_chars_by_field may cap those "
        "environment fields, context_policy.synthetic_metric_fields may select "
        "synthetic failure-metric diagnostics and "
        "context_policy.synthetic_metric_max_chars_by_field may cap those "
        "synthetic metric fields, context_policy.materialization_error_fields "
        "may select materialization-error diagnostics and "
        "context_policy.materialization_error_max_chars_by_field may cap those "
        "fields, "
        "context_policy.inspiration_metric_ranking may rank upstream inspirations "
        "by a numeric metric before final selection, and "
        "context_policy.extra_context_max_chars may cap rendered plugin extra-context text. "
        "context_policy.plugin_context_enabled may disable plugin prompt-context "
        "generation for this prompt arm while preserving plugin provenance, and "
        "context_policy.plugin_context_allowlist may select plugin identity labels "
        "whose prompt-context hooks should run, context_policy."
        "plugin_context_excluded_labels may omit plugin identity labels before "
        "prompt-context hooks run, and context_policy."
        "plugin_context_order may reorder selected plugin prompt-context "
        "sections by safe plugin identity labels, context_policy."
        "plugin_context_required_terms may require plugin context text to "
        "contain safe terms before prompt visibility, context_policy."
        "plugin_context_excluded_terms may omit plugin context text containing "
        "safe terms before prompt visibility, context_policy."
        "plugin_context_ranking_terms may rank prompt-visible plugin context "
        "sections by deterministic term overlap, context_policy."
        "plugin_context_limit may cap how many ordered plugin context sections "
        "become prompt-visible, and context_policy."
        "plugin_context_max_chars may globally cap each plugin context section, "
        "context_policy.plugin_context_truncation may choose head or head_tail "
        "retention under plugin context caps, "
        "while context_policy.plugin_context_max_chars_by_label may cap plugin "
        "context text by safe plugin identity label before aggregate prompt packing. "
        "Return either the complete "
        "revised template as plain text, or one JSON object with schema "
        "\"libreevolve.prompt_mutation_response.v1\", template, and optional "
        "context_policy.\n\n"
        "[Prompt Performance Evidence]\n"
        f"{redacted_context}\n\n"
        "[Current Template Placeholders]\n"
        f"{json.dumps(current_fields, sort_keys=True)}\n\n"
        "[Current Template]\n"
        f"{safe_template}"
    )
    return mutation_prompt, context_metadata


def validate_meta_prompt_context_policy_capabilities(capabilities: object) -> dict:
    """Validate the meta-prompt-visible structured context-policy capability map."""
    if not isinstance(capabilities, dict):
        raise ValueError("meta-prompt context policy capabilities must be an object")
    required = {"schema", *_META_PROMPT_CONTEXT_POLICY_CAPABILITY_SECTIONS}
    missing = required - set(capabilities)
    if missing:
        raise ValueError(
            f"meta-prompt context policy capabilities missing fields: {sorted(missing)}"
        )
    unsupported = set(capabilities) - required
    if unsupported:
        raise ValueError(
            "meta-prompt context policy capabilities has unsupported fields: "
            f"{sorted(unsupported)}"
        )
    if capabilities["schema"] != META_PROMPT_CONTEXT_POLICY_CAPABILITIES_SCHEMA:
        raise ValueError("meta-prompt context policy capabilities schema is unsupported")
    policy_fields = set(validate_prompt_context_policy({})) - {"schema"}
    advertised_fields: set[str] = set()
    normalized = {"schema": capabilities["schema"]}
    for section in _META_PROMPT_CONTEXT_POLICY_CAPABILITY_SECTIONS:
        fields = _validate_meta_prompt_context_policy_capability_section(
            capabilities[section],
            section,
        )
        duplicates = advertised_fields.intersection(fields)
        if duplicates:
            raise ValueError(
                "meta-prompt context policy capabilities duplicate fields: "
                f"{sorted(duplicates)}"
            )
        advertised_fields.update(fields)
        normalized[section] = ",".join(fields)
    missing_policy_fields = policy_fields - advertised_fields
    if missing_policy_fields:
        raise ValueError(
            "meta-prompt context policy capabilities omit prompt policy fields: "
            f"{sorted(missing_policy_fields)}"
        )
    unsupported_policy_fields = advertised_fields - policy_fields
    if unsupported_policy_fields:
        raise ValueError(
            "meta-prompt context policy capabilities advertise unsupported fields: "
            f"{sorted(unsupported_policy_fields)}"
        )
    return normalized


def _validate_meta_prompt_context_policy_capability_section(
    value: object,
    section: str,
) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"meta-prompt context policy capabilities {section} must be text"
        )
    fields = value.split(",")
    normalized: list[str] = []
    seen: set[str] = set()
    for field in fields:
        if field != field.strip() or not field:
            raise ValueError(
                f"meta-prompt context policy capabilities {section} has malformed field"
            )
        if _META_PROMPT_CONTEXT_POLICY_CAPABILITY_RE.fullmatch(field) is None:
            raise ValueError(
                f"meta-prompt context policy capabilities {section} has unsafe field"
            )
        if field in seen:
            raise ValueError(
                f"meta-prompt context policy capabilities {section} repeats field"
            )
        seen.add(field)
        normalized.append(field)
    return normalized


def _retained_meta_prompt_evidence(
    *,
    raw_context: str,
    prompt_context: str,
    prompt_context_truncated: bool,
    mode: str,
) -> dict:
    if mode == "off":
        return {
            "text": None,
            "sha256": None,
            "chars": None,
            "stored_chars": 0,
            "redacted": None,
            "truncated": False,
            "prompt_sha256": None,
            "prompt_chars": None,
            "prompt_truncated": False,
            "max_retained_chars": _MAX_META_PROMPT_RETAINED_EVIDENCE_CHARS,
            "retention_mode": mode,
            "retention_policy": "off_no_evidence_or_hash",
        }
    raw_sha256 = hashlib.sha256(
        raw_context.encode("utf-8", errors="replace")
    ).hexdigest()
    prompt_sha256 = hashlib.sha256(
        prompt_context.encode("utf-8", errors="replace")
    ).hexdigest()
    if mode == "hash_only":
        return {
            "text": None,
            "sha256": raw_sha256,
            "chars": len(raw_context),
            "stored_chars": 0,
            "redacted": None,
            "truncated": False,
            "prompt_sha256": prompt_sha256,
            "prompt_chars": len(prompt_context),
            "prompt_truncated": prompt_context_truncated,
            "max_retained_chars": _MAX_META_PROMPT_RETAINED_EVIDENCE_CHARS,
            "retention_mode": mode,
            "retention_policy": "hash_only_with_raw_sha256",
        }
    if mode == "full":
        redacted = redact_sensitive_text(raw_context)
        text, metadata_truncated = _bounded_meta_prompt_retained_evidence(redacted)
        return {
            "text": text,
            "sha256": raw_sha256,
            "chars": len(raw_context),
            "stored_chars": len(text),
            "redacted": redacted != raw_context,
            "truncated": metadata_truncated,
            "prompt_sha256": prompt_sha256,
            "prompt_chars": len(prompt_context),
            "prompt_truncated": prompt_context_truncated,
            "max_retained_chars": _MAX_META_PROMPT_RETAINED_EVIDENCE_CHARS,
            "retention_mode": mode,
            "retention_policy": (
                "full_secret_redacted_text_with_metadata_cap_and_raw_sha256"
            ),
        }
    text, metadata_truncated = _bounded_meta_prompt_retained_evidence(prompt_context)
    return {
        "text": text,
        "sha256": raw_sha256,
        "chars": len(raw_context),
        "stored_chars": len(text),
        "redacted": prompt_context != raw_context,
        "truncated": prompt_context_truncated or metadata_truncated,
        "prompt_sha256": prompt_sha256,
        "prompt_chars": len(prompt_context),
        "prompt_truncated": prompt_context_truncated,
        "max_retained_chars": _MAX_META_PROMPT_RETAINED_EVIDENCE_CHARS,
        "retention_mode": mode,
        "retention_policy": (
            "redact_then_prompt_and_metadata_truncate_with_raw_sha256"
        ),
    }


def _bounded_meta_prompt_retained_evidence(text: str) -> tuple[str, bool]:
    if len(text) <= _MAX_META_PROMPT_RETAINED_EVIDENCE_CHARS:
        return text, False
    suffix = "...<truncated>"
    keep = max(0, _MAX_META_PROMPT_RETAINED_EVIDENCE_CHARS - len(suffix))
    return text[:keep] + suffix, True


def _meta_prompt_template_preview(template: str) -> tuple[str, dict]:
    redacted = redact_sensitive_text(template)
    truncated = len(redacted) > _MAX_META_PROMPT_TEMPLATE_CHARS
    if truncated:
        suffix = "...<truncated>"
        redacted = (
            redacted[: _MAX_META_PROMPT_TEMPLATE_CHARS - len(suffix)] + suffix
        )
    return redacted, {
        "sha256": hashlib.sha256(template.encode("utf-8")).hexdigest(),
        "raw_chars": len(template),
        "prompt_chars": len(redacted),
        "redacted": redacted != template,
        "truncated": truncated,
        "limit_chars": _MAX_META_PROMPT_TEMPLATE_CHARS,
    }


def _prompt_program_evidence(prompt_program, *, selected: bool) -> dict:
    metadata = prompt_program.metadata if isinstance(prompt_program.metadata, dict) else {}
    context_policy = (
        prompt_program.context_policy
        if isinstance(getattr(prompt_program, "context_policy", None), dict)
        else {}
    )
    policy = validate_prompt_context_policy(context_policy)
    evidence = {
        "id": prompt_program.id,
        "selected": selected,
        "generation": prompt_program.generation,
        "uses": prompt_program.uses,
        "reward_sum": _finite_json_number(prompt_program.reward_sum),
        "mean_reward": _finite_json_number(prompt_program.mean_reward),
        "template_sha256": hashlib.sha256(prompt_program.template.encode("utf-8")).hexdigest(),
        "template_chars": len(prompt_program.template),
        "context_policy_sha256": prompt_context_policy_sha256(policy),
        "context_policy_preview": _prompt_context_policy_preview(policy),
    }
    for key in (
        "last_prompt_reward",
        "last_prompt_penalty",
        "last_generation",
        "last_program_id",
        "last_candidate_score",
        "last_parent_score",
    ):
        if key in metadata:
            evidence[key] = _meta_prompt_safe_value(metadata[key])
    rejected = metadata.get("rejected_prompt_mutations")
    if isinstance(rejected, list) and rejected:
        evidence["recent_rejections"] = _meta_prompt_safe_value(rejected[-3:])
    return evidence


def _prompt_context_policy_preview(context_policy: dict) -> dict:
    policy = validate_prompt_context_policy(context_policy)
    default_policy = validate_prompt_context_policy({})
    non_default_policy = {
        key: value
        for key, value in policy.items()
        if value != default_policy.get(key)
    }
    return {
        "schema": "libreevolve.meta_prompt_context_policy_preview.v1",
        "sha256": prompt_context_policy_sha256(policy),
        "field_count": len(policy),
        "non_default_fields": sorted(non_default_policy),
        "non_default_policy": _meta_prompt_safe_value(non_default_policy),
    }


def _candidate_evidence(program: Program, parent: Program, prompt_reward: float) -> dict:
    evaluation = program.evaluation if isinstance(program.evaluation, dict) else {}
    composition = program.metadata.get("score_composition") if isinstance(program.metadata, dict) else None
    evidence = {
        "program_id": program.id,
        "parent_id": parent.id,
        "generation": program.generation,
        "candidate_score": _finite_json_number(program.fitness),
        "parent_score": _finite_json_number(parent.fitness),
        "prompt_reward": _finite_json_number(prompt_reward),
        "improvement": _finite_json_number(program.fitness - parent.fitness),
        "is_valid": evaluation.get("is_valid"),
        "error": _bounded_meta_prompt_text(evaluation.get("error")),
        "metrics": _meta_prompt_metrics(program.metrics),
    }
    if isinstance(composition, dict):
        evidence["score_composition"] = _meta_prompt_safe_value(composition)
    return evidence


def _failure_evidence(failure: dict) -> dict:
    keys = (
        "program_id",
        "parent_id",
        "generation",
        "score",
        "is_valid",
        "error",
        "diff_error",
        "admission_reason",
        "repetition_count",
    )
    evidence = {
        key: _meta_prompt_safe_value(failure[key])
        for key in keys
        if key in failure
    }
    if "mutation_text" in failure:
        evidence["mutation_text"] = _bounded_meta_prompt_text(failure.get("mutation_text"))
    return evidence


def _meta_prompt_metrics(metrics: dict) -> dict:
    safe: dict[str, object] = {}
    for key, value in sorted(metrics.items(), key=lambda item: str(item[0])):
        if len(safe) >= 10:
            break
        safe_key = _meta_prompt_safe_key(key)
        if safe_key in safe:
            safe_key = _meta_prompt_key_with_hash(str(key), str(key))
        safe[safe_key] = _meta_prompt_safe_value(value)
    return safe


def _meta_prompt_safe_value(value: object) -> object:
    if isinstance(value, dict):
        safe: dict[str, object] = {}
        for key, item in list(value.items())[:20]:
            safe_key = _meta_prompt_safe_key(key)
            if safe_key in safe:
                safe_key = _meta_prompt_key_with_hash(str(key), str(key))
            safe[safe_key] = _meta_prompt_safe_value(item)
        return safe
    if isinstance(value, list):
        return [_meta_prompt_safe_value(item) for item in value[:20]]
    if isinstance(value, tuple):
        return [_meta_prompt_safe_value(item) for item in value[:20]]
    if isinstance(value, str):
        return _bounded_meta_prompt_text(value)
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return _finite_json_number(value)
    return _bounded_meta_prompt_text(repr(value))


def _meta_prompt_safe_key(key: object) -> str:
    raw = str(key)
    redacted = redact_sensitive_text(raw)
    bounded = _bounded_meta_prompt_key(redacted)
    if bounded != raw:
        return _meta_prompt_key_with_hash(bounded, raw)
    return bounded


def _bounded_meta_prompt_key(key: str) -> str:
    if len(key) <= _MAX_META_PROMPT_KEY_CHARS:
        return key
    suffix = "...<truncated>"
    return key[: _MAX_META_PROMPT_KEY_CHARS - len(suffix)] + suffix


def _meta_prompt_key_with_hash(label: str, hash_source: str) -> str:
    digest = hashlib.sha256(hash_source.encode("utf-8")).hexdigest()[:12]
    suffix = f"#sha256:{digest}"
    base_limit = max(1, _MAX_META_PROMPT_KEY_CHARS - len(suffix))
    base = label if len(label) <= base_limit else label[:base_limit]
    return base + suffix


def _finite_json_number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    numeric = float(value)
    if not math.isfinite(numeric):
        return None
    return numeric


def _bounded_meta_prompt_text(value: object) -> str | None:
    if value is None:
        return None
    text = redact_sensitive_text(str(value))
    if len(text) > _MAX_META_PROMPT_TEXT_FIELD_CHARS:
        return text[: _MAX_META_PROMPT_TEXT_FIELD_CHARS - 15] + "...<truncated>"
    return text


def _program_llm_calls(
    call_span: list[dict],
    mutation_call: dict | None,
    critique_metadata: dict | None,
    result,
) -> list[dict]:
    if call_span:
        return [dict(call) for call in call_span]
    calls = []
    seen_call_keys = set()

    def append_call(call: object) -> None:
        if not isinstance(call, dict):
            return
        key = call.get("id") if isinstance(call.get("id"), str) else json.dumps(
            call,
            sort_keys=True,
            default=str,
        )
        if key in seen_call_keys:
            return
        seen_call_keys.add(key)
        calls.append(dict(call))

    append_call(mutation_call)
    if critique_metadata and isinstance(critique_metadata.get("llm_call"), dict):
        append_call(critique_metadata["llm_call"])
    if critique_metadata and isinstance(critique_metadata.get("reviewer_pool"), dict):
        reviewers = critique_metadata["reviewer_pool"].get("reviewers")
        if isinstance(reviewers, list):
            for reviewer in reviewers:
                if isinstance(reviewer, dict) and isinstance(
                    reviewer.get("llm_call"), dict
                ):
                    append_call(reviewer["llm_call"])
    feedback_records = result.metadata.get("llm_feedback", []) if result.metadata else []
    if isinstance(feedback_records, list):
        for record in feedback_records:
            if isinstance(record, dict) and isinstance(record.get("llm_call"), dict):
                append_call(record["llm_call"])
    return calls


def _run_critique_reviewers(
    *,
    llm,
    budget: RunBudget,
    workspace: CandidateWorkspace,
    base_prompt: str,
    original_diff: str,
    original_proposal_metadata: dict,
    config: Config,
    capture_proposal_metadata: bool | None = None,
    budget_event_sink: Callable[[dict], dict] | None = None,
) -> tuple[str, dict, dict]:
    if capture_proposal_metadata is None:
        capture_proposal_metadata = config.capture_proposal_metadata
    reviewers = _critique_reviewer_specs(config)
    records: list[dict] = []
    valid_records: list[dict] = []
    for index, reviewer in enumerate(reviewers):
        reviewer_prompt = build_critique_prompt(
            base_prompt,
            original_diff,
            critique_prompt=reviewer["prompt"] or None,
        )
        role = reviewer["role"]
        budget_reason = budget.check_before_llm_call(role=role)
        if budget_reason is not None:
            skipped = _skipped_llm_budget_record(
                role=role,
                stop_reason=budget.stop_reason,
                budget=budget,
            )
            status = {
                "accepted_revision": False,
                "selected_diff": "original",
                "original_diff_error": None,
                "revised_diff_error": "critique_budget_skipped",
                "fallback_reason": "critique_budget_skipped_original_mutation",
                **skipped,
            }
            if capture_proposal_metadata:
                status = {
                    **status,
                    "proposal_source": "original",
                    "original_proposal": original_proposal_metadata,
                    "revised_proposal": {},
                }
            record = _critique_metadata_record(
                prompt=reviewer_prompt,
                original_diff=original_diff,
                revised_diff="",
                backend_idx=-1,
                llm_call=None,
                critique_status=status,
                retention_mode=config.critique_retention_mode,
            )
            record.update(_critique_reviewer_record_fields(index, reviewer))
            records.append(record)
            break
        try:
            revised_diff, backend_idx = _generate_with_budget(
                llm,
                budget,
                reviewer_prompt,
                role=role,
                budget_event_sink=budget_event_sink,
            )
        except Exception as exc:
            failure = _bounded_llm_failure_record("critique", exc, llm)
            status = {
                "accepted_revision": False,
                "selected_diff": "original",
                "original_diff_error": None,
                "revised_diff_error": "llm_critique_failed",
                "fallback_reason": "critique_provider_failure_original_mutation",
                **failure,
                "reviewer_role": role,
            }
            if capture_proposal_metadata:
                status = {
                    **status,
                    "proposal_source": "original",
                    "original_proposal": original_proposal_metadata,
                    "revised_proposal": {},
                }
            record = _critique_metadata_record(
                prompt=reviewer_prompt,
                original_diff=original_diff,
                revised_diff="",
                backend_idx=-1,
                llm_call=failure.get("llm_call"),
                critique_status=status,
                retention_mode=config.critique_retention_mode,
            )
            record.update(_critique_reviewer_record_fields(index, reviewer))
            records.append(record)
            continue

        llm_call = _last_llm_call(llm)
        revised_proposal_metadata = (
            extract_proposal_metadata(revised_diff)
            if capture_proposal_metadata and isinstance(revised_diff, str)
            else {}
        )
        selected_diff, status = _select_critique_mutation(
            workspace,
            original_diff,
            revised_diff,
            config.mutation_mode,
        )
        if capture_proposal_metadata:
            proposal_source = status.get("selected_diff")
            status = {
                **status,
                "proposal_source": proposal_source,
                "original_proposal": original_proposal_metadata,
                "revised_proposal": revised_proposal_metadata,
            }
        record = _critique_metadata_record(
            prompt=reviewer_prompt,
            original_diff=original_diff,
            revised_diff=revised_diff,
            backend_idx=backend_idx,
            llm_call=llm_call,
            critique_status=status,
            retention_mode=config.critique_retention_mode,
        )
        record.update(_critique_reviewer_record_fields(index, reviewer))
        record["selected_candidate_diff"] = selected_diff
        records.append(record)
        if status["accepted_revision"]:
            valid_records.append(record)

    selected = _select_critique_reviewer_record(
        records,
        valid_records,
        policy=config.critique_aggregation_policy,
    )
    selected_diff = (
        selected.get("selected_candidate_diff")
        if isinstance(selected.get("selected_candidate_diff"), str)
        else original_diff
    )
    selected_revised_proposal = (
        selected.get("revised_proposal")
        if isinstance(selected.get("revised_proposal"), dict)
        and selected.get("selected_diff") == "revised"
        else {}
    )
    metadata = dict(selected)
    metadata.pop("selected_candidate_diff", None)
    metadata["reviewer_pool"] = {
        "schema": "libreevolve.critique_reviewer_pool.v1",
        "enabled": len(reviewers) > 1 or bool(config.critique_reviewers),
        "aggregation_policy": config.critique_aggregation_policy,
        "reviewer_count": len(reviewers),
        "completed_review_count": len(records),
        "valid_revision_count": len(valid_records),
        "selected_reviewer": selected.get("reviewer_name"),
        "selected_reviewer_role": selected.get("reviewer_role"),
        "reviewers": [
            {key: value for key, value in record.items() if key != "selected_candidate_diff"}
            for record in records
        ],
    }
    return selected_diff, metadata, selected_revised_proposal


def _critique_reviewer_specs(config: Config) -> list[dict]:
    if config.critique_reviewers:
        return [
            {
                "name": reviewer["name"],
                "prompt": reviewer["prompt"] or config.critique_prompt,
                "role": reviewer["role"],
            }
            for reviewer in config.critique_reviewers
        ]
    return [
        {
            "name": "default",
            "prompt": config.critique_prompt,
            "role": "critique",
        }
    ]


def _critique_reviewer_record_fields(index: int, reviewer: Mapping[str, object]) -> dict:
    return {
        "reviewer_index": index,
        "reviewer_name": reviewer["name"],
        "reviewer_role": reviewer["role"],
    }


def _select_critique_reviewer_record(
    records: list[dict],
    valid_records: list[dict],
    *,
    policy: str,
) -> dict:
    if valid_records:
        if policy == "last_valid":
            return valid_records[-1]
        return valid_records[0]
    if records:
        return records[-1]
    return {
        "status": "skipped",
        "accepted_revision": False,
        "selected_diff": "original",
        "original_diff_error": None,
        "revised_diff_error": "no_critique_reviewers_completed",
        "fallback_reason": "no_critique_reviewers_completed_original_mutation",
        "backend_idx": -1,
        "llm_call": None,
        "reviewer_index": None,
        "reviewer_name": None,
        "reviewer_role": None,
    }


def _select_critique_mutation(
    workspace: CandidateWorkspace,
    original_diff: str,
    revised_diff: object,
    mutation_mode: str,
) -> tuple[str, dict]:
    """Validate critique revisions before replacing the original mutation."""

    _, revised_error = apply_workspace_mutation(
        workspace, revised_diff, mutation_mode=mutation_mode
    )
    status = {
        "selected_diff": "revised",
        "accepted_revision": revised_error is None,
        "revised_diff_error": revised_error,
        "original_diff_error": None,
        "fallback_reason": None,
    }
    if revised_error is None:
        return revised_diff, status

    _, original_error = apply_workspace_mutation(
        workspace, original_diff, mutation_mode=mutation_mode
    )
    status["original_diff_error"] = original_error
    if original_error is None:
        status["selected_diff"] = "original"
        status["fallback_reason"] = "invalid_revised_diff"
        return original_diff, status
    status["selected_diff"] = "original"
    status["fallback_reason"] = "no_valid_mutation"
    return original_diff, status


def _evaluation_is_valid(program: Program) -> bool:
    return program.evaluation.get("is_valid") is True


def _backend_reward(program: Program, parent: Program, backend_idx: int) -> dict:
    admission = (
        program.metadata.get("archive_admission")
        if isinstance(program.metadata.get("archive_admission"), dict)
        else {}
    )
    eligible = (
        admission.get("admitted") is True
        and program.evaluation.get("is_valid") is True
        and math.isfinite(program.fitness)
        and math.isfinite(parent.fitness)
    )
    raw_improvement = (
        program.fitness - parent.fitness
        if math.isfinite(program.fitness) and math.isfinite(parent.fitness)
        else None
    )
    reward = max(0.0, raw_improvement) if eligible and raw_improvement is not None else 0.0
    reason = "admitted_valid_improvement" if eligible else str(
        admission.get("reason") or program.evaluation.get("error") or "not_admitted"
    )
    return {
        "backend_idx": backend_idx,
        "policy": "admitted_valid_nonnegative_improvement",
        "eligible": eligible,
        "reward": reward,
        "raw_improvement": raw_improvement,
        "reason": reason,
    }


def _prompt_reward(score: float, parent_score: float, mode: str) -> float:
    if mode == "improvement":
        return score - parent_score
    return score
