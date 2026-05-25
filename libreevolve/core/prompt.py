from __future__ import annotations

import random
from dataclasses import dataclass, field

from libreevolve.population.program import Program
from libreevolve.problems.loader import Problem


@dataclass
class PromptSampler:
    """Configurable prompt sampler for AlphaEvolve-style context assembly."""

    variants: list[str] = field(default_factory=list)
    rng: random.Random = field(default_factory=random.Random)

    def build(
        self,
        parent: Program,
        inspirations: list[Program],
        problem: Problem,
        extra_context: str,
        recent_failures: list[tuple[str, float]] | None = None,
    ) -> str:
        variant = self.rng.choice(self.variants) if self.variants else _DEFAULT_TEMPLATE
        return variant.format(
            task=problem.task_description,
            context=_render_context(problem),
            parent_score=parent.fitness,
            parent_metrics=_render_metrics(parent),
            parent_feedback=_render_feedback(parent),
            parent_code=parent.code,
            inspirations=_render_inspirations(inspirations),
            extra_context=extra_context,
            recent_failures=_render_failures(recent_failures),
        )


_DEFAULT_TEMPLATE = """[SYSTEM]
You are an expert programmer evolving solutions for: {task}

[EXPLICIT CONTEXT]
{context}

[CURRENT PROGRAM - normalized fitness: {parent_score:.4f}]
Metrics: {parent_metrics}
Evaluation feedback:
{parent_feedback}
```python
{parent_code}
```

[INSPIRATION PROGRAMS]
{inspirations}

[EXTRA CONTEXT]
{extra_context}
{recent_failures}
[TASK]
Propose a targeted improvement using SEARCH/REPLACE diffs.
Rules: No comments. No markdown fences. No explanation. Just the raw diff block.

Example format (do NOT copy this, use actual code from the program above):
<<<SEARCH
def foo():
    return 1
===
def foo():
    return 2
>>>REPLACE
"""


def _render_context(problem: Problem) -> str:
    if not problem.context_files:
        return "(none)"
    return "\n\n".join(
        f"--- {name} ---\n{content}" for name, content in problem.context_files.items()
    )


def _render_metrics(program: Program) -> str:
    return ", ".join(f"{k}={v}" for k, v in program.metrics.items()) or "(none)"


def _render_feedback(program: Program) -> str:
    stages = program.evaluation.get("stages", []) if program.evaluation else []
    if not stages:
        return "(none)"
    lines = []
    for stage in stages[-3:]:
        status = "passed" if stage.get("passed") else "failed"
        error = stage.get("error")
        suffix = f", error={error}" if error else ""
        lines.append(f"- {stage.get('name')}: {status}, score={stage.get('score')}{suffix}")
    return "\n".join(lines)


def _render_inspirations(inspirations: list[Program]) -> str:
    if not inspirations:
        return "(none)"
    return "".join(
        f"\n--- Inspiration {i + 1} (fitness {ins.fitness:.4f}; metrics: {_render_metrics(ins)}) ---\n{ins.code}\n"
        for i, ins in enumerate(inspirations)
    )


def _render_failures(recent_failures: list[tuple[str, float]] | None) -> str:
    if not recent_failures:
        return ""
    lines = "\n".join(f"  Score {score:.2f}: {code}" for code, score in recent_failures)
    return f"\n[RECENTLY FAILED - do NOT repeat these]\n{lines}\n"
