"""Configuration contracts for the bounded engineering preview."""

import dataclasses

import pytest

from libreevolve.alpha import alpha_config
from libreevolve.core.config import Config, ConfigError


def test_defaults_match_bounded_reference_lane():
    config = Config()
    assert config.max_generations == 3
    assert config.max_evaluations == 4
    assert config.max_runtime_seconds == 900
    assert config.max_llm_calls == config.max_llm_provider_attempts == 3
    assert config.mutation_mode == "full"
    assert config.llm_max_retries == 0
    assert config.llm_max_call_attempts == 1
    assert config.llm_fallback is False
    assert config.backends == [{"type": "codex", "model": "gpt-5.6-luna",
                                "reasoning_effort": "high"}]


@pytest.mark.parametrize("field", [
    "max_evaluations", "max_runtime_seconds", "max_llm_calls",
    "max_llm_provider_attempts",
])
def test_run_limits_cannot_be_unset(field):
    with pytest.raises(ConfigError, match="explicit"):
        Config(**{field: None})


@pytest.mark.parametrize("kwargs", [
    {"max_generations": -1}, {"max_generations": True},
    {"max_evaluations": -1}, {"max_runtime_seconds": float("inf")},
    {"max_runtime_seconds": 0}, {"eval_timeout_sec": float("nan")},
    {"max_llm_calls": -1}, {"max_llm_provider_attempts": True},
    {"llm_max_response_chars": 0}, {"max_candidate_workspace_files": 0},
    {"problem_name": "../escape"}, {"problem_name": "bad/name"},
    {"run_id": "bad\nname"}, {"mutation_mode": "adaptive"},
])
def test_invalid_bounds_and_identifiers_are_rejected(kwargs):
    with pytest.raises(ConfigError):
        Config(**kwargs)


@pytest.mark.parametrize("kwargs", [
    {"max_llm_tokens": 10}, {"max_llm_cost_microusd": 10},
    {"llm_role_token_limits": {"mutation": 10}},
    {"llm_role_cost_microusd_limits": {"mutation": 10}},
])
def test_subscription_token_and_dollar_caps_are_not_claimed(kwargs):
    with pytest.raises(ConfigError, match="token or dollar caps"):
        Config(**kwargs)


@pytest.mark.parametrize("spec", [
    {"type": "openai", "model": "gpt-5.6-luna", "reasoning_effort": "high"},
    {"type": "custom", "model": "local", "reasoning_effort": "high"},
    {"type": "codex", "model": "different-model", "reasoning_effort": "high"},
    {"type": "codex", "model": "gpt-5.6-luna", "reasoning_effort": "max"},
])
def test_only_reference_backend_is_configurable(spec):
    with pytest.raises(ConfigError):
        Config(backends=[spec])


def test_backend_ensemble_and_subscription_price_are_rejected():
    backend = Config().backends[0]
    with pytest.raises(ConfigError, match="one Codex"):
        Config(backends=[dict(backend), dict(backend)])
    with pytest.raises(ConfigError, match="charges are unknown"):
        Config(backends=[{**backend, "cost_usd_per_million_tokens": 1}])


@pytest.mark.parametrize("field", [
    "plugins", "async_candidate_evaluation", "async_llm_sampling",
    "meta_prompt_evolution", "critique_enabled", "llm_feedback",
    "adaptive_mutation_full_max_chars", "candidate_language_runners",
    "candidate_build_systems",
])
def test_experimental_configuration_is_absent(field):
    assert field not in {item.name for item in dataclasses.fields(Config)}
    with pytest.raises(TypeError, match="unexpected keyword"):
        Config(**{field: None})


def test_reference_configuration_validation_is_idempotent():
    config = Config(**alpha_config("gpt-5.6-luna"))
    first = dataclasses.asdict(config)
    config.validate()
    assert dataclasses.asdict(config) == first


def test_default_mutable_values_are_run_local():
    first, second = Config(), Config()
    first.backends[0]["model"] = "changed"
    first.validator_env_allowlist.append("EXAMPLE")
    assert second.backends[0]["model"] == "gpt-5.6-luna"
    assert second.validator_env_allowlist == []


def test_revalidation_catches_mutated_backend_before_run():
    config = Config()
    config.backends[0]["model"] = "different-model"
    with pytest.raises(ConfigError):
        config.validate()
