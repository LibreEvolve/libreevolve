"""Core evolution loop: prompt construction, LLM-driven mutation, evaluation.

Source: AlphaEvolve (arXiv:2506.13131) — core loop structure, explore/exploit
sampling, and failure history in prompt from CodeEvolve (arXiv:2510.14150).
"""
from __future__ import annotations
import random
from libreevolve.core.config import Config
from libreevolve.core.database import ProgramDatabase
from libreevolve.core.diff import apply_diff
from libreevolve.core.evaluator import CascadeEvaluator
from libreevolve.llm.ensemble import build_llm
from libreevolve.plugins.base import PluginBase
from libreevolve.population.program import Program
from libreevolve.problems.loader import Problem

VALID_THRESHOLD = 0.0


def build_prompt(parent: Program, inspirations: list[Program],
                 problem: Problem, extra_context: str,
                 recent_failures: list[tuple[str, float]] | None = None) -> str:
    insp = "".join(f"\n--- Inspiration {i+1} (score {ins.fitness:.4f}) ---\n{ins.code}\n"
                   for i, ins in enumerate(inspirations))
    failures = ""
    if recent_failures:
        lines = "\n".join(f"  Score {score:.2f}: {code}"
                          for code, score in recent_failures)
        failures = f"\n[RECENTLY FAILED - do NOT repeat these]\n{lines}\n"
    return (f"[SYSTEM]\nYou are an expert programmer evolving solutions for: "
            f"{problem.task_description}\n\n"
            f"[CURRENT BEST PROGRAM - score: {parent.fitness:.4f}]\n"
            f"```python\n{parent.code}\n```\n"
            f"\n[INSPIRATION PROGRAMS]{insp}\n"
            f"[EXTRA CONTEXT]\n{extra_context}\n"
            f"{failures}\n"
            f"[TASK]\nPropose a targeted improvement using SEARCH/REPLACE diffs.\n"
            f"Rules: No comments. No markdown fences. No explanation. Just the raw diff block.\n\n"
            f"Example format (do NOT copy this, use actual code from the program above):\n"
            f"<<<SEARCH\ndef foo():\n    return 1\n===\ndef foo():\n    return 2\n>>>REPLACE\n")


def evolve(problem: Problem, config: Config,
           plugins: list[PluginBase] | None = None) -> "Program | None":
    if plugins is None:
        plugins = []
    random.seed(config.seed)
    db        = ProgramDatabase(config)
    evaluator = CascadeEvaluator(problem, timeout_sec=config.eval_timeout_sec)
    llm       = build_llm(config)

    # Seed population (diff_error=None bypasses Tier 0)
    for seed_code in problem.initial_programs:
        score   = evaluator.evaluate(seed_code, diff_error=None)
        program = Program(code=seed_code, fitness=score)
        db.log(program)
        db.add(program)

    recent_failures: list[tuple[str, float]] = []
    _MAX_FAILURES = 5

    for gen in range(config.max_generations):
        for plugin in plugins:
            plugin.on_generation_start(gen, db)

        strategy = "explore" if random.random() < 0.3 else "exploit"
        parent = db.sample(strategy=strategy)
        if parent is None:
            break

        inspirations = db.sample_diverse(k=config.num_inspirations)
        context = "\n".join(p.build_extra_context(parent, inspirations) for p in plugins)
        prompt = build_prompt(parent, inspirations, problem, context,
                              recent_failures=recent_failures or None)

        diff, backend_idx = llm.generate(prompt)   # LLMEnsemble returns (str, int)
        child_code, diff_error = apply_diff(parent.code, diff)
        score = evaluator.evaluate(child_code, diff_error=diff_error)

        if score < VALID_THRESHOLD and child_code != parent.code:
            oneliner = child_code.replace("\n", " ")[:120]
            recent_failures.append((oneliner, score))
            recent_failures = recent_failures[-_MAX_FAILURES:]

        # Construct Program BEFORE calling on_evaluated (plugins need full object)
        program = Program(code=child_code, fitness=score,
                          parent_id=parent.id, generation=gen,
                          lineage=parent.lineage + [parent.id],
                          metadata={"prompt": prompt, "diff": diff})

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
