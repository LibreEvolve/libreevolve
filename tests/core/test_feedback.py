from unittest.mock import MagicMock
from pathlib import Path

from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.evaluator import EvaluationResult
from libreevolve.core.feedback import apply_llm_feedback, parse_feedback_response
from libreevolve.problems.loader import Problem


def _problem():
    return Problem(
        name="p",
        task_description="make code simple",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=[],
        problem_dir=Path("."),
    )


def test_parse_feedback_json_response():
    parsed = parse_feedback_response('{"score": 0.75, "feedback": "simple"}')
    assert parsed["score"] == 0.75
    assert parsed["feedback"] == "simple"


def test_parse_feedback_numeric_fallback():
    parsed = parse_feedback_response("score: 0.5 because it is clear")
    assert parsed["score"] == 0.5


def test_apply_llm_feedback_adds_metric_and_weighted_score():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    result = EvaluationResult(fitness=0.4, metrics={"score": 0.4, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 0.2}],
        llm,
    )

    assert updated.fitness == 0.5
    assert updated.metrics["simplicity"] == 0.5
    assert updated.metadata["llm_feedback"][0]["backend_idx"] == 2


def test_apply_llm_feedback_can_discard_candidate():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.1, "feedback": "too complex"}', 0)
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "min_score": 0.5}],
        llm,
    )

    assert updated.is_valid is False
    assert updated.fitness == -0.1
    assert updated.error == "llm_feedback_discard"


def test_apply_llm_feedback_skips_invalid_candidates_by_default():
    llm = MagicMock()
    result = EvaluationResult(
        fitness=-0.2,
        metrics={"score": -0.2, "is_valid": False},
        is_valid=False,
        error="syntax_error",
    )

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x ="),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 0.2}],
        llm,
    )

    assert updated is result
    llm.generate.assert_not_called()
