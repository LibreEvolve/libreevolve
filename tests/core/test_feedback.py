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


def test_parse_feedback_without_score_keeps_feedback_only():
    parsed = parse_feedback_response("unclear")
    assert "score" not in parsed
    assert parsed["feedback"] == "unclear"


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


def test_apply_llm_feedback_prompt_includes_full_workspace():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    workspace = CandidateWorkspace(
        files={
            "main.py": "from helper import value\nresult = value()\n",
            "helper.py": "def value():\n    return 41\n",
        },
        primary_file="main.py",
    )
    result = EvaluationResult(
        fitness=0.4,
        metrics={"score": 0.4, "is_valid": True},
        is_valid=True,
        stdout="validator output",
    )

    apply_llm_feedback(
        result,
        workspace,
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 0.2}],
        llm,
    )

    prompt = llm.generate.call_args.args[0]
    assert "Primary file: main.py" in prompt
    assert "--- FILE helper.py ---" in prompt
    assert "def value():" in prompt
    assert "validator output" in prompt


def test_apply_llm_feedback_prompt_redacts_and_truncates_workspace():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    workspace = CandidateWorkspace(
        files={
            "main.py": 'OPENAI_API_KEY = "sk-proj_abcdefghijklmnopqrstuvwxyz"\n'
            + ("x = 1\n" * 1000),
        },
        primary_file="main.py",
    )
    result = EvaluationResult(fitness=0.4, metrics={"score": 0.4}, is_valid=True)

    apply_llm_feedback(
        result,
        workspace,
        _problem(),
        [{"name": "simplicity", "metric": "simplicity"}],
        llm,
    )

    prompt = llm.generate.call_args.args[0]
    assert "sk-proj_abcdefghijklmnopqrstuvwxyz" not in prompt
    assert "[REDACTED]" in prompt
    assert "[truncated" in prompt


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


def test_apply_llm_feedback_records_backend_failure_without_changing_score():
    llm = MagicMock()
    llm.generate.side_effect = RuntimeError("provider down")
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 0.2}],
        llm,
    )

    assert updated.fitness == 0.8
    assert updated.is_valid is True
    assert "simplicity" not in updated.metrics
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "llm_feedback_failed"
    assert record["exception"] == "RuntimeError"


def test_apply_llm_feedback_records_malformed_response_score():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": "bad", "feedback": "no"}', 1)
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 0.2}],
        llm,
    )

    assert updated.fitness == 0.8
    assert "simplicity" not in updated.metrics
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "llm_feedback_failed"
    assert "score" in record["message"]
    assert record["backend_idx"] == 1


def test_apply_llm_feedback_records_string_discard_without_discarding():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.9, "discard": "false"}', 1)
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 0.2}],
        llm,
    )

    assert updated.is_valid is True
    assert updated.fitness == 0.8
    assert "simplicity" not in updated.metrics
    assert "discard" in updated.metadata["llm_feedback"][0]["message"]


def test_apply_llm_feedback_records_non_finite_score():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": NaN}', 1)
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 0.2}],
        llm,
    )

    assert updated.fitness == 0.8
    assert "finite" in updated.metadata["llm_feedback"][0]["message"]
