from __future__ import annotations
from alphaevolve.core.config import Config
from alphaevolve.core.database import ProgramDatabase
from alphaevolve.core.diff import apply_diff
from alphaevolve.core.evaluator import CascadeEvaluator
from alphaevolve.llm.ensemble import build_llm
from alphaevolve.plugins.base import PluginBase
from alphaevolve.population.program import Program
from alphaevolve.problems.loader import Problem

VALID_THRESHOLD = 0.0


def build_prompt(parent: Program, inspirations: list[Program],
                 problem: Problem, extra_context: str) -> str:
    insp = "".join(f"\n--- Inspiration {i+1} (score {ins.fitness:.4f}) ---\n{ins.code}\n"
                   for i, ins in enumerate(inspirations))
    return (f"[SYSTEM]\nYou are an expert programmer evolving solutions for: "
            f"{problem.task_description}\n\n"
            f"[CURRENT BEST PROGRAM - score: {parent.fitness:.4f}]\n"
            f"```python\n{parent.code}\n```\n"
            f"\n[INSPIRATION PROGRAMS]{insp}\n"
            f"[EXTRA CONTEXT]\n{extra_context}\n\n"
            f"[TASK]\nPropose a targeted improvement using SEARCH/REPLACE diffs only:\n\n"
            f"<<<SEARCH\n<exact lines to replace>\n===\n<replacement lines>\n>>>REPLACE\n")


def evolve(problem: Problem, config: Config,
           plugins: list[PluginBase] | None = None) -> Program:
    if plugins is None:
        plugins = []
    db        = ProgramDatabase(config)
    evaluator = CascadeEvaluator(problem, timeout_sec=config.eval_timeout_sec)
    llm       = build_llm(config)

    # Seed population (diff_error=None bypasses Tier 0)
    for seed_code in problem.initial_programs:
        score   = evaluator.evaluate(seed_code, diff_error=None)
        program = Program(code=seed_code, fitness=score)
        db.log(program)
        db.add(program)

    for gen in range(config.max_generations):
        for plugin in plugins:
            plugin.on_generation_start(gen, db)

        parent = db.sample(strategy="exploit")
        if parent is None:
            break

        inspirations = db.sample_diverse(k=config.num_inspirations)
        context = "\n".join(p.build_extra_context(parent, inspirations) for p in plugins)
        prompt = build_prompt(parent, inspirations, problem, context)

        diff, backend_idx = llm.generate(prompt)   # LLMEnsemble returns (str, int)
        child_code, diff_error = apply_diff(parent.code, diff)
        score = evaluator.evaluate(child_code, diff_error=diff_error)

        # Construct Program BEFORE calling on_evaluated (plugins need full object)
        program = Program(code=child_code, fitness=score,
                          parent_id=parent.id, generation=gen)

        for plugin in plugins:
            score = plugin.on_evaluated(program, score)
        program.fitness = score

        db.log(program)
        if score >= VALID_THRESHOLD:
            db.add(program)

        llm.record_reward(backend_idx, max(0.0, score - parent.fitness))
        db.maybe_migrate(gen)

        for plugin in plugins:
            plugin.on_generation_end(gen, db.best())

    return db.best()
