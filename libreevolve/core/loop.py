"""Core evolution loop: prompt construction, LLM-driven mutation, evaluation.

Source: AlphaEvolve (arXiv:2506.13131) — core loop structure, explore/exploit
sampling, and failure history in prompt from CodeEvolve (arXiv:2510.14150).
"""
from __future__ import annotations
import random
from libreevolve.core.config import Config
from libreevolve.core.candidate import apply_candidate_mutation
from libreevolve.core.database import ProgramDatabase
from libreevolve.core.evaluator import CascadeEvaluator
from libreevolve.core.prompt import PromptSampler
from libreevolve.llm.ensemble import build_llm
from libreevolve.plugins.base import PluginBase
from libreevolve.population.program import Program
from libreevolve.problems.loader import Problem

VALID_THRESHOLD = 0.0


def build_prompt(parent: Program, inspirations: list[Program],
                 problem: Problem, extra_context: str,
                 recent_failures: list[tuple[str, float]] | None = None) -> str:
    return PromptSampler().build(
        parent, inspirations, problem, extra_context, recent_failures=recent_failures
    )


def evolve(problem: Problem, config: Config,
           plugins: list[PluginBase] | None = None) -> "Program | None":
    if plugins is None:
        plugins = []
    random.seed(config.seed)
    db        = ProgramDatabase(config, perf_bounds=(0.0, 1.0))
    evaluator = CascadeEvaluator(
        problem, timeout_sec=config.eval_timeout_sec, stages=config.eval_stages
    )
    llm       = build_llm(config)
    prompt_sampler = PromptSampler(config.prompt_variants, random.Random(config.seed))

    # Seed population (diff_error=None bypasses Tier 0)
    for seed_code in problem.initial_programs:
        result = evaluator.evaluate(seed_code, diff_error=None)
        program = Program(
            code=seed_code,
            fitness=result.fitness,
            metrics=result.metrics,
            evaluation=result.to_dict(),
        )
        db.log(program)
        if result.fitness >= VALID_THRESHOLD:
            db.add(program)

    recent_failures: list[tuple[str, float]] = []
    _MAX_FAILURES = 5

    for gen in range(config.max_generations):
        for plugin in plugins:
            plugin.on_generation_start(gen, db)

        strategy = "explore" if random.random() < config.explore_ratio else "exploit"
        parent = db.sample(strategy=strategy)
        if parent is None:
            break

        inspirations = db.sample_diverse(k=config.num_inspirations)
        context = "\n".join(p.build_extra_context(parent, inspirations) for p in plugins)
        prompt = prompt_sampler.build(
            parent, inspirations, problem, context,
            recent_failures=recent_failures or None,
        )

        diff, backend_idx = llm.generate(prompt)   # LLMEnsemble returns (str, int)
        child_code, diff_error = apply_candidate_mutation(
            parent.code, diff, mutation_mode=config.mutation_mode
        )
        result = evaluator.evaluate(child_code, diff_error=diff_error)
        score = result.fitness

        if score < VALID_THRESHOLD and child_code != parent.code:
            oneliner = (
                f"{result.error or 'invalid'}: " + child_code.replace("\n", " ")[:120]
            )
            recent_failures.append((oneliner, score))
            recent_failures = recent_failures[-_MAX_FAILURES:]

        # Construct Program BEFORE calling on_evaluated (plugins need full object)
        program = Program(code=child_code, fitness=score,
                          parent_id=parent.id, generation=gen,
                          lineage=parent.lineage + [parent.id],
                          metadata={"prompt": prompt, "diff": diff,
                                    "mutation_mode": config.mutation_mode},
                          metrics=result.metrics,
                          evaluation=result.to_dict())

        for plugin in plugins:
            score = plugin.on_evaluated(program, score)
            program.fitness = score  # keep in sync for next plugin

        db.log(program)
        if score >= VALID_THRESHOLD:
            db.add(program)

        llm.record_reward(backend_idx, max(0.0, score - parent.fitness))
        db.maybe_migrate(gen)

        best = db.best()
        for plugin in plugins:
            plugin.on_generation_end(gen, best)

    return db.best()
