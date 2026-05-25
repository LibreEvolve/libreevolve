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

    assert "--- CONTEXT SOURCE: notes.md ---" in prompt
    assert "Prefer simple arithmetic." in prompt
    assert "score=0.25" in prompt
    assert "- validate: passed, score=0.25" in prompt


def test_prompt_sampler_renders_context_citations_when_sources_are_available():
    problem = Problem(
        name="demo",
        task_description="Improve solve().",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=["x=1"],
        problem_dir=Path("."),
        context_files={"papers/a.md": "alpha context"},
        context_sources=[
            {
                "path": "papers/a.md",
                "sha256": "1234567890abcdef",
                "chars_original": 13,
                "excerpt_start": 0,
                "excerpt_end": 13,
                "extraction_status": "ok",
            }
        ],
    )
    parent = Program(code="x=1", fitness=0.0)

    prompt = PromptSampler().build(parent, [], problem, extra_context="")

    assert (
        "--- CONTEXT SOURCE: papers/a.md "
        "(sha256=1234567890ab, chars=13, excerpt=0:13, status=ok) ---"
    ) in prompt
    assert "alpha context" in prompt


def test_prompt_sampler_renders_multi_file_candidates():
    problem = Problem(
        name="demo",
        task_description="Improve solve().",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=[],
        problem_dir=Path("."),
    )
    parent = Program(
        files={"main.py": "from helper import solve\n", "helper.py": "def solve(): return 1\n"},
        primary_file="main.py",
        fitness=0.0,
    )

    prompt = PromptSampler().build(parent, [], problem, extra_context="", recent_failures=[])

    assert "--- FILE helper.py ---" in prompt
    assert "--- FILE main.py ---" in prompt
    assert "<<<FILE path" in prompt


def test_default_prompt_mentions_canonical_diff_fences():
    problem = Problem(
        name="demo",
        task_description="Improve solve().",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=["def solve():\n    return 1\n"],
        problem_dir=Path("."),
    )
    parent = Program(code="def solve():\n    return 1\n", fitness=0.0)

    prompt = PromptSampler().build(parent, [], problem, extra_context="", recent_failures=[])

    assert "AlphaEvolve-style" in prompt
    assert "`<<<<<<< SEARCH`" in prompt
    assert "`>>>>>>> REPLACE`" in prompt


def test_default_prompt_uses_full_replacement_instructions_for_full_mode():
    problem = Problem(
        name="demo",
        task_description="Improve solve().",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=["def solve():\n    return 1\n"],
        problem_dir=Path("."),
    )
    parent = Program(code="def solve():\n    return 1\n", fitness=0.0)

    prompt = PromptSampler().build(
        parent,
        [],
        problem,
        extra_context="",
        recent_failures=[],
        mutation_mode="full",
    )

    assert "Mutation mode: full" in prompt
    assert "Return full replacement code, not SEARCH/REPLACE diffs." in prompt
    assert "<<<BLOCK block_name" in prompt
    assert "Example format (do NOT copy this" not in prompt


def test_custom_prompt_templates_can_use_or_ignore_mutation_mode_fields():
    problem = Problem(
        name="demo",
        task_description="Improve solve().",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=["x=1"],
        problem_dir=Path("."),
    )
    parent = Program(code="x=1", fitness=0.0)

    ignored = PromptSampler().build(
        parent, [], problem, extra_context="", template="Task: {task}",
        mutation_mode="full",
    )
    rendered = PromptSampler().build(
        parent, [], problem, extra_context="",
        template="{mutation_mode}\n{mutation_instructions}",
        mutation_mode="full",
    )

    assert ignored == "Task: Improve solve()."
    assert rendered.startswith("full\nReturn full replacement code")


def test_prompt_sampler_renders_structured_failure_records():
    problem = Problem(
        name="demo",
        task_description="Improve solve().",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=["x=1"],
        problem_dir=Path("."),
    )
    parent = Program(code="x=1", fitness=0.0)

    prompt = PromptSampler().build(
        parent,
        [],
        problem,
        extra_context="",
        recent_failures=[
            {
                "score": -0.4,
                "error": "no_diff_blocks",
                "diff_error": "no_diff_blocks",
                "changed_files": [],
                "repetition_count": 2,
                "mutation_text": "not a diff",
            }
        ],
    )

    assert "RECENTLY FAILED" in prompt
    assert "diff_error=no_diff_blocks" in prompt
    assert "changed_files=(none)" in prompt
    assert "repeats=2" in prompt
