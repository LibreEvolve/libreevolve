import os, tempfile
import pytest
from pathlib import Path
from alphaevolve.core.config import Config
from alphaevolve.core.loop import evolve
from alphaevolve.problems.loader import load_problem

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="no API key")
def test_hello_world_completes():
    """10 generations on hello_world must complete without error."""
    examples = Path(__file__).parent.parent.parent / "alphaevolve/problems/examples/hello_world"
    problem = load_problem(examples)
    config = Config(
        max_generations=10, num_inspirations=2,
        log_dir=tempfile.mkdtemp(), problem_name="hw_test",
        backends=[{"type": "anthropic", "model": "claude-haiku-4-5-20251001"}],
        eval_timeout_sec=10.0,
    )
    best = evolve(problem, config)
    assert best is not None and isinstance(best.fitness, float) and best.code != ""

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="no API key")
def test_hello_world_fitness_non_negative():
    examples = Path(__file__).parent.parent.parent / "alphaevolve/problems/examples/hello_world"
    problem = load_problem(examples)
    config = Config(max_generations=10, log_dir=tempfile.mkdtemp(), problem_name="hw_fitness",
                    backends=[{"type": "anthropic", "model": "claude-haiku-4-5-20251001"}],
                    eval_timeout_sec=10.0)
    best = evolve(problem, config)
    assert best.fitness >= 0.0
