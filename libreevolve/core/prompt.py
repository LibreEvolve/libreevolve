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
        template: str | None = None,
        mutation_mode: str = "diff",
    ) -> str:
        variant = template or (self.rng.choice(self.variants) if self.variants else _DEFAULT_TEMPLATE)
        return variant.format(
            task=problem.task_description,
            context=_render_context(problem),
            parent_score=parent.fitness,
            parent_metrics=_render_metrics(parent),
            parent_feedback=_render_feedback(parent),
            parent_code=_render_program_files(parent),
            inspirations=_render_inspirations(inspirations),
            extra_context=extra_context,
            recent_failures=_render_failures(recent_failures),
            mutation_mode=mutation_mode,
            mutation_instructions=_render_mutation_instructions(mutation_mode),
        )


DEFAULT_TEMPLATE = """[SYSTEM]
You are an expert programmer evolving solutions for: {task}

[EXPLICIT CONTEXT]
{context}

[CURRENT PROGRAM - normalized fitness: {parent_score:.4f}]
Metrics: {parent_metrics}
Evaluation feedback:
{parent_feedback}
{parent_code}

[INSPIRATION PROGRAMS]
{inspirations}

[EXTRA CONTEXT]
{extra_context}
{recent_failures}
[TASK]
Propose a targeted improvement.
Mutation mode: {mutation_mode}
{mutation_instructions}
"""

_DEFAULT_TEMPLATE = DEFAULT_TEMPLATE


def _render_context(problem: Problem) -> str:
    if not problem.context_files:
        return "(none)"
    return "\n\n".join(
        f"--- CONTEXT SOURCE: {name} ---\n{content}"
        for name, content in problem.context_files.items()
    )


def _render_mutation_instructions(mutation_mode: str) -> str:
    if mutation_mode == "full":
        return """Return full replacement code, not SEARCH/REPLACE diffs.
For multi-file candidates, wrap each changed file as:
<<<FILE path/to/file.py
complete replacement file content
>>>FILE
Use topology commands when needed:
<<<FILE DELETE path/to/obsolete.py
>>>FILE
<<<FILE MOVE old/path.py -> new/path.py
>>>FILE
<<<FILE PRIMARY path/to/main.py
>>>FILE
For a single-file candidate without evolve blocks, return only the complete
replacement primary file. If the file has one evolve block, return only the
replacement block body. If it has multiple evolve blocks, return one section per
changed block:
<<<BLOCK block_name
replacement block body
>>>BLOCK
Rules: No markdown fences. No explanation. No SEARCH/REPLACE blocks."""
    return """For multi-file candidates, wrap each file edit in
`<<<FILE path ... >>>FILE`; otherwise edit the current primary file.
Use either compact `<<<SEARCH` / `>>>REPLACE` fences or AlphaEvolve-style
`<<<<<<< SEARCH` / `>>>>>>> REPLACE` fences.
For workspace topology changes, use command file sections such as
`<<<FILE DELETE path/to/file.py ... >>>FILE`,
`<<<FILE MOVE old/path.py -> new/path.py ... >>>FILE`, or
`<<<FILE PRIMARY path/to/main.py ... >>>FILE`.
Rules: No comments. No markdown fences. No explanation. Just the raw diff block.

Example format (do NOT copy this, use actual code from the program above):
<<<SEARCH
def foo():
    return 1
===
def foo():
    return 2
>>>REPLACE"""


def _render_metrics(program: Program) -> str:
    return ", ".join(f"{k}={v}" for k, v in program.metrics.items()) or "(none)"


def _render_program_files(program: Program) -> str:
    workspace = program.workspace()
    if len(workspace.files) == 1:
        return f"```python\n{workspace.code}\n```"
    rendered = []
    for path, content in sorted(workspace.files.items()):
        fence = "python" if path.endswith(".py") else ""
        rendered.append(f"--- FILE {path} ---\n```{fence}\n{content}\n```")
    return "\n\n".join(rendered)


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
        f"\n--- Inspiration {i + 1} (fitness {ins.fitness:.4f}; metrics: {_render_metrics(ins)}) ---\n{_render_program_files(ins)}\n"
        for i, ins in enumerate(inspirations)
    )


def _render_failures(recent_failures: list[tuple[str, float]] | None) -> str:
    if not recent_failures:
        return ""
    lines = "\n".join(f"  Score {score:.2f}: {code}" for code, score in recent_failures)
    return f"\n[RECENTLY FAILED - do NOT repeat these]\n{lines}\n"
