from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from google.genai import types

from libreevolve.llm.ensemble import ProviderResponseError
from libreevolve.llm.gemini import GeminiBackend, gemini_model_lane


@pytest.fixture(autouse=True)
def gemini_api_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")


def _response(
    *parts,
    finish_reason=types.FinishReason.STOP,
    prompt_tokens=3,
    output_tokens=5,
):
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(role="model", parts=list(parts)),
                finish_reason=finish_reason,
                index=0,
            )
        ],
        usage_metadata=types.GenerateContentResponseUsageMetadata(
            prompt_token_count=prompt_tokens,
            candidates_token_count=output_tokens,
            total_token_count=prompt_tokens + output_tokens,
            thoughts_token_count=2,
        ),
        response_id="gemini-response-1",
        model_version="gemini-2.0-flash-001",
    )


def _diagnostics(metadata):
    return {
        row["key"]: row.get("value")
        for row in metadata["provider_diagnostics"]["items"]
    }


def test_gemini_generate_maps_config_roles_and_metadata(mocker):
    client = MagicMock()
    client.models.generate_content.return_value = _response(
        types.Part.from_text(text="first "),
        types.Part.from_text(text="second"),
    )
    client_cls = mocker.patch(
        "libreevolve.llm.gemini.genai_sdk.Client",
        return_value=client,
    )

    backend = GeminiBackend(
        model="gemini-2.0-flash",
        max_tokens=123,
        temperature=0.2,
        top_p=0.9,
        stop=["END"],
        seed=7,
        timeout_sec=1.25,
        api_version="v1beta",
        provider_max_retries=0,
        prompt_roles={
            "mutation": {
                "system": "System instruction",
                "developer": "Developer instruction",
            }
        },
    )

    assert backend.generate("prompt", role="mutation") == "first second"
    assert backend.name == "gemini/gemini-2.0-flash"
    assert backend.api_mode == "generate_content"
    assert backend.client_context == {"api_version": "v1beta"}
    assert backend.request_parameters == {
        "temperature": 0.2,
        "top_p": 0.9,
        "stop": ["END"],
        "seed": 7,
    }
    client_kwargs = client_cls.call_args.kwargs
    assert client_kwargs["api_key"] == "test-gemini-key"  # pragma: allowlist secret
    assert client_kwargs["http_options"].api_version == "v1beta"
    assert client_kwargs["http_options"].timeout == 1250
    call = client.models.generate_content.call_args.kwargs
    assert call["model"] == "gemini-2.0-flash"
    assert call["contents"] == "prompt"
    config = call["config"]
    assert config.max_output_tokens == 123
    assert config.temperature == 0.2
    assert config.top_p == 0.9
    assert config.stop_sequences == ["END"]
    assert config.seed == 7
    assert config.system_instruction == "System instruction\n\nDeveloper instruction"
    assert backend.provider_response_metadata["usage"] == {
        "input_tokens": 3,
        "output_tokens": 5,
        "total_tokens": 8,
    }
    assert backend.provider_response_metadata["finish_reason"] == "STOP"
    assert backend.provider_response_metadata["response_id"] == "gemini-response-1"
    diagnostics = _diagnostics(backend.provider_response_metadata)
    assert diagnostics["candidate_count"] == 1
    assert diagnostics["content_part_count"] == 2
    assert diagnostics["text_part_count"] == 2
    assert diagnostics["thoughts_token_count"] == 2


def test_gemini_credentials_follow_documented_precedence(mocker, monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key")
    client_cls = mocker.patch("libreevolve.llm.gemini.genai_sdk.Client")

    GeminiBackend(model="gemini-2.0-pro")

    assert client_cls.call_args.kwargs["api_key"] == "google-key"  # pragma: allowlist secret


def test_gemini_requires_environment_credential(mocker, monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client_cls = mocker.patch("libreevolve.llm.gemini.genai_sdk.Client")

    with pytest.raises(ValueError, match="GOOGLE_API_KEY or GEMINI_API_KEY"):
        GeminiBackend(model="gemini-2.0-flash")

    assert client_cls.call_count == 0


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"model": ""}, "model"),
        ({"max_tokens": 0}, "max_tokens"),
        ({"temperature": 2.1}, "temperature"),
        ({"top_p": 0}, "top_p"),
        ({"stop": []}, "stop"),
        ({"seed": -1}, "seed"),
        ({"timeout_sec": 0}, "timeout_sec"),
        ({"api_version": "v2"}, "api_version"),
        ({"provider_max_retries": 11}, "provider_max_retries"),
    ],
)
def test_gemini_rejects_invalid_constructor_values(mocker, kwargs, message):
    client_cls = mocker.patch("libreevolve.llm.gemini.genai_sdk.Client")

    with pytest.raises(ValueError, match=message):
        GeminiBackend(**kwargs)

    assert client_cls.call_count == 0


@pytest.mark.parametrize(
    ("finish_reason", "category"),
    [
        (types.FinishReason.MAX_TOKENS, "incomplete"),
        (types.FinishReason.SAFETY, "refusal"),
        (types.FinishReason.RECITATION, "refusal"),
        (types.FinishReason.MALFORMED_FUNCTION_CALL, "incomplete"),
    ],
)
def test_gemini_rejects_non_complete_candidate(mocker, finish_reason, category):
    client = MagicMock()
    client.models.generate_content.return_value = _response(
        types.Part.from_text(text="partial"),
        finish_reason=finish_reason,
    )
    mocker.patch("libreevolve.llm.gemini.genai_sdk.Client", return_value=client)
    backend = GeminiBackend(model="gemini-2.0-flash", provider_max_retries=0)

    with pytest.raises(ProviderResponseError) as excinfo:
        backend.generate("prompt")

    assert excinfo.value.category == category
    assert backend.provider_response_metadata["finish_reason"] == finish_reason.value


def test_gemini_rejects_tool_only_and_mixed_output(mocker):
    client = MagicMock()
    mocker.patch("libreevolve.llm.gemini.genai_sdk.Client", return_value=client)
    backend = GeminiBackend(model="gemini-2.0-flash", provider_max_retries=0)
    tool = types.Part.from_function_call(name="tool", args={"value": 1})

    client.models.generate_content.return_value = _response(tool)
    with pytest.raises(ProviderResponseError) as tool_error:
        backend.generate("prompt")
    assert tool_error.value.category == "tool_call_only"

    client.models.generate_content.return_value = _response(
        types.Part.from_text(text="partial"),
        tool,
    )
    with pytest.raises(ProviderResponseError) as mixed_error:
        backend.generate("prompt")
    assert mixed_error.value.category == "mixed_content"


def test_gemini_rejects_prompt_block_and_empty_candidates(mocker):
    client = MagicMock()
    mocker.patch("libreevolve.llm.gemini.genai_sdk.Client", return_value=client)
    backend = GeminiBackend(model="gemini-2.0-flash", provider_max_retries=0)
    client.models.generate_content.return_value = SimpleNamespace(
        candidates=[],
        prompt_feedback=SimpleNamespace(block_reason="SAFETY"),
        usage_metadata=None,
        response_id=None,
        model_version=None,
    )

    with pytest.raises(ProviderResponseError) as blocked:
        backend.generate("prompt")
    assert blocked.value.category == "refusal"

    client.models.generate_content.return_value.prompt_feedback = None
    with pytest.raises(ProviderResponseError) as empty:
        backend.generate("prompt")
    assert empty.value.category == "empty_response"


def test_gemini_retries_provider_failure_and_records_attempts(mocker):
    client = MagicMock()
    client.models.generate_content.side_effect = [
        RuntimeError("temporary"),
        _response(types.Part.from_text(text="ok")),
    ]
    mocker.patch("libreevolve.llm.gemini.genai_sdk.Client", return_value=client)
    mocker.patch("libreevolve.llm.gemini.time.sleep")
    backend = GeminiBackend(model="gemini-2.0-flash", provider_max_retries=1)

    assert backend.generate("prompt") == "ok"
    assert backend.provider_response_metadata["adapter_retry"] == {
        "policy": "bounded_provider_internal_retries",
        "max_retries": 1,
        "attempts": 2,
        "failed_attempts": 1,
        "failures": [{"attempt": 0, "error_type": "RuntimeError"}],
    }


def test_gemini_model_lane_classification():
    assert gemini_model_lane("gemini-2.0-flash") == "flash"
    assert gemini_model_lane("gemini-2.0-pro") == "pro"
    assert gemini_model_lane("custom-gemini") == "general"
