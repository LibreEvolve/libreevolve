"""Core evolution loop: prompt construction, LLM-driven mutation, evaluation.

Inspired by AlphaEvolve's evolutionary loop and adjacent code-evolution systems.
This synchronous loop is intentionally smaller than the paper systems.
"""
from __future__ import annotations
import math
import random
from pathlib import Path
from libreevolve.core.budget import RunBudget
from libreevolve.core.config import Config
from libreevolve.core.candidate import CandidateWorkspace, apply_workspace_mutation
from libreevolve.core.database import ProgramDatabase
from libreevolve.core.evaluator import CascadeEvaluator, evaluator_entrypoint_provenance
from libreevolve.core.feedback import apply_llm_feedback, build_critique_prompt
from libreevolve.core.meta_prompt import PromptDatabase
from libreevolve.core.prompt import PromptSampler
from libreevolve.core.provenance import (
    git_state,
    plugin_provenance,
    problem_provenance,
    source_provenance,
)
from libreevolve.llm.ensemble import build_llm
from libreevolve.plugins.base import PluginBase
from libreevolve.population.program import Program
from libreevolve.problems.loader import Problem

VALID_THRESHOLD = 0.0


def build_prompt(parent: Program, inspirations: list[Program],
                 problem: Problem, extra_context: str,
                 recent_failures: list[dict | tuple[str, float]] | None = None,
                 mutation_mode: str = "diff") -> str:
    return PromptSampler().build(
        parent, inspirations, problem, extra_context,
        recent_failures=recent_failures,
        mutation_mode=mutation_mode,
    )


def evolve(problem: Problem, config: Config,
           plugins: list[PluginBase] | None = None) -> "Program | None":
    config.validate()
    if plugins is None:
        plugins = []
    random.seed(config.seed)
    budget = RunBudget.from_config(config)
    db        = ProgramDatabase(
        config,
        perf_bounds=(0.0, 1.0),
        context_sources=problem.context_sources,
        evaluator_sources=evaluator_entrypoint_provenance(problem, config.eval_stages),
        run_provenance={
            "git": git_state(Path.cwd()),
            "source": source_provenance(),
            "problem": problem_provenance(problem.problem_dir),
            "plugins": plugin_provenance(plugins),
        },
    )
    evaluator = CascadeEvaluator(
        problem,
        timeout_sec=config.eval_timeout_sec,
        stages=config.eval_stages,
        validator_env_allowlist=config.validator_env_allowlist,
        artifact_dir=Path(config.log_dir) / config.problem_name / "evaluator_artifacts",
        artifact_include=config.evaluator_artifact_include,
        artifact_exclude=config.evaluator_artifact_exclude,
        artifact_max_files=config.evaluator_artifact_max_files,
        artifact_max_bytes=config.evaluator_artifact_max_bytes,
        artifact_redact_secrets=config.evaluator_artifact_redact_secrets,
    )
    llm       = build_llm(config)
    prompt_sampler = PromptSampler(config.prompt_variants, random.Random(config.seed))
    prompt_db = PromptDatabase(
        Path(config.log_dir) / config.problem_name,
        templates=config.prompt_variants or None,
        reward_bounds=(float(config.prompt_reward_bounds[0]), float(config.prompt_reward_bounds[1])),
        explore_coeff=config.prompt_explore_coeff,
        reward_mode=config.prompt_reward_mode,
    )

    # Seed population (diff_error=None bypasses Tier 0)
    seed_workspaces = problem.initial_workspaces or [
        CandidateWorkspace.from_code(code) for code in problem.initial_programs
    ]
    for seed_workspace in seed_workspaces:
        if budget.check_before_evaluation():
            break
        result = evaluator.evaluate(seed_workspace, diff_error=None)
        budget.record_evaluation(result.elapsed_sec, seed=True)
        program = Program(
            code=seed_workspace.code,
            files=dict(seed_workspace.files),
            primary_file=seed_workspace.primary_file,
            fitness=result.fitness,
            metrics=result.metrics,
            evaluation=result.to_dict(),
            metadata={"budget": budget.snapshot()},
        )
        _annotate_metric_policy(program, problem)
        db.admit(program, threshold=VALID_THRESHOLD)
        db.log(program)

    recent_failures: list[dict] = []
    _MAX_FAILURES = 5

    for gen in range(config.max_generations):
        if budget.check_before_generation():
            break
        budget.record_generation_start()
        for plugin in plugins:
            plugin.on_generation_start(gen, db)

        strategy = "explore" if random.random() < config.explore_ratio else "exploit"
        parent = db.sample(strategy=strategy)
        if parent is None:
            budget.stop_reason = "no_parent"
            break

        inspirations = db.sample_diverse(
            k=config.num_inspirations,
            exclude_ids={parent.id},
        )
        context = "\n".join(p.build_extra_context(parent, inspirations) for p in plugins)
        prompt_program = prompt_db.select()
        prompt = prompt_sampler.build(
            parent, inspirations, problem, context,
            recent_failures=recent_failures or None,
            template=prompt_program.template,
            mutation_mode=config.mutation_mode,
        )

        diff, backend_idx = llm.generate(prompt, role="mutation")
        mutation_llm_call = _last_llm_call(llm)
        critique_metadata = None
        if config.critique_enabled:
            critique_prompt = build_critique_prompt(
                prompt, diff, critique_prompt=config.critique_prompt or None
            )
            revised_diff, critique_backend_idx = llm.generate(critique_prompt, role="critique")
            critique_llm_call = _last_llm_call(llm)
            selected_diff, critique_status = _select_critique_mutation(
                parent.workspace(),
                diff,
                revised_diff,
                config.mutation_mode,
            )
            critique_metadata = {
                "prompt": critique_prompt,
                "original_diff": diff,
                "revised_diff": revised_diff,
                "backend_idx": critique_backend_idx,
                "llm_call": critique_llm_call,
                **critique_status,
            }
            diff = selected_diff
        child_workspace, diff_error = apply_workspace_mutation(
            parent.workspace(), diff, mutation_mode=config.mutation_mode
        )
        result = evaluator.evaluate(child_workspace, diff_error=diff_error)
        budget.record_evaluation(result.elapsed_sec, seed=False)
        result = apply_llm_feedback(
            result, child_workspace, problem, config.llm_feedback, llm
        )
        score = result.fitness

        # Construct Program BEFORE calling on_evaluated (plugins need full object)
        child_code = child_workspace.code
        program = Program(code=child_code, fitness=score,
                          files=dict(child_workspace.files),
                          primary_file=child_workspace.primary_file,
                          parent_id=parent.id, generation=gen,
                          lineage=parent.lineage + [parent.id],
                          metadata={"prompt": prompt, "diff": diff,
                                    "backend_idx": backend_idx,
                                    "critique": critique_metadata,
                                    "mutation_mode": config.mutation_mode,
                                    "prompt_program_id": prompt_program.id,
                                    "llm_calls": _program_llm_calls(
                                        mutation_llm_call, critique_metadata, result
                                    ),
                                    "budget": budget.snapshot()},
                          metrics=result.metrics,
                          evaluation=result.to_dict())

        _annotate_metric_policy(program, problem)
        score = _apply_plugin_scores(program, score, plugins)
        _annotate_metric_policy(program, problem)

        if program.fitness < VALID_THRESHOLD or not _evaluation_is_valid(program):
            failure = db.log_failure(program, parent, diff, diff_error)
            recent_failures.append(failure)
            recent_failures = recent_failures[-_MAX_FAILURES:]

        db.admit(program, threshold=VALID_THRESHOLD)
        db.log(program)
        prompt_reward = _prompt_reward(score, parent.fitness, config.prompt_reward_mode)
        prompt_db.record_result(
            prompt_program.id,
            prompt_reward,
            metadata={
                "last_generation": gen,
                "last_program_id": program.id,
                "last_candidate_score": score,
                "last_parent_score": parent.fitness,
            },
        )
        if (
            config.meta_prompt_evolution
            and config.meta_prompt_interval > 0
            and (gen + 1) % config.meta_prompt_interval == 0
        ):
            mutation_prompt = (
                "Improve this LibreEvolve prompt template for future code evolution. "
                "Keep all existing Python format placeholders intact. Return only "
                "the complete revised template.\n\n"
                f"{prompt_program.template}"
            )
            template, prompt_backend_idx = llm.generate(mutation_prompt, role="meta_prompt")
            prompt_db.mutate(
                prompt_program.id,
                template,
                generation=gen + 1,
                metadata={
                    "source": "llm",
                    "backend_idx": prompt_backend_idx,
                    "llm_call": _last_llm_call(llm),
                },
            )
        llm.record_reward(backend_idx, max(0.0, score - parent.fitness))
        db.maybe_migrate(gen)

        best = db.best()
        for plugin in plugins:
            plugin.on_generation_end(gen, best)
        budget.record_generation_complete()

    best = db.best()
    db.update_manifest_runtime(budget.finish(best_found=best is not None))
    return best


def _apply_plugin_scores(
    program: Program, initial_score: float, plugins: list[PluginBase]
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

    for plugin in plugins:
        before = score
        before_metrics = dict(program.metrics)
        name = plugin.__class__.__name__
        record = {
            "plugin": name,
            "before": before,
            "after": before,
            "delta": 0.0,
            "metrics_added": [],
            "metrics_changed": [],
            "accepted": False,
            "error": None,
        }
        proposed = plugin.on_evaluated(program, score)
        if isinstance(proposed, bool) or not isinstance(proposed, (int, float)):
            record["error"] = "invalid_plugin_score"
        elif not math.isfinite(float(proposed)):
            record["error"] = "non_finite_plugin_score"
        else:
            score = float(proposed)
            record["after"] = score
            record["delta"] = score - before
            record["accepted"] = True
        after_metrics = dict(program.metrics)
        record["metrics_added"] = sorted(set(after_metrics) - set(before_metrics))
        record["metrics_changed"] = sorted(
            key
            for key in set(after_metrics) & set(before_metrics)
            if after_metrics[key] != before_metrics[key]
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
    for metric in problem.metrics:
        name = metric.get("name")
        if not isinstance(name, str) or name not in program.metrics:
            continue
        value = program.metrics[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        numeric = float(value)
        if not math.isfinite(numeric):
            continue
        normalized[name] = problem.normalize_metric(name, numeric)
    if not normalized:
        return
    selection_score = sum(normalized.values()) / len(normalized)
    program.metadata = dict(program.metadata)
    program.metadata["normalized_metrics"] = normalized
    program.metadata["selection_score"] = selection_score
    program.metadata["selection_policy"] = {
        "type": "mean_normalized_declared_metrics",
        "metrics": list(normalized),
        "primary_metric": problem.primary_metric,
    }


def _last_llm_call(llm) -> dict | None:
    call = getattr(llm, "last_call", None)
    return dict(call) if isinstance(call, dict) else None


def _program_llm_calls(
    mutation_call: dict | None,
    critique_metadata: dict | None,
    result,
) -> list[dict]:
    calls = []
    if mutation_call:
        calls.append(mutation_call)
    if critique_metadata and isinstance(critique_metadata.get("llm_call"), dict):
        calls.append(dict(critique_metadata["llm_call"]))
    feedback_records = result.metadata.get("llm_feedback", []) if result.metadata else []
    if isinstance(feedback_records, list):
        for record in feedback_records:
            if isinstance(record, dict) and isinstance(record.get("llm_call"), dict):
                calls.append(dict(record["llm_call"]))
    return calls


def _select_critique_mutation(
    workspace: CandidateWorkspace,
    original_diff: str,
    revised_diff: str,
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
    return revised_diff, status


def _evaluation_is_valid(program: Program) -> bool:
    return bool(program.evaluation.get("is_valid", True))


def _prompt_reward(score: float, parent_score: float, mode: str) -> float:
    if mode == "improvement":
        return score - parent_score
    return score
