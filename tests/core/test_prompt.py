from pathlib import Path

from libreevolve.core.prompt import PromptSampler
from libreevolve.population.program import Program
from libreevolve.problems.loader import Problem


def test_prompt_sampler_renders_context_and_feedback():
    problem = Problem(
        name="demo",
        task_description="Improve solve().",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=["def solve():\n    return 1\n"],
        problem_dir=Path("."),
        context_files={"notes.md": "Prefer simple arithmetic."},
    )
    parent = Program(
        id="p0",
        code="def solve():\n    return 1\n",
        fitness=0.25,
        metrics={"score": 0.25, "is_valid": True},
        evaluation={
            "stages": [
                {"name": "syntax", "passed": True, "score": None},
                {"name": "validate", "passed": True, "score": 0.25},
            ]
        },
    )

    prompt = PromptSampler().build(parent, [], problem, extra_context="", recent_failures=[])

    assert "Prefer simple arithmetic." in prompt
    assert "score=0.25" in prompt
    assert "- validate: passed, score=0.25" in prompt
