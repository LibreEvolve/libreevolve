import json
import hashlib
import math
import pytest
import time
from pathlib import Path
from unittest.mock import MagicMock, call
from libreevolve.core.artifact_schema import ARTIFACT_SCHEMA_VERSION
from libreevolve.core.jsonl import strict_json_dumps
from libreevolve.core.config import Config
from libreevolve.core.prompt import PromptSampler
from libreevolve.llm.ensemble import (
    LLMCallLedgerError,
    LLMEnsemble,
    LLM_PROVIDER_DIAGNOSTICS_SCHEMA,
    LLMRoleCallLimitError,
    ProviderCallTimeoutError,
    ProviderResponseError,
    build_llm,
    load_llm_call_ledger,
    validate_restored_backend_specs,
    validate_restored_llm_prompt,
)
from libreevolve.llm.backend_registry import (
    build_registry_backends,
    builtin_backend_registry,
    validate_backend_registry_specs,
)
from libreevolve.population.program import Program
from libreevolve.problems.loader import Problem

def _b(name="b", resp="<<<SEARCH\nfoo\n===\nbar\n>>>REPLACE"):
    m = MagicMock(); m.name = name; m.api_mode = None; m.generate.return_value = resp; return m


class ConfiguredEchoBackend:
    api_mode = "custom"

    def __init__(self, model, max_tokens=None, prefix="", nested=None):
        self._model = model
        self._max_tokens = max_tokens
        self._prefix = prefix
        self._nested = nested or {}
        self.calls = []

    @property
    def name(self):
        return f"custom/{self._model}"

    def generate(self, prompt, **kwargs):
        self.calls.append({"prompt": prompt, "kwargs": dict(kwargs)})
        role = kwargs.get("role", "missing")
        enabled = self._nested.get("enabled", False)
        return f"{self._prefix}:{self._model}:{self._max_tokens}:{enabled}:{role}:{prompt}"


class ConstructibleNonBackend:
    def __init__(self, model):
        self.model = model


class FakeRateLimitError(RuntimeError):
    pass


class FakeStatusError(RuntimeError):
    def __init__(self, status_code):
        super().__init__(f"status {status_code}")
        self.status_code = status_code


def _role_accounting(**overrides):
    record = {
        "calls": 0,
        "successes": 0,
        "failures": 0,
        "reward_accounted_calls": 0,
        "telemetry_only_calls": 0,
        "ensemble_retry_attempts": 0,
        "ensemble_fallback_attempts": 0,
        "provider_internal_attempts": 0,
        "provider_internal_failed_attempts": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cost_microusd": 0,
        "wall_clock_seconds": 0.0,
        "provider_response_failures": 0,
        "timeout_failures": 0,
        "rate_limit_failures": 0,
        "transport_failures": 0,
        "provider_server_error_failures": 0,
        "provider_client_error_failures": 0,
        "unknown_failures": 0,
    }
    record.update(overrides)
    return record


def _assert_role_accounting(actual, **expected_overrides):
    expected = _role_accounting(**expected_overrides)
    actual = dict(actual)
    wall_clock_seconds = actual.pop("wall_clock_seconds")
    expected.pop("wall_clock_seconds")
    assert actual == expected
    assert isinstance(wall_clock_seconds, float)
    assert math.isfinite(wall_clock_seconds)
    assert wall_clock_seconds >= 0.0


def test_returns_tuple():
    diff, idx = LLMEnsemble([_b()]).generate("p")
    assert isinstance(diff, str) and idx == 0

def test_single_backend_always_idx0():
    b = _b(); ens = LLMEnsemble([b])
    assert all(ens.generate("p")[1] == 0 for _ in range(3))

def test_ucb1_explores_both_first():
    b1, b2 = _b("b1"), _b("b2")
    ens = LLMEnsemble([b1, b2])
    _, i1 = ens.generate("p"); _, i2 = ens.generate("p")
    assert {i1, i2} == {0, 1}

def test_record_reward_updates_wins():
    ens = LLMEnsemble([_b()]); ens.generate("p")
    call_id = ens.last_call["id"]
    ens.record_reward(0, 2.5)
    assert ens.wins[0] == 1.0
    assert ens.last_call["reward"] == 1.0
    assert ens.last_call["reward_raw"] == 2.5
    assert ens.last_call["rewarded"] is True
    with pytest.raises(ValueError, match="already been rewarded"):
        ens.record_reward(0, 0.5, call_id=call_id)


def test_record_reward_rejects_invalid_rewards():
    ens = LLMEnsemble([_b()]); ens.generate("p")
    for reward in (-1.0, math.nan, math.inf, "1.0", True):
        with pytest.raises(ValueError, match="backend reward"):
            ens.record_reward(0, reward)
    assert ens.wins[0] == 0.0


def test_record_reward_rejects_invalid_indexes():
    ens = LLMEnsemble([_b("a"), _b("b")])
    for idx in (-1, 2, True, "0"):
        with pytest.raises(ValueError, match="index"):
            ens.record_reward(idx, 1.0)
    assert ens.wins == [0.0, 0.0]


def test_record_reward_rejects_without_unrewarded_successful_call():
    ens = LLMEnsemble([_b()])

    with pytest.raises(ValueError, match="no unrewarded successful call"):
        ens.record_reward(0, 1.0)

    assert ens.wins == [0.0]


def test_build_llm_instantiates_configured_custom_backend():
    config = Config(
        backends=[
            {
                "type": "custom",
                "model": "fixture-model",
                "class_path": f"{__name__}:ConfiguredEchoBackend",
                "max_tokens": 17,
                "kwargs": {"prefix": "echo", "nested": {"enabled": True}},
                "cost": 2.0,
                "latency": 3.0,
                "depth": 4.0,
                "role": "depth",
            }
        ]
    )

    ensemble = build_llm(config)
    response, idx = ensemble.generate("prompt text", role="feedback:grader")

    assert idx == 0
    assert response == "echo:fixture-model:17:True:feedback:grader:prompt text"
    assert ensemble.backends[0].calls == [
        {"prompt": "prompt text", "kwargs": {"role": "feedback:grader"}}
    ]
    assert ensemble.backends[0].name == "custom/fixture-model"
    assert ensemble.backend_metadata[0] == {
        "cost": 2.0,
        "latency": 3.0,
        "depth": 4.0,
        "role": "depth",
    }
    assert ensemble.last_call["backend_name"] == "custom/fixture-model"
    assert ensemble.last_call["api_mode"] == "custom"
    assert ensemble.last_call["scheduler_accounting"] == "telemetry_only"
    assert ensemble.counts == [0]
    assert ensemble.total == 0


def test_configured_custom_backend_prompt_is_validated_before_backend_call():
    config = Config(
        backends=[
            {
                "type": "custom",
                "model": "fixture-model",
                "class_path": f"{__name__}:ConfiguredEchoBackend",
            }
        ]
    )
    ensemble = build_llm(config)

    with pytest.raises(ValueError, match="prompt"):
        ensemble.generate(["not", "text"], role="mutation")

    assert ensemble.backends[0].calls == []
    assert ensemble.call_history == []
    assert ensemble.counts == [0]


def test_build_llm_forwards_builtin_backend_timeout(mocker):
    openai_client = mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI")
    config = Config(
        backends=[
            {
                "type": "openai",
                "model": "gpt-4o-mini",
                "timeout_sec": 9,
                "provider_max_retries": 1,
            }
        ]
    )

    ensemble = build_llm(config)

    assert ensemble.backends[0]._timeout_sec == 9.0
    assert ensemble.backends[0]._provider_max_retries == 1
    openai_client.assert_called_once_with(timeout=9.0)


def test_build_llm_forwards_ensemble_call_timeout():
    config = Config(
        backends=[
            {
                "type": "custom",
                "model": "fixture-model",
                "class_path": f"{__name__}:ConfiguredEchoBackend",
            }
        ],
        llm_call_timeout_sec=0.25,
    )

    ensemble = build_llm(config)

    assert ensemble.call_timeout_sec == 0.25


def test_build_llm_forwards_prompt_role_policy_and_records_hash_only_telemetry(mocker):
    client = MagicMock()
    client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="answer"))
    ]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=client)
    config = Config(
        backends=[{"type": "openai", "model": "gpt-4o-mini"}],
        llm_prompt_roles={
            "mutation": {
                "system": "System text for mutation",
                "developer": "Developer text for mutation",
            }
        },
    )

    ensemble = build_llm(config)
    response, idx = ensemble.generate("prompt text", role="mutation")

    assert (response, idx) == ("answer", 0)
    assert client.chat.completions.create.call_args.kwargs["messages"] == [
        {"role": "system", "content": "System text for mutation"},
        {"role": "developer", "content": "Developer text for mutation"},
        {"role": "user", "content": "prompt text"},
    ]
    policy = ensemble.last_call["prompt_role_policy"]
    assert policy["policy"] == "configured_structured_messages"
    assert policy["matched_role"] == "mutation"
    assert policy["message_roles"] == ["system", "developer", "user"]
    assert policy["instruction_metadata"]["system"]["chars"] == len(
        "System text for mutation"
    )
    assert "System text for mutation" not in json.dumps(ensemble.last_call)


def test_build_llm_revalidates_mutated_prompt_role_policy():
    config = Config(llm_prompt_roles={"mutation": {"system": "ok"}})
    config.llm_prompt_roles["bad role"] = {"system": "bad"}

    with pytest.raises(ValueError, match="manifest-safe role label"):
        build_llm(config)


def test_build_llm_revalidates_mutated_custom_backend_specs():
    config = Config(
        backends=[
            {
                "type": "custom",
                "model": "fixture-model",
                "class_path": f"{__name__}:ConfiguredEchoBackend",
            }
        ]
    )
    config.backends[0]["kwargs"] = {"model": "shadow"}

    with pytest.raises(ValueError, match="top-level backend field"):
        build_llm(config)


def test_build_llm_rejects_custom_backend_without_protocol():
    config = Config(
        backends=[
            {
                "type": "custom",
                "model": "fixture-model",
                "class_path": f"{__name__}:ConstructibleNonBackend",
            }
        ]
    )

    with pytest.raises(ValueError, match="must implement generate"):
        build_llm(config)


def test_record_reward_rejects_unknown_wrong_backend_and_failed_call_ids():
    bad = _b("bad")
    bad.generate.side_effect = RuntimeError("provider down")
    good = _b("good", "answer")
    ens = LLMEnsemble([bad, good], fallback=True)

    response, idx = ens.generate("prompt text")
    failed_id = ens.call_history[0]["id"]
    success_id = ens.call_history[1]["id"]

    assert (response, idx) == ("answer", 1)
    with pytest.raises(ValueError, match="not found"):
        ens.record_reward(1, 1.0, call_id="missing-call")
    with pytest.raises(ValueError, match="belongs to backend"):
        ens.record_reward(0, 1.0, call_id=success_id)
    with pytest.raises(ValueError, match="not a successful call"):
        ens.record_reward(0, 1.0, call_id=failed_id)
    with pytest.raises(ValueError, match="non-empty string"):
        ens.record_reward(1, 1.0, call_id="")

    ens.record_reward(1, 1.0, call_id=success_id)
    assert ens.wins == [0.0, 1.0]

def test_counts_increment():
    ens = LLMEnsemble([_b()])
    assert ens.counts[0] == 0; ens.generate("p"); assert ens.counts[0] == 1


def test_auxiliary_roles_do_not_change_mutation_scheduler_accounting():
    b1 = _b("b1", "answer")
    b2 = _b("b2", "other")
    ens = LLMEnsemble([b1, b2])

    response, idx = ens.generate("feedback prompt", role="feedback:grader")

    assert (response, idx) == ("answer", 0)
    assert ens.counts == [0, 0]
    assert ens.total == 0
    assert ens.scheduler_state["unrewarded_success_call_ids"] == [[], []]
    assert ens.last_call["scheduler_accounting"] == "telemetry_only"
    assert ens.last_call["counts_before"] == [0, 0]
    assert ens.last_call["counts_after"] == [0, 0]
    _assert_role_accounting(
        ens.scheduler_state["role_accounting"]["feedback:grader"],
        calls=1,
        successes=1,
        telemetry_only_calls=1,
    )
    with pytest.raises(ValueError, match="not rewardable"):
        ens.record_reward(0, 1.0, call_id=ens.last_call["id"])

    response, idx = ens.generate("mutation prompt", role="mutation")

    assert (response, idx) == ("answer", 0)
    assert ens.counts == [1, 0]
    assert ens.total == 1
    assert ens.last_call["scheduler_accounting"] == "rewarded"
    assert ens.scheduler_state["role_accounting"]["mutation"]["reward_accounted_calls"] == 1
    assert ens.scheduler_state["reward_accounting_policy"] == {
        "policy": "configured_reward_accounted_roles_v1",
        "reward_accounted_roles": ["mutation"],
    }


def test_configured_reward_accounted_roles_advance_scheduler_counts():
    b1 = _b("b1", "answer")
    b2 = _b("b2", "other")
    ens = LLMEnsemble([b1, b2], reward_accounted_roles=["mutation", "critique"])

    response, idx = ens.generate("critique prompt", role="critique")

    assert (response, idx) == ("answer", 0)
    assert ens.counts == [1, 0]
    assert ens.total == 1
    assert ens.last_call["scheduler_accounting"] == "rewarded"
    assert ens.last_call["counts_before"] == [0, 0]
    assert ens.last_call["counts_after"] == [1, 0]
    assert ens.scheduler_state["unrewarded_success_call_ids"][0] == [
        ens.last_call["id"]
    ]
    assert ens.scheduler_state["reward_accounting_policy"] == {
        "policy": "configured_reward_accounted_roles_v1",
        "reward_accounted_roles": ["critique", "mutation"],
    }
    _assert_role_accounting(
        ens.scheduler_state["role_accounting"]["critique"],
        calls=1,
        successes=1,
        reward_accounted_calls=1,
    )
    role_state = ens.scheduler_state["role_scheduler_state"]["critique"]
    assert role_state["policy"] == "per_role_scheduler_audit_state_not_selection_policy"
    assert role_state["selection_policy"] == (
        "backend_metadata_role_scoped_when_configured_else_global"
    )
    assert role_state["counts"] == [1, 0]
    assert role_state["wins"] == [0.0, 0.0]
    assert role_state["total"] == 1
    assert role_state["unrewarded_success_call_ids"][0] == [ens.last_call["id"]]

    ens.record_reward(0, 0.75, call_id=ens.last_call["id"])

    role_state = ens.scheduler_state["role_scheduler_state"]["critique"]
    assert role_state["wins"] == [0.75, 0.0]
    assert role_state["unrewarded_success_call_ids"] == [[], []]
    assert role_state["rewarded_call_ids"] == [ens.last_call["id"]]


def test_shared_role_scheduler_scope_uses_global_selection_state():
    b1 = _b("b1", "mutation answer")
    b2 = _b("b2", "critique answer")
    ens = LLMEnsemble(
        [b1, b2],
        reward_accounted_roles=["mutation", "critique"],
    )
    _, mutation_idx = ens.generate("mutation prompt", role="mutation")
    ens.record_reward(mutation_idx, 1.0, call_id=ens.last_call["id"])

    _, critique_idx = ens.generate("critique prompt", role="critique")

    assert mutation_idx == 0
    assert critique_idx == 1
    assert ens.scheduler_state["role_scheduler_scope"] == "shared"
    assert ens.last_call["scheduler_policy"]["selection_scope"] == "global_backend_bandit"
    role_state = ens.scheduler_state["role_scheduler_state"]["critique"]
    assert role_state["selection_policy"] == (
        "backend_metadata_role_scoped_when_configured_else_global"
    )
    assert role_state["counts"] == [0, 1]


def test_role_scoped_scheduler_scope_uses_independent_role_counts():
    b1 = _b("b1", "mutation and critique answer")
    b2 = _b("b2", "unused shared-state exploration")
    ens = LLMEnsemble(
        [b1, b2],
        reward_accounted_roles=["mutation", "critique"],
        role_scheduler_scope="role_scoped",
    )
    _, mutation_idx = ens.generate("mutation prompt", role="mutation")
    ens.record_reward(mutation_idx, 1.0, call_id=ens.last_call["id"])

    _, critique_idx = ens.generate("critique prompt", role="critique")

    assert mutation_idx == 0
    assert critique_idx == 0
    assert ens.counts == [2, 0]
    assert ens.total == 2
    assert ens.scheduler_state["role_scheduler_scope"] == "role_scoped"
    policy = ens.last_call["scheduler_policy"]
    assert policy["selection_scope"] == "role_owned_backend_bandit"
    assert policy["role_selection_policy"] == (
        "role_owned_counts_global_backend_eligibility"
    )
    assert policy["role_reward_accounting"] == "rewarded"
    assert policy["role_selection_state_owner"] == "role_scheduler_state"
    role_state = ens.scheduler_state["role_scheduler_state"]["critique"]
    assert role_state["selection_policy"] == "role_owned_bandit_selection_state"
    assert role_state["counts"] == [1, 0]
    assert role_state["wins"] == [0.0, 0.0]
    assert role_state["total"] == 1


def test_scheduler_state_restores_role_scheduler_state():
    source = LLMEnsemble(
        [_b("b1", "answer"), _b("b2", "other")],
        reward_accounted_roles=["mutation", "critique"],
    )
    source.generate("critique prompt", role="critique")
    call_id = source.last_call["id"]
    source.record_reward(0, 0.5, call_id=call_id)

    restored = LLMEnsemble(
        [_b("b1", "answer"), _b("b2", "other")],
        reward_accounted_roles=["mutation"],
    )
    restored.restore_scheduler_state(source.scheduler_state)

    assert restored.scheduler_state["reward_accounting_policy"] == {
        "policy": "configured_reward_accounted_roles_v1",
        "reward_accounted_roles": ["critique", "mutation"],
    }
    assert restored.scheduler_state["role_scheduler_state"]["critique"]["counts"] == [
        1,
        0,
    ]
    assert restored.scheduler_state["role_scheduler_state"]["critique"]["wins"] == [
        0.5,
        0.0,
    ]
    assert restored.scheduler_state["role_scheduler_state"]["critique"][
        "rewarded_call_ids"
    ] == [call_id]


def test_scheduler_state_restores_role_scoped_scheduler_scope():
    source = LLMEnsemble(
        [_b("b1", "answer"), _b("b2", "other")],
        reward_accounted_roles=["mutation", "critique"],
        role_scheduler_scope="role_scoped",
    )
    source.generate("critique prompt", role="critique")

    restored = LLMEnsemble(
        [_b("b1", "answer"), _b("b2", "other")],
        reward_accounted_roles=["mutation"],
    )
    restored.restore_scheduler_state(source.scheduler_state)

    assert restored.scheduler_state["role_scheduler_scope"] == "role_scoped"
    assert restored.scheduler_state["role_scheduler_state"]["critique"][
        "selection_policy"
    ] == "role_owned_bandit_selection_state"


def test_scheduler_state_restores_all_loop_llm_roles():
    roles = ["mutation", "critique", "feedback:grader", "meta_prompt"]
    source = LLMEnsemble(
        [_b("b1", "answer"), _b("b2", "other")],
        reward_accounted_roles=roles,
    )
    call_ids = {}
    backend_indices = {}
    for index, role in enumerate(roles):
        _, backend_idx = source.generate(f"{role} prompt", role=role)
        call_ids[role] = source.last_call["id"]
        backend_indices[role] = backend_idx
        source.record_reward(backend_idx, 0.1 * (index + 1), call_id=call_ids[role])

    restored = LLMEnsemble(
        [_b("b1", "answer"), _b("b2", "other")],
        reward_accounted_roles=["mutation"],
    )
    restored.restore_scheduler_state(source.scheduler_state)

    assert restored.scheduler_state["reward_accounting_policy"] == {
        "policy": "configured_reward_accounted_roles_v1",
        "reward_accounted_roles": ["critique", "feedback:grader", "meta_prompt", "mutation"],
    }
    for index, role in enumerate(roles):
        role_state = restored.scheduler_state["role_scheduler_state"][role]
        expected_counts = [0, 0]
        expected_counts[backend_indices[role]] = 1
        expected_wins = [0.0, 0.0]
        expected_wins[backend_indices[role]] = pytest.approx(0.1 * (index + 1))
        assert role_state["counts"] == expected_counts
        assert role_state["wins"] == expected_wins
        assert role_state["total"] == 1
        assert role_state["rewarded_call_ids"] == [call_ids[role]]
        assert role_state["unrewarded_success_call_ids"] == [[], []]


def test_restore_scheduler_state_accepts_legacy_without_role_scheduler_state():
    ens = LLMEnsemble([_b()])
    state = ens.scheduler_state
    state.pop("role_scheduler_state")

    ens.restore_scheduler_state(state)

    assert ens.scheduler_state["role_scheduler_state"] == {}


def test_restore_scheduler_state_accepts_legacy_without_role_call_limits():
    source = LLMEnsemble([_b()])
    state = source.scheduler_state
    state.pop("role_call_limits")
    restored = LLMEnsemble([_b()], max_calls_by_role={"mutation": 2})

    restored.restore_scheduler_state(state)

    assert restored.scheduler_state["role_call_limits"] == {
        "policy": "logical_generate_call_limits_by_role_v1",
        "max_calls_by_role": {"mutation": 2},
        "logical_calls_by_role": {},
    }


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"strategy": "typo"}, "strategy"),
        ({"strategy": 7}, "strategy"),
        ({"explore_coeff": -1.0}, "exploration coefficient"),
        ({"explore_coeff": math.nan}, "exploration coefficient"),
        ({"explore_coeff": math.inf}, "exploration coefficient"),
        ({"explore_coeff": True}, "exploration coefficient"),
        ({"explore_coeff": "1.0"}, "exploration coefficient"),
        ({"max_retries": -1}, "max_retries"),
        ({"max_retries": 1.5}, "max_retries"),
        ({"max_retries": True}, "max_retries"),
        ({"max_retries": "1"}, "max_retries"),
        ({"max_retries": 11}, "max_retries"),
        ({"max_call_attempts": 0}, "max_call_attempts"),
        ({"max_call_attempts": -1}, "max_call_attempts"),
        ({"max_call_attempts": 1.5}, "max_call_attempts"),
        ({"max_call_attempts": True}, "max_call_attempts"),
        ({"max_call_attempts": "32"}, "max_call_attempts"),
        ({"max_call_attempts": 33}, "max_call_attempts"),
        ({"fallback": "false"}, "fallback"),
        ({"fallback": 1}, "fallback"),
        ({"max_response_chars": 0}, "max_response_chars"),
        ({"max_response_chars": -1}, "max_response_chars"),
        ({"max_response_chars": 1.5}, "max_response_chars"),
        ({"max_response_chars": True}, "max_response_chars"),
        ({"max_response_chars": "100"}, "max_response_chars"),
        ({"max_call_history": 0}, "max_call_history"),
        ({"max_call_history": -1}, "max_call_history"),
        ({"max_call_history": 1.5}, "max_call_history"),
        ({"max_call_history": True}, "max_call_history"),
        ({"max_call_history": "100"}, "max_call_history"),
        ({"call_timeout_sec": 0}, "call_timeout_sec"),
        ({"call_timeout_sec": -1.0}, "call_timeout_sec"),
        ({"call_timeout_sec": math.nan}, "call_timeout_sec"),
        ({"call_timeout_sec": True}, "call_timeout_sec"),
        ({"call_timeout_sec": "1"}, "call_timeout_sec"),
        ({"max_prompt_chars": 0}, "max_prompt_chars"),
        ({"max_prompt_chars": -1}, "max_prompt_chars"),
        ({"max_prompt_chars": 1.5}, "max_prompt_chars"),
        ({"max_prompt_chars": True}, "max_prompt_chars"),
        ({"max_prompt_chars": "100"}, "max_prompt_chars"),
        ({"max_prompt_estimated_tokens": 0}, "max_prompt_estimated_tokens"),
        ({"max_prompt_estimated_tokens": -1}, "max_prompt_estimated_tokens"),
        ({"max_prompt_estimated_tokens": 1.5}, "max_prompt_estimated_tokens"),
        ({"max_prompt_estimated_tokens": True}, "max_prompt_estimated_tokens"),
        ({"max_prompt_estimated_tokens": "100"}, "max_prompt_estimated_tokens"),
        ({"reward_accounted_roles": []}, "reward_accounted_roles"),
        ({"reward_accounted_roles": "mutation"}, "reward_accounted_roles"),
        ({"reward_accounted_roles": ["bad role"]}, "role label"),
        ({"backend_metadata": "bad"}, "backend_metadata"),
        ({"backend_metadata": []}, "backend_metadata"),
        ({"backend_metadata": [{}, {}]}, "backend_metadata"),
        ({"backend_metadata": ["bad"]}, "backend_metadata"),
        ({"backend_metadata": [{1: "bad"}]}, "keys"),
        (
            {"backend_metadata": [{"api_key=sk-proj_backendmetakey_secret_1234567890": "value"}]},  # pragma: allowlist secret
            "manifest-safe metadata labels",
        ),
        ({"backend_metadata": [{"backend\u202emeta": "value"}]}, "manifest-safe metadata labels"),
        ({"backend_metadata": [{"bad key": "value"}]}, "manifest-safe metadata labels"),
        ({"backend_metadata": [{"nested": {"bad\nkey": "value"}}]}, "manifest-safe metadata labels"),
        ({"backend_metadata": [{"cost": 0.0}]}, "cost"),
        ({"backend_metadata": [{"cost_usd_per_million_tokens": 0.0}]}, "cost_usd_per_million_tokens"),
        ({"backend_metadata": [{"context_window_tokens": 0}]}, "context_window_tokens"),
        ({"backend_metadata": [{"reserved_output_tokens": -1}]}, "reserved_output_tokens"),
        ({"backend_metadata": [{"reserved_output_tokens": 1}]}, "context_window_tokens"),
        (
            {"backend_metadata": [{"context_window_tokens": 8, "reserved_output_tokens": 8}]},
            "reserved_output_tokens",
        ),
        ({"backend_metadata": [{"latency": -1.0}]}, "latency"),
        ({"backend_metadata": [{"depth": math.nan}]}, "depth"),
        ({"backend_metadata": [{"role": "bad role"}]}, "role"),
        (
            {"backend_metadata": [{"label": "api_key=sk-proj_meta_secret_1234567890"}]},  # pragma: allowlist secret
            "secret-like",
        ),
        ({"backend_metadata": [{"raw": object()}]}, "JSON-safe"),
        ({"role_backend_indices": {"critique": [1]}}, "role_backend_indices"),
    ],
)
def test_constructor_rejects_invalid_scheduler_controls(kwargs, message):
    with pytest.raises(ValueError, match=message):
        LLMEnsemble([_b()], **kwargs)


def test_constructor_normalizes_and_copies_backend_metadata():
    metadata = [{"cost": 2, "latency": 3, "depth": 4, "role": "breadth", "nested": {"ok": [1]}}]
    ens = LLMEnsemble([_b("b1", "answer")], backend_metadata=metadata)
    metadata[0]["nested"]["ok"].append(2)

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["backend_metadata"]["cost"] == 2.0
    assert record["backend_metadata"]["latency"] == 3.0
    assert record["backend_metadata"]["depth"] == 4.0
    assert record["backend_metadata"]["nested"]["ok"] == [1]

    ens.backend_metadata[0]["nested"]["ok"].append(99)
    assert ens.call_history[0]["backend_metadata"]["nested"]["ok"] == [1]


def test_backend_metadata_accessor_is_defensive_copy_for_selection_and_telemetry():
    b1 = _b("b1", "one")
    b2 = _b("b2", "two")
    ens = LLMEnsemble(
        [b1, b2],
        strategy="throughput_depth",
        backend_metadata=[
            {"cost": 1.0, "latency": 1.0, "depth": 1.0, "label": "safe"},
            {"cost": 1.0, "latency": 1.0, "depth": 2.0},
        ],
    )
    metadata = ens.backend_metadata
    metadata[1]["depth"] = "api_key=sk-proj_scheduler_meta_secret_1234567890"  # pragma: allowlist secret
    metadata[0]["label"] = object()

    response_1, idx_1 = ens.generate("prompt one")
    response_2, idx_2 = ens.generate("prompt two")
    ens.record_reward(idx_1, 1.0)
    response_3, idx_3 = ens.generate("prompt three")

    assert response_1 == "one"
    assert response_2 == "two"
    assert response_3 in {"one", "two"}
    assert {idx_1, idx_2} == {0, 1}
    assert idx_3 in {0, 1}
    assert ens.backend_metadata[0]["label"] == "safe"
    assert ens.backend_metadata[1]["depth"] == 2.0
    assert ens.call_history[0]["backend_metadata"]["label"] == "safe"
    strict_json_dumps(ens.call_history)


def test_constructor_accepts_maximum_retry_cap():
    ens = LLMEnsemble([_b()], max_retries=10)

    assert ens.max_retries == 10


def test_constructor_accepts_maximum_call_attempt_cap():
    ens = LLMEnsemble([_b()], max_call_attempts=32)

    assert ens.max_call_attempts == 32


def test_constructor_rejects_unsafe_backend_metadata_keys_before_backend_calls():
    raw_secret_key = "api_key=sk-proj_backendmetakey_secret_1234567890"  # pragma: allowlist secret
    backend = _b("b1", "answer")

    with pytest.raises(ValueError) as excinfo:
        LLMEnsemble([backend], backend_metadata=[{raw_secret_key: "value"}])

    assert "metadata labels" in str(excinfo.value)
    assert raw_secret_key not in str(excinfo.value)
    assert backend.generate.call_count == 0


@pytest.mark.parametrize(
    ("backend", "mutate", "message"),
    [
        (
            {"type": "ollama", "model": "llama3"},
            lambda config: config.backends[0].__setitem__(
                "model",
                "sk-proj_buildllm_model_secret_1234567890",
            ),
            "model",
        ),
        ({"type": "ollama", "model": "llama3"}, lambda config: config.backends[0].__setitem__("type", "unknown"), "type"),
        ({"type": "ollama", "model": "llama3"}, lambda config: config.backends[0].__setitem__("max_tokens", False), "max_tokens"),
        (
            {"type": "ollama", "model": "llama3"},
            lambda config: config.backends[0].__setitem__("provider_max_retries", 11),
            "provider_max_retries",
        ),
        ({"type": "ollama", "model": "llama3"}, lambda config: config.backends[0].__setitem__("cost", 0), "cost"),
        ({"type": "ollama", "model": "llama3"}, lambda config: config.backends[0].__setitem__("role", "bad role"), "role"),
        ({"type": "ollama", "model": "llama3"}, lambda config: config.backends[0].__setitem__("extra", True), "unsupported"),
        (
            {
                "type": "custom",
                "model": "fixture-model",
                "class_path": f"{__name__}:ConfiguredEchoBackend",
            },
            lambda config: config.backends[0].__setitem__("class_path", "not-import-syntax"),
            "class_path",
        ),
        (
            {
                "type": "custom",
                "model": "fixture-model",
                "class_path": f"{__name__}:ConfiguredEchoBackend",
            },
            lambda config: config.backends[0].__setitem__("timeout_sec", 10),
            "unsupported",
        ),
        (
            {
                "type": "custom",
                "model": "fixture-model",
                "class_path": f"{__name__}:ConfiguredEchoBackend",
            },
            lambda config: config.backends[0].__setitem__("provider_max_retries", 1),
            "unsupported",
        ),
    ],
)
def test_build_llm_revalidates_post_validation_backend_mutations(backend, mutate, message):
    config = Config(backends=[backend])
    mutate(config)

    with pytest.raises(ValueError, match=message) as excinfo:
        build_llm(config)

    assert "sk-proj_buildllm_model_secret_1234567890" not in str(excinfo.value)


def test_build_llm_revalidates_post_validation_retry_mutation():
    config = Config(backends=[{"type": "ollama", "model": "llama3"}])
    config.llm_max_retries = 11

    with pytest.raises(ValueError, match="llm max_retries"):
        build_llm(config)


def test_build_llm_revalidates_post_validation_call_attempt_mutation():
    config = Config(backends=[{"type": "ollama", "model": "llama3"}])
    config.llm_max_call_attempts = 0

    with pytest.raises(ValueError, match="llm max_call_attempts"):
        build_llm(config)


def test_build_llm_revalidates_post_validation_call_history_limit_mutation():
    config = Config(backends=[{"type": "ollama", "model": "llama3"}])
    config.llm_call_history_max = 0

    with pytest.raises(ValueError, match="llm max_call_history"):
        build_llm(config)


def test_build_llm_copies_valid_backend_specs_before_construction():
    config = Config(
        backends=[
            {
                "type": "ollama",
            "model": "library/qwen2.5-coder:7b-instruct",
            "max_tokens": 64,
            "cost": 2,
            "cost_usd_per_million_tokens": 0.75,
            "prompt_max_estimated_tokens": 4096,
            "context_window_tokens": 8192,
            "latency": 3,
            "depth": 4,
            "role": "breadth",
            }
        ]
    )

    ensemble = build_llm(config)
    config.backends[0]["cost"] = 999

    assert ensemble.backends[0].name == "ollama/library/qwen2.5-coder:7b-instruct"
    assert ensemble.backend_metadata[0] == {
        "cost": 2.0,
        "cost_usd_per_million_tokens": 0.75,
        "prompt_max_estimated_tokens": 4096,
        "context_window_tokens": 8192,
        "reserved_output_tokens": 64,
        "latency": 3.0,
        "depth": 4.0,
        "role": "breadth",
    }


def test_validate_restored_backend_specs_returns_normalized_defensive_copy():
    specs = [
        {
            "type": "custom",
            "model": "fixture-model",
            "class_path": f"{__name__}:ConfiguredEchoBackend",
            "max_tokens": 64,
            "cost": 2,
            "prompt_max_estimated_tokens": 2048,
            "context_window_tokens": 4096,
            "reserved_output_tokens": 128,
            "latency": 3,
            "depth": 4,
            "role": "feedback:simplicity",
            "kwargs": {"nested": {"enabled": True}},
        }
    ]

    restored = validate_restored_backend_specs(specs)
    specs[0]["kwargs"]["nested"]["enabled"] = False

    assert restored == [
        {
            "type": "custom",
            "model": "fixture-model",
            "class_path": f"{__name__}:ConfiguredEchoBackend",
            "max_tokens": 64,
            "cost": 2.0,
            "prompt_max_estimated_tokens": 2048,
            "context_window_tokens": 4096,
            "reserved_output_tokens": 128,
            "latency": 3.0,
            "depth": 4.0,
            "role": "feedback:simplicity",
            "kwargs": {"nested": {"enabled": True}},
        }
    ]


def test_validate_backend_registry_specs_uses_shared_backend_normalizer():
    specs = [
        {
            "type": "custom",
            "model": "fixture-model",
            "class_path": f"{__name__}:ConfiguredEchoBackend",
            "max_tokens": 64,
            "cost": 2,
            "latency": 3,
            "depth": 4,
            "role": "feedback:simplicity",
            "kwargs": {"nested": {"enabled": True}},
        }
    ]

    restored = validate_backend_registry_specs(specs)
    specs[0]["kwargs"]["nested"]["enabled"] = False

    assert restored[0]["kwargs"]["nested"]["enabled"] is True
    assert restored[0]["cost"] == 2.0
    assert restored[0]["role"] == "feedback:simplicity"


def test_backend_registry_rejects_malformed_specs_before_construction():
    with pytest.raises(ValueError, match="model"):
        validate_backend_registry_specs(
            [
                {
                    "type": "openai",
                    "model": "api_key=sk-proj_registry_model_secret_1234567890",  # pragma: allowlist secret
                }
            ]
        )


def test_build_registry_backends_constructs_validated_custom_backends():
    backends, metadata = build_registry_backends(
        [
            {
                "type": "custom",
                "model": "fixture-model",
                "class_path": f"{__name__}:ConfiguredEchoBackend",
                "max_tokens": 12,
                "cost": 2,
                "kwargs": {"prefix": "ok:"},
            }
        ]
    )

    assert isinstance(backends[0], ConfiguredEchoBackend)
    assert backends[0].generate("prompt") == "ok::fixture-model:12:False:missing:prompt"
    assert metadata == [{"cost": 2.0, "latency": 1.0, "depth": 1.0, "role": "general"}]


def test_builtin_backend_registry_exposes_validated_constructor_fields():
    registry = builtin_backend_registry()

    assert registry["openai"]["schema"] == "libreevolve.backend_registry.v1"
    assert registry["openai"]["constructor"] == "libreevolve.llm.openai:OpenAIBackend"
    assert "reasoning_effort" in registry["openai"]["constructor_fields"]
    assert "host" in registry["ollama"]["constructor_fields"]


@pytest.mark.parametrize(
    ("spec", "message"),
    [
        (
            {"type": "openai", "model": "api_key=sk-proj_restored_model_secret_1234567890"},  # pragma: allowlist secret
            "model",
        ),
        ({"type": "ollama", "model": "llama3", "max_tokens": 0}, "max_tokens"),
        (
            {"type": "ollama", "model": "llama3", "prompt_max_estimated_tokens": 0},
            "prompt_max_estimated_tokens",
        ),
        (
            {"type": "anthropic", "model": "claude", "provider_max_retries": -1},
            "provider_max_retries",
        ),
        (
            {
                "type": "custom",
                "model": "fixture-model",
                "class_path": f"{__name__}:ConfiguredEchoBackend",
                "timeout_sec": 10,
            },
            "unsupported",
        ),
        (
            {
                "type": "openai",
                "model": "gpt-5.1",
                "api_mode": "chat_completions",
                "reasoning_effort": "medium",
            },
            "reasoning_effort",
        ),
    ],
)
def test_validate_restored_backend_specs_rejects_malformed_specs(spec, message):
    with pytest.raises(ValueError, match=message) as excinfo:
        validate_restored_backend_specs([spec])

    assert "sk-proj_restored_model_secret_1234567890" not in str(excinfo.value)


def test_validate_restored_llm_prompt_uses_live_prompt_boundary():
    assert validate_restored_llm_prompt("  prompt text  ") == "  prompt text  "
    assert validate_restored_llm_prompt("prompt", max_chars=6) == "prompt"

    with pytest.raises(ValueError, match="must be text"):
        validate_restored_llm_prompt(None)
    with pytest.raises(ValueError, match="non-empty"):
        validate_restored_llm_prompt("   ")
    with pytest.raises(ValueError, match="max_prompt_chars"):
        validate_restored_llm_prompt("too long", max_chars=3)


def test_build_llm_passes_openai_api_mode_policy(mocker):
    backend_cls = mocker.patch("libreevolve.llm.openai.OpenAIBackend")
    config = Config(
        backends=[
            {
                "type": "openai",
                "model": "gpt-5.1",
                "api_mode": "responses",
            }
        ]
    )

    build_llm(config)

    backend_cls.assert_called_once_with(
        model="gpt-5.1",
        api_mode="responses",
    )


def test_build_llm_passes_reward_accounted_roles(mocker):
    backend = _b("configured", "answer")
    mocker.patch(
        "libreevolve.llm.backend_registry.build_registry_backends",
        return_value=([backend], [{}]),
    )
    config = Config(
        llm_reward_accounted_roles=["mutation", "critique"],
        backends=[{"type": "anthropic", "model": "claude-sonnet-4-6"}],
    )

    ensemble = build_llm(config)
    ensemble.generate("critique prompt", role="critique")

    assert ensemble.last_call["scheduler_accounting"] == "rewarded"
    assert ensemble.scheduler_state["reward_accounting_policy"] == {
        "policy": "configured_reward_accounted_roles_v1",
        "reward_accounted_roles": ["critique", "mutation"],
    }


def test_build_llm_passes_role_scheduler_scope(mocker):
    backend = _b("configured", "answer")
    mocker.patch(
        "libreevolve.llm.backend_registry.build_registry_backends",
        return_value=([backend], [{}]),
    )
    config = Config(
        llm_reward_accounted_roles=["mutation", "critique"],
        llm_role_scheduler_scope="role_scoped",
        backends=[{"type": "anthropic", "model": "claude-sonnet-4-6"}],
    )

    ensemble = build_llm(config)
    ensemble.generate("critique prompt", role="critique")

    assert ensemble.scheduler_state["role_scheduler_scope"] == "role_scoped"
    assert ensemble.last_call["scheduler_policy"]["selection_scope"] == (
        "role_owned_backend_bandit"
    )


def test_build_llm_passes_role_call_limits(mocker):
    backend = _b("configured", "answer")
    mocker.patch(
        "libreevolve.llm.backend_registry.build_registry_backends",
        return_value=([backend], [{}]),
    )
    config = Config(
        llm_role_call_limits={"critique": 1},
        backends=[{"type": "anthropic", "model": "claude-sonnet-4-6"}],
    )

    ensemble = build_llm(config)
    ensemble.generate("critique prompt", role="critique")

    with pytest.raises(LLMRoleCallLimitError):
        ensemble.generate("critique prompt", role="critique")


def test_build_llm_passes_role_failure_quarantine_policy(mocker):
    backend = _b("configured", "answer")
    mocker.patch(
        "libreevolve.llm.backend_registry.build_registry_backends",
        return_value=([backend], [{}]),
    )
    config = Config(
        llm_role_failure_quarantine_after={"critique": 2},
        backends=[{"type": "anthropic", "model": "claude-sonnet-4-6"}],
    )

    ensemble = build_llm(config)

    assert ensemble.scheduler_state["provider_failure_policy_state"] == {
        "schema": "libreevolve.provider_failure_policy_state.v1",
        "policy": "role_backend_consecutive_failure_quarantine_v1",
        "role_quarantine_after": {"critique": 2},
        "roles": {},
    }


def test_role_failure_quarantine_excludes_backend_after_threshold():
    bad = _b("bad")
    bad.generate.side_effect = TimeoutError("slow")
    good = _b("good", "accepted")
    ens = LLMEnsemble(
        [bad, good],
        fallback=True,
        role_failure_quarantine_after={"mutation": 1},
    )

    first = ens.generate("prompt text", role="mutation")
    second = ens.generate("prompt text two", role="mutation")

    assert first == ("accepted", 1)
    assert second == ("accepted", 1)
    assert bad.generate.call_count == 1
    failed_call = ens.call_history[0]
    assert failed_call["backend_idx"] == 0
    assert failed_call["provider_failure_policy"]["quarantine_decision"] == (
        "quarantined_role_backend_after_threshold"
    )
    assert failed_call["provider_failure_policy"]["penalty_decision"] == (
        "zero_reward_scheduler_penalty"
    )
    assert failed_call["provider_failure_policy"]["quarantine_threshold"] == 1
    assert failed_call["provider_failure_policy"]["consecutive_failures"] == 1
    assert failed_call["provider_failure_policy"]["backend_quarantined"] is True
    state = ens.scheduler_state["provider_failure_policy_state"]
    assert state["role_quarantine_after"] == {"mutation": 1}
    assert state["roles"]["mutation"]["backends"] == [
        {
            "backend_idx": 0,
            "total_failures": 1,
            "consecutive_failures": 1,
            "quarantined": True,
            "last_failure_category": "timeout",
        }
    ]
    assert ens.call_history[-1]["backend_idx"] == 1
    assert ens.call_history[-1]["fallback_attempt"] == 0


def test_scheduler_state_restores_provider_failure_quarantine():
    bad = _b("bad")
    bad.generate.side_effect = TimeoutError("slow")
    good = _b("good", "accepted")
    source = LLMEnsemble(
        [bad, good],
        fallback=True,
        role_failure_quarantine_after={"mutation": 1},
    )
    source.generate("prompt text", role="mutation")

    restored_bad = _b("restored_bad")
    restored_bad.generate.side_effect = TimeoutError("still slow")
    restored_good = _b("restored_good", "restored accepted")
    restored = LLMEnsemble([restored_bad, restored_good], fallback=True)
    restored.restore_scheduler_state(source.scheduler_state)

    result = restored.generate("prompt after restore", role="mutation")

    assert result == ("restored accepted", 1)
    assert restored_bad.generate.call_count == 0
    assert restored.scheduler_state["provider_failure_policy_state"][
        "role_quarantine_after"
    ] == {"mutation": 1}


def test_build_llm_passes_role_backend_indices(mocker):
    mutation_backend = _b("mutation", "mutation")
    critique_backend = _b("critique", "critique")
    mocker.patch(
        "libreevolve.llm.backend_registry.build_registry_backends",
        return_value=([mutation_backend, critique_backend], [{}, {}]),
    )
    config = Config(
        backends=[
            {"type": "anthropic", "model": "claude-sonnet-4-6"},
            {"type": "anthropic", "model": "claude-sonnet-4-6"},
        ],
        llm_reward_accounted_roles=["mutation", "critique"],
        llm_role_backend_indices={"critique": [1]},
    )

    ensemble = build_llm(config)
    response, idx = ensemble.generate("critique prompt", role="critique")

    assert (response, idx) == ("critique", 1)
    assert mutation_backend.generate.call_count == 0
    assert critique_backend.generate.call_count == 1
    policy = ensemble.last_call["scheduler_policy"]
    assert policy["role_selection_policy"] == "explicit_role_backend_indices"
    assert policy["role_backend_policy"] == "config.llm_role_backend_indices"
    assert ensemble.scheduler_state["role_backend_policy"] == {
        "policy": "explicit_role_backend_indices_else_backend_metadata_else_global_v1",
        "configured_role_backend_indices": {"critique": [1]},
        "metadata_role_backend_indices": {},
        "fallback_policy": "use_backend_metadata_then_global_bandit_when_role_not_configured",
    }


def test_role_call_limits_cap_logical_generate_calls():
    backend = _b("limited", "answer")
    ens = LLMEnsemble([backend], max_calls_by_role={"critique": 1})

    assert ens.generate("critique prompt", role="critique") == ("answer", 0)

    with pytest.raises(
        LLMRoleCallLimitError,
        match="LLM call budget exhausted before critique",
    ):
        ens.generate("another critique prompt", role="critique")

    assert backend.generate.call_count == 1
    assert ens.generate("mutation prompt", role="mutation") == ("answer", 0)
    assert ens.scheduler_state["role_call_limits"] == {
        "policy": "logical_generate_call_limits_by_role_v1",
        "max_calls_by_role": {"critique": 1},
        "logical_calls_by_role": {"critique": 1, "mutation": 1},
    }


def test_role_call_limits_support_wildcard_feedback_scope():
    backend = _b("limited", "answer")
    ens = LLMEnsemble([backend], max_calls_by_role={"feedback:*": 1})

    assert ens.generate("review", role="feedback:quality") == ("answer", 0)
    with pytest.raises(
        LLMRoleCallLimitError,
        match=r"llm_role_call_limits\[feedback:\*\]=1",
    ):
        ens.generate("review", role="feedback:safety")

    assert backend.generate.call_count == 1
    assert ens.scheduler_state["role_call_limits"] == {
        "policy": "logical_generate_call_limits_by_role_v1",
        "max_calls_by_role": {"feedback:*": 1},
        "logical_calls_by_role": {"feedback:quality": 1},
    }


def test_scheduler_state_restores_role_call_limits_and_consumption():
    source = LLMEnsemble([_b("source", "answer")], max_calls_by_role={"critique": 1})
    source.generate("critique prompt", role="critique")

    restored = LLMEnsemble([_b("restored", "answer")])
    restored.restore_scheduler_state(source.scheduler_state)

    with pytest.raises(
        LLMRoleCallLimitError,
        match="LLM call budget exhausted before critique",
    ):
        restored.generate("critique prompt", role="critique")

    assert restored.scheduler_state["role_call_limits"] == {
        "policy": "logical_generate_call_limits_by_role_v1",
        "max_calls_by_role": {"critique": 1},
        "logical_calls_by_role": {"critique": 1},
    }


def test_build_llm_passes_builtin_request_parameters(mocker):
    openai_backend_cls = mocker.patch("libreevolve.llm.openai.OpenAIBackend")
    anthropic_backend_cls = mocker.patch("libreevolve.llm.anthropic.AnthropicBackend")
    ollama_backend_cls = mocker.patch("libreevolve.llm.ollama.OllamaBackend")
    config = Config(
        backends=[
            {
                "type": "openai",
                "model": "gpt-4o-mini",
                "temperature": 0.2,
                "top_p": 0.9,
                "stop": "END",
                "seed": 123,
            },
            {
                "type": "anthropic",
                "model": "claude-sonnet-4-6",
                "temperature": 0.3,
                "top_p": 0.8,
                "stop": ["DONE"],
            },
            {
                "type": "ollama",
                "model": "llama3",
                "temperature": 0.4,
                "top_p": 0.7,
                "stop": ["HALT"],
                "seed": 456,
            },
        ]
    )

    build_llm(config)

    openai_backend_cls.assert_called_once_with(
        model="gpt-4o-mini",
        temperature=0.2,
        top_p=0.9,
        stop=["END"],
        seed=123,
    )
    anthropic_backend_cls.assert_called_once_with(
        model="claude-sonnet-4-6",
        temperature=0.3,
        top_p=0.8,
        stop=["DONE"],
    )
    ollama_backend_cls.assert_called_once_with(
        model="llama3",
        temperature=0.4,
        top_p=0.7,
        stop=["HALT"],
        seed=456,
    )


def test_build_llm_passes_builtin_client_context(mocker):
    openai_backend_cls = mocker.patch("libreevolve.llm.openai.OpenAIBackend")
    anthropic_backend_cls = mocker.patch("libreevolve.llm.anthropic.AnthropicBackend")
    ollama_backend_cls = mocker.patch("libreevolve.llm.ollama.OllamaBackend")
    config = Config(
        backends=[
            {
                "type": "openai",
                "model": "gpt-4o-mini",
                "base_url": "https://gateway.example/v1",
                "organization": "org-example",
                "project": "proj_example",
            },
            {
                "type": "anthropic",
                "model": "claude-sonnet-4-6",
                "base_url": "https://anthropic.example/v1",
            },
            {
                "type": "ollama",
                "model": "llama3",
                "host": "http://localhost:11434",
            },
        ]
    )

    build_llm(config)

    openai_backend_cls.assert_called_once_with(
        model="gpt-4o-mini",
        base_url="https://gateway.example/v1",
        organization="org-example",
        project="proj_example",
    )
    anthropic_backend_cls.assert_called_once_with(
        model="claude-sonnet-4-6",
        base_url="https://anthropic.example/v1",
    )
    ollama_backend_cls.assert_called_once_with(
        model="llama3",
        host="http://localhost:11434",
    )


def test_build_llm_passes_configured_response_size_limit():
    config = Config(
        llm_max_response_chars=3,
        backends=[{"type": "ollama", "model": "llama3"}],
    )

    ensemble = build_llm(config)

    assert ensemble.max_response_chars == 3


def test_build_llm_passes_configured_prompt_size_limit():
    config = Config(
        prompt_max_chars=12,
        backends=[{"type": "ollama", "model": "llama3"}],
    )

    ensemble = build_llm(config)

    assert ensemble.max_prompt_chars == 12


def test_build_llm_passes_configured_prompt_estimated_token_limit():
    config = Config(
        prompt_max_estimated_tokens=12,
        backends=[{"type": "ollama", "model": "llama3"}],
    )

    ensemble = build_llm(config)

    assert ensemble.max_prompt_estimated_tokens == 12


def test_generate_enforces_backend_prompt_estimated_token_limit_before_call():
    backend = _b("limited", "answer")
    ens = LLMEnsemble(
        [backend],
        backend_metadata=[{"prompt_max_estimated_tokens": 2}],
    )

    with pytest.raises(ValueError, match=r"max_prompt_estimated_tokens \(3 > 2\)"):
        ens.generate("prompt text")

    assert backend.generate.call_count == 0
    assert ens.call_history == []
    assert ens.counts == [0]


def test_generate_uses_role_scoped_provider_token_counter_before_backend_call(monkeypatch):
    class FakeEncoding:
        name = "fixture_base"

        def encode(self, text):
            return text.split()

    class FakeEncoderPackage:
        @staticmethod
        def encoding_for_model(model):
            return FakeEncoding()

        @staticmethod
        def get_encoding(name):
            return FakeEncoding()

    monkeypatch.setattr(
        "libreevolve.llm.tokenization.importlib.import_module",
        lambda name: FakeEncoderPackage,
    )
    mutation_backend = _b("mutation", "mutation-answer")
    feedback_backend = _b("feedback", "feedback-answer")
    ens = LLMEnsemble(
        [mutation_backend, feedback_backend],
        backend_metadata=[
            {"type": "anthropic", "model": "claude-sonnet-4-6", "role": "mutation"},
            {
                "type": "openai",
                "model": "gpt-4o-mini",
                "role": "feedback:grader",
                "prompt_max_estimated_tokens": 2,
            },
        ],
    )

    with pytest.raises(ValueError, match=r"max_prompt_estimated_tokens \(3 > 2\)"):
        ens.generate("a b c", role="feedback:grader")

    mutation_backend.generate.assert_not_called()
    feedback_backend.generate.assert_not_called()
    assert ens.call_history == []
    assert ens.counts == [0, 0]


def test_generate_records_role_prompt_token_counter_capability(monkeypatch):
    class FakeEncoding:
        name = "fixture_base"

        def encode(self, text):
            return text.split()

    class FakeEncoderPackage:
        @staticmethod
        def encoding_for_model(model):
            return FakeEncoding()

        @staticmethod
        def get_encoding(name):
            return FakeEncoding()

    monkeypatch.setattr(
        "libreevolve.llm.tokenization.importlib.import_module",
        lambda name: FakeEncoderPackage,
    )
    backend = _b("critic", "answer")
    ens = LLMEnsemble(
        [backend],
        max_prompt_estimated_tokens=5,
        backend_metadata=[{"type": "openai", "model": "gpt-4o-mini", "role": "critique"}],
    )

    ens.generate("a b c", role="critique")

    record = ens.call_history[0]
    assert record["prompt_estimated_tokens"] == 2
    assert record["prompt_token_count_policy"] == "provider_token_counter"
    assert record["prompt_provider_tokens"] == 3
    assert record["prompt_token_limit_count"] == 3
    capability = record["prompt_token_counter_capability"]
    assert capability["schema"] == "libreevolve.prompt_token_counter_capability.v1"
    assert capability["role"] == "critique"
    assert capability["status"] == "ready"
    assert capability["counter_name"] == "openai:encoding:fixture_base"
    assert capability["eligible_backend_indices"] == [0]


def test_generate_records_effective_backend_prompt_estimated_token_limit():
    backend = _b("limited", "answer")
    ens = LLMEnsemble(
        [backend],
        max_prompt_estimated_tokens=10,
        backend_metadata=[{"prompt_max_estimated_tokens": 8}],
    )

    ens.generate("prompt text")

    record = ens.call_history[0]
    assert record["max_prompt_estimated_tokens"] == 8
    assert record["configured_max_prompt_estimated_tokens"] == 10
    assert record["backend_prompt_max_estimated_tokens"] == 8


def test_generate_enforces_backend_context_window_prompt_limit_before_call():
    backend = _b("windowed", "answer")
    ens = LLMEnsemble(
        [backend],
        backend_metadata=[{"context_window_tokens": 10, "reserved_output_tokens": 6}],
    )

    with pytest.raises(ValueError, match=r"max_prompt_estimated_tokens \(5 > 4\)"):
        ens.generate("abcdefghijklmnopq")

    assert backend.generate.call_count == 0
    assert ens.call_history == []


def test_generate_records_backend_context_window_prompt_limit():
    backend = _b("windowed", "answer")
    ens = LLMEnsemble(
        [backend],
        max_prompt_estimated_tokens=12,
        backend_metadata=[
            {
                "prompt_max_estimated_tokens": 10,
                "context_window_tokens": 9,
                "reserved_output_tokens": 2,
            }
        ],
    )

    ens.generate("prompt text")

    record = ens.call_history[0]
    assert record["max_prompt_estimated_tokens"] == 7
    assert record["configured_max_prompt_estimated_tokens"] == 12
    assert record["backend_prompt_max_estimated_tokens"] == 10
    assert record["backend_context_window_tokens"] == 9
    assert record["backend_reserved_output_tokens"] == 2
    assert record["backend_context_window_prompt_estimated_tokens"] == 7


def test_build_llm_passes_configured_call_attempt_limit():
    config = Config(
        llm_max_call_attempts=7,
        backends=[{"type": "ollama", "model": "llama3"}],
    )

    ensemble = build_llm(config)

    assert ensemble.max_call_attempts == 7


def test_build_llm_passes_configured_call_history_limit():
    config = Config(
        llm_call_history_max=3,
        backends=[{"type": "ollama", "model": "llama3"}],
    )

    ensemble = build_llm(config)

    assert ensemble.max_call_history == 3


def test_build_llm_passes_configured_provider_error_retention_mode():
    config = Config(
        provider_error_retention_mode="hash_only",
        backends=[{"type": "ollama", "model": "llama3"}],
    )

    ensemble = build_llm(config)

    assert ensemble.provider_error_retention_mode == "hash_only"


def test_build_llm_passes_configured_provider_response_retention_mode():
    config = Config(
        provider_response_retention_mode="full",
        backends=[{"type": "ollama", "model": "llama3"}],
    )

    ensemble = build_llm(config)

    assert ensemble.provider_response_retention_mode == "full"


def test_constructor_snapshots_backend_arm_list():
    b1 = _b("b1", "one")
    b2 = _b("b2", "two")
    late = _b("late", "late")
    backends = [b1, b2]
    ens = LLMEnsemble(backends)

    backends.append(late)
    backends.clear()
    backends.extend([late, b2, b1])

    response_1, idx_1 = ens.generate("prompt one")
    response_2, idx_2 = ens.generate("prompt two")

    assert (response_1, idx_1) == ("one", 0)
    assert (response_2, idx_2) == ("two", 1)
    assert ens.counts == [1, 1]
    assert ens.wins == [0.0, 0.0]
    assert [record["backend_name"] for record in ens.call_history] == ["b1", "b2"]
    assert late.generate.call_count == 0


def test_scheduler_counter_accessors_are_defensive_copies():
    ens = LLMEnsemble([_b("b1", "one")])
    ens.generate("prompt text")

    counts = ens.counts
    wins = ens.wins
    counts[0] = "bad"
    wins[0] = math.nan

    assert ens.counts == [1]
    assert ens.wins == [0.0]
    ens.generate("prompt text two")
    assert ens.counts == [2]


def test_scheduler_state_snapshot_is_defensive_copy():
    ens = LLMEnsemble([_b("b1", "one")])
    ens.generate("prompt text")
    call_id = ens.last_call["id"]
    state = ens.scheduler_state

    state["counts"][0] = "bad"
    state["wins"][0] = math.nan
    state["total"] = -1
    state["unrewarded_success_call_ids"][0].append("bad")
    state["rewarded_call_ids"].append("bad")
    state["reward_accounting_policy"]["reward_accounted_roles"].append("critique")
    state["role_accounting"]["mutation"]["calls"] = 99

    fresh = ens.scheduler_state
    assert fresh["counts"] == [1]
    assert fresh["wins"] == [0.0]
    assert fresh["total"] == 1
    assert fresh["unrewarded_success_call_ids"] == [[call_id]]
    assert fresh["rewarded_call_ids"] == []
    assert fresh["reward_accounting_policy"] == {
        "policy": "configured_reward_accounted_roles_v1",
        "reward_accounted_roles": ["mutation"],
    }
    assert fresh["role_accounting"]["mutation"]["calls"] == 1


def test_restore_scheduler_state_validates_and_restores():
    b1 = _b("b1", "one")
    b2 = _b("b2", "two")
    ens = LLMEnsemble([b1, b2])

    ens.restore_scheduler_state({"counts": [3, 2], "wins": [1.5, 0], "total": 5})

    assert ens.counts == [3, 2]
    assert ens.wins == [1.5, 0.0]
    assert ens.total == 5
    assert ens.scheduler_state["role_accounting"] == {}
    assert ens.scheduler_state["reward_accounting_policy"] == {
        "policy": "configured_reward_accounted_roles_v1",
        "reward_accounted_roles": ["mutation"],
    }
    ens.generate("prompt text")
    assert ens.total == 6


def test_restore_scheduler_state_restores_reward_accounting_policy():
    source = LLMEnsemble(
        [_b("b1", "one")],
        reward_accounted_roles=["mutation", "critique"],
    )
    source.generate("critique prompt", role="critique")

    restored = LLMEnsemble([_b("b1", "one")])
    restored.restore_scheduler_state(source.scheduler_state)
    restored.generate("critique prompt two", role="critique")

    assert restored.scheduler_state["reward_accounting_policy"] == {
        "policy": "configured_reward_accounted_roles_v1",
        "reward_accounted_roles": ["critique", "mutation"],
    }
    assert restored.last_call["scheduler_accounting"] == "rewarded"
    assert restored.counts == [2]
    assert restored.total == 2


def test_restore_scheduler_state_preserves_reward_call_ledger():
    source = LLMEnsemble([_b("b1", "one")])
    source.generate("prompt one")
    delayed_id = source.last_call["id"]
    source.generate("prompt two")
    rewarded_id = source.last_call["id"]
    source.record_reward(0, 1.0, call_id=rewarded_id)

    restored = LLMEnsemble([_b("b1", "one")])
    restored.restore_scheduler_state(source.scheduler_state)

    with pytest.raises(ValueError, match="already been rewarded"):
        restored.record_reward(0, 1.0, call_id=rewarded_id)

    restored.record_reward(0, 0.5, call_id=delayed_id)
    assert restored.wins == [1.5]
    with pytest.raises(ValueError, match="no unrewarded successful call"):
        restored.record_reward(0, 0.5)


@pytest.mark.parametrize(
    ("state", "message"),
    [
        (None, "mapping"),
        ({"counts": [0], "wins": [0.0], "total": 0, "extra": 1}, "unsupported"),
        ({"counts": [0], "wins": [0.0]}, "counts, wins, and total"),
        ({"counts": [0, 0], "wins": [0.0], "total": 0}, "counts"),
        ({"counts": [0], "wins": [0.0, 0.0], "total": 0}, "wins"),
        ({"counts": ["bad"], "wins": [0.0], "total": 0}, r"counts\[0\]"),
        ({"counts": [True], "wins": [0.0], "total": 0}, r"counts\[0\]"),
        ({"counts": [-1], "wins": [0.0], "total": 0}, r"counts\[0\]"),
        ({"counts": [0], "wins": [math.nan], "total": 0}, r"wins\[0\]"),
        ({"counts": [0], "wins": [-1.0], "total": 0}, r"wins\[0\]"),
        ({"counts": [0], "wins": [True], "total": 0}, r"wins\[0\]"),
        ({"counts": [0], "wins": [0.0], "total": True}, "total"),
        ({"counts": [0], "wins": [0.0], "total": -1}, "total"),
        ({"counts": [1], "wins": [0.0], "total": 0}, "sum"),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "unrewarded_success_call_ids": "bad",
            },
            "unrewarded_success_call_ids",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "unrewarded_success_call_ids": [["call-1"], []],
            },
            "unrewarded_success_call_ids",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "unrewarded_success_call_ids": [["call-1", "call-1"]],
            },
            "appears more than once",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "unrewarded_success_call_ids": [["call-1"]],
                "rewarded_call_ids": ["call-1"],
            },
            "both rewarded and unrewarded",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "rewarded_call_ids": ["call-1", "call-1"],
            },
            "appears more than once",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "rewarded_call_ids": [""],
            },
            "non-empty call ids",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "call_history_retention": None,
            },
            "call_history_retention",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "call_history_retention": {
                    "policy": "unbounded",
                    "max_records": 1,
                    "retained_records": 0,
                    "total_records": 0,
                    "dropped_records": 0,
                },
            },
            "policy",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "call_history_retention": {
                    "policy": "bounded_in_memory_window",
                    "max_records": 1,
                    "retained_records": 2,
                    "total_records": 2,
                    "dropped_records": 0,
                },
            },
            "retained_records",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "reward_accounting_policy": "bad",
            },
            "reward_accounting_policy",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "reward_accounting_policy": {
                    "policy": "configured_reward_accounted_roles_v1",
                    "reward_accounted_roles": ["bad role"],
                },
            },
            "role label",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "role_scheduler_scope": "global",
            },
            "role_scheduler_scope",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "role_accounting": "bad",
            },
            "role_accounting",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "role_accounting": {
                    "mutation": {
                        "calls": 1,
                        "successes": 1,
                        "failures": 0,
                        "reward_accounted_calls": 1,
                        "telemetry_only_calls": 0,
                    }
                },
            },
            "missing fields",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "role_accounting": {
                    "mutation": _role_accounting(
                        calls=1,
                        reward_accounted_calls=1,
                    )
                },
            },
            "status counts",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "role_scheduler_state": {
                    "mutation": {
                        "policy": "per_role_scheduler_audit_state_not_selection_policy",
                        "selection_policy": (
                            "backend_metadata_role_scoped_when_configured_else_global"
                        ),
                        "counts": [1],
                        "wins": [0.0],
                        "total": 0,
                        "unrewarded_success_call_ids": [[]],
                        "rewarded_call_ids": [],
                    }
                },
            },
            "total must be >= counts sum",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "role_call_limits": "bad",
            },
            "role_call_limits",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "role_call_limits": {
                    "policy": "logical_generate_call_limits_by_role_v1",
                    "max_calls_by_role": {"mutation": 1},
                    "logical_calls_by_role": {"mutation": 2},
                },
            },
            "exceeds max_calls_by_role",
        ),
        (
            {
                "counts": [0],
                "wins": [0.0],
                "total": 0,
                "role_call_limits": {
                    "policy": "logical_generate_call_limits_by_role_v1",
                    "max_calls_by_role": {"feedback:*": 1},
                    "logical_calls_by_role": {"feedback:a": 1, "feedback:b": 1},
                },
            },
            r"max_calls_by_role\['feedback:\*'\]",
        ),
    ],
)
def test_restore_scheduler_state_rejects_malformed_state(state, message):
    ens = LLMEnsemble([_b()])

    with pytest.raises(ValueError, match=message):
        ens.restore_scheduler_state(state)

    assert ens.scheduler_state == {
        "counts": [0],
        "wins": [0.0],
        "total": 0,
        "unrewarded_success_call_ids": [[]],
        "rewarded_call_ids": [],
        "call_history_retention": {
            "policy": "bounded_in_memory_window",
            "max_records": 500,
            "retained_records": 0,
            "total_records": 0,
            "dropped_records": 0,
        },
        "reward_accounting_policy": {
            "policy": "configured_reward_accounted_roles_v1",
            "reward_accounted_roles": ["mutation"],
        },
        "role_scheduler_scope": "shared",
        "role_accounting": {},
        "role_scheduler_state": {},
        "role_call_limits": {
            "policy": "logical_generate_call_limits_by_role_v1",
            "max_calls_by_role": {},
            "logical_calls_by_role": {},
        },
        "role_backend_policy": {
            "policy": "explicit_role_backend_indices_else_backend_metadata_else_global_v1",
            "configured_role_backend_indices": {},
            "metadata_role_backend_indices": {},
            "fallback_policy": "use_backend_metadata_then_global_bandit_when_role_not_configured",
        },
        "provider_failure_policy_state": {
            "schema": "libreevolve.provider_failure_policy_state.v1",
            "policy": "role_backend_consecutive_failure_quarantine_v1",
            "role_quarantine_after": {},
            "roles": {},
        },
    }


def test_call_history_retains_bounded_window_with_total_accounting():
    ens = LLMEnsemble([_b("b1", "answer")], max_call_history=2)

    ens.generate("prompt one")
    first_id = ens.last_call["id"]
    ens.generate("prompt two")
    second_id = ens.last_call["id"]
    ens.generate("prompt three")
    third_id = ens.last_call["id"]

    assert [record["id"] for record in ens.call_history] == [second_id, third_id]
    assert first_id not in {record["id"] for record in ens.call_history}
    assert ens.last_call["id"] == third_id
    assert ens.call_history_retention == {
        "policy": "bounded_in_memory_window",
        "max_records": 2,
        "retained_records": 2,
        "total_records": 3,
        "dropped_records": 1,
    }
    assert ens.scheduler_state["call_history_retention"]["dropped_records"] == 1


def test_call_history_retention_snapshot_is_defensive_copy():
    ens = LLMEnsemble([_b("b1", "answer")], max_call_history=1)
    ens.generate("prompt text")

    retention = ens.call_history_retention
    retention["retained_records"] = 999
    retention["policy"] = "corrupted"

    assert ens.call_history_retention == {
        "policy": "bounded_in_memory_window",
        "max_records": 1,
        "retained_records": 1,
        "total_records": 1,
        "dropped_records": 0,
    }


def test_record_reward_can_claim_evicted_successful_call_by_id():
    ens = LLMEnsemble([_b("b1", "answer")], max_call_history=1)

    ens.generate("prompt one")
    first_id = ens.last_call["id"]
    ens.generate("prompt two")

    assert first_id not in {record["id"] for record in ens.call_history}
    ens.record_reward(0, 0.75, call_id=first_id)

    assert ens.wins == [0.75]
    assert first_id in ens.scheduler_state["rewarded_call_ids"]
    assert all(record.get("rewarded") is not True for record in ens.call_history)


def test_generate_records_normalized_call_telemetry():
    ens = LLMEnsemble(
        [_b("b1", "answer")],
        backend_metadata=[{"cost": 2.0, "latency": 3.0, "depth": 4.0, "role": "breadth"}],
    )

    response, idx = ens.generate("prompt text", role="mutation")

    assert response == "answer"
    assert idx == 0
    assert len(ens.call_history) == 1
    record = ens.call_history[0]
    assert record["role"] == "mutation"
    assert record["backend_idx"] == 0
    assert record["backend_name"] == "b1"
    assert record["backend_metadata"]["role"] == "breadth"
    assert record["backend_telemetry_diagnostics"] == []
    assert record["provider_status_code"] is None
    assert record["client_context"] == {}
    assert record["scheduler_accounting"] == "rewarded"
    assert record["status"] == "ok"
    assert record["prompt_chars"] == len("prompt text")
    assert record["output_chars"] == len("answer")
    assert len(record["prompt_sha256"]) == 64
    assert len(record["output_sha256"]) == 64
    assert record["output"] is None
    assert record["output_retention"] == {
        "retention_mode": "hash_only",
        "retention_policy": "hash_only_with_raw_sha256",
        "sha256": record["output_sha256"],
        "chars": len("answer"),
        "stored_chars": 0,
        "redacted": False,
        "truncated": False,
    }
    assert record["usage"] is None
    assert record["adapter_retry"] is None
    assert record["sequence_id"] == 1
    assert record["counts_before"] == [0]
    assert record["counts_after"] == [1]


def test_call_ids_are_deterministic_for_matching_call_streams():
    first = LLMEnsemble([_b("b1", "answer")])
    second = LLMEnsemble([_b("b1", "answer")])

    first.generate("prompt text", role="mutation")
    second.generate("prompt text", role="mutation")

    assert first.call_history[0]["id"].startswith("llm-call-")
    assert first.call_history[0]["id"] == second.call_history[0]["id"]


def test_repeated_matching_calls_in_one_stream_keep_distinct_ids():
    ens = LLMEnsemble([_b("b1", "answer")])

    ens.generate("prompt text", role="mutation")
    ens.generate("prompt text", role="mutation")

    assert ens.call_history[0]["prompt_sha256"] == ens.call_history[1]["prompt_sha256"]
    assert ens.call_history[0]["id"] != ens.call_history[1]["id"]


def test_generate_streams_call_records_to_configured_sink():
    records = []
    ens = LLMEnsemble([_b("b1", "answer")])
    ens.set_call_record_sink(records.append)

    ens.generate("prompt text", role="mutation")
    records[0]["backend_name"] = "mutated"

    assert len(records) == 1
    assert records[0]["sequence_id"] == 1
    assert ens.call_history[0]["backend_name"] == "b1"


def test_record_reward_streams_reward_event_to_configured_sink():
    records = []
    ens = LLMEnsemble([_b("b1", "answer")])
    ens.set_call_record_sink(records.append)

    ens.generate("prompt text", role="mutation")
    call_id = records[0]["id"]
    ens.record_reward(0, 0.75, call_id=call_id)

    assert [record["record_type"] for record in records if "record_type" in record] == [
        "reward"
    ]
    assert records[1]["call_id"] == call_id
    assert records[1]["reward"] == 0.75
    assert records[1]["rewarded"] is True


def _write_llm_call_ledger(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )


def _valid_llm_call_records() -> list[dict]:
    records = []
    ens = LLMEnsemble([_b("b1", "answer")])
    ens.set_call_record_sink(records.append)
    ens.generate("prompt text", role="mutation")
    ens.record_reward(0, 0.75, call_id=records[0]["id"])
    return records


def _malformed_provider_diagnostics_record() -> dict:
    value = "api_key=sk-proj_replayeddiagnostic_secret_1234567890"  # pragma: allowlist secret
    return {
        "policy": "bounded_provider_diagnostics_v1",
        "max_items": 8,
        "max_string_chars": 200,
        "items": [
            {
                "key": "warning",
                "value": value,
                "value_type": "str",
                "sha256": "0" * 64,
                "chars": len(value),
                "stored_chars": len(value),
                "redacted": False,
                "truncated": False,
            }
        ],
        "omitted_items": 0,
    }


def test_load_llm_call_ledger_validates_call_and_reward_rows(tmp_path):
    records = _valid_llm_call_records()
    ledger = tmp_path / "llm_calls.jsonl"
    _write_llm_call_ledger(ledger, records)

    replay = load_llm_call_ledger(ledger, backend_count=1)

    call_id = records[0]["id"]
    assert replay["call_count"] == 1
    assert replay["reward_count"] == 1
    assert replay["last_sequence_id"] == 1
    assert replay["successful_call_ids"] == [call_id]
    assert replay["rewarded_call_ids"] == [call_id]
    assert replay["unrewarded_success_call_ids"] == []
    assert replay["provider_failure_policy_summary"] == {
        "schema": "libreevolve.provider_failure_policy_summary.v1",
        "scope": "llm_call_ledger_replay",
        "roles": {},
        "total_failed_policy_records": 0,
        "remaining_gap": (
            "provider_output_replay_and_hard_cancellation_not_implemented"
        ),
    }
    _assert_role_accounting(
        replay["role_accounting"]["mutation"],
        calls=1,
        successes=1,
        reward_accounted_calls=1,
    )
    replay["calls"][call_id]["backend_idx"] = 99
    assert load_llm_call_ledger(ledger, backend_count=1)["calls"][call_id]["backend_idx"] == 0


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda rows: rows[0].update({"sequence_id": 2}), "sequence_id must be 1"),
        (lambda rows: rows.append(dict(rows[0])), "duplicate call id"),
        (lambda rows: rows[1].update({"call_id": "missing"}), "unknown call id"),
        (lambda rows: rows.append(dict(rows[1])), "duplicate reward"),
        (lambda rows: rows[1].update({"backend_idx": 99}), "backend_idx out of range"),
        (lambda rows: rows[0].update({"counts_after": [0]}), "counts_after is inconsistent"),
        (
            lambda rows: rows[0].update({"scheduler_accounting": "invalid"}),
            "scheduler_accounting",
        ),
        (lambda rows: rows[0].update({"role": "api_key=sk-proj_role_secret_1234567890"}), "role"),  # pragma: allowlist secret
        (
            lambda rows: rows[0].update(
                {"backend_name": "api_key=sk-proj_restoredbackend_secret_1234567890"}  # pragma: allowlist secret
            ),
            "backend_name",
        ),
        (lambda rows: rows[0].update({"api_mode": "bad mode"}), "api_mode"),
        (
            lambda rows: rows[0].update(
                {
                    "backend_metadata": {
                        "label": "api_key=sk-proj_restoredmetadata_secret_1234567890"  # pragma: allowlist secret
                    }
                }
            ),
            "backend_metadata",
        ),
        (
            lambda rows: rows[0].update({"backend_telemetry_diagnostics": "bad"}),
            "backend_telemetry_diagnostics",
        ),
        (
            lambda rows: rows[0].update(
                {
                    "backend_defaults": {
                        "policy": "effective_backend_generation_defaults_v1",
                        "max_tokens": 0,
                        "provider_max_retries": 2,
                    }
                }
            ),
            "backend_defaults.max_tokens",
        ),
        (
            lambda rows: rows[0].update(
                {"client_context": {"base_url": "https://example.test?x=1"}}
            ),
            "client_context",
        ),
        (
            lambda rows: rows[0].update(
                {"usage": {"input_tokens": -1}}
            ),
            "usage.input_tokens",
        ),
        (
            lambda rows: rows[0].update(
                {
                    "cost_estimate": {
                        "policy": "backend_metadata_cost_per_million_tokens_v1",
                        "source": "backend_metadata.cost_usd_per_million_tokens",
                        "pricing_source": "configured_backend_metadata",
                        "pricing_status": "configured_estimate_not_live_provider_pricing",
                        "token_count_source": "provider_response_metadata.usage.total_tokens",
                        "cost_usd_per_million_tokens": 5.0,
                        "total_tokens": 2000,
                        "cost_microusd": 1,
                    }
                }
            ),
            "cost_estimate.cost_microusd is inconsistent",
        ),
        (
            lambda rows: rows[0].update(
                {
                    "cost_estimate_status": {
                        "policy": "backend_metadata_cost_estimate_status_v1",
                        "status": "estimated",
                        "reason": "missing_configured_backend_cost_rate",
                        "pricing_source": "configured_backend_metadata",
                        "token_count_source": "provider_response_metadata.usage.total_tokens",
                        "live_pricing_status": "not_fetched",
                    }
                }
            ),
            "cost_estimate_status.reason is inconsistent",
        ),
        (
            lambda rows: rows[0].update(
                {"response_id": "api_key=sk-proj_responseid_secret_1234567890"}  # pragma: allowlist secret
            ),
            "response_id",
        ),
        (
            lambda rows: rows[0].update({"request_id": "req_\u202e123"}),
            "request_id",
        ),
        (
            lambda rows: rows[0].update(
                {
                    "adapter_retry": {
                        "policy": "bounded_provider_internal_retries",
                        "max_retries": 0,
                        "attempts": 2,
                        "failed_attempts": 0,
                        "failures": [],
                    }
                }
            ),
            "adapter_retry.attempts",
        ),
        (
            lambda rows: rows[0].update(
                {"provider_diagnostics": _malformed_provider_diagnostics_record()}
            ),
            "provider_diagnostics",
        ),
        (
            lambda rows: rows[0].update({"provider_diagnostics": {"warning": "safe"}}),
            "provider_diagnostics.policy",
        ),
        (
            lambda rows: rows[0].update(
                {
                    "backend_telemetry_diagnostics": [
                        {"field": "backend_name", "reason": "unsafe_or_non_string", "value_type": "bad type"}
                    ]
                }
            ),
            "value_type",
        ),
        (
            lambda rows: rows[0].update(
                {
                    "provider_response_error": {
                        "category": "empty_text",
                        "source": "LLM_backend",
                    }
                }
            ),
            "ok call provider_response_error must be null",
        ),
        (
            lambda rows: rows[0].update(
                {
                    "provider_failure_policy": {
                        "schema": "libreevolve.provider_failure_policy.v1",
                        "scope": "ensemble_call_local_retry_fallback_policy",
                        "role": "mutation",
                        "provider_failure_category": "timeout",
                        "retry_decision": "no_retry",
                        "fallback_decision": "no_fallback",
                        "quarantine_decision": "not_quarantined_by_ensemble_policy",
                        "penalty_decision": "not_penalized_by_ensemble_policy",
                        "remaining_gap": (
                            "provider_output_replay_and_hard_cancellation_not_implemented"
                        ),
                    }
                }
            ),
            "ok call provider_failure_policy must be null",
        ),
        (
            lambda rows: rows[0].update({"provider_failure_category": "timeout"}),
            "ok call provider_failure_category must be null",
        ),
        (
            lambda rows: rows[0].update(
                {
                    "cancellation_record": {
                        "schema": "libreevolve.provider_cancellation_record.v1",
                        "scope": "ensemble_call_timeout",
                        "role": "mutation",
                        "backend_idx": 0,
                        "call_id": rows[0]["id"],
                        "cancellation_kind": "ensemble_wait_deadline",
                        "timeout_sec": 0.1,
                        "status": "deadline_exceeded",
                        "budget_action": "telemetry_only",
                        "hard_cancel_ready": False,
                        "in_flight_cancellation": (
                            "unsupported_daemon_worker_may_continue"
                        ),
                        "remaining_gap": (
                            "provider_sdk_hard_cancellation_not_implemented"
                        ),
                    }
                }
            ),
            "ok call cancellation_record must be null",
        ),
        (
            lambda rows: rows[0].update({"provider_status_code": 429}),
            "ok call provider_status_code must be null",
        ),
        (
            lambda rows: rows[0].update(
                {
                    "status": "error",
                    "output_sha256": None,
                    "output_retention": None,
                    "provider_failure_category": "provider_client_error",
                    "provider_status_code": 99,
                    "counts_after": [1],
                }
            ),
            "provider_status_code",
        ),
        (lambda rows: rows[1].update({"reward": 2.0}), "reward exceeds"),
        (lambda rows: rows[1].update({"reward_raw": 0.5}), "reward exceeds reward_raw"),
    ],
)
def test_load_llm_call_ledger_rejects_malformed_replay_rows(
    tmp_path, mutate, message
):
    records = _valid_llm_call_records()
    mutate(records)
    ledger = tmp_path / "llm_calls.jsonl"
    _write_llm_call_ledger(ledger, records)

    with pytest.raises(LLMCallLedgerError, match=message):
        load_llm_call_ledger(ledger, backend_count=1)


def test_load_llm_call_ledger_validates_provider_failure_policy(tmp_path):
    records = []
    backend = _b("b1")
    backend.generate.side_effect = TimeoutError("slow")
    ens = LLMEnsemble([backend])
    ens.set_call_record_sink(records.append)

    with pytest.raises(TimeoutError):
        ens.generate("prompt text", role="mutation")

    ledger = tmp_path / "llm_calls.jsonl"
    _write_llm_call_ledger(ledger, records)

    replay = load_llm_call_ledger(ledger, backend_count=1)
    call = replay["calls"][records[0]["id"]]

    assert call["provider_failure_policy"] == records[0]["provider_failure_policy"]
    assert call["provider_failure_policy"]["provider_failure_category"] == "timeout"
    assert call["provider_failure_policy"]["quarantine_decision"] == (
        "not_quarantined_by_ensemble_policy"
    )
    assert replay["provider_failure_policy_summary"] == {
        "schema": "libreevolve.provider_failure_policy_summary.v1",
        "scope": "llm_call_ledger_replay",
        "roles": {
            "mutation": {
                "failed_policy_records": 1,
                "provider_failure_categories": {"timeout": 1},
                "retry_decisions": {"no_retry": 1},
                "fallback_decisions": {"no_fallback": 1},
                "quarantine_decisions": {
                    "not_quarantined_by_ensemble_policy": 1,
                },
                "penalty_decisions": {
                    "not_penalized_by_ensemble_policy": 1,
                },
            }
        },
        "total_failed_policy_records": 1,
        "remaining_gap": (
            "provider_output_replay_and_hard_cancellation_not_implemented"
        ),
    }


def test_load_llm_call_ledger_validates_timeout_cancellation_record(tmp_path):
    records = []

    class SlowBackend:
        name = "slow"
        api_mode = None

        def generate(self, prompt, **kwargs):
            time.sleep(0.05)
            return "late"

    ens = LLMEnsemble([SlowBackend()], call_timeout_sec=0.001)
    ens.set_call_record_sink(records.append)

    with pytest.raises(ProviderCallTimeoutError):
        ens.generate("prompt text", role="feedback:judge")

    ledger = tmp_path / "llm_calls.jsonl"
    _write_llm_call_ledger(ledger, records)

    replay = load_llm_call_ledger(ledger, backend_count=1)
    call = replay["calls"][records[0]["id"]]

    assert call["cancellation_record"] == {
        "schema": "libreevolve.provider_cancellation_record.v1",
        "scope": "ensemble_call_timeout",
        "role": "feedback:judge",
        "backend_idx": 0,
        "call_id": records[0]["id"],
        "cancellation_kind": "ensemble_wait_deadline",
        "timeout_sec": 0.001,
        "status": "deadline_exceeded",
        "budget_action": "telemetry_only",
        "hard_cancel_ready": False,
        "in_flight_cancellation": "unsupported_daemon_worker_may_continue",
        "remaining_gap": "provider_sdk_hard_cancellation_not_implemented",
    }


def test_load_llm_call_ledger_rejects_malformed_timeout_cancellation_record(tmp_path):
    records = []

    class SlowBackend:
        name = "slow"
        api_mode = None

        def generate(self, prompt, **kwargs):
            time.sleep(0.05)
            return "late"

    ens = LLMEnsemble([SlowBackend()], call_timeout_sec=0.001)
    ens.set_call_record_sink(records.append)

    with pytest.raises(ProviderCallTimeoutError):
        ens.generate("prompt text", role="mutation")
    records[0]["cancellation_record"]["call_id"] = "wrong-call-id"

    ledger = tmp_path / "llm_calls.jsonl"
    _write_llm_call_ledger(ledger, records)

    with pytest.raises(LLMCallLedgerError, match="cancellation_record.call_id"):
        load_llm_call_ledger(ledger, backend_count=1)


def test_load_llm_call_ledger_rejects_duplicate_json_names(tmp_path):
    ledger = tmp_path / "llm_calls.jsonl"
    ledger.write_text(
        '{"id":"one","id":"two","sequence_id":1,"role":"mutation"}\n',
        encoding="utf-8",
    )

    with pytest.raises(LLMCallLedgerError, match="duplicate JSON object name 'id'"):
        load_llm_call_ledger(ledger)


def test_load_llm_call_ledger_rejects_reward_for_failed_call(tmp_path):
    records = []
    failing_backend = _b("b1", "answer")
    failing_backend.generate.side_effect = RuntimeError("provider down")
    ens = LLMEnsemble([failing_backend], fallback=False)
    ens.set_call_record_sink(records.append)
    with pytest.raises(RuntimeError):
        ens.generate("prompt text", role="mutation")
    records.append(
        {
            "record_type": "reward",
            "call_id": records[0]["id"],
            "backend_idx": 0,
            "reward": 0.5,
            "reward_raw": 0.5,
            "rewarded": True,
        }
    )
    ledger = tmp_path / "llm_calls.jsonl"
    _write_llm_call_ledger(ledger, records)

    with pytest.raises(LLMCallLedgerError, match="non-successful call"):
        load_llm_call_ledger(ledger, backend_count=1)


def test_load_llm_call_ledger_rejects_reward_for_telemetry_only_call(tmp_path):
    records = []
    ens = LLMEnsemble([_b("b1", "answer")])
    ens.set_call_record_sink(records.append)
    ens.generate("prompt text", role="critique")
    records.append(
        {
            "record_type": "reward",
            "call_id": records[0]["id"],
            "backend_idx": 0,
            "reward": 0.5,
            "reward_raw": 0.5,
            "rewarded": True,
        }
    )
    ledger = tmp_path / "llm_calls.jsonl"
    _write_llm_call_ledger(ledger, records)

    with pytest.raises(LLMCallLedgerError, match="non-rewardable call"):
        load_llm_call_ledger(ledger, backend_count=1)


def test_load_llm_call_ledger_rejects_invalid_provider_response_error(tmp_path):
    records = []
    failing_backend = _b("b1", None)
    ens = LLMEnsemble([failing_backend], fallback=False)
    ens.set_call_record_sink(records.append)
    with pytest.raises(ValueError):
        ens.generate("prompt text", role="mutation")
    records[0]["provider_response_error"]["category"] = "unknown"
    ledger = tmp_path / "llm_calls.jsonl"
    _write_llm_call_ledger(ledger, records)

    with pytest.raises(LLMCallLedgerError, match="category is unsupported"):
        load_llm_call_ledger(ledger, backend_count=1)


def test_load_llm_call_ledger_rejects_invalid_provider_failure_category(tmp_path):
    records = []
    failing_backend = _b("b1", "answer")
    failing_backend.generate.side_effect = RuntimeError("provider down")
    ens = LLMEnsemble([failing_backend], fallback=False)
    ens.set_call_record_sink(records.append)
    with pytest.raises(RuntimeError):
        ens.generate("prompt text", role="mutation")
    records[0]["provider_failure_category"] = "not_a_category"
    ledger = tmp_path / "llm_calls.jsonl"
    _write_llm_call_ledger(ledger, records)

    with pytest.raises(LLMCallLedgerError, match="provider_failure_category"):
        load_llm_call_ledger(ledger, backend_count=1)


def test_load_llm_call_ledger_rejects_invalid_provider_error_retention(tmp_path):
    records = []
    failing_backend = _b("b1", "answer")
    failing_backend.generate.side_effect = RuntimeError("provider down")
    ens = LLMEnsemble([failing_backend], fallback=False)
    ens.set_call_record_sink(records.append)
    with pytest.raises(RuntimeError):
        ens.generate("prompt text", role="mutation")
    records[0]["error_retention"]["retention_policy"] = "wrong"
    ledger = tmp_path / "llm_calls.jsonl"
    _write_llm_call_ledger(ledger, records)

    with pytest.raises(LLMCallLedgerError, match="error_retention.retention_policy"):
        load_llm_call_ledger(ledger, backend_count=1)


def test_load_llm_call_ledger_rejects_invalid_provider_response_retention(tmp_path):
    records = []
    ens = LLMEnsemble([_b("b1", "answer")], provider_response_retention_mode="full")
    ens.set_call_record_sink(records.append)
    ens.generate("prompt text", role="mutation")
    records[0]["output_retention"]["retention_policy"] = "wrong"
    ledger = tmp_path / "llm_calls.jsonl"
    _write_llm_call_ledger(ledger, records)

    with pytest.raises(LLMCallLedgerError, match="output_retention.retention_policy"):
        load_llm_call_ledger(ledger, backend_count=1)


def test_load_llm_call_ledger_rejects_output_text_without_retention_mode(tmp_path):
    records = []
    ens = LLMEnsemble([_b("b1", "answer")])
    ens.set_call_record_sink(records.append)
    ens.generate("prompt text", role="mutation")
    records[0]["output"] = "answer"
    ledger = tmp_path / "llm_calls.jsonl"
    _write_llm_call_ledger(ledger, records)

    with pytest.raises(LLMCallLedgerError, match="output must be null"):
        load_llm_call_ledger(ledger, backend_count=1)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda rows: rows[0].update({"schema_version": 999}), "unsupported schema_version"),
        (
            lambda rows: rows[0].update(
                {
                    "schema_version": ARTIFACT_SCHEMA_VERSION,
                    "record_schema": "libreevolve.other.v1",
                }
            ),
            "unsupported record_schema",
        ),
        (lambda rows: rows[1].update({"schema_version": 999}), "unsupported schema_version"),
    ],
)
def test_load_llm_call_ledger_rejects_unsupported_declared_schema(
    tmp_path,
    mutate,
    message,
):
    records = _valid_llm_call_records()
    records[0]["schema_version"] = ARTIFACT_SCHEMA_VERSION
    records[0]["record_schema"] = "libreevolve.llm_call.v1"
    records[1]["schema_version"] = ARTIFACT_SCHEMA_VERSION
    records[1]["record_schema"] = "libreevolve.llm_reward.v1"
    mutate(records)
    ledger = tmp_path / "llm_calls.jsonl"
    _write_llm_call_ledger(ledger, records)

    with pytest.raises(LLMCallLedgerError, match=message):
        load_llm_call_ledger(ledger, backend_count=1)


def test_generate_rejects_oversized_response_before_success_accounting():
    backend = _b("b1", "A" * 11)
    ens = LLMEnsemble([backend], max_response_chars=10)

    with pytest.raises(ValueError, match="exceeded maximum accepted size"):
        ens.generate("prompt text", role="mutation")

    assert ens.counts == [1]
    assert ens.wins == [0.0]
    record = ens.call_history[0]
    assert record["status"] == "error"
    assert record["output_chars"] == 0
    assert record["output_sha256"] is None
    assert record["error_type"] == "ProviderResponseError"
    assert record["provider_failure_category"] == "provider_response"
    assert record["provider_status_code"] is None
    assert record["provider_response_error"] == {
        "category": "oversized_text",
        "source": "LLM_backend",
    }
    assert record["provider_failure_policy"] == {
        "schema": "libreevolve.provider_failure_policy.v1",
        "scope": "ensemble_call_local_retry_fallback_policy",
        "role": "mutation",
        "provider_failure_category": "provider_response",
        "retry_decision": "no_retry",
        "fallback_decision": "no_fallback",
        "quarantine_decision": "not_quarantined_by_ensemble_policy",
        "penalty_decision": "not_penalized_by_ensemble_policy",
        "remaining_gap": (
            "provider_output_replay_and_hard_cancellation_not_implemented"
        ),
    }
    assert "11 chars > 10" in record["error"]
    assert record["counts_after"] == [1]


def test_generate_falls_back_after_oversized_response():
    too_large = _b("large", "A" * 11)
    ok = _b("ok", "accepted")
    ens = LLMEnsemble([too_large, ok], max_response_chars=10, fallback=True)

    response, idx = ens.generate("prompt text", role="mutation")

    assert response == "accepted"
    assert idx == 1
    assert ens.counts == [1, 1]
    assert [record["status"] for record in ens.call_history] == ["error", "ok"]
    assert ens.call_history[0]["will_fallback"] is True
    assert ens.call_history[0]["provider_failure_policy"]["fallback_decision"] == "fallback"
    assert ens.call_history[1]["output_chars"] == len("accepted")


def test_generate_sanitizes_backend_object_telemetry_before_call_history():
    raw_secret = "sk-proj_backend_name_secret_1234567890"  # pragma: allowlist secret

    class UnsafeTelemetryBackend:
        name = f"api_key={raw_secret}"
        api_mode = object()

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble([UnsafeTelemetryBackend()])

    response, idx = ens.generate("prompt text", role="mutation")

    assert response == "answer"
    assert idx == 0
    record = ens.call_history[0]
    assert record["backend_name"] == "UnsafeTelemetryBackend"
    assert record["api_mode"] is None
    assert {
        "field": "backend_name",
        "reason": "unsafe_or_non_string",
        "value_type": "str",
    } in record["backend_telemetry_diagnostics"]
    assert {
        "field": "api_mode",
        "reason": "unsafe_or_non_string",
        "value_type": "object",
    } in record["backend_telemetry_diagnostics"]
    assert raw_secret not in strict_json_dumps(record)


def test_generate_records_backend_request_parameter_telemetry():
    class ParameterizedBackend:
        name = "parameterized"
        api_mode = "chat"
        request_parameters = {
            "temperature": 0.2,
            "top_p": 0.9,
            "stop": ["END"],
            "seed": 123,
        }

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble([ParameterizedBackend()])

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["request_parameters"] == {
        "temperature": 0.2,
        "top_p": 0.9,
        "stop": ["END"],
        "seed": 123,
    }
    assert record["backend_telemetry_diagnostics"] == []
    record["request_parameters"]["stop"].append("MUTATED")
    assert ens.call_history[0]["request_parameters"]["stop"] == ["END"]


def test_generate_records_backend_defaults_telemetry():
    class DefaultsBackend:
        name = "defaults"
        api_mode = "chat"
        backend_defaults = {
            "policy": "effective_backend_generation_defaults_v1",
            "max_tokens": 4096,
            "provider_max_retries": 2,
            "timeout_sec": None,
            "api_mode": "chat",
            "api_mode_policy": None,
            "reasoning_effort": None,
        }

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble([DefaultsBackend()])

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["backend_defaults"] == {
        "policy": "effective_backend_generation_defaults_v1",
        "max_tokens": 4096,
        "provider_max_retries": 2,
        "timeout_sec": None,
        "api_mode": "chat",
        "api_mode_policy": None,
        "reasoning_effort": None,
    }
    assert record["backend_telemetry_diagnostics"] == []
    record["backend_defaults"]["max_tokens"] = 1
    assert ens.call_history[0]["backend_defaults"]["max_tokens"] == 4096


def test_generate_sanitizes_invalid_backend_defaults_telemetry():
    class UnsafeDefaultsBackend:
        name = "unsafe-defaults"
        api_mode = "chat"
        backend_defaults = {
            "policy": "effective_backend_generation_defaults_v1",
            "max_tokens": 4096,
            "provider_max_retries": 2,
            "api_mode": "api_key=sk-proj_backenddefault_secret_1234567890",  # pragma: allowlist secret
        }

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble([UnsafeDefaultsBackend()])

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["backend_defaults"] == {}
    assert {
        "field": "backend_defaults",
        "reason": "unsafe_or_non_string",
        "value_type": "dict",
    } in record["backend_telemetry_diagnostics"]
    assert "sk-proj_backenddefault_secret_1234567890" not in strict_json_dumps(record)


def test_generate_sanitizes_invalid_backend_request_parameter_telemetry():
    class UnsafeRequestParameterBackend:
        name = "unsafe-request-params"
        api_mode = "chat"
        request_parameters = {"stop": ["api_key=sk-proj_requestparam_secret_1234567890"]}  # pragma: allowlist secret

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble([UnsafeRequestParameterBackend()])

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["request_parameters"] == {}
    assert {
        "field": "request_parameters",
        "reason": "unsafe_or_non_string",
        "value_type": "dict",
    } in record["backend_telemetry_diagnostics"]
    assert "sk-proj_requestparam_secret_1234567890" not in strict_json_dumps(record)


def test_generate_records_backend_client_context_telemetry():
    class ContextualBackend:
        name = "contextual"
        api_mode = "chat"
        client_context = {
            "base_url": "https://gateway.example/v1",
            "organization": "org-example",
            "project": "proj_example",
        }

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble([ContextualBackend()])

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["client_context"] == {
        "base_url": "https://gateway.example/v1",
        "organization": "org-example",
        "project": "proj_example",
    }
    assert record["backend_telemetry_diagnostics"] == []
    record["client_context"]["organization"] = "mutated"
    assert ens.call_history[0]["client_context"]["organization"] == "org-example"


def test_generate_sanitizes_invalid_backend_client_context_telemetry():
    class UnsafeClientContextBackend:
        name = "unsafe-client-context"
        api_mode = "chat"
        client_context = {"base_url": "https://example.test?api_key=sk-proj_clientctx_secret_1234567890"}  # pragma: allowlist secret

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble([UnsafeClientContextBackend()])

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["client_context"] == {}
    assert {
        "field": "client_context",
        "reason": "unsafe_or_non_string",
        "value_type": "dict",
    } in record["backend_telemetry_diagnostics"]
    assert "sk-proj_clientctx_secret_1234567890" not in strict_json_dumps(record)


def test_generate_records_backend_provider_response_metadata():
    class MetadataBackend:
        name = "metadata"
        api_mode = "chat"
        provider_response_metadata = {
            "usage": {
                "input_tokens": 7,
                "output_tokens": 11,
                "total_tokens": 18,
            },
            "finish_reason": "stop",
            "request_id": "req_123",
            "response_id": "resp_456",
            "adapter_retry": {
                "policy": "bounded_provider_internal_retries",
                "max_retries": 1,
                "attempts": 2,
                "failed_attempts": 1,
                "failures": [{"attempt": 0, "error_type": "RuntimeError"}],
            },
        }

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble([MetadataBackend()])

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["usage"] == {
        "input_tokens": 7,
        "output_tokens": 11,
        "total_tokens": 18,
    }
    assert record["finish_reason"] == "stop"
    assert record["request_id"] == "req_123"
    assert record["response_id"] == "resp_456"
    assert record["adapter_retry"] == {
        "policy": "bounded_provider_internal_retries",
        "max_retries": 1,
        "attempts": 2,
        "failed_attempts": 1,
        "failures": [{"attempt": 0, "error_type": "RuntimeError"}],
    }
    assert record["backend_telemetry_diagnostics"] == []
    assert ens.scheduler_state["role_accounting"]["mutation"]["input_tokens"] == 7
    assert ens.scheduler_state["role_accounting"]["mutation"]["output_tokens"] == 11
    assert ens.scheduler_state["role_accounting"]["mutation"]["total_tokens"] == 18
    record["usage"]["input_tokens"] = 999
    assert ens.call_history[0]["usage"]["input_tokens"] == 7


def test_generate_records_bounded_provider_diagnostics_metadata():
    raw_secret = "sk-proj_providerdiagnostic_secret_1234567890"  # pragma: allowlist secret
    warning = "api_key=" + raw_secret + " " + ("x" * 260)

    class DiagnosticsBackend:
        name = "diagnostics"
        api_mode = "chat"
        provider_response_metadata = {
            "provider_diagnostics": {
                "cache_hit": False,
                "empty_value": None,
                "request_window_remaining": 42,
                "aa_warning": warning,
                **{f"extra_{index}": index for index in range(10)},
            },
        }

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble([DiagnosticsBackend()])

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    diagnostics = record["provider_diagnostics"]
    assert diagnostics == {
        "policy": "bounded_provider_diagnostics_v1",
        "max_items": 8,
        "max_string_chars": 200,
        "items": diagnostics["items"],
        "omitted_items": 6,
    }
    assert len(diagnostics["items"]) == 8
    by_key = {item["key"]: item for item in diagnostics["items"]}
    assert by_key["cache_hit"] == {
        "key": "cache_hit",
        "value": False,
        "value_type": "bool",
    }
    assert by_key["empty_value"] == {
        "key": "empty_value",
        "value": None,
        "value_type": "null",
    }
    warning_item = by_key["aa_warning"]
    assert warning_item["value_type"] == "str"
    assert warning_item["sha256"] == hashlib.sha256(warning.encode("utf-8")).hexdigest()
    assert warning_item["chars"] == len(warning)
    assert warning_item["stored_chars"] == 200
    assert warning_item["redacted"] is True
    assert warning_item["truncated"] is True
    assert raw_secret not in strict_json_dumps(record)
    assert record["backend_telemetry_diagnostics"] == []
    diagnostics["items"][0]["key"] = "mutated"
    assert ens.call_history[0]["provider_diagnostics"]["items"][0]["key"] != "mutated"


def test_generate_records_configured_provider_cost_estimate():
    class MetadataBackend:
        name = "metadata"
        api_mode = "chat"
        provider_response_metadata = {
            "usage": {
                "input_tokens": 400,
                "output_tokens": 1600,
                "total_tokens": 2000,
            },
        }

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble(
        [MetadataBackend()],
        backend_metadata=[{"cost_usd_per_million_tokens": 5.0}],
    )

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["cost_estimate"] == {
        "policy": "backend_metadata_cost_per_million_tokens_v1",
        "source": "backend_metadata.cost_usd_per_million_tokens",
        "pricing_source": "configured_backend_metadata",
        "pricing_status": "configured_estimate_not_live_provider_pricing",
        "token_count_source": "provider_response_metadata.usage.total_tokens",
        "cost_usd_per_million_tokens": 5.0,
        "total_tokens": 2000,
        "cost_microusd": 10000,
    }
    assert record["cost_estimate_status"] == {
        "policy": "backend_metadata_cost_estimate_status_v1",
        "status": "estimated",
        "reason": "estimated_from_configured_rate_and_provider_total_tokens",
        "pricing_source": "configured_backend_metadata",
        "token_count_source": "provider_response_metadata.usage.total_tokens",
        "live_pricing_status": "not_fetched",
    }
    assert ens.scheduler_state["role_accounting"]["mutation"]["cost_microusd"] == 10000


def test_provider_diagnostics_summary_aggregates_retained_call_history():
    class DiagnosticsBackend:
        name = "diagnostics"
        api_mode = "chat"
        backend_defaults = {
            "policy": "effective_backend_generation_defaults_v1",
            "api_mode": "chat",
            "api_mode_policy": "configured",
            "max_tokens": 4096,
            "provider_max_retries": 2,
            "timeout_sec": None,
            "reasoning_effort": None,
        }
        provider_response_metadata = {
            "usage": {
                "input_tokens": 3,
                "output_tokens": 5,
                "total_tokens": 8,
            },
            "provider_diagnostics": {
                "system_fingerprint": "fp_safe",
                "duration_ms": 12,
            },
        }

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble(
        [DiagnosticsBackend()],
        backend_metadata=[{"cost_usd_per_million_tokens": 2.5}],
    )

    ens.generate("prompt text", role="mutation")

    summary = ens.provider_diagnostics_summary
    assert summary["schema"] == LLM_PROVIDER_DIAGNOSTICS_SCHEMA
    assert summary["status"] == "snapshot"
    assert summary["source"] == "LLMEnsemble.call_history"
    assert summary["totals"] == {
        "call_count": 1,
        "usage_record_count": 1,
        "provider_response_retention_record_count": 1,
        "provider_response_hash_count": 1,
        "provider_response_text_retained_count": 0,
        "provider_response_stored_chars": 0,
        "provider_response_redacted_count": 0,
        "provider_response_truncated_count": 0,
        "provider_response_retention_modes": {"hash_only": 1},
        "provider_response_retention_policies": {"hash_only_with_raw_sha256": 1},
        "provider_error_retention_record_count": 0,
        "provider_error_hash_count": 0,
        "provider_error_text_retained_count": 0,
        "provider_error_stored_chars": 0,
        "provider_error_redacted_count": 0,
        "provider_error_truncated_count": 0,
        "provider_error_retention_modes": {},
        "provider_error_retention_policies": {},
        "provider_diagnostics_record_count": 1,
        "provider_diagnostic_item_count": 2,
        "provider_diagnostic_omitted_item_count": 0,
        "cost_estimate_count": 1,
        "cost_not_estimated_count": 0,
        "configured_pricing_estimate_count": 1,
        "live_pricing_record_count": 0,
        "backend_defaults_record_count": 1,
    }
    assert summary["backend_count"] == 1
    backend = summary["backends"][0]
    assert backend == {
        "backend_idx": 0,
        "backend_name": "diagnostics",
        "api_mode": "chat",
        "calls": 1,
        "successes": 1,
        "failures": 0,
        "usage_record_count": 1,
        "input_tokens": 3,
        "output_tokens": 5,
        "total_tokens": 8,
        "provider_response_retention_record_count": 1,
        "provider_response_hash_count": 1,
        "provider_response_text_retained_count": 0,
        "provider_response_stored_chars": 0,
        "provider_response_redacted_count": 0,
        "provider_response_truncated_count": 0,
        "provider_response_retention_modes": {"hash_only": 1},
        "provider_response_retention_policies": {"hash_only_with_raw_sha256": 1},
        "provider_error_retention_record_count": 0,
        "provider_error_hash_count": 0,
        "provider_error_text_retained_count": 0,
        "provider_error_stored_chars": 0,
        "provider_error_redacted_count": 0,
        "provider_error_truncated_count": 0,
        "provider_error_retention_modes": {},
        "provider_error_retention_policies": {},
        "provider_diagnostics_record_count": 1,
        "provider_diagnostic_item_count": 2,
        "provider_diagnostic_omitted_item_count": 0,
        "diagnostic_keys": {"duration_ms": 1, "system_fingerprint": 1},
        "cost_estimate_count": 1,
        "cost_not_estimated_count": 0,
        "configured_pricing_estimate_count": 1,
        "live_pricing_record_count": 0,
        "cost_status_reasons": {
            "estimated_from_configured_rate_and_provider_total_tokens": 1,
        },
        "backend_defaults_record_count": 1,
        "backend_default_api_modes": {"chat": 1},
    }
    assert len(summary["records_sha256"]) == 64
    assert summary["limitations"] == [
        "retained_call_history_window_only",
        "provider_response_error_text_retention_follows_configured_modes",
        "bounded_scalar_provider_diagnostics_not_full_raw_provider_payloads",
        "configured_cost_estimates_not_live_provider_pricing",
    ]


def test_provider_diagnostics_summary_aggregates_error_retention():
    sensitive_value = "provider-error-retention-password-1234567890"

    class FailingBackend:
        name = "failing"
        api_mode = "responses"

        def generate(self, prompt, **kwargs):
            raise RuntimeError("provider failed password=" + sensitive_value)

    ens = LLMEnsemble(
        [FailingBackend()],
        provider_error_retention_mode="full",
        fallback=False,
    )

    with pytest.raises(RuntimeError):
        ens.generate("prompt text", role="mutation")

    summary = ens.provider_diagnostics_summary
    assert summary["totals"]["provider_error_retention_record_count"] == 1
    assert summary["totals"]["provider_error_hash_count"] == 1
    assert summary["totals"]["provider_error_text_retained_count"] == 1
    assert summary["totals"]["provider_error_stored_chars"] > 0
    assert summary["totals"]["provider_error_redacted_count"] == 1
    assert summary["totals"]["provider_error_retention_modes"] == {"full": 1}
    assert summary["totals"]["provider_error_retention_policies"] == {
        ("full_" + "sec" + "ret_redacted_text_with_raw_sha256"): 1,
    }
    backend = summary["backends"][0]
    assert backend["backend_name"] == "failing"
    assert backend["api_mode"] == "responses"
    assert backend["provider_error_retention_record_count"] == 1
    assert backend["provider_error_hash_count"] == 1
    assert backend["provider_error_text_retained_count"] == 1
    assert backend["provider_error_redacted_count"] == 1
    assert sensitive_value not in strict_json_dumps(summary)


def test_generate_records_provider_cost_estimate_status_without_configured_rate():
    class MetadataBackend:
        name = "metadata"
        api_mode = "chat"
        provider_response_metadata = {
            "usage": {
                "input_tokens": 1,
                "output_tokens": 2,
                "total_tokens": 3,
            },
        }

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble([MetadataBackend()])

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["cost_estimate"] is None
    assert record["cost_estimate_status"] == {
        "policy": "backend_metadata_cost_estimate_status_v1",
        "status": "not_estimated",
        "reason": "missing_configured_backend_cost_rate",
        "pricing_source": "configured_backend_metadata",
        "token_count_source": "provider_response_metadata.usage.total_tokens",
        "live_pricing_status": "not_fetched",
    }


@pytest.mark.parametrize(
    ("role", "expected_accounting"),
    [
        (
            "mutation",
            _role_accounting(
                calls=1,
                successes=1,
                reward_accounted_calls=1,
                provider_internal_attempts=2,
                provider_internal_failed_attempts=1,
                input_tokens=7,
                output_tokens=11,
                total_tokens=18,
            ),
        ),
        (
            "critique",
            _role_accounting(
                calls=1,
                successes=1,
                telemetry_only_calls=1,
                provider_internal_attempts=2,
                provider_internal_failed_attempts=1,
                input_tokens=7,
                output_tokens=11,
                total_tokens=18,
            ),
        ),
        (
            "feedback:grader",
            _role_accounting(
                calls=1,
                successes=1,
                telemetry_only_calls=1,
                provider_internal_attempts=2,
                provider_internal_failed_attempts=1,
                input_tokens=7,
                output_tokens=11,
                total_tokens=18,
            ),
        ),
        (
            "meta_prompt",
            _role_accounting(
                calls=1,
                successes=1,
                telemetry_only_calls=1,
                provider_internal_attempts=2,
                provider_internal_failed_attempts=1,
                input_tokens=7,
                output_tokens=11,
                total_tokens=18,
            ),
        ),
    ],
)
def test_generate_records_provider_usage_and_retry_metadata_for_loop_roles(
    role,
    expected_accounting,
):
    class RoleMetadataBackend:
        name = "role-metadata"
        api_mode = "chat"

        def __init__(self):
            self.provider_response_metadata = {}

        def generate(self, prompt, **kwargs):
            safe_role = kwargs["role"].replace(":", "_")
            self.provider_response_metadata = {
                "usage": {
                    "input_tokens": 7,
                    "output_tokens": 11,
                    "total_tokens": 18,
                },
                "finish_reason": "stop",
                "request_id": f"req_{safe_role}",
                "response_id": f"resp_{safe_role}",
                "adapter_retry": {
                    "policy": "bounded_provider_internal_retries",
                    "max_retries": 1,
                    "attempts": 2,
                    "failed_attempts": 1,
                    "failures": [{"attempt": 0, "error_type": "RuntimeError"}],
                },
            }
            return "answer"

    ens = LLMEnsemble([RoleMetadataBackend()])

    ens.generate("prompt text", role=role)

    record = ens.call_history[0]
    assert record["role"] == role
    assert record["usage"] == {
        "input_tokens": 7,
        "output_tokens": 11,
        "total_tokens": 18,
    }
    assert record["finish_reason"] == "stop"
    assert record["request_id"] == f"req_{role.replace(':', '_')}"
    assert record["response_id"] == f"resp_{role.replace(':', '_')}"
    assert record["adapter_retry"] == {
        "policy": "bounded_provider_internal_retries",
        "max_retries": 1,
        "attempts": 2,
        "failed_attempts": 1,
        "failures": [{"attempt": 0, "error_type": "RuntimeError"}],
    }
    assert record["backend_telemetry_diagnostics"] == []
    _assert_role_accounting(
        ens.scheduler_state["role_accounting"][role],
        **expected_accounting,
    )


def test_generate_sanitizes_invalid_backend_provider_response_metadata():
    class UnsafeProviderMetadataBackend:
        name = "unsafe-provider-metadata"
        api_mode = "chat"
        provider_response_metadata = {
            "request_id": "req_\u200dhidden",
            "response_id": "api_key=sk-proj_providermeta_secret_1234567890",  # pragma: allowlist secret
        }

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble([UnsafeProviderMetadataBackend()])

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["usage"] is None
    assert record["finish_reason"] is None
    assert record["request_id"] is None
    assert record["response_id"] is None
    assert record["adapter_retry"] is None
    assert {
        "field": "provider_response_metadata",
        "reason": "unsafe_or_non_string",
        "value_type": "dict",
    } in record["backend_telemetry_diagnostics"]
    assert "sk-proj_providermeta_secret_1234567890" not in strict_json_dumps(record)


def test_generate_sanitizes_invalid_provider_diagnostics_metadata():
    class UnsafeProviderDiagnosticsBackend:
        name = "unsafe-provider-diagnostics"
        api_mode = "chat"
        provider_response_metadata = {
            "provider_diagnostics": {
                "nested": {"raw": "provider payload"},
            },
        }

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble([UnsafeProviderDiagnosticsBackend()])

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["provider_diagnostics"] is None
    assert {
        "field": "provider_response_metadata",
        "reason": "unsafe_or_non_string",
        "value_type": "dict",
    } in record["backend_telemetry_diagnostics"]


def test_generate_records_backend_telemetry_attribute_errors_safely():
    class BrokenTelemetryBackend:
        @property
        def name(self):
            raise RuntimeError("name failed")

        @property
        def api_mode(self):
            raise RuntimeError("api mode failed")

        def generate(self, prompt, **kwargs):
            return "answer"

    ens = LLMEnsemble([BrokenTelemetryBackend()])

    ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["backend_name"] == "BrokenTelemetryBackend"
    assert record["api_mode"] is None
    assert {
        "field": "backend_name",
        "reason": "attribute_error",
        "error_type": "RuntimeError",
    } in record["backend_telemetry_diagnostics"]
    assert {
        "field": "api_mode",
        "reason": "attribute_error",
        "error_type": "RuntimeError",
    } in record["backend_telemetry_diagnostics"]
    strict_json_dumps(record)


@pytest.mark.parametrize(
    "role",
    [
        "",
        "feedback:",
        "bad role",
        "bad\nrole",
        ["mutation"],
        "api_key=sk-proj_telemetry_secret_1234567890",  # pragma: allowlist secret
    ],
)
def test_generate_rejects_unsafe_call_roles_before_scheduler_state(role):
    backend = _b("b1", "answer")
    ens = LLMEnsemble([backend])

    with pytest.raises(ValueError, match="role"):
        ens.generate("prompt text", role=role)

    assert backend.generate.call_count == 0
    assert ens.total == 0
    assert ens.counts == [0]
    assert ens.call_history == []


def test_generate_rejects_non_text_prompt_before_scheduler_state():
    backend = _b("b1", "answer")
    ens = LLMEnsemble([backend])

    with pytest.raises(ValueError, match="prompt"):
        ens.generate(["not", "text"], role="mutation")

    assert backend.generate.call_count == 0
    assert ens.total == 0
    assert ens.counts == [0]
    assert ens.call_history == []


@pytest.mark.parametrize("prompt", ["", "   ", "\n\t"])
def test_generate_rejects_blank_prompt_before_scheduler_state(prompt):
    backend = _b("b1", "answer")
    ens = LLMEnsemble([backend])

    with pytest.raises(ValueError, match="non-empty"):
        ens.generate(prompt, role="mutation")

    assert backend.generate.call_count == 0
    assert ens.total == 0
    assert ens.counts == [0]
    assert ens.call_history == []


def test_generate_rejects_oversized_prompt_before_scheduler_state():
    backend = _b("b1", "answer")
    ens = LLMEnsemble([backend], max_prompt_chars=10)

    with pytest.raises(ValueError, match="max_prompt_chars"):
        ens.generate("x" * 11, role="mutation")

    assert backend.generate.call_count == 0
    assert ens.total == 0
    assert ens.counts == [0]
    assert ens.call_history == []


def test_generate_rejects_estimated_token_oversized_prompt_before_scheduler_state():
    backend = _b("b1", "answer")
    ens = LLMEnsemble([backend], max_prompt_estimated_tokens=2)

    with pytest.raises(ValueError, match="max_prompt_estimated_tokens"):
        ens.generate("x" * 9, role="mutation")

    assert backend.generate.call_count == 0
    assert ens.total == 0
    assert ens.counts == [0]
    assert ens.call_history == []


def test_generate_allows_secret_like_prompt_but_keeps_telemetry_hash_only():
    secret = "api_key=sk-proj_prompt_secret_1234567890"  # pragma: allowlist secret
    backend = _b("b1", "answer")
    ens = LLMEnsemble([backend], max_prompt_chars=100)

    response, idx = ens.generate(secret, role="mutation")

    assert response == "answer"
    assert idx == 0
    backend.generate.assert_called_once_with(secret, role="mutation")
    rendered = json.dumps(ens.call_history[0], sort_keys=True)
    assert secret not in rendered
    assert ens.call_history[0]["prompt_chars"] == len(secret)
    assert ens.call_history[0]["prompt_estimated_tokens"] == math.ceil(len(secret) / 4)
    assert len(ens.call_history[0]["prompt_sha256"]) == 64


def test_generate_preserves_valid_prompt_whitespace():
    backend = _b("b1", "answer")
    ens = LLMEnsemble([backend])

    response, idx = ens.generate("  prompt text\n", role="mutation")

    assert response == "answer"
    assert idx == 0
    backend.generate.assert_called_once_with("  prompt text\n", role="mutation")
    assert ens.call_history[0]["prompt_chars"] == len("  prompt text\n")


def test_generate_passes_validated_role_to_backend():
    seen = []

    class RoleAwareBackend:
        name = "role-aware"
        api_mode = None

        def generate(self, prompt, **kwargs):
            seen.append(kwargs)
            return "answer"

    ens = LLMEnsemble([RoleAwareBackend()])

    response, idx = ens.generate("prompt text", role="feedback:grader")

    assert response == "answer"
    assert idx == 0
    assert seen == [{"role": "feedback:grader"}]
    assert ens.last_call["role"] == "feedback:grader"
    assert ens.last_call["scheduler_accounting"] == "telemetry_only"
    assert ens.counts == [0]


def test_generate_passes_role_to_retry_and_fallback_backends():
    failing = _b("failing", "bad")
    failing.generate.side_effect = RuntimeError("temporary")
    ok = _b("ok", "answer")
    ens = LLMEnsemble([failing, ok], max_retries=1, fallback=True)

    response, idx = ens.generate("prompt text", role="critique")

    assert response == "answer"
    assert idx == 1
    assert failing.generate.call_args_list == [
        call("prompt text", role="critique"),
        call("prompt text", role="critique"),
    ]
    ok.generate.assert_called_once_with("prompt text", role="critique")
    assert [record["role"] for record in ens.call_history] == ["critique"] * 3
    assert [record["scheduler_accounting"] for record in ens.call_history] == [
        "telemetry_only",
        "telemetry_only",
        "telemetry_only",
    ]
    _assert_role_accounting(
        ens.scheduler_state["role_accounting"]["critique"],
        calls=3,
        successes=1,
        failures=2,
        telemetry_only_calls=3,
        ensemble_retry_attempts=1,
        ensemble_fallback_attempts=1,
        unknown_failures=2,
    )
    assert ens.counts == [0, 0]
    assert ens.total == 0


def test_generate_rejects_blank_prompt_rendered_from_template_before_backend_call():
    backend = _b("b1", "answer")
    ens = LLMEnsemble([backend])
    prompt = " \n\t"

    with pytest.raises(ValueError, match="non-empty"):
        ens.generate(prompt, role="mutation")

    assert backend.generate.call_count == 0
    assert ens.total == 0
    assert ens.counts == [0]
    assert ens.call_history == []


@pytest.mark.parametrize("response", [None, "", 7])
def test_generate_records_malformed_backend_output_as_failed_call(response):
    backend = _b("b1")
    backend.generate.return_value = response
    ens = LLMEnsemble([backend])

    with pytest.raises(ValueError, match="LLM backend returned"):
        ens.generate("prompt text", role="mutation")

    assert ens.counts == [1]
    assert ens.total == 1
    assert len(ens.call_history) == 1
    record = ens.call_history[-1]
    assert record["status"] == "error"
    assert record["error_type"] == "ProviderResponseError"
    assert record["provider_failure_category"] == "provider_response"
    expected_category = "empty_text" if response == "" else "non_text"
    expected = {"category": expected_category, "source": "LLM_backend"}
    if response is None:
        expected["value_type"] = "NoneType"
    elif response == 7:
        expected["value_type"] = "int"
    assert record["provider_response_error"] == expected
    assert record["counts_after"] == [1]


@pytest.mark.parametrize("response", ["   ", "\n\t"])
def test_generate_records_whitespace_only_backend_output_as_failed_call(response):
    backend = _b("b1")
    backend.generate.return_value = response
    ens = LLMEnsemble([backend])

    with pytest.raises(ValueError, match="empty output"):
        ens.generate("prompt text", role="mutation")

    assert ens.counts == [1]
    assert ens.total == 1
    assert len(ens.call_history) == 1
    record = ens.call_history[-1]
    assert record["status"] == "error"
    assert record["error_type"] == "ProviderResponseError"
    assert record["provider_failure_category"] == "provider_response"
    assert record["provider_response_error"] == {
        "category": "empty_text",
        "source": "LLM_backend",
    }
    assert record["output_chars"] == 0
    assert record["counts_after"] == [1]


def test_generate_retries_malformed_backend_output_before_success():
    backend = _b("b1")
    backend.generate.side_effect = [None, "ok"]
    ens = LLMEnsemble([backend], max_retries=1)

    response, idx = ens.generate("prompt text", role="mutation")

    assert response == "ok"
    assert idx == 0
    assert ens.counts == [1]
    assert ens.call_history[0]["status"] == "error"
    assert ens.call_history[0]["will_retry"] is True
    assert ens.call_history[1]["status"] == "ok"


def test_call_history_and_last_call_return_copied_telemetry():
    ens = LLMEnsemble(
        [_b("b1", "answer")],
        backend_metadata=[{"role": "breadth", "nested": {"cost": 1.0}}],
    )
    ens.generate("prompt text", role="mutation")

    history = ens.call_history
    history[0]["status"] = "corrupted"
    history[0]["backend_metadata"]["nested"]["cost"] = 999.0
    last = ens.last_call
    assert last is not None
    last["backend_metadata"]["role"] = "corrupted"

    assert ens.call_history[0]["status"] == "ok"
    assert ens.call_history[0]["backend_metadata"]["nested"]["cost"] == 1.0
    assert ens.last_call["backend_metadata"]["role"] == "breadth"


def test_generate_records_failed_call_before_reraising():
    backend = _b("b1")
    backend.generate.side_effect = RuntimeError("provider down")
    ens = LLMEnsemble([backend])

    try:
        ens.generate("prompt text", role="mutation")
    except RuntimeError:
        pass

    assert ens.counts[0] == 1
    assert ens.call_history[-1]["status"] == "error"
    assert ens.call_history[-1]["error_type"] == "RuntimeError"
    assert ens.call_history[-1]["provider_failure_category"] == "unknown"
    assert "provider down" in ens.call_history[-1]["error"]
    assert ens.call_history[-1]["error_retention"]["retention_mode"] == "redacted"


@pytest.mark.parametrize(
    ("mode", "expect_hash"),
    [
        ("hash_only", True),
        ("off", False),
    ],
)
def test_provider_error_retention_modes_omit_error_text(mode, expect_hash):
    backend = _b("b1")
    secret = "sk-proj_provider_error_retention_secret_1234567890"  # pragma: allowlist secret
    backend.generate.side_effect = RuntimeError(f"provider down {secret}")
    ens = LLMEnsemble([backend], provider_error_retention_mode=mode)

    with pytest.raises(RuntimeError):
        ens.generate("prompt text", role="mutation")

    record = ens.call_history[-1]
    rendered = json.dumps(record, sort_keys=True)
    assert record["status"] == "error"
    assert record["error"] is None
    assert secret not in rendered
    assert record["error_retention"]["retention_mode"] == mode
    if expect_hash:
        assert len(record["error_retention"]["sha256"]) == 64
        assert record["error_retention"]["chars"] == len(f"provider down {secret}")
    else:
        assert record["error_retention"]["sha256"] is None
        assert record["error_retention"]["chars"] is None


@pytest.mark.parametrize(
    ("mode", "expect_text", "expect_hash"),
    [
        ("full", True, True),
        ("redacted", True, True),
        ("hash_only", False, True),
        ("off", False, False),
    ],
)
def test_provider_response_retention_modes(mode, expect_text, expect_hash):
    backend = _b("b1")
    secret = "sk-proj_provider_response_retention_secret_1234567890"  # pragma: allowlist secret
    backend.generate.return_value = f"accepted {secret}"
    ens = LLMEnsemble([backend], provider_response_retention_mode=mode)

    response, _ = ens.generate("prompt text", role="mutation")

    assert response == f"accepted {secret}"
    record = ens.call_history[-1]
    rendered = json.dumps(record, sort_keys=True)
    assert secret not in rendered
    assert record["output_retention"]["retention_mode"] == mode
    if expect_text:
        assert record["output"] == "accepted [REDACTED]"
        assert record["output_retention"]["stored_chars"] == len("accepted [REDACTED]")
    else:
        assert record["output"] is None
        assert record["output_retention"]["stored_chars"] == 0
    if expect_hash:
        assert len(record["output_retention"]["sha256"]) == 64
        assert record["output_retention"]["chars"] == len(f"accepted {secret}")
    else:
        assert record["output_retention"]["sha256"] is None
        assert record["output_retention"]["chars"] is None


@pytest.mark.parametrize(
    ("exc", "category"),
    [
        (TimeoutError("timed out"), "timeout"),
        (FakeRateLimitError("rate limit"), "rate_limit"),
        (ConnectionError("connection reset"), "transport"),
        (FakeStatusError(503), "provider_server_error"),
        (FakeStatusError(400), "provider_client_error"),
        (
            ProviderResponseError(
                "empty output",
                category="empty_text",
                source="fixture",
            ),
            "provider_response",
        ),
    ],
)
def test_generate_classifies_provider_failure_category(exc, category):
    backend = _b("b1")
    backend.generate.side_effect = exc
    ens = LLMEnsemble([backend])

    with pytest.raises(exc.__class__):
        ens.generate("prompt text", role="mutation")

    record = ens.call_history[-1]
    assert record["status"] == "error"
    assert record["provider_failure_category"] == category
    assert record["provider_failure_policy"]["role"] == "mutation"
    assert record["provider_failure_policy"]["provider_failure_category"] == category
    assert record["provider_failure_policy"]["retry_decision"] == "no_retry"
    assert record["provider_failure_policy"]["fallback_decision"] == "no_fallback"
    assert (
        record["provider_failure_policy"]["quarantine_decision"]
        == "not_quarantined_by_ensemble_policy"
    )
    assert (
        record["provider_failure_policy"]["penalty_decision"]
        == "not_penalized_by_ensemble_policy"
    )
    expected_status = getattr(exc, "status_code", None)
    if isinstance(expected_status, int) and not isinstance(expected_status, bool):
        assert record["provider_status_code"] == expected_status
    else:
        assert record["provider_status_code"] is None
    assert ens.scheduler_state["role_accounting"]["mutation"][f"{category}_failures"] == 1


def test_generate_redacts_and_bounds_failed_call_telemetry():
    raw_secret = "sk-" + "proj-" + "abcdefghijklmnopqrstuvwxyz123456"
    backend = _b("b1")
    backend.generate.side_effect = RuntimeError(
        "provider failed api_key=" + raw_secret + " " + ("x" * 800)
    )
    ens = LLMEnsemble([backend])

    with pytest.raises(RuntimeError):
        ens.generate("prompt text", role="feedback:grader")

    record = ens.call_history[-1]
    assert record["status"] == "error"
    assert record["role"] == "feedback:grader"
    assert record["error_type"] == "RuntimeError"
    assert raw_secret not in record["error"]
    assert "[REDACTED]" in record["error"]
    assert record["error"].endswith("...[truncated]")
    assert len(record["error"]) <= 514


def test_generate_records_failed_call_when_exception_stringification_breaks():
    class BrokenStrError(RuntimeError):
        def __str__(self):
            raise RuntimeError("format failed")

    backend = _b("b1")
    backend.generate.side_effect = BrokenStrError()
    ens = LLMEnsemble([backend])

    with pytest.raises(BrokenStrError):
        ens.generate("prompt text", role="mutation")

    assert ens.total == 1
    assert ens.counts == [1]
    assert len(ens.call_history) == 1
    record = ens.call_history[0]
    assert record["status"] == "error"
    assert record["error_type"] == "BrokenStrError"
    assert record["error"] == (
        "<exception message unavailable; __str__ raised RuntimeError>"
    )
    assert record["counts_before"] == [0]
    assert record["counts_after"] == [1]
    assert record["will_retry"] is False
    assert record["will_fallback"] is False


def test_generate_records_failed_call_when_exception_repr_breaks():
    class BrokenReprError(RuntimeError):
        def __repr__(self):
            raise RuntimeError("repr failed")

    backend = _b("b1")
    backend.generate.side_effect = BrokenReprError(
        "provider failed token=ghp_brokenreprsecret1234567890"
    )
    ens = LLMEnsemble([backend])

    with pytest.raises(BrokenReprError):
        ens.generate("prompt text", role="mutation")

    record = ens.call_history[0]
    assert record["status"] == "error"
    assert record["error_type"] == "BrokenReprError"
    assert "ghp_brokenreprsecret1234567890" not in record["error"]
    assert "[REDACTED]" in record["error"]


def test_generate_times_out_slow_backend_with_structured_telemetry():
    class SlowBackend:
        name = "slow"
        api_mode = None

        def __init__(self):
            self.calls = 0

        def generate(self, prompt, **kwargs):
            self.calls += 1
            time.sleep(0.05)
            return "late"

    backend = SlowBackend()
    ens = LLMEnsemble([backend], call_timeout_sec=0.001)

    started = time.perf_counter()
    with pytest.raises(ProviderCallTimeoutError, match="timed out"):
        ens.generate("prompt text", role="mutation")
    elapsed = time.perf_counter() - started

    assert elapsed < 0.04
    assert backend.calls == 1
    assert ens.counts == [1]
    assert ens.total == 1
    record = ens.call_history[0]
    assert record["status"] == "error"
    assert record["error_type"] == "ProviderCallTimeoutError"
    assert record["provider_failure_category"] == "timeout"
    assert record["call_timeout_sec"] == 0.001
    assert record["cancellation_record"] == {
        "schema": "libreevolve.provider_cancellation_record.v1",
        "scope": "ensemble_call_timeout",
        "role": "mutation",
        "backend_idx": 0,
        "call_id": record["id"],
        "cancellation_kind": "ensemble_wait_deadline",
        "timeout_sec": 0.001,
        "status": "deadline_exceeded",
        "budget_action": "telemetry_only",
        "hard_cancel_ready": False,
        "in_flight_cancellation": "unsupported_daemon_worker_may_continue",
        "remaining_gap": "provider_sdk_hard_cancellation_not_implemented",
    }
    assert record["counts_after"] == [1]
    _assert_role_accounting(
        ens.scheduler_state["role_accounting"]["mutation"],
        calls=1,
        failures=1,
        reward_accounted_calls=1,
        timeout_failures=1,
    )


def test_generate_can_fallback_after_ensemble_call_timeout():
    class SlowBackend:
        name = "slow"
        api_mode = None

        def generate(self, prompt, **kwargs):
            time.sleep(0.05)
            return "late"

    ok = _b("ok", "answer")
    ens = LLMEnsemble([SlowBackend(), ok], call_timeout_sec=0.001, fallback=True)

    response, idx = ens.generate("prompt text", role="mutation")

    assert (response, idx) == ("answer", 1)
    assert [record["status"] for record in ens.call_history] == ["error", "ok"]
    assert ens.call_history[0]["provider_failure_category"] == "timeout"
    assert ens.call_history[0]["will_fallback"] is True
    assert ens.call_history[0]["cancellation_record"]["budget_action"] == "fallback"
    assert ens.call_history[1]["fallback_attempt"] == 1


def test_generate_retries_same_backend_before_success():
    backend = _b("b1")
    backend.generate.side_effect = [RuntimeError("rate limit"), "ok"]
    ens = LLMEnsemble([backend], max_retries=1)

    response, idx = ens.generate("prompt text", role="mutation")

    assert response == "ok"
    assert idx == 0
    assert backend.generate.call_count == 2
    assert ens.counts == [1]
    assert ens.call_history[0]["status"] == "error"
    assert ens.call_history[0]["retry_attempt"] == 0
    assert ens.call_history[0]["will_retry"] is True
    assert ens.call_history[1]["status"] == "ok"
    assert ens.call_history[1]["retry_attempt"] == 1


def test_generate_falls_back_to_next_backend_after_failure():
    bad = _b("bad")
    good = _b("good", "fallback")
    bad.generate.side_effect = RuntimeError("provider down")
    ens = LLMEnsemble([bad, good], max_retries=0, fallback=True)

    response, idx = ens.generate("prompt text", role="mutation")

    assert response == "fallback"
    assert idx == 1
    assert ens.counts == [1, 1]
    assert ens.call_history[0]["backend_idx"] == 0
    assert ens.call_history[0]["status"] == "error"
    assert ens.call_history[0]["counts_after"] == [1, 0]
    assert ens.call_history[0]["will_fallback"] is True
    assert ens.call_history[1]["backend_idx"] == 1
    assert ens.call_history[1]["status"] == "ok"
    assert ens.call_history[1]["fallback_attempt"] == 1


def test_generate_total_attempt_cap_suppresses_fallback_when_exhausted():
    bad = _b("bad")
    good = _b("good", "fallback")
    error = RuntimeError("provider down")
    bad.generate.side_effect = error
    ens = LLMEnsemble([bad, good], max_retries=10, max_call_attempts=1, fallback=True)

    with pytest.raises(RuntimeError, match="provider down"):
        ens.generate("prompt text", role="mutation")

    assert bad.generate.call_count == 1
    assert good.generate.call_count == 0
    assert ens.counts == [1, 0]
    [record] = ens.call_history
    assert record["backend_idx"] == 0
    assert record["retry_attempt"] == 0
    assert record["fallback_attempt"] == 0
    assert record["attempt_index"] == 0
    assert record["max_call_attempts"] == 1
    assert record["will_retry"] is False
    assert record["will_fallback"] is False


def test_generate_does_not_treat_failed_fallback_backend_as_untried_forever():
    bad = _b("bad")
    good = _b("good", "fallback")
    bad.generate.side_effect = RuntimeError("provider down")
    ens = LLMEnsemble([bad, good], max_retries=0, fallback=True)

    first_response, first_idx = ens.generate("prompt one", role="mutation")
    ens.record_reward(first_idx, 1.0)
    second_response, second_idx = ens.generate("prompt two", role="mutation")

    assert (first_response, first_idx) == ("fallback", 1)
    assert (second_response, second_idx) == ("fallback", 1)
    assert ens.counts == [1, 2]
    assert bad.generate.call_count == 1
    assert good.generate.call_count == 2
    assert [record["backend_idx"] for record in ens.call_history] == [0, 1, 1]
    assert ens.call_history[0]["status"] == "error"
    assert ens.call_history[1]["status"] == "ok"
    assert ens.call_history[2]["status"] == "ok"


def test_generate_can_disable_fallback():
    bad = _b("bad")
    good = _b("good", "fallback")
    bad.generate.side_effect = RuntimeError("provider down")
    ens = LLMEnsemble([bad, good], max_retries=0, fallback=False)

    try:
        ens.generate("prompt text", role="mutation")
    except RuntimeError:
        pass

    assert bad.generate.call_count == 1
    assert good.generate.call_count == 0
    assert ens.counts == [1, 0]
    assert ens.call_history[-1]["will_fallback"] is False


def test_high_reward_preferred_at_zero_explore():
    b1, b2 = _b("b1"), _b("b2")
    ens = LLMEnsemble([b1, b2], explore_coeff=0.0)
    ens.generate("p"); ens.generate("p")
    ens.record_reward(0, 10.0); ens.record_reward(1, 0.0)
    _, idx = ens.generate("p")
    assert idx == 0

def test_ucb1_converges_on_superior_arm():
    """After many rounds with arm 0 winning, arm 0 should be selected next."""
    b1, b2 = _b("b1"), _b("b2")
    ens = LLMEnsemble([b1, b2])
    for _ in range(20):
        _, idx = ens.generate("p")
        ens.record_reward(idx, 1.0 if idx == 0 else 0.0)
    _, idx = ens.generate("p")
    assert idx == 0

def test_throughput_depth_strategy_uses_metadata():
    fast = _b("fast")
    deep = _b("deep")
    ens = LLMEnsemble(
        [fast, deep],
        explore_coeff=0.0,
        strategy="throughput_depth",
        backend_metadata=[
            {"cost": 1.0, "latency": 1.0, "depth": 1.0},
            {"cost": 1.0, "latency": 1.0, "depth": 5.0},
        ],
    )

    _, first = ens.generate("p")
    _, second = ens.generate("p")
    _, third = ens.generate("p")

    assert [first, second] == [0, 1]
    assert third == 1


def test_throughput_depth_strategy_treats_backend_role_as_descriptive_metadata():
    breadth = _b("breadth")
    depth = _b("depth")
    ens = LLMEnsemble(
        [breadth, depth],
        explore_coeff=0.0,
        strategy="throughput_depth",
        backend_metadata=[
            {"role": "breadth", "cost": 1.0, "latency": 1.0, "depth": 10.0},
            {"role": "depth", "cost": 10.0, "latency": 10.0, "depth": 1.0},
        ],
    )

    _, first = ens.generate("p")
    _, second = ens.generate("p")
    _, third = ens.generate("p")

    assert [first, second] == [0, 1]
    assert third == 0
    assert ens.call_history[-1]["backend_metadata"]["role"] == "breadth"


def test_throughput_depth_metadata_is_normalized_against_reward_scale():
    shallow = _b("shallow")
    huge_depth = _b("huge-depth")
    ens = LLMEnsemble(
        [shallow, huge_depth],
        explore_coeff=0.0,
        strategy="throughput_depth",
        backend_metadata=[
            {"cost": 1.0, "latency": 1.0, "depth": 1.0},
            {"cost": 1.0, "latency": 1.0, "depth": 1_000_000.0},
        ],
    )

    _, first = ens.generate("p")
    _, second = ens.generate("p")
    ens.record_reward(first, 1.0)
    ens.record_reward(second, 0.0)
    _, third = ens.generate("p")

    assert [first, second] == [0, 1]
    assert third == 0


def test_throughput_depth_call_telemetry_records_effective_policy():
    b1 = _b("b1")
    b2 = _b("b2")
    ens = LLMEnsemble(
        [b1, b2],
        strategy="throughput_depth",
        backend_metadata=[
            {"cost": 2.0, "latency": 1.0, "depth": 1.0},
            {"cost": 1.0, "latency": 2.0, "depth": 4.0},
        ],
    )

    ens.generate("p")
    policy = ens.call_history[0]["scheduler_policy"]

    assert policy == {
        "strategy": "throughput_depth",
        "selection_scope": "global_backend_bandit",
        "role_selection_policy": "shared_selection_reward_accounting_configurable_by_role",
        "reward_accounted_roles": ["mutation"],
        "role_reward_accounting": "rewarded",
        "role_reward_contract": {
            "policy": "finite_non_negative_reward_clipped_to_max_reward_v1",
            "reward_update_api": "LLMEnsemble.record_reward",
            "raw_reward": "finite_non_negative_number",
            "applied_reward": "min(raw_reward, max_reward)",
            "max_reward": 1.0,
        },
        "role_quota_policy": {
            "policy": "pre_selection_logical_call_limits_v1",
            "enforcement": "checked_before_backend_selection",
            "matching_scopes": [],
            "unmatched_policy": "unbounded_by_role_call_limit",
        },
        "role_scheduler_scope": "shared",
        "role_selection_state_owner": "global_scheduler_state",
        "explore_coeff": 1.0,
        "max_retries": 0,
        "max_call_attempts": 32,
        "fallback": True,
        "call_timeout_sec": None,
        "max_prompt_chars": None,
        "max_prompt_estimated_tokens": None,
        "metadata_normalization": "per_selection_minmax",
        "metadata_weights": {"depth": 0.10, "cost": -0.05, "latency": -0.05},
        "neutral_normalized_metadata": 0.5,
    }


def test_scheduler_policy_records_role_reward_policy_without_per_role_routing():
    backend = _b("b1")
    ens = LLMEnsemble(
        [backend],
        reward_accounted_roles=["mutation", "critique"],
    )

    ens.generate("prompt text", role="feedback")
    policy = ens.last_call["scheduler_policy"]

    assert policy["selection_scope"] == "global_backend_bandit"
    assert (
        policy["role_selection_policy"]
        == "shared_selection_reward_accounting_configurable_by_role"
    )
    assert policy["reward_accounted_roles"] == ["critique", "mutation"]
    assert policy["role_reward_accounting"] == "telemetry_only"
    assert policy["role_selection_state_owner"] == "none_telemetry_only"
    assert policy["role_reward_contract"] == {
        "policy": "finite_non_negative_reward_clipped_to_max_reward_v1",
        "reward_update_api": "LLMEnsemble.record_reward",
        "raw_reward": "finite_non_negative_number",
        "applied_reward": "min(raw_reward, max_reward)",
        "max_reward": 1.0,
    }
    assert ens.last_call["scheduler_accounting"] == "telemetry_only"


def test_scheduler_policy_records_matching_role_quota_scopes():
    backend = _b("b1")
    ens = LLMEnsemble(
        [backend],
        max_calls_by_role={"feedback:*": 3, "critique": 1},
    )

    ens.generate("prompt text", role="feedback:safety")
    policy = ens.last_call["scheduler_policy"]

    assert policy["role_quota_policy"] == {
        "policy": "pre_selection_logical_call_limits_v1",
        "enforcement": "checked_before_backend_selection",
        "matching_scopes": [{"scope": "feedback:*", "limit": 3}],
        "unmatched_policy": "bounded_by_matching_role_call_limits",
    }


def test_backend_role_metadata_scopes_live_selection_when_matching_role_exists():
    mutation_backend = _b("mutation-backend")
    critique_backend = _b("critique-backend")
    general_backend = _b("general-backend")
    ens = LLMEnsemble(
        [mutation_backend, critique_backend, general_backend],
        backend_metadata=[
            {"role": "mutation"},
            {"role": "critique"},
            {},
        ],
        reward_accounted_roles=["mutation", "critique"],
    )

    response, idx = ens.generate("critique prompt", role="critique")

    assert idx == 1
    assert response == critique_backend.generate.return_value
    assert mutation_backend.generate.call_count == 0
    assert critique_backend.generate.call_count == 1
    assert general_backend.generate.call_count == 0
    policy = ens.last_call["scheduler_policy"]
    assert policy["selection_scope"] == "role_scoped_backend_bandit"
    assert (
        policy["role_selection_policy"]
        == "backend_metadata_role_match_when_available"
    )
    assert policy["role_reward_accounting"] == "rewarded"
    assert policy["role_selection_state_owner"] == "global_scheduler_state"
    assert policy["role"] == "critique"
    assert policy["role_matched_backend_indices"] == [1]
    assert ens.counts == [0, 1, 0]
    role_state = ens.scheduler_state["role_scheduler_state"]["critique"]
    assert role_state["counts"] == [0, 1, 0]


def test_configured_role_backend_indices_override_metadata_role_routing():
    mutation_backend = _b("mutation-backend")
    configured_critique_backend = _b("configured-critique-backend")
    metadata_critique_backend = _b("metadata-critique-backend")
    ens = LLMEnsemble(
        [
            mutation_backend,
            configured_critique_backend,
            metadata_critique_backend,
        ],
        backend_metadata=[
            {"role": "mutation"},
            {},
            {"role": "critique"},
        ],
        reward_accounted_roles=["mutation", "critique"],
        role_backend_indices={"critique": [1]},
    )

    response, idx = ens.generate("critique prompt", role="critique")

    assert idx == 1
    assert response == configured_critique_backend.generate.return_value
    assert mutation_backend.generate.call_count == 0
    assert configured_critique_backend.generate.call_count == 1
    assert metadata_critique_backend.generate.call_count == 0
    policy = ens.last_call["scheduler_policy"]
    assert policy["selection_scope"] == "role_scoped_backend_bandit"
    assert policy["role_selection_policy"] == "explicit_role_backend_indices"
    assert policy["role_backend_policy"] == "config.llm_role_backend_indices"
    assert policy["role_matched_backend_indices"] == [1]
    assert ens.scheduler_state["role_backend_policy"][
        "configured_role_backend_indices"
    ] == {"critique": [1]}
    assert ens.scheduler_state["role_backend_policy"][
        "metadata_role_backend_indices"
    ] == {"critique": [2], "mutation": [0]}


def test_backend_role_metadata_falls_back_to_global_selection_without_match():
    b1 = _b("b1")
    b2 = _b("b2")
    ens = LLMEnsemble(
        [b1, b2],
        backend_metadata=[{"role": "mutation"}, {"role": "critique"}],
    )

    response, idx = ens.generate("feedback prompt", role="feedback:grader")

    assert idx == 0
    assert response == b1.generate.return_value
    policy = ens.last_call["scheduler_policy"]
    assert policy["selection_scope"] == "global_backend_bandit"
    assert (
        policy["role_selection_policy"]
        == "shared_selection_reward_accounting_configurable_by_role"
    )
    assert "role_matched_backend_indices" not in policy
    assert ens.counts == [0, 0]
    assert ens.total == 0


def test_throughput_depth_initializes_all_backends_before_metadata_priority():
    shallow = _b("shallow")
    deep = _b("deep")
    ens = LLMEnsemble(
        [shallow, deep],
        explore_coeff=0.0,
        strategy="throughput_depth",
        backend_metadata=[
            {"cost": 1.0, "latency": 1.0, "depth": 1.0},
            {"cost": 1.0, "latency": 1.0, "depth": 100.0},
        ],
    )

    for _ in range(4):
        ens.generate("p")

    assert ens.counts[0] >= 1
    assert ens.counts[1] >= 1
