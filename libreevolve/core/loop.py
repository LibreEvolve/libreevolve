"""Core evolution loop: prompt construction, LLM-driven mutation, evaluation.

Inspired by AlphaEvolve's evolutionary loop and adjacent code-evolution systems.
This synchronous loop is intentionally smaller than the paper systems.
"""
from __future__ import annotations
import math
import random
from pathlib import Path
from libreevolve.core.config import Config
from libreevolve.core.candidate import CandidateWorkspace, apply_workspace_mutation
from libreevolve.core.database import ProgramDatabase
from libreevolve.core.evaluator import CascadeEvaluator
from libreevolve.core.feedback import apply_llm_feedback, build_critique_prompt
from libreevolve.core.meta_prompt import PromptDatabase
from libreevolve.core.prompt import PromptSampler
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
    db        = ProgramDatabase(config, perf_bounds=(0.0, 1.0))
    evaluator = CascadeEvaluator(
        problem, timeout_sec=config.eval_timeout_sec, stages=config.eval_stages
    )
    llm       = build_llm(config)
    prompt_sampler = PromptSampler(config.prompt_variants, random.Random(config.seed))
    prompt_db = PromptDatabase(
        Path(config.log_dir) / config.problem_name,
        templates=config.prompt_variants or None,
    )

    # Seed population (diff_error=None bypasses Tier 0)
    seed_workspaces = problem.initial_workspaces or [
        CandidateWorkspace.from_code(code) for code in problem.initial_programs
    ]
    for seed_workspace in seed_workspaces:
        result = evaluator.evaluate(seed_workspace, diff_error=None)
        program = Program(
            code=seed_workspace.code,
            files=dict(seed_workspace.files),
            primary_file=seed_workspace.primary_file,
            fitness=result.fitness,
            metrics=result.metrics,
            evaluation=result.to_dict(),
        )
        db.admit(program, threshold=VALID_THRESHOLD)
        db.log(program)

    recent_failures: list[dict] = []
    _MAX_FAILURES = 5

    for gen in range(config.max_generations):
        for plugin in plugins:
            plugin.on_generation_start(gen, db)

        strategy = "explore" if random.random() < config.explore_ratio else "exploit"
        parent = db.sample(strategy=strategy)
        if parent is None:
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

        diff, backend_idx = llm.generate(prompt)   # LLMEnsemble returns (str, int)
        critique_metadata = None
        if config.critique_enabled:
            critique_prompt = build_critique_prompt(
                prompt, diff, critique_prompt=config.critique_prompt or None
            )
            revised_diff, critique_backend_idx = llm.generate(critique_prompt)
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
                **critique_status,
            }
            diff = selected_diff
        child_workspace, diff_error = apply_workspace_mutation(
            parent.workspace(), diff, mutation_mode=config.mutation_mode
        )
        result = evaluator.evaluate(child_workspace, diff_error=diff_error)
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
                                    "prompt_program_id": prompt_program.id},
                          metrics=result.metrics,
                          evaluation=result.to_dict())

        score = _apply_plugin_scores(program, score, plugins)

        if program.fitness < VALID_THRESHOLD or not _evaluation_is_valid(program):
            failure = db.log_failure(program, parent, diff, diff_error)
            recent_failures.append(failure)
            recent_failures = recent_failures[-_MAX_FAILURES:]

        db.admit(program, threshold=VALID_THRESHOLD)
        db.log(program)
        prompt_db.record_result(
            prompt_program.id,
            score,
            metadata={"last_generation": gen, "last_program_id": program.id},
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
            template, prompt_backend_idx = llm.generate(mutation_prompt)
            prompt_db.mutate(
                prompt_program.id,
                template,
                generation=gen + 1,
                metadata={"source": "llm", "backend_idx": prompt_backend_idx},
            )
        llm.record_reward(backend_idx, max(0.0, score - parent.fitness))
        db.maybe_migrate(gen)

        best = db.best()
        for plugin in plugins:
            plugin.on_generation_end(gen, best)

    return db.best()


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
