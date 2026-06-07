from types import SimpleNamespace

import libreevolve.llm.tokenization as tokenization
from libreevolve.llm.tokenization import (
    PROMPT_TOKEN_COUNTER_CAPABILITY_SCHEMA,
    discover_prompt_token_counter,
)


class _FakeEncoding:
    name = "fixture_base"

    def encode(self, text):
        return text.split()


def test_discover_prompt_token_counter_uses_optional_openai_tiktoken(monkeypatch):
    fake_provider_encoder = SimpleNamespace(
        encoding_for_model=lambda model: _FakeEncoding(),
        get_encoding=lambda name: _FakeEncoding(),
    )
    monkeypatch.setattr(
        tokenization.importlib,
        "import_module",
        lambda name: fake_provider_encoder,
    )

    counter, record = discover_prompt_token_counter(
        [{"type": "openai", "model": "gpt-4o-mini"}]
    )

    assert counter is not None
    assert counter("one two three") == 3
    assert record["schema"] == PROMPT_TOKEN_COUNTER_CAPABILITY_SCHEMA
    assert record["status"] == "ready"
    assert record["counter_name"] == "openai:encoding:fixture_base"
    assert record["backends"][0]["status"] == "ready"
    assert record["backends"][0]["encoding_source"] == "model_encoding"


def test_discover_prompt_token_counter_requires_all_eligible_backends(monkeypatch):
    fake_provider_encoder = SimpleNamespace(
        encoding_for_model=lambda model: _FakeEncoding(),
        get_encoding=lambda name: _FakeEncoding(),
    )
    monkeypatch.setattr(
        tokenization.importlib,
        "import_module",
        lambda name: fake_provider_encoder,
    )

    counter, record = discover_prompt_token_counter(
        [
            {"type": "openai", "model": "gpt-4o-mini"},
            {"type": "anthropic", "model": "claude-sonnet-4-6"},
        ]
    )

    assert counter is None
    assert record["status"] == "unavailable"
    assert record["reason"] == "some_eligible_backends_lack_provider_counter"
    assert record["eligible_backend_indices"] == [0, 1]
    assert record["backends"][1]["reason"] == "no_local_tokenizer_registered"


def test_discover_prompt_token_counter_honors_role_backend_indices(monkeypatch):
    fake_provider_encoder = SimpleNamespace(
        encoding_for_model=lambda model: _FakeEncoding(),
        get_encoding=lambda name: _FakeEncoding(),
    )
    monkeypatch.setattr(
        tokenization.importlib,
        "import_module",
        lambda name: fake_provider_encoder,
    )

    counter, record = discover_prompt_token_counter(
        [
            {"type": "anthropic", "model": "claude-sonnet-4-6"},
            {"type": "openai", "model": "gpt-4o-mini"},
        ],
        role_backend_indices={"mutation": [1]},
    )

    assert counter is not None
    assert record["status"] == "ready"
    assert record["selection_scope"] == "role_scoped_backends"
    assert record["eligible_backend_indices"] == [1]
