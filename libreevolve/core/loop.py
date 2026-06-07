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
    validate_controller_budget_state,
    validate_restored_budget_snapshot,
)
from libreevolve.core.config import Config
from libreevolve.core.candidate import (
    CandidateWorkspace,
    apply_workspace_mutation,
    validate_evolve_blocks,
    validate_candidate_workspace_limits,
)
from libreevolve.core.database import (
    ProgramDatabase,
    archive_event_replay_audit,
    load_archive_restore_bundle,
    validate_archive_event_replay_audit,
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
    LLM_BUDGET_REPORT_SCHEMA,
    validate_llm_budget_report,
)
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
_META_PROMPT_CONTEXT_POLICY_CAPABILITIES = {
    "schema": "libreevolve.meta_prompt_context_policy_capabilities.v1",
    "channel_controls": (
        "disabled_sections,section_priorities,mutation_instruction_variant,"
        "mutation_instruction_include_example,proposal_metadata_enabled,"
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
            "policy": "runtime_observed_usage_not_budget_enforced",
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
            "policy": "runtime_observed_usage_not_budget_enforced",
            "paper_budget_ready": False,
            "reason": "no_llm_role_accounting_records",
        }

    adapter_attempts_by_role = _runtime_llm_budget_adapter_attempts_by_role(llm)
    report = {
        "schema": LLM_BUDGET_REPORT_SCHEMA,
        "status": "audit_snapshot",
        "policy": "runtime_observed_usage_not_budget_enforced",
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
    return {
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
        "unsupported_surfaces": [
            "provider_outputs",
            "controller_pending_work",
            "plugin_internal_state",
            "validator_subprocess_state",
            "ordered_migration_event_replay",
        ],
    }


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
    snapshot = validate_restored_budget_snapshot(
        controller_budget_state["snapshot"],
    )
    budget = _budget_for_controller_event_replay(snapshot)
    events = controller_budget_state["events"]
    if not isinstance(events, list):  # pragma: no cover - validated by caller.
        raise BudgetSnapshotError("controller budget replay events must be a list")
    for event in events:
        apply_controller_budget_event(budget, event)
    replayed_snapshot = budget.snapshot()
    _validate_controller_budget_replay_matches_snapshot(
        replayed_snapshot,
        snapshot,
    )
    return snapshot


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


def _budget_for_controller_event_replay(snapshot: Mapping[str, object]) -> RunBudget:
    limits = snapshot["limits"]
    wall_clock = snapshot["wall_clock"]
    if not isinstance(limits, Mapping) or not isinstance(wall_clock, Mapping):
        raise BudgetSnapshotError("controller budget replay snapshot is malformed")
    started_at_utc = wall_clock["started_at"]
    if not isinstance(started_at_utc, str):
        raise BudgetSnapshotError("controller budget replay started_at is malformed")
    return RunBudget(
        max_generations=limits["max_generations"],
        max_evaluations=limits["max_evaluations"],
        max_evaluator_seconds=limits["max_evaluator_seconds"],
        max_runtime_seconds=limits["max_runtime_seconds"],
        started_at=0.0,
        started_at_utc=started_at_utc,
        max_evaluator_subprocess_attempts=limits["max_evaluator_subprocess_attempts"],
        max_evaluator_stage_samples=limits["max_evaluator_stage_samples"],
        max_evaluator_retry_attempts=limits["max_evaluator_retry_attempts"],
        max_evaluator_timeouts=limits["max_evaluator_timeouts"],
        max_evaluator_sample_budget_exhaustions=limits[
            "max_evaluator_sample_budget_exhaustions"
        ],
        max_evaluator_stage_budget_exhaustions=limits[
            "max_evaluator_stage_budget_exhaustions"
        ],
        max_llm_calls=limits["max_llm_calls"],
        max_llm_provider_attempts=limits["max_llm_provider_attempts"],
        max_llm_tokens=limits["max_llm_tokens"],
        max_llm_cost_microusd=limits["max_llm_cost_microusd"],
        max_llm_seconds=limits["max_llm_seconds"],
        llm_role_provider_attempt_limits=dict(
            limits["llm_role_provider_attempt_limits"],
        ),
        llm_role_token_limits=dict(limits["llm_role_token_limits"]),
        llm_role_cost_microusd_limits=dict(
            limits["llm_role_cost_microusd_limits"],
        ),
        llm_role_seconds_limits=dict(limits["llm_role_seconds_limits"]),
    )


def _validate_controller_budget_replay_matches_snapshot(
    replayed_snapshot: Mapping[str, object],
    snapshot: Mapping[str, object],
) -> None:
    if replayed_snapshot["limits"] != snapshot["limits"]:
        raise BudgetSnapshotError(
            "controller budget replay limits do not match manifest budget snapshot"
        )
    if replayed_snapshot["stop_reason"] != snapshot["stop_reason"]:
        raise BudgetSnapshotError(
            "controller budget replay stop_reason does not match manifest budget snapshot"
        )
    replayed_consumed = dict(replayed_snapshot["consumed"])
    snapshot_consumed = dict(snapshot["consumed"])
    replayed_consumed.pop("runtime_seconds", None)
    snapshot_consumed.pop("runtime_seconds", None)
    if replayed_consumed != snapshot_consumed:
        raise BudgetSnapshotError(
            "controller budget replay consumption does not match manifest budget snapshot"
        )


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
    programs_logged = len(db.all_programs())
    archive_state = db.archive_state_snapshot()
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


def _runtime_controller_state(run_dir: Path, budget: RunBudget) -> dict:
    event_stream = _controller_budget_event_stream_summary(
        run_dir / "controller_budget_events.jsonl"
    )
    return {
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


def _retrieval_manifest_summary(programs: list[Program]) -> dict:
    events: dict[tuple, dict] = {}
    by_plugin: dict[str, dict] = {}
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
                key = (
                    plugin_name,
                    event.get("query"),
                    event.get("timestamp"),
                    event.get("status"),
                    event.get("synthesis_sha256"),
                    event.get("error"),
                )
                if key in events:
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
                events[key] = summary
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
        "context_policy_capabilities": copy.deepcopy(
            _META_PROMPT_CONTEXT_POLICY_CAPABILITIES
        ),
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
