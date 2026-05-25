"""Core evolution loop: prompt construction, LLM-driven mutation, evaluation.

Inspired by AlphaEvolve's evolutionary loop and adjacent code-evolution systems.
This synchronous loop is intentionally smaller than the paper systems.
"""
from __future__ import annotations
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
                 recent_failures: list[tuple[str, float]] | None = None,
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
            critique_metadata = {
                "prompt": critique_prompt,
                "original_diff": diff,
                "revised_diff": revised_diff,
                "backend_idx": critique_backend_idx,
            }
            diff = revised_diff
        child_workspace, diff_error = apply_workspace_mutation(
            parent.workspace(), diff, mutation_mode=config.mutation_mode
        )
        result = evaluator.evaluate(child_workspace, diff_error=diff_error)
        result = apply_llm_feedback(
            result, child_workspace, problem, config.llm_feedback, llm
        )
        score = result.fitness

        child_code = child_workspace.code
        if score < VALID_THRESHOLD and child_code != parent.code:
            oneliner = (
                f"{result.error or 'invalid'}: " + child_code.replace("\n", " ")[:120]
            )
            recent_failures.append((oneliner, score))
            recent_failures = recent_failures[-_MAX_FAILURES:]

        # Construct Program BEFORE calling on_evaluated (plugins need full object)
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

        for plugin in plugins:
            score = plugin.on_evaluated(program, score)
            program.fitness = score  # keep in sync for next plugin

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
        if score >= VALID_THRESHOLD:
            db.add(program)

        llm.record_reward(backend_idx, max(0.0, score - parent.fitness))
        db.maybe_migrate(gen)

        best = db.best()
        for plugin in plugins:
            plugin.on_generation_end(gen, best)

    return db.best()
