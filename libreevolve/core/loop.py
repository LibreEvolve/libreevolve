"""Core evolution loop: prompt construction, LLM-driven mutation, evaluation.

The engineering preview executes bounded proposals and evaluations serially.
"""
from __future__ import annotations
from collections.abc import Callable, Mapping
import copy
import hashlib
import json
import math
import random
import stat as stat_module
import unicodedata
from pathlib import Path

from libreevolve.core.artifact_schema import EVALUATOR_RESULT_RECORD_SCHEMA, RUN_ARTIFACT_NAMES, run_artifact_schema, validate_non_jsonl_artifact_policy_manifest, validate_quarantine_artifact_policy_manifest, validate_run_artifact_bundle_report, versioned_record
from libreevolve.core.best_artifacts import (
    attach_best_artifact_export,
    export_best_artifacts,
)
from libreevolve.core.budget import RunBudget
from libreevolve.core.config import Config, MAX_ADAPTIVE_MUTATION_FAILURE_SWITCH_COUNT
from libreevolve.core.candidate import CandidateWorkspace, apply_workspace_mutation, validate_evolve_blocks, validate_candidate_workspace_limits
from libreevolve.core.database import ProgramDatabase, validate_seed_source_record
from libreevolve.core.diff import extract_explanatory_preamble, extract_proposal_metadata, strip_proposal_metadata, validate_proposal_metadata_preamble
from libreevolve.core.evaluator import (
    CascadeEvaluator,
    EvaluationResult,
    evaluation_accounting,
    preflight_evaluator_contracts,
)
from libreevolve.core.jsonl import iter_strict_jsonl_objects, strict_json_dumps
from libreevolve.core.loop_models import _PreparedCandidate
from libreevolve.core.meta_prompt import PromptDatabase
from libreevolve.core.prompt import PromptSampler, validate_direct_context_files, validate_direct_task_description, validate_prompt_context_policy
from libreevolve.core.provenance import git_state, problem_provenance, runtime_environment_provenance, source_provenance
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.llm.ensemble import (
    LLM_PROVIDER_DIAGNOSTICS_SCHEMA,
    LLMEnsemble,
    build_llm,
    validate_scheduler_state_snapshot,
)
from libreevolve.llm.cancellation_policy import (
    PROVIDER_CANCELLATION_POLICY_SCHEMA,
    PROVIDER_CANCELLATION_RUNTIME_READINESS_SCHEMA,
    validate_provider_cancellation_policy,
)
from libreevolve.llm.budget_report import (
    LLM_BUDGET_REPORT_POLICY,
    LLM_BUDGET_REPORT_SCHEMA,
    LLM_BUDGET_REPORT_STATUS,
    validate_llm_budget_report,
)
from libreevolve.llm.tokenization import discover_prompt_token_counter
from libreevolve.population.program import Program
from libreevolve.problems.loader import Problem

VALID_THRESHOLD = 0.0
CONTROLLER_STATE_VALIDATION_SCHEMA = "libreevolve.controller_state_validation.v1"
_MAX_ABORT_MESSAGE_CHARS = 2048
_MAX_ARTIFACT_ERROR_CHARS = 500


_MAX_DIRECT_INLINE_SEED_CHARS = 1_000_000
_PROMPT_EXECUTION_OUTPUT_FIELDS = ("stdout", "stderr", "error")
_PROMPT_EXECUTION_OUTPUT_DEFAULT_FIELD_CHARS = 400
_PROMPT_STAGE_SUMMARY_MAX_ITEMS = 3
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
        "surface": "validator_subprocess_randomness",
        "restored_by_runtime_rng": False,
        "boundary": "stage_rng_seeds_are_recorded_per_evaluation",
    },
]


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


def _initial_run_rng(config: Config):
    return random.Random(config.seed), _RNG_RESUME_STATUS_LEGACY_NOT_WIRED


def _initial_run_budget(config: Config):
    return RunBudget.from_config(config)


def _attach_llm_call_logger(llm: object, db: ProgramDatabase) -> None:
    setter = getattr(llm, "set_call_record_sink", None)
    if callable(setter):
        setter(db.log_llm_call)


def _retained_abort_text(value: object, *, max_chars: int, mode: str = "redacted") -> dict:
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
    message = _retained_abort_text(exc, max_chars=_MAX_ABORT_MESSAGE_CHARS)
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


def evolve(
    problem: Problem,
    config: Config,
) -> "Program | None":
    config.validate()
    run_dir = (Path(config.log_dir) / config.problem_name).resolve(strict=False)
    _validate_problem_for_evolve(problem, config)
    run_rng, rng_resume_status = _initial_run_rng(config)
    budget = _initial_run_budget(config)
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
        "environment": runtime_environment_provenance(),
    }
    dotenv_source = _problem_dotenv_source(problem)
    if dotenv_source is not None:
        run_provenance["dotenv"] = dotenv_source
    llm_scheduler_resume_status = _LLM_SCHEDULER_RESUME_STATUS_LEGACY_NOT_WIRED
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
        evaluation_cache_contract_sha256 = _evaluation_cache_contract_sha256(
            problem,
            config,
            evaluator_sources,
        )
        evaluation_cache: dict[str, dict] = {}
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
        _MAX_FAILURES = MAX_ADAPTIVE_MUTATION_FAILURE_SWITCH_COUNT
        strict_seed_invalid_count = 0

        # Seed population (diff_error=None bypasses Tier 0)
        seed_entries = _seed_workspace_entries(problem)
        for seed_index, (seed_workspace, seed_source) in enumerate(seed_entries):
            phase = "seed_evaluation"
            if budget.check_before_evaluation():
                break
            seed_candidate_id = _deterministic_seed_candidate_id(
                seed_index,
                seed_workspace,
            )
            result = evaluator.evaluate(seed_workspace, diff_error=None)
            seed_cache_metadata = _store_evaluation_cache_result(
                evaluation_cache,
                seed_workspace,
                evaluation_cache_contract_sha256,
                result,
                source_program_id=seed_candidate_id,
                source_generation=0,
                source_candidate_type="seed",
            )
            result = _evaluation_result_with_cache_metadata(
                result,
                seed_cache_metadata,
            )
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
                id=seed_candidate_id,
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
                    "evaluation_cache": seed_cache_metadata,
                    "budget": budget.snapshot(),
                },
            )
            _annotate_metric_policy(program, problem)
            admission = db.admit(program, threshold=VALID_THRESHOLD)
            if not _seed_meets_strict_initial_program_contract(program, problem):
                strict_seed_invalid_count += 1
            if not admission.get("admitted"):
                failure = db.log_seed_failure(program, admission)
                recent_failures.append(failure)
                recent_failures = recent_failures[-_MAX_FAILURES:]
            db.log(program)

        proposal_count = config.proposals_per_generation
        if (
            config.initial_program_validity_policy == "alphaevolve_strict"
            and strict_seed_invalid_count > 0
        ):
            budget.stop_reason = "invalid_initial_programs"
        for proposal_loop_index in range(config.max_generations * proposal_count):
            if budget.stop_reason is not None:
                break
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
            mutation_mode, mutation_mode_selection = _select_mutation_mode(
                config,
                parent,
                recent_failures,
            )

            if proposal_index == 0:
                budget.record_generation_start()
                db.log_controller_budget_event({"kind": "generation_started"})
                phase = f"generation:{gen}:generation_start"

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
            phase = f"generation:{gen}:context"
            context = ""
            prompt = prompt_sampler.build(
                parent, inspirations, problem, context,
                recent_failures=recent_failures or None,
                template=prompt_program.template,
                mutation_mode=mutation_mode,
                capture_proposal_metadata=proposal_metadata_enabled,
                context_policy=prompt_program.context_policy,
            )
            prompt_sampler.last_metadata["prompt_token_counter_capability"] = dict(
                prompt_token_counter_capability
            )
            prompt_sampler.last_metadata["mutation_mode_selection"] = copy.deepcopy(
                mutation_mode_selection
            )
            metric_diverse_inspiration = _metric_diverse_inspiration_record(
                inspirations,
                inspiration_selection_metadata,
                prompt_sampler.last_metadata,
                db.objective_schema_snapshot(),
            )
            inspiration_selection_metadata["metric_diversity"] = (
                metric_diverse_inspiration
            )
            prompt_sampler.last_metadata["metric_diverse_inspiration"] = (
                metric_diverse_inspiration
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
                        "mutation_mode": mutation_mode,
                        "mutation_mode_selection": copy.deepcopy(
                            mutation_mode_selection
                        ),
                        "parent_selection": parent_selection_metadata,
                        "inspiration_selection": inspiration_selection_metadata,
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
            explanatory_preamble_metadata = extract_explanatory_preamble(diff)
            proposal_metadata = original_proposal_metadata
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
                (
                    child_workspace,
                    diff_error,
                    mutation_mode_selection,
                ) = _apply_selected_workspace_mutation(
                    parent.workspace(),
                    mutation_payload,
                    mutation_mode_selection,
                )
            _validate_workspace_size_for_config(child_workspace, config)
            candidate_id = _deterministic_generated_candidate_id(
                generation=candidate_generation,
                loop_generation_index=gen,
                proposal_index=proposal_index,
                parent_id=parent.id,
                prompt_program_id=prompt_program.id,
                mutation_text=diff,
                workspace=child_workspace,
            )
            retained_prompt = _retained_prompt_text(
                prompt,
                mode=config.mutation_prompt_retention_mode,
            )
            retained_prompt = _apply_explicit_context_retention_to_prompt(
                retained_prompt,
                context_text=prompt_sampler.last_context_text,
                mode=config.explicit_context_retention_mode,
            )
            prepared = _PreparedCandidate(
                submission_order=proposal_loop_index,
                loop_generation_index=gen,
                proposal_index=proposal_index,
                proposals_per_generation=proposal_count,
                candidate_generation=candidate_generation,
                parent=parent,
                child_workspace=child_workspace,
                diff_error=diff_error,
                candidate_id=candidate_id,
                retained_prompt=copy.deepcopy(retained_prompt),
                diff=diff,
                prompt_diagnostics=copy.deepcopy(prompt_sampler.last_metadata),
                proposal_metadata=copy.deepcopy(proposal_metadata),
                explanatory_preamble=copy.deepcopy(
                    explanatory_preamble_metadata
                ),
                backend_idx=backend_idx,
                parent_selection_metadata=copy.deepcopy(
                    parent_selection_metadata
                ),
                inspiration_selection_metadata=copy.deepcopy(
                    inspiration_selection_metadata
                ),
                prompt_program=copy.deepcopy(prompt_program),
                mutation_mode=str(mutation_mode_selection["effective_mode"]),
                mutation_mode_selection=copy.deepcopy(mutation_mode_selection),
                mutation_llm_call=copy.deepcopy(mutation_llm_call),
                proposal_llm_calls=copy.deepcopy(
                    _llm_call_span(llm, candidate_llm_call_start)
                ),
            )
            phase = f"generation:{gen}:candidate_evaluation"
            result = _evaluate_prepared_candidate_synchronously(
                prepared,
                evaluator=evaluator,
                evaluation_cache=evaluation_cache,
                evaluation_cache_contract_sha256=(
                    evaluation_cache_contract_sha256
                ),
                budget=budget,
                db=db,
            )
            evaluation_cache_metadata = result.metadata["evaluation_cache"]
            phase = f"generation:{gen}:llm_feedback"
            budget.check_before_evaluation()
            score = result.fitness

            # Preserve the complete candidate and evaluation before admission.
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
                                        "explanatory_preamble": explanatory_preamble_metadata,
                                        "backend_idx": backend_idx,
                                        "mutation_mode": prepared.mutation_mode,
                                        "mutation_mode_selection": copy.deepcopy(
                                            prepared.mutation_mode_selection
                                        ),
                                        "causal_reward_baseline": {
                                            "source": "parent_program",
                                            "parent_id": parent.id,
                                            "score": parent.fitness,
                                        },
                                        "parent_selection": parent_selection_metadata,
                                        "inspiration_selection": inspiration_selection_metadata,
                                        "prompt_program_id": prompt_program.id,
                                        "evaluation_cache": evaluation_cache_metadata,
                                        "llm_calls": _program_llm_calls(
                                            _llm_call_span(llm, candidate_llm_call_start),
                                            mutation_llm_call,
                                        ),
                                        "budget": budget.snapshot()},
                              metrics=result.metrics,
                              evaluation=result.to_dict())

            _annotate_metric_policy(program, problem)
            phase = f"generation:{gen}:evaluated"
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
            _record_mutation_backend_reward(
                prepared,
                backend_reward["reward"],
                llm=llm,
                db=db,
            )
            program.metadata["llm_calls"] = _program_llm_calls(
                _llm_call_span(llm, candidate_llm_call_start),
                mutation_llm_call,
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
            if proposal_index == proposal_count - 1:
                phase = f"generation:{gen}:migration"
                db.maybe_migrate(candidate_generation)

                best = db.best()
                phase = f"generation:{gen}:generation_end"
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
            llm=llm,
            run_rng=run_rng,
            rng_resume_status=rng_resume_status,
            llm_scheduler_resume_status=llm_scheduler_resume_status,
        )
        return best
    except BaseException as exc:
        try:
            _write_aborted_runtime(
                db,
                config,
                budget,
                run_dir,
                phase,
                exc,
                llm=llm,
                run_rng=run_rng,
                rng_resume_status=rng_resume_status,
                llm_scheduler_resume_status=llm_scheduler_resume_status,
            )
        except BaseException as finalize_exc:
            _note_abort_finalization_failure(exc, finalize_exc)
        raise


def _select_mutation_mode(config: Config, parent: Program, recent_failures: list[dict]) -> tuple[str, dict]:
    return config.mutation_mode, {
        "schema": "libreevolve.mutation_mode_selection.v1",
        "configured_mode": config.mutation_mode,
        "selected_mode": config.mutation_mode,
        "effective_mode": config.mutation_mode,
        "selection_reason": "configured_run_wide_mode",
    }


def _apply_selected_workspace_mutation(
    workspace: CandidateWorkspace,
    mutation_payload: object,
    raw_selection: Mapping[str, object],
) -> tuple[CandidateWorkspace, str | None, dict]:
    selection = copy.deepcopy(dict(raw_selection))
    mode = selection.get("selected_mode")
    if mode not in {"diff", "full"}:
        raise RuntimeError("mutation-mode selection is missing a supported mode")
    child, error = apply_workspace_mutation(workspace, mutation_payload, mutation_mode=mode)
    return child, error, selection


def _record_mutation_backend_reward(prepared: _PreparedCandidate, reward: float, *, llm: LLMEnsemble, db: ProgramDatabase) -> None:
    llm.record_reward(prepared.backend_idx, reward, call_id=(prepared.mutation_llm_call.get("id") if prepared.mutation_llm_call else None))


def _evaluate_prepared_candidate_synchronously(
    prepared: _PreparedCandidate,
    *,
    evaluator: CascadeEvaluator,
    evaluation_cache: dict[str, dict],
    evaluation_cache_contract_sha256: str,
    budget: RunBudget,
    db: ProgramDatabase,
) -> EvaluationResult:
    cache_hit = _lookup_evaluation_cache_result(
        evaluation_cache,
        prepared.child_workspace,
        evaluation_cache_contract_sha256,
        diff_error=prepared.diff_error,
    )
    if cache_hit is not None:
        result = _evaluation_cache_hit_result(cache_hit)
        _log_candidate_evaluation_cache_hit(db, result)
        return result
    result = evaluator.evaluate(
        prepared.child_workspace,
        diff_error=prepared.diff_error,
    )
    result = _record_uncached_candidate_evaluation(
        prepared,
        result,
        evaluation_cache=evaluation_cache,
        evaluation_cache_contract_sha256=evaluation_cache_contract_sha256,
        budget=budget,
        db=db,
    )
    return result


def _record_uncached_candidate_evaluation(
    prepared: _PreparedCandidate,
    result: EvaluationResult,
    *,
    evaluation_cache: dict[str, dict],
    evaluation_cache_contract_sha256: str,
    budget: RunBudget,
    db: ProgramDatabase,
) -> EvaluationResult:
    if prepared.diff_error is None:
        evaluation_cache_metadata = _store_evaluation_cache_result(
            evaluation_cache,
            prepared.child_workspace,
            evaluation_cache_contract_sha256,
            result,
            source_program_id=prepared.candidate_id,
            source_generation=prepared.candidate_generation,
            source_candidate_type="generated",
        )
    else:
        evaluation_cache_metadata = _evaluation_cache_bypass_metadata(
            prepared.child_workspace,
            evaluation_cache_contract_sha256,
            reason="diff_error_present",
        )
    result = _evaluation_result_with_cache_metadata(
        result,
        evaluation_cache_metadata,
    )
    result_accounting = evaluation_accounting(result)
    budget.record_evaluation(
        result.elapsed_sec,
        seed=False,
        accounting=result_accounting,
    )
    event = {
        "kind": "candidate_evaluation",
        "elapsed_sec": result.elapsed_sec,
        "accounting": result_accounting,
    }
    db.log_controller_budget_event(event)
    return result


def _log_candidate_evaluation_cache_hit(
    db: ProgramDatabase,
    result: EvaluationResult,
) -> None:
    metadata = result.metadata.get("evaluation_cache")
    if not isinstance(metadata, Mapping):
        raise RuntimeError("evaluation cache-hit metadata is missing")
    event = {
        "kind": "candidate_evaluation_cache_hit",
        "cache_key_sha256": metadata["cache_key_sha256"],
        "workspace_sha256": metadata["workspace_sha256"],
        "source_program_id": metadata["source_program_id"],
    }
    db.log_controller_budget_event(event)


def _write_completed_runtime(
    db: ProgramDatabase,
    config: Config,
    budget: RunBudget,
    run_dir: Path,
    best: Program | None,
    *,
    llm: object | None = None,
    run_rng: random.Random,
    rng_resume_status: str,
    llm_scheduler_resume_status: str,
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
    runtime["history"] = _runtime_history_summary(
        db,
        run_dir,
        budget,
    )
    runtime["artifacts"] = _runtime_artifact_pointers(run_dir)
    runtime["run_artifact_bundle_report"] = _run_artifact_bundle_report(
        run_dir,
        runtime,
    )
    attach_best_artifact_export(runtime, best_export)
    _attach_runtime_summaries(
        runtime,
        db,
        config,
        llm=llm,
        llm_scheduler_resume_status=llm_scheduler_resume_status,
    )
    db.update_manifest_runtime(runtime)


def _write_aborted_runtime(
    db: ProgramDatabase,
    config: Config,
    budget: RunBudget,
    run_dir: Path,
    phase: str,
    exc: BaseException,
    *,
    llm: object | None = None,
    run_rng: random.Random,
    rng_resume_status: str,
    llm_scheduler_resume_status: str,
) -> None:
    budget.stop_reason = "aborted"
    abort = {
        "exception_type": exc.__class__.__name__,
        **_aborted_exception_manifest(exc),
        "phase": phase,
        "role": _phase_role(phase),
        "keyboard_interrupt": isinstance(exc, KeyboardInterrupt),
    }
    # Keep a minimal terminal record even if richer persistence diagnostics fail.
    runtime = {"status": "aborted", "stop_reason": "aborted", "abort": abort}
    try:
        runtime.update(budget.snapshot())
        runtime.update(status="aborted", stop_reason="aborted", abort=abort)
        _mark_runtime_wall_clock_status(runtime, "aborted")
        runtime["rng"] = _runtime_rng_state(
            run_rng, config.seed, resume_status=rng_resume_status,
        )
        db.log_controller_budget_event({"kind": "stop", "stop_reason": "aborted"})
    except BaseException as finalize_exc:
        _note_abort_finalization_failure(exc, finalize_exc)
    best_export = None
    try:
        best = db.best()
        if best is not None:
            best_export = export_best_artifacts(best, run_dir)
            if best_export.get("status") == "failed":
                _note_abort_finalization_failure(
                    exc,
                    RuntimeError(
                        "Best artifact export failed: "
                        f"{best_export.get('error_type')}: {best_export.get('error')}"
                    ),
                )
    except BaseException as finalize_exc:
        _note_abort_finalization_failure(exc, finalize_exc)
    try:
        runtime["history"] = _runtime_history_summary(
            db,
            run_dir,
            budget,
        )
        runtime["artifacts"] = _runtime_artifact_pointers(run_dir)
        runtime["run_artifact_bundle_report"] = _run_artifact_bundle_report(
            run_dir,
            runtime,
        )
        _attach_runtime_summaries(
            runtime,
            db,
            config,
            llm=llm,
            llm_scheduler_resume_status=llm_scheduler_resume_status,
        )
    except BaseException as finalize_exc:
        _note_abort_finalization_failure(exc, finalize_exc)
    try:
        runtime.update(status="aborted", stop_reason="aborted", abort=abort)
        attach_best_artifact_export(runtime, best_export)
        db.update_manifest_runtime(runtime)
    except BaseException as finalize_exc:
        _note_abort_finalization_failure(exc, finalize_exc)


def _note_abort_finalization_failure(exc: BaseException, failure: BaseException) -> None:
    try:
        message = _aborted_exception_manifest(failure)["message"]
        exc.add_note(
            "Failed to finalize aborted run: "
            f"{failure.__class__.__name__}: {message}"
        )
    except BaseException:
        # A broken exception formatter or add_note must not mask the original.
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


def _attach_runtime_summaries(
    runtime: dict,
    db: ProgramDatabase,
    config: Config,
    *,
    llm: object | None = None,
    llm_scheduler_resume_status: str = _LLM_SCHEDULER_RESUME_STATUS_RESTORE_SUPPORTED,
) -> None:
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
    runtime["provider_cancellation_policy"] = _runtime_provider_cancellation_policy(
        config,
        llm_scheduler,
    )


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
                "llm_role_scheduler_scope": config.llm_role_scheduler_scope,
            },
            "reward_accounting_policy": state.get(
                "reward_accounting_policy",
                {
                    "policy": "configured_reward_accounted_roles_v1",
                    "reward_accounted_roles": ["mutation"],
                },
            ),
            "role_scheduler_scope": state.get("role_scheduler_scope", "shared"),
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
        "role_scheduler_scope": state.get("role_scheduler_scope", "shared"),
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


def validate_controller_state_snapshot(controller_state: object) -> dict:
    """Validate the terminal serial controller state."""
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
    controller_status = controller_state.get("status")
    status_models = {
        "terminal_synchronous_controller_drained": "single_process_serial_loop",
    }
    if controller_status not in status_models:
        issues.append("controller_state_status_not_terminal_drained")
    controller_model = controller_state.get("controller_model")
    expected_controller_model = status_models.get(controller_status)
    if controller_model != expected_controller_model:
        issues.append("controller_model_status_mismatch")
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


def _runtime_provider_cancellation_policy(
    config: Config,
    llm_scheduler_record: Mapping[str, object] | None = None,
) -> dict:
    provider_timeout_rules = [
        _provider_timeout_policy_rule(role, config)
        for role in ("mutation",)
    ]
    ensemble_timeout_rules = [
        _ensemble_timeout_policy_rule(role, config)
        for role in ("mutation",)
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
            "roles": ["mutation"],
            "source": "loop_llm_generate_roles",
        },
        "runtime_readiness": {
            "schema": PROVIDER_CANCELLATION_RUNTIME_READINESS_SCHEMA,
            "live_provider_sdk_cancellation": False,
            "timeout_driven_stop_enforcement": False,
            "cross_run_provider_quarantine_resume": False,
            "remaining_gap": [
                "live_provider_sdk_cancellation",
                "timeout_driven_stop_enforcement",
                "cross_run_provider_quarantine_resume",
            ],
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
    }


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
    for name in sorted(RUN_ARTIFACT_NAMES):
        if name == "manifest.json":
            artifacts[name] = _manifest_artifact_pointer(run_dir / name, name)
        else:
            path = run_dir / name
            artifacts[name] = _runtime_artifact_pointer(path, name, resolved_run_dir)
    return artifacts


def _run_artifact_bundle_report(run_dir: Path, runtime: Mapping[str, object]) -> dict:
    artifact_schema = run_artifact_schema()
    artifacts = runtime.get("artifacts")
    if not isinstance(artifacts, Mapping):
        artifacts = {}
    manifest_view = {
        "artifact_schema": artifact_schema,
        "runtime": {
            "artifacts": artifacts,
            "history": runtime.get("history") if isinstance(runtime.get("history"), Mapping) else {},
        },
    }
    accepted_streams = [
        name
        for name in sorted(artifact_schema["jsonl_records"])
        if isinstance(artifacts.get(name), Mapping)
        and artifacts[name].get("present") is True
    ]
    quarantine_validation = validate_quarantine_artifact_policy_manifest(
        {"artifact_schema": artifact_schema},
        run_dir=run_dir,
    )
    non_jsonl_validation = validate_non_jsonl_artifact_policy_manifest(manifest_view)
    issue_codes = []
    for validation in (quarantine_validation, non_jsonl_validation):
        if not isinstance(validation, Mapping):
            continue
        for issue in validation.get("issues", []):
            if isinstance(issue, Mapping) and isinstance(issue.get("code"), str):
                issue_codes.append(issue["code"])
    report = {
        "schema": "libreevolve.run_artifact_bundle_report.v1",
        "source": "runtime_artifact_schema_pointers_and_quarantine_diagnostics",
        "accepted_stream_count": len(accepted_streams),
        "accepted_streams": accepted_streams,
        "quarantine_stream_count": quarantine_validation["checked_stream_count"],
        "quarantine_record_count": quarantine_validation["record_count"],
        "quarantine_streams": quarantine_validation["present_streams"],
        "quarantine_validation_ok": quarantine_validation["ok"],
        "non_jsonl_checked_artifact_count": non_jsonl_validation[
            "checked_artifact_count"
        ],
        "non_jsonl_validation_ok": non_jsonl_validation["ok"],
        "issue_codes": sorted(set(issue_codes)),
        "accepted_state_boundary": {
            "quarantine_rows_are_diagnostics": True,
            "quarantine_rows_replayed_as_state": False,
            "non_jsonl_artifacts_are_policy_checked": non_jsonl_validation["ok"],
            "provider_output_replay": False,
            "pending_controller_work_replay": False,
        },
        "claim_ready": False,
        "claim_readiness": {
            "accepted_streams_counted": True,
            "quarantine_diagnostics_validated": quarantine_validation["ok"],
            "non_jsonl_policy_validated": non_jsonl_validation["ok"],
            "persisted_manifest_report": True,
            "promotion_gate_validated": True,
            "full_restore_replay_certification": False,
            "remaining_gap": [
                "provider_output_replay_or_exclusion_in_resumed_trace",
                "pending_controller_work_replay",
                "restored_run_certification_model",
            ],
        },
    }
    validation = validate_run_artifact_bundle_report(report)
    report["promotion_gate"] = _run_artifact_bundle_promotion_gate(validation)
    report["validation"] = validate_run_artifact_bundle_report(report)
    return report


def _run_artifact_bundle_promotion_gate(validation: Mapping[str, object]) -> dict:
    issues = validation.get("issues")
    issue_codes = []
    if isinstance(issues, list):
        issue_codes = [
            issue["code"]
            for issue in issues
            if isinstance(issue, Mapping) and isinstance(issue.get("code"), str)
        ]
    ok = validation.get("ok") is True
    return {
        "schema": "libreevolve.run_artifact_bundle_promotion_gate.v1",
        "status": "passed" if ok else "failed",
        "validation_schema": validation.get("schema"),
        "validation_ok": ok,
        "issue_codes": issue_codes,
        "applied_at": "manifest_runtime_finalization",
        "accepted_state_only": True,
        "bundle_report_schema_validated": True,
        "provider_output_replay": False,
        "pending_controller_work_replay": False,
        "full_restore_replay_certification": False,
    }


def _manifest_artifact_pointer(path: Path, name: str) -> dict:
    record = {
        "path": name,
        "exists": path.exists(),
        "present": path.exists() or path.is_symlink(),
        "is_symlink": path.is_symlink(),
        "is_junction": _path_is_junction(path),
        "broken_link": False,
        "hash_scope": "final_manifest_self_reference_deferred",
    }
    if record["is_symlink"] or record["is_junction"]:
        record["kind"] = "link"
    elif path.is_file():
        record["kind"] = "file"
    elif path.is_dir():
        record["kind"] = "directory"
    else:
        record["kind"] = "missing"
    return record


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


def _runtime_history_summary(
    db: ProgramDatabase,
    run_dir: Path,
    budget: RunBudget,
) -> dict:
    history_exists = (run_dir / "history.jsonl").exists()
    programs = db.all_programs()
    summary = {
        "programs_logged": len(programs),
        "history_partially_written": history_exists,
        "no_candidates_evaluated": budget.evaluations == 0 and not programs,
        "failure_index": db.failure_index_snapshot(),
        "evaluator_result_export": _write_evaluator_results(run_dir, programs),
        "archive_state": db.archive_state_snapshot(),
        "controller_state": _runtime_controller_state(
            run_dir,
            budget,
        ),
    }
    if summary["no_candidates_evaluated"]:
        absence_reason = _no_candidate_absence_reason(budget)
        summary["candidate_absence_reason"] = absence_reason
        if not history_exists:
            summary["history_absent_reason"] = absence_reason
    return summary


def _seed_meets_strict_initial_program_contract(
    program: Program,
    problem: Problem,
) -> bool:
    metric_names = [
        metric.get("name")
        for metric in problem.metrics
        if isinstance(metric, Mapping) and isinstance(metric.get("name"), str)
    ]
    return (
        isinstance(program.evaluation, Mapping)
        and program.evaluation.get("is_valid") is True
        and all(name in program.metrics for name in metric_names)
    )


def _write_evaluator_results(run_dir: Path, programs: list[Program]) -> dict:
    path = run_dir / "evaluator_results.jsonl"
    records = [
        _evaluator_result_record(program, index)
        for index, program in enumerate(programs)
        if isinstance(program.evaluation, Mapping) and program.evaluation
    ]
    if not records:
        return {
            "schema": "libreevolve.evaluator_result_export.v1",
            "path": "evaluator_results.jsonl",
            "record_schema": EVALUATOR_RESULT_RECORD_SCHEMA,
            "record_count": 0,
            "exists": False,
            "sha256": None,
        }
    lines = [
        strict_json_dumps(versioned_record(EVALUATOR_RESULT_RECORD_SCHEMA, record))
        for record in records
    ]
    text = "\n".join(lines) + "\n"
    path.write_text(text, encoding="utf-8")
    return {
        "schema": "libreevolve.evaluator_result_export.v1",
        "path": "evaluator_results.jsonl",
        "record_schema": EVALUATOR_RESULT_RECORD_SCHEMA,
        "record_count": len(records),
        "exists": True,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "row_policy": "derived_from_final_program_evaluation_payloads",
    }


def _evaluator_result_record(program: Program, index: int) -> dict:
    evaluation = program.evaluation if isinstance(program.evaluation, Mapping) else {}
    metadata = evaluation.get("metadata") if isinstance(evaluation.get("metadata"), Mapping) else {}
    metrics = {
        str(name): _paper_metric_table_number(value)
        for name, value in sorted(program.metrics.items())
        if isinstance(name, str)
        and isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    }
    raw_id = f"{index}:{program.id}:{program.generation}:{_workspace_sha256(program.workspace())}"
    record = {
        "row_id": hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:24],
        "row_index": index,
        "candidate_id": program.id,
        "candidate_type": (
            program.metadata.get("candidate_type")
            if isinstance(program.metadata, Mapping)
            else None
        ),
        "generation": program.generation,
        "parent_id": program.parent_id,
        "is_valid": evaluation.get("is_valid"),
        "score": _finite_json_number(program.fitness),
        "metrics": metrics,
        "metric_names": sorted(metrics),
        "evaluator_mode": metadata.get("evaluator_mode"),
        "configured_stage_count": len(metadata.get("configured_stage_results", []))
        if isinstance(metadata.get("configured_stage_results"), list)
        else 0,
        "llm_feedback_count": len(metadata.get("llm_feedback", []))
        if isinstance(metadata.get("llm_feedback"), list)
        else 0,
        "execution_output": _evaluator_result_execution_output_record(evaluation),
        "stage_summary_io": _evaluator_result_stage_summary_io_record(evaluation),
        "source_policy": "derived_from_program_evaluation_payload",
    }
    error = evaluation.get("error")
    if isinstance(error, str) and error:
        record["error"] = error[:240]
    return record


def _evaluator_result_execution_output_record(evaluation: Mapping[str, object]) -> dict:
    fields = {
        field: _prompt_execution_output_field_record(
            evaluation.get(field),
            field=field,
            selected=True,
            prompt_visible=True,
            field_cap_chars=_PROMPT_EXECUTION_OUTPUT_DEFAULT_FIELD_CHARS,
            omission_reason=None,
        )
        for field in _PROMPT_EXECUTION_OUTPUT_FIELDS
    }
    present_fields = [
        field
        for field, record in fields.items()
        if record["raw_present"]
    ]
    return {
        "schema": "libreevolve.evaluator_result_execution_output.v1",
        "source": "evaluation_stdout_stderr_error_fields",
        "field_policy": "redacted_bounded_prompt_preview_fields",
        "default_max_chars": _PROMPT_EXECUTION_OUTPUT_DEFAULT_FIELD_CHARS,
        "present_fields": present_fields,
        "field_records": fields,
    }


def _evaluator_result_stage_summary_io_record(evaluation: Mapping[str, object]) -> dict:
    stages = evaluation.get("stages")
    stage_records = []
    if isinstance(stages, list):
        for stage_index, stage in enumerate(stages[-_PROMPT_STAGE_SUMMARY_MAX_ITEMS:]):
            if not isinstance(stage, Mapping):
                continue
            fields = {
                field: _prompt_execution_output_field_record(
                    stage.get(field),
                    field=field,
                    selected=True,
                    prompt_visible=True,
                    field_cap_chars=_PROMPT_EXECUTION_OUTPUT_DEFAULT_FIELD_CHARS,
                    omission_reason=None,
                )
                for field in _PROMPT_EXECUTION_OUTPUT_FIELDS
            }
            present_fields = [
                field
                for field, record in fields.items()
                if record["raw_present"]
            ]
            stage_records.append(
                {
                    "stage_index": stage_index,
                    "stage_name": stage.get("name"),
                    "present_fields": present_fields,
                    "field_records": fields,
                }
            )
    return {
        "schema": "libreevolve.evaluator_result_stage_summary_io.v1",
        "source": "evaluation_stages_stdout_stderr_error_fields",
        "field_policy": "last_prompt_visible_stage_records_with_redacted_bounded_previews",
        "default_max_chars": _PROMPT_EXECUTION_OUTPUT_DEFAULT_FIELD_CHARS,
        "stage_record_count": len(stage_records),
        "stage_records": stage_records,
    }


def _paper_metric_table_number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    numeric = float(value)
    if not math.isfinite(numeric):
        return None
    return numeric


def _metric_diverse_inspiration_record(
    inspirations: list[Program],
    selection_metadata: Mapping[str, object],
    prompt_metadata: Mapping[str, object],
    objective_schema: Mapping[str, object],
) -> dict:
    policy = (
        prompt_metadata.get("inspiration_policy")
        if isinstance(prompt_metadata.get("inspiration_policy"), Mapping)
        else {}
    )
    rendered_count = policy.get("rendered_count")
    if isinstance(rendered_count, bool) or not isinstance(rendered_count, int):
        limit = policy.get("limit")
        if isinstance(limit, bool) or not isinstance(limit, int):
            visible = list(inspirations)
        elif limit <= 0:
            visible = []
        else:
            visible = list(inspirations)[:limit]
    else:
        visible = list(inspirations)[: max(0, rendered_count)]
    metric_order = _metric_diverse_declared_metric_order(objective_schema)
    target_metrics = _metric_diverse_target_metrics(selection_metadata)
    target_metrics_by_program: dict[str, list[str]] = {}
    for target in target_metrics:
        program_id = target["program_id"]
        metric = target["metric"]
        target_metrics_by_program.setdefault(program_id, [])
        if metric not in target_metrics_by_program[program_id]:
            target_metrics_by_program[program_id].append(metric)

    records: list[dict] = []
    for index, program in enumerate(visible):
        record = _metric_diverse_visible_inspiration_record(
            program,
            index,
            metric_order,
            target_metrics_by_program.get(program.id, []),
        )
        if record is not None:
            records.append(record)
    distinct_metric_niches = _unique_in_order(
        [
            str(record["metric_niche"])
            for record in records
            if isinstance(record.get("metric_niche"), str)
        ]
    )
    metric_diverse = len(distinct_metric_niches) >= 2
    prompt_sha256 = prompt_metadata.get("prompt_sha256")
    return {
        "schema": "libreevolve.metric_diverse_inspiration.v1",
        "source": "prompt_visible_inspiration_selection_metadata",
        "selection_strategy": selection_metadata.get("strategy"),
        "sample_kind": selection_metadata.get("sample_kind"),
        "requested_count": selection_metadata.get("requested_count"),
        "selected_count": selection_metadata.get("selected_count"),
        "selected_program_ids": list(selection_metadata.get("selected_program_ids", []))
        if isinstance(selection_metadata.get("selected_program_ids"), list)
        else [],
        "visible_count": len(visible),
        "visible_program_ids": [program.id for program in visible],
        "rendered_count_source": "prompt_diagnostics.inspiration_policy.rendered_count",
        "prompt_sha256": prompt_sha256 if isinstance(prompt_sha256, str) else None,
        "declared_metric_order": metric_order,
        "target_metrics": target_metrics,
        "records": records,
        "record_count": len(records),
        "distinct_metric_count": len(distinct_metric_niches),
        "distinct_metric_niches": distinct_metric_niches,
        "metric_diverse_prompt_visible": metric_diverse,
        "status": (
            "metric_diverse_prompt_visible"
            if metric_diverse
            else "not_metric_diverse_prompt_visible"
        ),
        "benchmark_policy": {
            "schema": "libreevolve.metric_diverse_prompt_benchmark_boundary.v1",
            "benchmark_required_metric_diverse_prompt_policy": False,
            "cross_run_metric_diverse_prompt_fixture": False,
            "scalar_and_single_metric_comparison": False,
            "alphaevolve_section_2_4_claim_ready": False,
        },
        "benchmark_comparison_readiness": (
            _metric_diverse_benchmark_comparison_readiness(metric_diverse)
        ),
        "claim_ready": False,
        "claim_readiness": {
            "prompt_visible_metric_diversity_evidence": metric_diverse,
            "benchmark_required_metric_diverse_prompt_policy": False,
            "cross_run_metric_diverse_prompt_fixture": False,
            "scalar_and_single_metric_comparison": False,
            "remaining_gap": (
                [
                    "benchmark_required_metric_diverse_prompt_policy",
                    "cross_run_metric_diverse_prompt_fixture",
                    "scalar_and_single_metric_comparison",
                ]
                if metric_diverse
                else [
                    "prompt_visible_slate_did_not_cover_multiple_metric_niches",
                    "benchmark_required_metric_diverse_prompt_policy",
                    "cross_run_metric_diverse_prompt_fixture",
                    "scalar_and_single_metric_comparison",
                ]
            ),
        },
    }


def _metric_diverse_declared_metric_order(
    objective_schema: Mapping[str, object],
) -> list[str]:
    metrics = objective_schema.get("metrics")
    if not isinstance(metrics, list):
        return []
    names: list[str] = []
    for metric in metrics:
        if not isinstance(metric, Mapping):
            continue
        name = metric.get("name")
        if isinstance(name, str) and name and name not in names:
            names.append(name)
    return names


def _metric_diverse_target_metrics(
    selection_metadata: Mapping[str, object],
) -> list[dict]:
    records = selection_metadata.get("target_metrics")
    if not isinstance(records, list):
        return []
    normalized: list[dict] = []
    for record in records:
        if not isinstance(record, Mapping):
            continue
        metric = record.get("metric")
        program_id = record.get("program_id")
        if isinstance(metric, str) and metric and isinstance(program_id, str) and program_id:
            normalized.append({"metric": metric, "program_id": program_id})
    return normalized


def _metric_diverse_visible_inspiration_record(
    program: Program,
    visible_index: int,
    metric_order: list[str],
    target_metrics: list[str],
) -> dict | None:
    normalized_metrics = _metric_diverse_normalized_metrics(program, metric_order)
    if not normalized_metrics:
        return None
    metric_niche = _metric_diverse_metric_niche(
        normalized_metrics,
        metric_order,
        target_metrics,
    )
    if metric_niche is None:
        return None
    raw_value = program.metrics.get(metric_niche)
    normalized_value = normalized_metrics.get(metric_niche)
    return {
        "program_id": program.id,
        "visible_index": visible_index,
        "metric_niche": metric_niche,
        "metric_niche_source": (
            "selection_metadata.target_metrics"
            if metric_niche in target_metrics
            else "max_normalized_declared_metric"
        ),
        "target_metrics": list(target_metrics),
        "raw_metric_value": float(raw_value)
        if isinstance(raw_value, (int, float)) and not isinstance(raw_value, bool)
        else None,
        "normalized_metric_value": normalized_value,
        "normalized_metrics": normalized_metrics,
        "fitness": program.fitness,
        "generation": program.generation,
    }


def _metric_diverse_normalized_metrics(
    program: Program,
    metric_order: list[str],
) -> dict[str, float]:
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    raw = metadata.get("normalized_metrics")
    if not isinstance(raw, Mapping):
        return {}
    allowed = set(metric_order)
    values: dict[str, float] = {}
    for name in metric_order:
        value = raw.get(name)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            numeric = float(value)
            if math.isfinite(numeric):
                values[name] = max(0.0, min(1.0, numeric))
    if values or allowed:
        return values
    for name, value in raw.items():
        if not isinstance(name, str) or not name:
            continue
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            numeric = float(value)
            if math.isfinite(numeric):
                values[name] = max(0.0, min(1.0, numeric))
    return values


def _metric_diverse_metric_niche(
    normalized_metrics: Mapping[str, float],
    metric_order: list[str],
    target_metrics: list[str],
) -> str | None:
    for metric in target_metrics:
        if metric in normalized_metrics:
            return metric
    ordered_names = [
        name for name in metric_order if name in normalized_metrics
    ] + sorted(name for name in normalized_metrics if name not in set(metric_order))
    if not ordered_names:
        return None
    order_index = {name: index for index, name in enumerate(ordered_names)}
    return max(
        ordered_names,
        key=lambda name: (
            float(normalized_metrics[name]),
            -order_index[name],
        ),
    )


def _unique_in_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _metric_diverse_benchmark_comparison_readiness(
    prompt_visible_metric_diversity_evidence: bool,
) -> dict:
    remaining_gap = [
        "benchmark_prompt_policy_enforced",
        "cross_run_metric_diverse_fixture",
        "scalar_only_baseline_comparison",
        "single_metric_target_baseline_comparison",
        "equal_budget_comparison_report",
    ]
    if not prompt_visible_metric_diversity_evidence:
        remaining_gap.insert(0, "prompt_visible_metric_diversity_evidence")
    return {
        "schema": "libreevolve.metric_diverse_benchmark_comparison_readiness.v1",
        "prompt_visible_metric_diversity_evidence": (
            bool(prompt_visible_metric_diversity_evidence)
        ),
        "benchmark_prompt_policy_enforced": False,
        "cross_run_metric_diverse_fixture": False,
        "scalar_only_baseline_comparison": False,
        "single_metric_target_baseline_comparison": False,
        "equal_budget_comparison_report": False,
        "alphaevolve_section_2_4_claim_ready": False,
        "remaining_gap": remaining_gap,
    }


def _prompt_execution_output_field_record(
    value: object,
    *,
    field: str,
    selected: bool,
    prompt_visible: bool,
    field_cap_chars: int | None,
    omission_reason: str | None,
) -> dict:
    raw = _prompt_execution_output_raw_text(value)
    max_chars = (
        field_cap_chars
        if isinstance(field_cap_chars, int)
        and not isinstance(field_cap_chars, bool)
        else _PROMPT_EXECUTION_OUTPUT_DEFAULT_FIELD_CHARS
    )
    display_text = None
    display_sha256 = None
    display_chars = 0
    redacted = False
    truncated = False
    raw_sha256 = None
    raw_chars = 0
    if raw is not None:
        raw_sha256 = hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()
        raw_chars = len(raw)
        redacted_text = redact_sensitive_text(raw)
        redacted = redacted_text != raw
        truncated = len(redacted_text) > max_chars
        if prompt_visible:
            display_text = _prompt_execution_output_truncate(
                redacted_text,
                max_chars,
            ).replace("\n", "\\n")
            display_sha256 = hashlib.sha256(
                display_text.encode("utf-8", errors="replace")
            ).hexdigest()
            display_chars = len(display_text)
    return {
        "field": field,
        "selected": selected,
        "field_cap_chars": field_cap_chars,
        "raw_present": raw is not None,
        "raw_chars": raw_chars,
        "raw_sha256": raw_sha256,
        "redacted": redacted,
        "truncated": truncated,
        "prompt_visible": prompt_visible,
        "omission_reason": omission_reason,
        "display_text": display_text,
        "display_chars": display_chars,
        "display_sha256": display_sha256,
    }


def _prompt_execution_output_raw_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).replace("\r\n", "\n").strip()
    return text or None


def _prompt_execution_output_truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    notice = f"...[truncated {len(text) - max_chars} chars]"
    keep = max(0, max_chars - len(notice))
    return text[:keep] + notice


def _runtime_controller_state(run_dir: Path, budget: RunBudget) -> dict:
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
        "event_stream": _controller_budget_event_stream_summary(
            run_dir / "controller_budget_events.jsonl"
        ),
        "limitations": [
            "synchronous_terminal_snapshot_not_async_queue_checkpoint",
            "no_mid_generation_resume_boundary",
            "provider_outputs_not_replayed",
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
    if "llm_feedback" in phase:
        return "feedback"
    if "llm_meta_prompt" in phase:
        return "meta_prompt"
    if "candidate_evaluation" in phase or "seed_evaluation" in phase:
        return "evaluation"
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


def _evaluation_cache_contract_sha256(
    problem: Problem,
    config: Config,
    evaluator_sources: object,
) -> str:
    stdin_text = config.evaluator_stdin_text
    payload = {
        "schema": "libreevolve.evaluation_cache_contract.v1",
        "problem_name": problem.name,
        "primary_metric": problem.primary_metric,
        "metrics": _evaluation_cache_json_value(problem.metrics),
        "evaluator_sources": _evaluation_cache_json_value(evaluator_sources),
        "eval_stages": _evaluation_cache_json_value(config.eval_stages),
        "validator_network_policy": config.validator_network_policy,
        "validator_env_allowlist": list(config.validator_env_allowlist),
        "evaluator_data_include": list(config.evaluator_data_include),
        "evaluator_data_exclude": list(config.evaluator_data_exclude),
        "evaluator_stdin_text_sha256": (
            hashlib.sha256(stdin_text.encode("utf-8")).hexdigest()
            if isinstance(stdin_text, str)
            else None
        ),
        "evaluator_stdin_file": (
            str(config.evaluator_stdin_file)
            if config.evaluator_stdin_file is not None
            else None
        ),
        "cache_stage": "pre_llm_feedback_evaluator_result",
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _evaluation_cache_json_value(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {
            str(key): _evaluation_cache_json_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_evaluation_cache_json_value(item) for item in value]
    return repr(value)


def _evaluation_cache_key(
    workspace: CandidateWorkspace,
    evaluator_contract_sha256: str,
    *,
    diff_error: object | None,
) -> dict | None:
    if diff_error is not None:
        return None
    workspace_hash = _workspace_sha256(workspace)
    payload = {
        "schema": "libreevolve.evaluation_cache_key.v1",
        "workspace_sha256": workspace_hash,
        "evaluator_contract_sha256": evaluator_contract_sha256,
        "diff_error": None,
    }
    cache_key_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "schema": "libreevolve.evaluation_cache_key.v1",
        "cache_key_sha256": cache_key_sha256,
        "workspace_sha256": workspace_hash,
        "evaluator_contract_sha256": evaluator_contract_sha256,
        "diff_error": None,
    }


def _store_evaluation_cache_result(
    cache: dict[str, dict],
    workspace: CandidateWorkspace,
    evaluator_contract_sha256: str,
    result: EvaluationResult,
    *,
    source_program_id: str,
    source_generation: int,
    source_candidate_type: str,
) -> dict:
    key = _evaluation_cache_key(
        workspace,
        evaluator_contract_sha256,
        diff_error=None,
    )
    assert key is not None
    entry = {
        **key,
        "result": copy.deepcopy(result),
        "source_program_id": source_program_id,
        "source_generation": source_generation,
        "source_candidate_type": source_candidate_type,
        "source_fitness": result.fitness,
        "source_metric_names": sorted(result.metrics),
        "source_elapsed_sec": result.elapsed_sec,
    }
    cache[key["cache_key_sha256"]] = entry
    return {
        "schema": "libreevolve.evaluation_cache_record.v1",
        "status": "stored",
        "cache_hit": False,
        "cache_key_sha256": key["cache_key_sha256"],
        "workspace_sha256": key["workspace_sha256"],
        "evaluator_contract_sha256": evaluator_contract_sha256,
        "source_program_id": source_program_id,
        "source_generation": source_generation,
        "source_candidate_type": source_candidate_type,
        "cache_stage": "pre_llm_feedback_evaluator_result",
        "budget_policy": "store_consumed_normal_evaluator_budget",
    }


def _lookup_evaluation_cache_result(
    cache: dict[str, dict],
    workspace: CandidateWorkspace,
    evaluator_contract_sha256: str,
    *,
    diff_error: object | None,
) -> dict | None:
    key = _evaluation_cache_key(
        workspace,
        evaluator_contract_sha256,
        diff_error=diff_error,
    )
    if key is None:
        return None
    return cache.get(key["cache_key_sha256"])


def _evaluation_cache_hit_result(entry: Mapping[str, object]) -> EvaluationResult:
    cached = entry.get("result")
    if not isinstance(cached, EvaluationResult):
        raise RuntimeError("evaluation cache entry is malformed")
    result = copy.deepcopy(cached)
    source_elapsed_sec = result.elapsed_sec
    result.elapsed_sec = 0.0
    for stage in result.stages:
        stage.elapsed_sec = 0.0
    metadata = {
        "schema": "libreevolve.evaluation_cache_record.v1",
        "status": "hit",
        "cache_hit": True,
        "cache_key_sha256": entry["cache_key_sha256"],
        "workspace_sha256": entry["workspace_sha256"],
        "evaluator_contract_sha256": entry["evaluator_contract_sha256"],
        "source_program_id": entry["source_program_id"],
        "source_generation": entry["source_generation"],
        "source_candidate_type": entry["source_candidate_type"],
        "cache_stage": "pre_llm_feedback_evaluator_result",
        "budget_policy": "cache_hit_does_not_consume_evaluator_call_budget",
        "source_elapsed_sec": source_elapsed_sec,
    }
    result.metadata = dict(result.metadata)
    result.metadata["evaluation_cache"] = metadata
    return result


def _evaluation_cache_bypass_metadata(
    workspace: CandidateWorkspace,
    evaluator_contract_sha256: str,
    *,
    reason: str,
) -> dict:
    return {
        "schema": "libreevolve.evaluation_cache_record.v1",
        "status": "bypassed",
        "cache_hit": False,
        "workspace_sha256": _workspace_sha256(workspace),
        "evaluator_contract_sha256": evaluator_contract_sha256,
        "reason": reason,
        "cache_stage": "pre_llm_feedback_evaluator_result",
        "budget_policy": "bypass_consumed_normal_evaluator_budget",
    }


def _evaluation_result_with_cache_metadata(
    result: EvaluationResult,
    metadata: Mapping[str, object],
) -> EvaluationResult:
    updated = copy.deepcopy(result)
    updated.metadata = dict(updated.metadata)
    updated.metadata["evaluation_cache"] = dict(metadata)
    return updated


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


def _normalize_seed_source(index: int, source: dict | None) -> dict:
    return validate_seed_source_record(index, source)


def _has_unicode_format_control(value: str) -> bool:
    return any(unicodedata.category(ch) == "Cf" for ch in value)


def _seed_post_processing_policy() -> dict:
    return {
        "policy": "raw_evaluator_baseline",
        "llm_feedback": "not_applied",
    }


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


def _finite_json_number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    numeric = float(value)
    if not math.isfinite(numeric):
        return None
    return numeric


def _program_llm_calls(
    call_span: list[dict],
    mutation_call: dict | None,
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
    return calls


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
