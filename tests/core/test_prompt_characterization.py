"""Focused characterization tests for the prompt sampler state boundaries."""

from __future__ import annotations

import random
from pathlib import Path

from libreevolve.core.prompt import (
    PROMPT_CONTEXT_POLICY_SCHEMA,
    PromptSampler,
    prompt_context_policy_sha256,
    validate_prompt_context_policy,
)
from libreevolve.population.program import Program
from libreevolve.problems.loader import Problem


_TEMPLATE = "{task}\n{context}\n{mutation_instructions}"


def _problem(*, context_files: dict[str, str] | None = None) -> Problem:
    return Problem(
        name="prompt-characterization",
        task_description="Improve solve().",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=["x = 1\n"],
        problem_dir=Path("."),
        context_files=dict(context_files or {}),
    )


def _parent() -> Program:
    return Program(
        id="parent",
        code="x = 1\n",
        fitness=0.25,
        metrics={"score": 0.25},
    )


def test_prompt_sampler_overwrites_last_call_side_channels_and_copies_policy():
    sampler = PromptSampler()
    policy = {
        "disabled_sections": ["context"],
        "section_priorities": {"extra_context": 2},
    }

    sampler.build(
        _parent(),
        [],
        _problem(context_files={"notes.md": "first context"}),
        extra_context="",
        template=_TEMPLATE,
        context_policy=policy,
    )
    first_context = sampler.last_context_text
    first_metadata = sampler.last_metadata

    policy["disabled_sections"].append("recent_failures")
    policy["section_priorities"]["extra_context"] = 99

    assert "first context" in first_context
    assert first_metadata["prompt_context_policy"]["schema"] == (
        PROMPT_CONTEXT_POLICY_SCHEMA
    )
    assert first_metadata["prompt_context_policy"]["disabled_sections"] == [
        "context"
    ]
    assert first_metadata["prompt_context_policy"]["section_priorities"] == {
        "extra_context": 2
    }

    sampler.build(
        _parent(),
        [],
        _problem(),
        extra_context="",
        template=_TEMPLATE,
    )

    assert sampler.last_context_text == "(none)"
    assert sampler.last_metadata is not first_metadata
    assert sampler.last_metadata["context_order"] == []
    assert first_metadata["context_order"] == ["notes.md"]
    assert "first context" in first_context


def test_prompt_context_policy_normalization_is_defensive_and_hash_is_deterministic():
    raw_policy = {
        "section_priorities": {"extra_context": 7},
        "context_source_required_terms": ["Matrix", "matrix"],
        "disabled_sections": ["context", "context"],
    }
    equivalent_policy = {
        "disabled_sections": ["context"],
        "context_source_required_terms": ["matrix"],
        "section_priorities": {"extra_context": 7},
    }

    normalized = validate_prompt_context_policy(raw_policy)

    assert normalized["schema"] == PROMPT_CONTEXT_POLICY_SCHEMA
    assert normalized["disabled_sections"] == ["context"]
    assert normalized["context_source_required_terms"] == ["matrix"]
    assert normalized["section_priorities"] == {"extra_context": 7}
    assert normalized["disabled_sections"] is not raw_policy["disabled_sections"]
    assert normalized["context_source_required_terms"] is not raw_policy[
        "context_source_required_terms"
    ]
    assert normalized["section_priorities"] is not raw_policy["section_priorities"]

    first_hash = prompt_context_policy_sha256(raw_policy)
    assert first_hash == prompt_context_policy_sha256(raw_policy)
    assert first_hash == prompt_context_policy_sha256(equivalent_policy)
    assert first_hash == prompt_context_policy_sha256(normalized)

    raw_policy["disabled_sections"].append("recent_failures")
    raw_policy["context_source_required_terms"].append("kernel")
    raw_policy["section_priorities"]["extra_context"] = 99

    assert normalized["disabled_sections"] == ["context"]
    assert normalized["context_source_required_terms"] == ["matrix"]
    assert normalized["section_priorities"] == {"extra_context": 7}


def test_prompt_sampler_reuses_the_supplied_run_owned_rng_in_draw_order():
    variants = ["first {task}", "second {task}", "third {task}"]
    run_rng = random.Random(2026)
    expected_rng = random.Random(2026)
    sampler = PromptSampler(variants=variants, rng=run_rng)

    expected_variant = expected_rng.choice(variants)
    prompt = sampler.build(_parent(), [], _problem(), extra_context="")

    assert sampler.rng is run_rng
    assert prompt == expected_variant.format(task="Improve solve().")
    assert run_rng.getstate() == expected_rng.getstate()


def test_prompt_sampler_does_not_advance_process_global_rng():
    global_state = random.getstate()
    expected_global_rng = random.Random()
    expected_global_rng.setstate(global_state)
    expected_next = expected_global_rng.random()

    try:
        sampler = PromptSampler(
            variants=["first {task}", "second {task}"],
            rng=random.Random(11),
        )
        sampler.build(_parent(), [], _problem(), extra_context="")
        observed_next = random.random()
    finally:
        random.setstate(global_state)

    assert observed_next == expected_next
