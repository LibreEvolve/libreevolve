import hashlib
import json
from unittest.mock import MagicMock
import math
from pathlib import Path

import pytest

from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.evaluator import EvaluationResult, EvaluationStageResult
from libreevolve.core.feedback import (
    apply_llm_feedback,
    build_critique_prompt,
    parse_feedback_response,
)
from libreevolve.core.jsonl import strict_json_dumps
from libreevolve.llm.ensemble import LLMEnsemble
from libreevolve.problems.loader import Problem


class _FeedbackBackend:
    def __init__(self, response: str) -> None:
        self.response = response

    def generate(self, prompt: str, role: str = "mutation") -> str:
        return self.response


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


def _problem_with_latency_metric():
    return Problem(
        name="p",
        task_description="make code simple",
        metrics=[
            {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
            {
                "name": "review_latency_ms",
                "direction": "minimize",
                "bounds": [0.0, 100.0],
                "source": "feedback",
            },
        ],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=[],
        problem_dir=Path("."),
    )


def test_build_critique_prompt_rejects_non_text_inputs():
    with pytest.raises(ValueError, match="base_prompt"):
        build_critique_prompt(None, "<<<SEARCH\nx\n===\ny\n>>>REPLACE")
    with pytest.raises(ValueError, match="mutation_text"):
        build_critique_prompt("base", {"diff": "x"})
    with pytest.raises(ValueError, match="critique_prompt"):
        build_critique_prompt("base", "mutation", {"api_key": "secret"})


def test_build_critique_prompt_rejects_empty_base_and_mutation_text():
    with pytest.raises(ValueError, match="base_prompt"):
        build_critique_prompt("   ", "mutation")
    with pytest.raises(ValueError, match="mutation_text"):
        build_critique_prompt("base", "\n\t")


def test_build_critique_prompt_redacts_secret_like_inputs_before_rendering():
    base_secret = "sk-proj_critique_base_secret_1234567890"
    mutation_secret = "ghp_critique_mutation_secret_1234567890"
    instruction_secret = "sk-proj_critique_instruction_secret_1234567890"

    prompt = build_critique_prompt(
        f"api_key={base_secret}\noriginal",
        f"token={mutation_secret}\n<<<SEARCH\nx\n===\ny\n>>>REPLACE",
        f"Review carefully with secret={instruction_secret}",
    )

    assert base_secret not in prompt
    assert mutation_secret not in prompt
    assert instruction_secret not in prompt
    assert prompt.count("[REDACTED]") == 3
    assert "[ORIGINAL PROMPT]" in prompt
    assert "[PROPOSED MUTATION]" in prompt


def test_build_critique_prompt_bounds_oversized_inputs():
    prompt = build_critique_prompt(
        "base-" + ("a" * 20_000),
        "mutation-" + ("b" * 20_000),
        "instruction-" + ("c" * 5000),
    )

    assert "[truncated" in prompt
    assert "a" * 13_000 not in prompt
    assert "b" * 9_000 not in prompt
    assert "c" * 3_000 not in prompt


def test_build_critique_prompt_uses_default_instruction_for_blank_custom_prompt():
    prompt = build_critique_prompt("base", "mutation", " ")

    assert prompt.startswith("Review the proposed mutation for correctness")
    assert "base" in prompt
    assert "mutation" in prompt


def test_parse_feedback_json_response():
    parsed = parse_feedback_response('{"score": 0.75, "feedback": "simple"}')
    assert parsed["score"] == 0.75
    assert parsed["feedback"] == "simple"


def test_parse_feedback_rejects_duplicate_json_names():
    with pytest.raises(ValueError, match="duplicate object name 'score'"):
        parse_feedback_response('{"score": 0.1, "score": 0.9, "feedback": "ambiguous"}')


def test_parse_feedback_rejects_nested_duplicate_json_names():
    with pytest.raises(ValueError, match="duplicate object name 'note'"):
        parse_feedback_response(
            '{"score": 0.5, "metadata": {"note": "first", "note": "second"}}'
        )


def test_parse_feedback_rejects_duplicate_names_in_fenced_json():
    response = '```json\n{"score": 0.1, "discard": true, "discard": false}\n```'

    with pytest.raises(ValueError, match="duplicate object name 'discard'"):
        parse_feedback_response(response)


def test_parse_feedback_numeric_fallback():
    parsed = parse_feedback_response("score: 0.5 because it is clear")
    assert parsed["score"] == 0.5


def test_parse_feedback_rejects_incidental_numbers_without_score_label():
    parsed = parse_feedback_response("I cannot grade this. HTTP 503 from reviewer.")
    assert "score" not in parsed
    assert "HTTP 503" in parsed["feedback"]


def test_parse_feedback_rejects_percentages_and_multi_number_prose():
    percent = parse_feedback_response("score: 90% confidence")
    multi = parse_feedback_response("attempt 1 of 2 looked better")

    assert "score" not in percent
    assert "score" not in multi


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
    assert updated.metadata["llm_feedback"][0]["normalized_score"] == 0.5
    assert updated.metadata["llm_feedback"][0]["score_bounds"] == [0.0, 1.0]
    assert updated.metadata["llm_feedback"][0]["score_direction"] == "maximize"
    assert updated.metadata["llm_feedback"][0]["weighted_delta"] == 0.1
    assert updated.metadata["llm_feedback"][0]["backend_idx"] == 2
    stage = updated.stages[-1]
    assert stage.name == "llm_feedback:simplicity"
    assert stage.passed is True
    assert stage.score == 0.5
    assert stage.metrics == {"simplicity": 0.5}
    assert stage.metadata["kind"] == "llm_feedback"
    assert stage.metadata["record_index"] == 0
    assert stage.metadata["backend_idx"] == 2
    assert stage.metadata["normalized_score"] == 0.5
    assert stage.metadata["score_bounds"] == [0.0, 1.0]
    assert stage.metadata["score_direction"] == "maximize"
    assert stage.metadata["weighted_delta"] == 0.1
    assert stage.error is None
    assert llm.generate.call_args.kwargs["role"] == "feedback:simplicity"


def test_apply_llm_feedback_rewards_configured_feedback_scheduler_role():
    llm = LLMEnsemble(
        [_FeedbackBackend('{"score": 0.75, "feedback": "good"}')],
        reward_accounted_roles=["mutation", "feedback:simplicity"],
    )
    result = EvaluationResult(
        fitness=0.4,
        metrics={"score": 0.4, "is_valid": True},
        is_valid=True,
    )

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 0.2}],
        llm,
    )

    record = updated.metadata["llm_feedback"][0]
    call_id = record["llm_call"]["id"]
    assert record["scheduler_reward"] == {
        "policy": "successful_feedback_normalized_score_v1",
        "applied": True,
        "reward": 0.75,
        "call_id": call_id,
        "backend_idx": 0,
    }
    role_state = llm.scheduler_state["role_scheduler_state"]["feedback:simplicity"]
    assert role_state["wins"] == [0.75]
    assert role_state["unrewarded_success_call_ids"] == [[]]
    assert role_state["rewarded_call_ids"] == [call_id]
    assert llm.last_call["rewarded"] is True
    assert llm.last_call["reward"] == 0.75


def test_apply_llm_feedback_leaves_telemetry_only_feedback_unrewarded():
    llm = LLMEnsemble([_FeedbackBackend('{"score": 0.75, "feedback": "good"}')])
    result = EvaluationResult(
        fitness=0.4,
        metrics={"score": 0.4, "is_valid": True},
        is_valid=True,
    )

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 0.2}],
        llm,
    )

    record = updated.metadata["llm_feedback"][0]
    assert record["scheduler_reward"] == {
        "policy": "successful_feedback_normalized_score_v1",
        "applied": False,
        "reward": 0.75,
        "reason": "telemetry_only_call",
    }
    assert llm.scheduler_state["role_scheduler_state"] == {}
    assert llm.last_call["rewarded"] is False


def test_apply_llm_feedback_redacts_bounds_and_hashes_successful_feedback_text():
    raw_secret = "sk-" + "proj_feedback_output_secret_1234567890"
    feedback_text = "secret=" + raw_secret + " " + ("x" * 800)
    response = json.dumps({"score": 0.5, "feedback": feedback_text})
    llm = MagicMock()
    llm.generate.return_value = (response, 2)
    result = EvaluationResult(fitness=0.4, metrics={"score": 0.4, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 0.2}],
        llm,
    )

    record = updated.metadata["llm_feedback"][0]
    serialized = strict_json_dumps(record)
    assert raw_secret not in serialized
    assert "[REDACTED]" in record["feedback"]
    assert "[truncated " in record["feedback"]
    assert "[REDACTED]" in record["raw_response"]
    assert record["feedback_retention"] == {
        "policy": "redact_bound_hash_v1",
        "retention_mode": "redacted",
        "sha256": hashlib.sha256(feedback_text.encode("utf-8")).hexdigest(),
        "chars": len(feedback_text),
        "stored_chars": len(record["feedback"]),
        "max_chars": 500,
        "redacted": True,
        "truncated": True,
    }
    assert record["raw_response_retention"]["policy"] == "redact_bound_hash_v1"
    assert record["raw_response_retention"]["retention_mode"] == "redacted"
    assert record["raw_response_retention"]["sha256"] == hashlib.sha256(
        response.encode("utf-8")
    ).hexdigest()
    assert record["raw_response_retention"]["chars"] == len(response)
    assert record["raw_response_retention"]["redacted"] is True


@pytest.mark.parametrize(
    ("mode", "expect_hash"),
    [
        ("hash_only", True),
        ("off", False),
    ],
)
def test_apply_llm_feedback_honors_feedback_retention_modes(mode, expect_hash):
    raw_secret = "sk-proj_feedback_retention_secret_1234567890"  # pragma: allowlist secret
    feedback_text = f"do not retain {raw_secret}"
    response = json.dumps({"score": 0.5, "feedback": feedback_text})
    llm = MagicMock()
    llm.generate.return_value = (response, 2)
    result = EvaluationResult(fitness=0.4, metrics={"score": 0.4, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 0.2}],
        llm,
        feedback_retention_mode=mode,
    )

    record = updated.metadata["llm_feedback"][0]
    serialized = strict_json_dumps(record)

    assert raw_secret not in serialized
    assert record["feedback"] is None
    assert record["raw_response"] is None
    assert record["feedback_retention"]["retention_mode"] == mode
    assert record["raw_response_retention"]["retention_mode"] == mode
    assert bool(record["feedback_retention"]["sha256"]) is expect_hash
    assert bool(record["raw_response_retention"]["sha256"]) is expect_hash
    assert record["feedback_retention"]["stored_chars"] == 0
    assert record["raw_response_retention"]["stored_chars"] == 0
    assert record["score"] == 0.5


def test_apply_llm_feedback_normalizes_bounded_maximize_score_for_fitness_delta():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 75, "feedback": "ok"}', 2)
    result = EvaluationResult(fitness=0.4, metrics={"score": 0.4, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [
            {
                "name": "quality",
                "metric": "quality_raw",
                "bounds": [0, 100],
                "direction": "maximize",
                "weight": 0.2,
                "min_score": 0.7,
            }
        ],
        llm,
    )

    record = updated.metadata["llm_feedback"][0]
    assert updated.metrics["quality_raw"] == 75.0
    assert record["score"] == 75.0
    assert record["normalized_score"] == 0.75
    assert record["score_bounds"] == [0.0, 100.0]
    assert record["score_direction"] == "maximize"
    assert record["weighted_delta"] == 0.15000000000000002
    assert updated.fitness == 0.55
    assert updated.is_valid is True


def test_apply_llm_feedback_normalizes_bounded_minimize_score_for_fitness_delta():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 25, "feedback": "lower is better"}', 2)
    result = EvaluationResult(fitness=0.4, metrics={"score": 0.4, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [
            {
                "name": "latency_review",
                "metric": "latency_ms",
                "bounds": [0, 100],
                "direction": "minimize",
                "weight": 0.2,
                "min_score": 0.7,
            }
        ],
        llm,
    )

    record = updated.metadata["llm_feedback"][0]
    assert updated.metrics["latency_ms"] == 25.0
    assert record["normalized_score"] == 0.75
    assert record["score_direction"] == "minimize"
    assert record["weighted_delta"] == 0.15000000000000002
    assert updated.fitness == 0.55
    assert updated.is_valid is True


def test_apply_llm_feedback_can_fill_declared_secondary_objective_metric():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 25, "feedback": "lower is better"}', 2)
    result = EvaluationResult(fitness=0.4, metrics={"score": 0.4, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem_with_latency_metric(),
        [
            {
                "name": "latency_review",
                "metric": "review_latency_ms",
                "objective_metric": True,
                "weight": 0.0,
            }
        ],
        llm,
    )

    record = updated.metadata["llm_feedback"][0]
    stage = updated.stages[-1]
    assert updated.metrics["review_latency_ms"] == 25.0
    assert record["normalized_score"] == 0.75
    assert record["score_bounds"] == [0.0, 100.0]
    assert record["score_direction"] == "minimize"
    assert record["objective_metric"] is True
    assert record["objective_metric_schema"] == {
        "name": "review_latency_ms",
        "bounds": [0.0, 100.0],
        "direction": "minimize",
        "primary": False,
        "metric_source": "feedback",
        "source": "problem_objective_schema",
    }
    assert stage.metadata["objective_metric"] is True
    assert stage.metadata["objective_metric_schema"]["name"] == "review_latency_ms"
    assert updated.fitness == 0.4


@pytest.mark.parametrize(
    ("grader", "message"),
    [
        (
            {"name": "bad", "metric": "unknown_metric", "objective_metric": True},
            "must reference a declared metric",
        ),
        (
            {"name": "bad", "metric": "score", "objective_metric": True},
            "cannot target the primary metric",
        ),
        (
            {"name": "bad", "metric": "score_secondary", "objective_metric": True},
            "must reference a declared metric",
        ),
        (
            {
                "name": "bad",
                "metric": "review_latency_ms",
                "objective_metric": True,
                "bounds": [0.0, 1.0],
            },
            "bounds must match problem metric bounds",
        ),
        (
            {
                "name": "bad",
                "metric": "review_latency_ms",
                "objective_metric": True,
                "direction": "maximize",
            },
            "direction must match problem metric direction",
        ),
        (
            {"name": "bad", "metric": "review_latency_ms", "objective_metric": "yes"},
            "objective_metric must be boolean",
        ),
    ],
)
def test_apply_llm_feedback_rejects_invalid_objective_metric_grader(grader, message):
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 25, "feedback": "ok"}', 2)
    result = EvaluationResult(fitness=0.4, metrics={"score": 0.4, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem_with_latency_metric(),
        [grader],
        llm,
    )

    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "invalid_feedback_config"
    assert message in record["message"]
    assert llm.generate.call_count == 0


def test_apply_llm_feedback_rejects_objective_metric_collision_with_evaluator_metric():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 25, "feedback": "ok"}', 2)
    result = EvaluationResult(
        fitness=0.4,
        metrics={"score": 0.4, "review_latency_ms": 90.0, "is_valid": True},
        is_valid=True,
    )

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem_with_latency_metric(),
        [{"name": "bad", "metric": "review_latency_ms", "objective_metric": True}],
        llm,
    )

    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "invalid_feedback_config"
    assert "conflicts with existing evaluation metric" in record["message"]
    assert updated.metrics["review_latency_ms"] == 90.0
    assert llm.generate.call_count == 0


def test_apply_llm_feedback_rejects_duplicate_json_names_without_score_side_effects():
    llm = MagicMock()
    llm.generate.return_value = (
        '{"score": 0.1, "score": 1.0, "discard": true, "discard": false, '
        '"feedback": "first", "feedback": "second"}',
        2,
    )
    result = EvaluationResult(fitness=0.2, metrics={"score": 0.2}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 1.0}],
        llm,
    )

    assert updated.fitness == 0.2
    assert updated.is_valid is True
    assert "simplicity" not in updated.metrics
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "llm_feedback_failed"
    assert record["exception"] == "ValueError"
    assert "duplicate object name 'score'" in record["message"]
    assert record["failure_delta"] == 0.0
    assert record["discard"] is False
    stage = updated.stages[-1]
    assert stage.name == "llm_feedback:simplicity"
    assert stage.error == "llm_feedback_failed"
    assert stage.score is None


def test_apply_llm_feedback_redacts_bounds_and_hashes_failed_raw_responses():
    raw_secret = "ghp_" + "feedback_failed_response_secret_1234567890"
    response = (
        '{"score": 0.1, "score": 0.9, "feedback": "token='
        + raw_secret
        + " "
        + ("z" * 1500)
        + '"}'
    )
    llm = MagicMock()
    llm.generate.return_value = (response, 2)
    result = EvaluationResult(fitness=0.2, metrics={"score": 0.2}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 1.0}],
        llm,
    )

    record = updated.metadata["llm_feedback"][0]
    attempt = record["failure_attempts"][0]
    serialized = strict_json_dumps(record)
    assert raw_secret not in serialized
    assert record["error"] == "llm_feedback_failed"
    assert "[REDACTED]" in record["raw_response"]
    assert "[truncated " in record["raw_response"]
    assert "[REDACTED]" in attempt["raw_response"]
    assert "[truncated " in attempt["raw_response"]
    assert record["raw_response_retention"] == {
        "policy": "redact_bound_hash_v1",
        "retention_mode": "redacted",
        "sha256": hashlib.sha256(response.encode("utf-8")).hexdigest(),
        "chars": len(response),
        "stored_chars": len(record["raw_response"]),
        "max_chars": 1000,
        "redacted": True,
        "truncated": True,
    }
    assert attempt["raw_response_retention"] == record["raw_response_retention"]


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


def test_apply_llm_feedback_prompt_includes_problem_context_with_provenance():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    problem = Problem(
        name="p",
        task_description="make code simple",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=[],
        problem_dir=Path("."),
        context_files={"constraints.md": "MUST return 42"},
        context_sources=[
            {
                "path": "constraints.md",
                "sha256": "abcdef1234567890",
                "chars_original": 14,
                "excerpt_start": 0,
                "excerpt_end": 14,
                "excerpt_page_spans": [
                    {
                        "page": 2,
                        "excerpt_start": 40,
                        "excerpt_end": 54,
                        "page_excerpt_start": 0,
                        "page_excerpt_end": 14,
                    }
                ],
                "extraction_status": "ok",
            }
        ],
    )

    apply_llm_feedback(
        EvaluationResult(fitness=0.4, metrics={"score": 0.4}, is_valid=True),
        CandidateWorkspace.from_code("x = 1"),
        problem,
        [{"name": "simplicity", "metric": "simplicity"}],
        llm,
    )

    prompt = llm.generate.call_args.args[0]
    assert "[CONTEXT]" in prompt
    assert "--- CONTEXT SOURCE: constraints.md" in prompt
    assert "sha256=abcdef123456" in prompt
    assert "pages=2:0-14" in prompt
    assert "MUST return 42" in prompt


def test_apply_llm_feedback_prompt_redacts_and_bounds_problem_context():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    secret = "sk-proj_feedbackcontextsecret1234567890"
    problem = Problem(
        name="p",
        task_description="make code simple",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=[],
        problem_dir=Path("."),
        context_files={
            "a.md": "secret " + secret + " " + ("a" * 5000),
            "b.md": "b" * 5000,
            "c.md": "c" * 5000,
        },
    )

    apply_llm_feedback(
        EvaluationResult(fitness=0.4, metrics={"score": 0.4}, is_valid=True),
        CandidateWorkspace.from_code("x = 1"),
        problem,
        [{"name": "simplicity", "metric": "simplicity"}],
        llm,
    )

    prompt = llm.generate.call_args.args[0]
    assert secret not in prompt
    assert "[REDACTED]" in prompt
    assert "[truncated" in prompt
    assert "context source(s) due to feedback prompt budget" in prompt


def test_apply_llm_feedback_prompt_redacts_and_truncates_workspace():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    workspace = CandidateWorkspace(
        files={
            "main.py": (
                "OPENAI_" + "API_" + "KEY = "
                + '"sk-' + 'proj-' + 'abcdefghijklmnopqrstuvwxyz"\n'
                + ("x = 1\n" * 1000)
            ),
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
    assert "sk-" + "proj-" + "abcdefghijklmnopqrstuvwxyz" not in prompt
    assert "[REDACTED]" in prompt
    assert "[truncated" in prompt


def test_apply_llm_feedback_rejects_mutated_non_finite_result_before_prompt():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    result = EvaluationResult(
        fitness=0.4,
        metrics={"score": 0.4, "is_valid": True},
        is_valid=True,
        stages=[
            EvaluationStageResult(
                name="stage",
                passed=False,
                error="OPENAI_API_KEY=sk-proj_feedbackdiag_secret_1234567890",  # pragma: allowlist secret
            )
        ],
    )
    result.fitness = math.nan
    result.metrics = {"score": math.nan, "latency": math.inf, "loss": -math.inf}
    result.elapsed_sec = math.inf
    result.stages[0].score = math.nan

    with pytest.raises(ValueError, match="EvaluationResult.fitness must be finite"):
        apply_llm_feedback(
            result,
            CandidateWorkspace.from_code("x = 1"),
            _problem(),
            [{"name": "simplicity", "metric": "simplicity"}],
            llm,
        )
    assert llm.generate.call_count == 0


def test_apply_llm_feedback_prompt_redacts_diagnostic_stdout_stderr_and_errors():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    stdout_secret = "sk-proj_feedbackstdoutsecret1234567890"
    stderr_secret = "ghp_feedbackstderrsecret1234567890"
    error_secret = "api_key=sk-proj_feedbackerrorsecret1234567890"  # pragma: allowlist secret
    stage_secret = "token=ghp_feedbackstagesecret1234567890"
    result = EvaluationResult(
        fitness=0.4,
        metrics={"score": 0.4, "is_valid": True},
        is_valid=True,
        stdout="stdout " + stdout_secret + " " + ("x" * 1500),
        stderr="stderr " + stderr_secret,
        error=error_secret,
        stages=[
            EvaluationStageResult(
                name="stage",
                passed=False,
                score=0.1,
                error=stage_secret,
                stdout="stage stdout " + stdout_secret,
                stderr="stage stderr " + stderr_secret,
            )
        ],
    )

    apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity"}],
        llm,
    )

    prompt = llm.generate.call_args.args[0]
    for secret in (stdout_secret, stderr_secret, error_secret, stage_secret):
        assert secret not in prompt
    assert "[REDACTED]" in prompt
    assert "[truncated" in prompt


def test_apply_llm_feedback_rejects_mutated_unsafe_metrics_before_prompt():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    key_secret = "api_key=sk-proj_feedbackmetrickeysecret1234567890"  # pragma: allowlist secret
    value_secret = "sk-proj_feedbackmetricvaluesecret1234567890"
    result = EvaluationResult(
        fitness=0.4,
        metrics={"score": 0.4, "is_valid": True},
        is_valid=True,
    )
    result.metrics = {
        "score": 0.4,
        "is_valid": True,
        key_secret: "normal",
        "plugin_note": value_secret + ("x" * 900),
        "long_note": "plain-" + ("z" * 900),
        "plugin_nested": {"token=ghp_feedbacknestedkey1234567890": value_secret},  # pragma: allowlist secret
    }

    with pytest.raises(ValueError, match="EvaluationResult.metrics must be JSON-safe"):
        apply_llm_feedback(
            result,
            CandidateWorkspace.from_code("x = 1"),
            _problem(),
            [{"name": "simplicity", "metric": "simplicity"}],
            llm,
        )
    assert llm.generate.call_count == 0


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
    stage = updated.stages[-1]
    assert stage.name == "llm_feedback:simplicity"
    assert stage.passed is False
    assert stage.score == 0.1
    assert stage.error == "llm_feedback_discard"
    assert stage.metadata["discard"] is True


def test_apply_llm_feedback_skips_later_graders_after_discard_by_default():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.1, "discard": true, "feedback": "reject"}', 0)
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [
            {"name": "first", "metric": "first", "weight": 0.2},
            {"name": "second", "metric": "second", "weight": 0.2},
        ],
        llm,
    )

    assert llm.generate.call_count == 1
    assert updated.is_valid is False
    assert "first" in updated.metrics
    assert "second" not in updated.metrics
    records = updated.metadata["llm_feedback"]
    assert records[0]["discard"] is True
    assert records[1]["error"] == "llm_feedback_skipped_invalid"
    assert records[1]["skipped"] is True
    assert [stage.name for stage in updated.stages[-2:]] == [
        "llm_feedback:first",
        "llm_feedback:second",
    ]
    assert updated.stages[-1].metadata["skipped"] is True
    assert updated.stages[-1].error == "llm_feedback_skipped_invalid"


def test_apply_llm_feedback_allows_post_discard_reviewer_with_include_invalid():
    llm = MagicMock()
    llm.generate.side_effect = [
        ('{"score": 0.1, "discard": true, "feedback": "reject"}', 0),
        ('{"score": 0.7, "feedback": "post review"}', 1),
    ]
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [
            {"name": "first", "metric": "first", "weight": 0.2},
            {"name": "second", "metric": "second", "weight": 0.2, "include_invalid": True},
        ],
        llm,
    )

    assert llm.generate.call_count == 2
    assert updated.is_valid is False
    assert updated.fitness == -0.1
    assert updated.metrics["first"] == 0.1
    assert updated.metrics["second"] == 0.7
    assert updated.metadata["llm_feedback"][1]["discard"] is False
    assert updated.metadata["llm_feedback"][1]["include_invalid"] is True
    assert updated.stages[-1].name == "llm_feedback:second"
    assert updated.stages[-1].passed is True
    assert updated.stages[-1].metadata["include_invalid"] is True


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

    assert updated is not result
    assert updated.fitness == result.fitness
    assert updated.metrics == result.metrics
    assert updated.metadata["llm_feedback"][0]["error"] == "llm_feedback_skipped_invalid"
    assert updated.stages[-1].name == "llm_feedback:simplicity"
    assert updated.stages[-1].metadata["skipped"] is True
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
    stage = updated.stages[-1]
    assert stage.name == "llm_feedback:simplicity"
    assert stage.passed is False
    assert stage.error == "llm_feedback_failed"
    assert stage.metadata["record_index"] == 0
    assert record["failure_policy"] == "ignore"
    assert record["failure_delta"] == 0.0
    assert record["failure_attempts"][0]["exception"] == "RuntimeError"
    assert stage.metadata["failure_policy"] == "ignore"
    assert stage.metadata["failure_attempt_count"] == 1


def test_apply_llm_feedback_retries_failed_grader_before_success():
    llm = MagicMock()
    llm.generate.side_effect = [
        RuntimeError("provider down"),
        ('{"score": 0.5, "feedback": "recovered"}', 1),
    ]
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [
            {
                "name": "simplicity",
                "metric": "simplicity",
                "weight": 0.2,
                "failure_retries": 1,
            }
        ],
        llm,
    )

    assert llm.generate.call_count == 2
    assert updated.fitness == 0.9
    assert updated.is_valid is True
    assert updated.metrics["simplicity"] == 0.5
    record = updated.metadata["llm_feedback"][0]
    assert record["retry_attempts"] == 1
    assert record["failure_attempts"][0]["message"] == "provider down"
    assert record["backend_idx"] == 1
    assert "error" not in record
    stage = updated.stages[-1]
    assert stage.passed is True
    assert stage.metadata["retry_attempts"] == 1
    assert stage.metadata["failure_attempt_count"] == 1


def test_apply_llm_feedback_penalizes_exhausted_failed_grader():
    llm = MagicMock()
    llm.generate.side_effect = [RuntimeError("first"), RuntimeError("second")]
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [
            {
                "name": "simplicity",
                "metric": "simplicity",
                "weight": 0.2,
                "failure_policy": "penalize",
                "failure_retries": 1,
                "failure_penalty": 0.25,
            }
        ],
        llm,
    )

    assert llm.generate.call_count == 2
    assert updated.fitness == 0.55
    assert updated.is_valid is True
    assert updated.metrics["feedback_adjusted_fitness"] == 0.55
    assert "simplicity" not in updated.metrics
    record = updated.metadata["llm_feedback"][0]
    assert record["failure_policy"] == "penalize"
    assert record["failure_delta"] == -0.25
    assert len(record["failure_attempts"]) == 2
    assert record["message"] == "second"
    stage = updated.stages[-1]
    assert stage.error == "llm_feedback_failed"
    assert stage.metadata["failure_delta"] == -0.25
    assert stage.metadata["failure_attempt_count"] == 2


def test_apply_llm_feedback_penalize_policy_defaults_penalty_to_weight():
    llm = MagicMock()
    llm.generate.side_effect = RuntimeError("provider down")
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [
            {
                "name": "simplicity",
                "metric": "simplicity",
                "weight": 0.2,
                "failure_policy": "penalize",
            }
        ],
        llm,
    )

    assert math.isclose(updated.fitness, 0.6)
    assert updated.metadata["llm_feedback"][0]["failure_delta"] == -0.2


def test_apply_llm_feedback_discards_exhausted_failed_grader():
    llm = MagicMock()
    llm.generate.side_effect = RuntimeError("provider down")
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [
            {
                "name": "simplicity",
                "metric": "simplicity",
                "weight": 0.2,
                "failure_policy": "discard",
            }
        ],
        llm,
    )

    assert updated.fitness == -0.1
    assert updated.is_valid is False
    assert updated.error == "llm_feedback_discard"
    assert "simplicity" not in updated.metrics
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "llm_feedback_failed"
    assert record["failure_policy"] == "discard"
    assert record["discard"] is True
    stage = updated.stages[-1]
    assert stage.error == "llm_feedback_failed"
    assert stage.metadata["discard"] is True
    assert stage.metadata["failure_policy"] == "discard"


def test_apply_llm_feedback_redacts_and_bounds_backend_failure_message():
    raw_secret = "ghp_feedbackfailuresecret1234567890"
    llm = MagicMock()
    llm.generate.side_effect = RuntimeError(
        "feedback provider failed token=" + raw_secret + " " + ("x" * 800)
    )
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 0.2}],
        llm,
    )

    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "llm_feedback_failed"
    assert raw_secret not in record["message"]
    assert "[REDACTED]" in record["message"]
    assert "[truncated " in record["message"]
    assert record["message"].endswith(" chars]")
    assert len(record["message"]) <= 525


def test_apply_llm_feedback_records_failure_when_exception_stringification_breaks():
    class BrokenStrError(RuntimeError):
        def __str__(self):
            raise RuntimeError("format failed")

    llm = MagicMock()
    llm.generate.side_effect = BrokenStrError()
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
    assert record["exception"] == "BrokenStrError"
    assert record["message"] == (
        "<exception message unavailable; __str__ raised RuntimeError>"
    )


def test_apply_llm_feedback_sanitizes_direct_llm_call_telemetry():
    raw_secret = "sk-proj_feedback_call_secret_1234567890"  # pragma: allowlist secret

    class DirectLLM:
        def __init__(self):
            self.last_call = None

        def generate(self, prompt, role):
            self.last_call = {
                "role": role,
                "api_key": raw_secret,
                "bad": object(),
                "long": "x" * 900,
                "many": list(range(25)),
                "nested": {"token": raw_secret},
            }
            return '{"score": 0.5, "feedback": "ok"}', 0

    updated = apply_llm_feedback(
        EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True),
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity"}],
        DirectLLM(),
    )

    payload = strict_json_dumps(updated.to_dict())
    assert raw_secret not in payload
    record_call = updated.metadata["llm_feedback"][0]["llm_call"]
    stage_call = updated.stages[-1].metadata["llm_call"]
    assert record_call == stage_call
    assert record_call["api_key"] == "[REDACTED]"
    assert record_call["nested"]["token"] == "[REDACTED]"
    assert record_call["bad"]["value_type"] == "object"
    assert len(record_call["many"]) == 20
    assert "[truncated " in record_call["long"]
    safety = record_call["telemetry_safety"]
    assert safety["redacted"] is True
    assert safety["stringified_values"] >= 1
    assert safety["omitted_items"] == 5
    assert safety["truncated_strings"] >= 1


def test_apply_llm_feedback_bounds_oversized_direct_llm_call_telemetry():
    class DirectLLM:
        def __init__(self):
            self.last_call = None

        def generate(self, prompt, role):
            self.last_call = {f"k{i}": "y" * 900 for i in range(25)}
            return '{"score": 0.5, "feedback": "ok"}', 0

    updated = apply_llm_feedback(
        EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True),
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity"}],
        DirectLLM(),
    )

    strict_json_dumps(updated.to_dict())
    call = updated.metadata["llm_feedback"][0]["llm_call"]
    assert call["telemetry_safety"]["omitted"] is True
    assert call["telemetry_safety"]["json_chars"] > call["telemetry_safety"]["max_json_chars"]
    assert len(call["preview"]) <= call["telemetry_safety"]["max_json_chars"] + 30
    assert updated.stages[-1].metadata["llm_call"] == call


def test_apply_llm_feedback_rejects_unsafe_direct_grader_labels_without_llm_call():
    llm = MagicMock()
    secret_like = "api_key=sk-proj_feedbacklabel_secret_1234567890"  # pragma: allowlist secret
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": secret_like, "metric": "bad metric", "weight": 0.2}],
        llm,
    )

    llm.generate.assert_not_called()
    assert updated.fitness == 0.8
    assert secret_like not in str(updated.metadata)
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "invalid_feedback_config"
    assert record["backend_idx"] is None


def test_apply_llm_feedback_rejects_non_text_direct_prompt_without_llm_call():
    llm = MagicMock()
    secret_like = "api_key=sk-proj_feedback_prompt_secret_1234567890"  # pragma: allowlist secret
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "review", "metric": "llm_review", "prompt": {"secret": secret_like}}],
        llm,
    )

    llm.generate.assert_not_called()
    payload = strict_json_dumps(updated.to_dict())
    assert secret_like not in payload
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "invalid_feedback_config"
    assert record["message"] == "llm_feedback.prompt must be a string"
    assert updated.stages[-1].error == "invalid_feedback_config"


def test_apply_llm_feedback_rejects_unsupported_direct_grader_fields():
    llm = MagicMock()
    secret_field = "api_key=sk-proj_feedback_schema_secret_1234567890"  # pragma: allowlist secret

    updated = apply_llm_feedback(
        EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True),
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "review", "metric": "llm_review", secret_field: "unused"}],
        llm,
    )

    llm.generate.assert_not_called()
    payload = strict_json_dumps(updated.to_dict())
    assert secret_field not in payload
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "invalid_feedback_config"
    assert "unsupported fields" in record["message"]
    assert "[REDACTED]" in record["message"]


def test_apply_llm_feedback_rejects_non_string_direct_grader_keys():
    llm = MagicMock()

    updated = apply_llm_feedback(
        EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True),
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "review", "metric": "llm_review", 7: "unused"}],
        llm,
    )

    llm.generate.assert_not_called()
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "invalid_feedback_config"
    assert "keys must be strings" in record["message"]
    assert updated.stages[-1].error == "invalid_feedback_config"


def test_apply_llm_feedback_records_non_mapping_grader_on_invalid_candidate():
    llm = MagicMock()

    updated = apply_llm_feedback(
        EvaluationResult(fitness=-0.1, metrics={"score": -0.1, "is_valid": False}, is_valid=False),
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        ["not-a-mapping"],
        llm,
    )

    llm.generate.assert_not_called()
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "invalid_feedback_config"
    assert record["message"] == "llm_feedback grader must be a mapping"
    assert updated.stages[-1].error == "invalid_feedback_config"


def test_apply_llm_feedback_uses_default_instruction_for_blank_direct_prompt():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)

    apply_llm_feedback(
        EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True),
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "review", "metric": "llm_review", "prompt": "  "}],
        llm,
    )

    prompt = llm.generate.call_args.args[0]
    assert prompt.startswith("Grade this candidate. Return JSON")


def test_apply_llm_feedback_redacts_and_bounds_direct_prompt_before_llm_call():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    secret_like = "sk-proj_feedback_prompt_secret_1234567890"  # pragma: allowlist secret

    apply_llm_feedback(
        EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True),
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [
            {
                "name": "review",
                "metric": "llm_review",
                "prompt": "Use token=" + secret_like + " " + ("x" * 5000),
            }
        ],
        llm,
    )

    prompt = llm.generate.call_args.args[0]
    instruction = prompt.split("\n\n[TASK]\n", 1)[0]
    assert secret_like not in prompt
    assert "token=[REDACTED]" in instruction
    assert "[truncated" in instruction
    assert len(instruction) <= 2030


def test_apply_llm_feedback_rejects_metric_names_that_program_metrics_reject():
    llm = MagicMock()
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "review", "metric": "llm-score", "weight": 0.2}],
        llm,
    )

    llm.generate.assert_not_called()
    assert updated.fitness == 0.8
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "invalid_feedback_config"
    assert "manifest-safe metric name" in record["message"]
    assert "llm-score" not in updated.metrics


def test_apply_llm_feedback_rejects_existing_evaluator_metric_collision():
    llm = MagicMock()
    result = EvaluationResult(
        fitness=0.8,
        metrics={"score": 0.8, "latency": 0.2, "is_valid": True},
        is_valid=True,
    )

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "review", "metric": "latency", "weight": 0.2}],
        llm,
    )

    llm.generate.assert_not_called()
    assert updated.metrics == result.metrics
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "invalid_feedback_config"
    assert "conflicts with existing evaluation metric" in record["message"]
    assert updated.stages[-1].error == "invalid_feedback_config"


def test_apply_llm_feedback_rejects_reserved_feedback_metric_name():
    llm = MagicMock()
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "review", "metric": "feedback_adjusted_fitness", "weight": 0.2}],
        llm,
    )

    llm.generate.assert_not_called()
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "invalid_feedback_config"
    assert "reserved" in record["message"]
    assert "feedback_adjusted_fitness" not in updated.metrics


def test_apply_llm_feedback_rejects_is_valid_feedback_metric_name():
    llm = MagicMock()
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "review", "metric": "is_valid", "weight": 0.2}],
        llm,
    )

    llm.generate.assert_not_called()
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "invalid_feedback_config"
    assert "manifest-safe metric name" in record["message"]
    assert "is_valid" not in updated.metrics


def test_apply_llm_feedback_rejects_duplicate_feedback_metric_in_same_call():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [
            {"name": "first", "metric": "llm_review", "weight": 0.2},
            {"name": "second", "metric": "llm_review", "weight": 0.2},
        ],
        llm,
    )

    assert llm.generate.call_count == 1
    assert updated.metrics["llm_review"] == 0.5
    assert updated.metadata["llm_feedback"][0]["name"] == "first"
    assert updated.metadata["llm_feedback"][1]["error"] == "invalid_feedback_config"
    assert "conflicts with existing evaluation metric" in updated.metadata["llm_feedback"][1]["message"]


def test_apply_llm_feedback_rejects_invalid_direct_numeric_policy_without_llm_call():
    llm = MagicMock()
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [
            {"name": "bad_weight", "metric": "bad_weight", "weight": "not-a-number"},
            {"name": "bad_bool", "metric": "bad_bool", "weight": True},
            {"name": "bad_weight_negative", "metric": "bad_weight_negative", "weight": -0.1},
            {"name": "bad_weight_large", "metric": "bad_weight_large", "weight": 1.1},
            {"name": "bad_min", "metric": "bad_min", "min_score": math.inf},
            {"name": "bad_min_negative", "metric": "bad_min_negative", "min_score": -0.1},
            {"name": "bad_min_large", "metric": "bad_min_large", "min_score": 1.1},
            {"name": "bad_bounds", "metric": "bad_bounds", "bounds": [1.0, 1.0]},
            {"name": "bad_bounds_type", "metric": "bad_bounds_type", "bounds": "0,1"},
            {"name": "bad_direction", "metric": "bad_direction", "direction": "lower"},
            {"name": "bad_include", "metric": "bad_include", "include_invalid": "yes"},
        ],
        llm,
    )

    llm.generate.assert_not_called()
    assert updated.fitness == 0.8
    assert updated.is_valid is True
    assert updated.metrics == {"score": 0.8, "is_valid": True}
    records = updated.metadata["llm_feedback"]
    assert [record["error"] for record in records] == ["invalid_feedback_config"] * 11
    assert "weight" in records[0]["message"]
    assert "weight" in records[1]["message"]
    assert "between 0 and 1" in records[2]["message"]
    assert "between 0 and 1" in records[3]["message"]
    assert "min_score" in records[4]["message"]
    assert "between 0 and 1" in records[5]["message"]
    assert "between 0 and 1" in records[6]["message"]
    assert "strictly increasing" in records[7]["message"]
    assert "bounds" in records[8]["message"]
    assert "direction" in records[9]["message"]
    assert "include_invalid" in records[10]["message"]


def test_apply_llm_feedback_allows_zero_weight_without_fitness_delta():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "weight": 0.0}],
        llm,
    )

    assert updated.fitness == 0.8
    assert updated.metrics["simplicity"] == 0.5
    assert updated.metadata["llm_feedback"][0]["weighted_delta"] == 0.0
    assert updated.stages[-1].metadata["weighted_delta"] == 0.0


def test_apply_llm_feedback_invalid_policy_does_not_block_valid_grader():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [
            {"name": "bad_weight", "metric": "bad_weight", "weight": "not-a-number"},
            {"name": "simplicity", "metric": "simplicity", "weight": 0.2},
        ],
        llm,
    )

    assert llm.generate.call_count == 1
    assert updated.fitness == 0.9
    assert "bad_weight" not in updated.metrics
    assert updated.metrics["simplicity"] == 0.5
    assert updated.metadata["llm_feedback"][0]["error"] == "invalid_feedback_config"
    assert updated.metadata["llm_feedback"][1]["name"] == "simplicity"


def test_apply_llm_feedback_rejects_invalid_policy_before_metric_side_effects():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 0.5, "feedback": "ok"}', 2)
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [{"name": "simplicity", "metric": "simplicity", "min_score": "not-a-number"}],
        llm,
    )

    llm.generate.assert_not_called()
    assert updated.fitness == result.fitness
    assert updated.metrics == result.metrics
    assert "simplicity" not in updated.metrics
    assert updated.metadata["llm_feedback"][0]["error"] == "invalid_feedback_config"


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


def test_apply_llm_feedback_rejects_incidental_status_code_as_score():
    llm = MagicMock()
    llm.generate.return_value = ("I cannot grade this. HTTP 503 from reviewer.", 1)
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


def test_apply_llm_feedback_rejects_out_of_bounds_score():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 1.5, "feedback": "too high"}', 1)
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
    assert "within configured bounds [0.0, 1.0]" in updated.metadata["llm_feedback"][0]["message"]


def test_apply_llm_feedback_rejects_score_outside_configured_bounds():
    llm = MagicMock()
    llm.generate.return_value = ('{"score": 125, "feedback": "too high"}', 1)
    result = EvaluationResult(fitness=0.8, metrics={"score": 0.8, "is_valid": True}, is_valid=True)

    updated = apply_llm_feedback(
        result,
        CandidateWorkspace.from_code("x = 1"),
        _problem(),
        [
            {
                "name": "quality",
                "metric": "quality_raw",
                "bounds": [0, 100],
                "weight": 0.2,
            }
        ],
        llm,
    )

    assert updated.fitness == 0.8
    assert "quality_raw" not in updated.metrics
    record = updated.metadata["llm_feedback"][0]
    assert record["error"] == "llm_feedback_failed"
    assert "within configured bounds [0.0, 100.0]" in record["message"]


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
