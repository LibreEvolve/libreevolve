import pytest
from unittest.mock import MagicMock
from libreevolve.llm.anthropic import AnthropicBackend
from libreevolve.llm.ensemble import ProviderResponseError
from libreevolve.llm.openai    import OpenAIBackend
from libreevolve.llm.ollama    import OllamaBackend
from libreevolve.llm.base      import LLMBackend

DEFAULT_ADAPTER_RETRY = {
    "policy": "bounded_provider_internal_retries",
    "max_retries": 2,
    "attempts": 1,
    "failed_attempts": 0,
    "failures": [],
}


def test_names():
    for cls, prefix, m in [(AnthropicBackend, "anthropic", "m"),
                           (OpenAIBackend, "openai", "m2"),
                           (OllamaBackend, "ollama", "m3")]:
        b = cls.__new__(cls); b._model = m
        assert b.name == f"{prefix}/{m}"

def test_anthropic_generate(mocker):
    mc = MagicMock()
    mc.messages.create.return_value.content = [MagicMock(text="diff")]
    mc.messages.create.return_value.id = "msg_123"
    mc.messages.create.return_value.stop_reason = "end_turn"
    mc.messages.create.return_value.usage = MagicMock(input_tokens=3, output_tokens=5)
    mc.messages.create.return_value._request_id = "req_anthropic"
    mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)
    backend = AnthropicBackend(model="m")
    assert backend.generate("p") == "diff"
    assert backend.provider_response_metadata == {
        "usage": {"input_tokens": 3, "output_tokens": 5, "total_tokens": 8},
        "finish_reason": "end_turn",
        "request_id": "req_anthropic",
        "response_id": "msg_123",
        "adapter_retry": DEFAULT_ADAPTER_RETRY,
    }

def test_openai_generate(mocker):
    mc = MagicMock()
    mc.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="d"), finish_reason="stop")
    ]
    mc.chat.completions.create.return_value.id = "chatcmpl_123"
    mc.chat.completions.create.return_value.usage = MagicMock(
        prompt_tokens=2,
        completion_tokens=4,
        total_tokens=6,
    )
    mc.chat.completions.create.return_value._request_id = "req_openai"
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)
    backend = OpenAIBackend(model="m")
    assert backend.generate("p") == "d"
    assert backend.provider_response_metadata == {
        "usage": {"input_tokens": 2, "output_tokens": 4, "total_tokens": 6},
        "finish_reason": "stop",
        "request_id": "req_openai",
        "response_id": "chatcmpl_123",
        "adapter_retry": DEFAULT_ADAPTER_RETRY,
    }

def test_ollama_generate(mocker):
    mocker.patch("libreevolve.llm.ollama.ollama_sdk.chat",
                 return_value={
                     "message": {"content": "out"},
                     "prompt_eval_count": 3,
                     "eval_count": 7,
                     "done_reason": "stop",
                 })
    backend = OllamaBackend(model="m")
    assert backend.generate("p") == "out"
    assert backend.provider_response_metadata == {
        "usage": {"input_tokens": 3, "output_tokens": 7, "total_tokens": 10},
        "finish_reason": "stop",
        "adapter_retry": DEFAULT_ADAPTER_RETRY,
    }


def test_backend_constructors_forward_timeout_to_clients(mocker):
    openai_client = mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI")
    anthropic_client = mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic")
    ollama_client = mocker.patch("libreevolve.llm.ollama.ollama_sdk.Client")

    OpenAIBackend(model="m", timeout_sec=12.5)
    AnthropicBackend(model="m", timeout_sec=13)
    OllamaBackend(model="m", timeout_sec=14, host="http://localhost:11434")

    openai_client.assert_called_once_with(timeout=12.5)
    anthropic_client.assert_called_once_with(timeout=13.0)
    ollama_client.assert_called_once_with(host="http://localhost:11434", timeout=14.0)


def test_ollama_timeout_constructs_client_without_custom_host(mocker):
    client = mocker.patch("libreevolve.llm.ollama.ollama_sdk.Client")

    OllamaBackend(model="m", timeout_sec=3)

    client.assert_called_once_with(timeout=3.0)


def test_openai_rejects_invalid_prompt_before_sdk_call(mocker):
    mc = MagicMock()
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)
    backend = OpenAIBackend(model="m")

    with pytest.raises(ValueError, match="prompt"):
        backend.generate(["not", "text"])

    assert mc.chat.completions.create.call_count == 0
    assert mc.responses.create.call_count == 0


def test_anthropic_rejects_blank_prompt_before_sdk_call(mocker):
    mc = MagicMock()
    mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)
    backend = AnthropicBackend(model="m")

    with pytest.raises(ValueError, match="non-empty"):
        backend.generate("")

    assert mc.messages.create.call_count == 0


def test_ollama_rejects_whitespace_prompt_before_sdk_call(mocker):
    mock_chat = mocker.patch("libreevolve.llm.ollama.ollama_sdk.chat")
    backend = OllamaBackend(model="m")

    with pytest.raises(ValueError, match="non-empty"):
        backend.generate("\n\t")

    assert mock_chat.call_count == 0


@pytest.mark.parametrize(
    ("cls", "kwargs", "message"),
    [
        (OpenAIBackend, {"model": ""}, "model"),
        (OpenAIBackend, {"model": " gpt-4o"}, "model"),
        (OpenAIBackend, {"model": "sk-proj_directmodelsecret1234567890"}, "model"),
        (OpenAIBackend, {"max_tokens": False}, "max_tokens"),
        (OpenAIBackend, {"max_tokens": 0}, "max_tokens"),
        (OpenAIBackend, {"reasoning_effort": "extreme"}, "reasoning_effort"),
        (OpenAIBackend, {"api_mode": "bad"}, "api_mode"),
        (OpenAIBackend, {"temperature": -0.1}, "temperature"),
        (OpenAIBackend, {"temperature": 2.1}, "temperature"),
        (OpenAIBackend, {"top_p": 0}, "top_p"),
        (OpenAIBackend, {"stop": ""}, "stop"),
        (OpenAIBackend, {"seed": -1}, "seed"),
        (OpenAIBackend, {"api_mode": "responses", "seed": 1}, "Chat Completions"),
        (OpenAIBackend, {"api_mode": "responses", "stop": "END"}, "Chat Completions"),
        (OpenAIBackend, {"base_url": "ftp://example.test"}, "http"),
        (OpenAIBackend, {"base_url": "https://user@example.test"}, "credentials"),
        (OpenAIBackend, {"base_url": "https://example.test?x=1"}, "query"),
        (OpenAIBackend, {"organization": "bad org"}, "organization"),
        (OpenAIBackend, {"project": "sk-proj_contextsecret1234567890"}, "project"),
        (OpenAIBackend, {"provider_max_retries": -1}, "provider_max_retries"),
        (
            OpenAIBackend,
            {"reasoning_effort": "high", "api_mode": "chat_completions"},
            "chat_completions",
        ),
        (
            OpenAIBackend,
            {"model": "gpt-5.1", "reasoning_effort": "minimal"},
            "gpt-5.1 models",
        ),
        (
            OpenAIBackend,
            {"model": "gpt-5-pro", "reasoning_effort": "medium"},
            "gpt-5-pro",
        ),
        (
            OpenAIBackend,
            {"model": "gpt-4o", "reasoning_effort": "none"},
            "gpt-5.1 or newer",
        ),
        (AnthropicBackend, {"model": ""}, "model"),
        (AnthropicBackend, {"max_tokens": 0}, "max_tokens"),
        (AnthropicBackend, {"temperature": 1.1}, "temperature"),
        (AnthropicBackend, {"top_p": 1.1}, "top_p"),
        (AnthropicBackend, {"stop": [7]}, "stop"),
        (AnthropicBackend, {"seed": 1}, "anthropic"),
        (AnthropicBackend, {"base_url": "ftp://example.test"}, "http"),
        (AnthropicBackend, {"provider_max_retries": True}, "provider_max_retries"),
        (OllamaBackend, {"model": ""}, "model"),
        (OllamaBackend, {"max_tokens": -1}, "max_tokens"),
        (OllamaBackend, {"temperature": 2.1}, "temperature"),
        (OllamaBackend, {"seed": 2_147_483_648}, "seed"),
        (OllamaBackend, {"host": "https://user@example.test"}, "credentials"),
        (OllamaBackend, {"provider_max_retries": 11}, "provider_max_retries"),
    ],
)
def test_backend_constructors_reject_invalid_direct_parameters(
    cls,
    kwargs,
    message,
    mocker,
):
    openai_client = mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI")
    anthropic_client = mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic")
    ollama_chat = mocker.patch("libreevolve.llm.ollama.ollama_sdk.chat")

    with pytest.raises(ValueError, match=message):
        cls(**kwargs)

    assert openai_client.return_value.chat.completions.create.call_count == 0
    assert openai_client.return_value.responses.create.call_count == 0
    assert anthropic_client.return_value.messages.create.call_count == 0
    assert ollama_chat.call_count == 0


def test_backend_constructors_accept_valid_manifest_safe_direct_parameters(mocker):
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI")
    mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic")

    openai_backend = OpenAIBackend(
        model="gpt-5.2",
        max_tokens=1,
        reasoning_effort="minimal",
    )
    anthropic_backend = AnthropicBackend(
        model="claude-sonnet-4-6",
        max_tokens=1,
    )
    ollama_backend = OllamaBackend(
        model="library/qwen2.5-coder:7b-instruct",
        max_tokens=1,
    )

    assert openai_backend.name == "openai/gpt-5.2"
    assert openai_backend.api_mode == "responses"
    assert anthropic_backend.name == "anthropic/claude-sonnet-4-6"
    assert ollama_backend.name == "ollama/library/qwen2.5-coder:7b-instruct"


def test_backend_request_parameters_are_defensive_copies(mocker):
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI")
    mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic")

    openai_backend = OpenAIBackend(model="m", temperature=0.2, top_p=0.9, stop=["END"])
    anthropic_backend = AnthropicBackend(model="m", temperature=0.3, top_p=0.8, stop="DONE")
    ollama_backend = OllamaBackend(model="m", temperature=0.4, top_p=0.7, stop=["HALT"], seed=123)

    assert openai_backend.request_parameters == {
        "temperature": 0.2,
        "top_p": 0.9,
        "stop": ["END"],
    }
    assert anthropic_backend.request_parameters == {
        "temperature": 0.3,
        "top_p": 0.8,
        "stop": ["DONE"],
    }
    assert ollama_backend.request_parameters == {
        "temperature": 0.4,
        "top_p": 0.7,
        "stop": ["HALT"],
        "seed": 123,
    }
    openai_backend.request_parameters["stop"].append("MUTATED")
    assert openai_backend.request_parameters["stop"] == ["END"]


def test_backend_defaults_are_recorded_and_copied(mocker):
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI")
    mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic")
    mocker.patch("libreevolve.llm.ollama.ollama_sdk.Client")

    openai_backend = OpenAIBackend(
        model="gpt-5.1",
        max_tokens=123,
        reasoning_effort="low",
        timeout_sec=9.5,
        provider_max_retries=1,
    )
    anthropic_backend = AnthropicBackend(
        model="claude-sonnet-4-6",
        max_tokens=234,
        provider_max_retries=0,
    )
    ollama_backend = OllamaBackend(
        model="llama3",
        max_tokens=345,
        timeout_sec=4.0,
        provider_max_retries=2,
    )

    assert openai_backend.backend_defaults == {
        "policy": "effective_backend_generation_defaults_v1",
        "max_tokens": 123,
        "provider_max_retries": 1,
        "timeout_sec": 9.5,
        "api_mode": "responses",
        "api_mode_policy": "auto",
        "reasoning_effort": "low",
    }
    assert anthropic_backend.backend_defaults == {
        "policy": "effective_backend_generation_defaults_v1",
        "max_tokens": 234,
        "provider_max_retries": 0,
        "timeout_sec": None,
        "api_mode": "messages",
    }
    assert ollama_backend.backend_defaults == {
        "policy": "effective_backend_generation_defaults_v1",
        "max_tokens": 345,
        "provider_max_retries": 2,
        "timeout_sec": 4.0,
        "api_mode": "chat",
    }
    openai_defaults = openai_backend.backend_defaults
    openai_defaults["max_tokens"] = 999
    assert openai_backend.backend_defaults["max_tokens"] == 123


def test_backend_client_contexts_are_forwarded_and_copied(mocker):
    openai_client = mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI")
    anthropic_client = mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic")
    ollama_client_cls = mocker.patch("libreevolve.llm.ollama.ollama_sdk.Client")

    openai_backend = OpenAIBackend(
        model="m",
        base_url="https://gateway.example/v1",
        organization="org-example",
        project="proj_example",
    )
    anthropic_backend = AnthropicBackend(
        model="m",
        base_url="https://anthropic.example/v1",
    )
    ollama_backend = OllamaBackend(
        model="m",
        host="http://localhost:11434",
    )

    openai_client.assert_called_once_with(
        base_url="https://gateway.example/v1",
        organization="org-example",
        project="proj_example",
    )
    anthropic_client.assert_called_once_with(base_url="https://anthropic.example/v1")
    ollama_client_cls.assert_called_once_with(host="http://localhost:11434")
    assert openai_backend.client_context == {
        "base_url": "https://gateway.example/v1",
        "organization": "org-example",
        "project": "proj_example",
    }
    assert anthropic_backend.client_context == {"base_url": "https://anthropic.example/v1"}
    assert ollama_backend.client_context == {"host": "http://localhost:11434"}
    openai_backend.client_context["base_url"] = "https://mutated.example"
    assert openai_backend.client_context["base_url"] == "https://gateway.example/v1"


def test_openai_accepts_model_specific_reasoning_efforts(mocker):
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI")

    gpt_51 = OpenAIBackend(model="gpt-5.1", reasoning_effort="none")
    gpt_55 = OpenAIBackend(model="gpt-5.5", reasoning_effort="xhigh")
    gpt_5_pro = OpenAIBackend(model="gpt-5-pro", reasoning_effort="high")

    assert gpt_51.api_mode == "responses"
    assert gpt_55.api_mode == "responses"
    assert gpt_5_pro.api_mode == "responses"


def test_openai_explicit_responses_api_mode_without_reasoning(mocker):
    mc = MagicMock()
    response = mc.responses.create.return_value
    response.output = [
        MagicMock(
            type="message",
            content=[MagicMock(type="output_text", text="ok")],
        )
    ]
    response.id = "resp_123"
    response.status = "completed"
    response.usage = MagicMock(input_tokens=5, output_tokens=8, total_tokens=13)
    response._request_id = "req_responses"
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)

    backend = OpenAIBackend(model="gpt-5.1", api_mode="responses")

    assert backend.api_mode == "responses"
    assert backend.generate("p") == "ok"
    assert backend.provider_response_metadata == {
        "usage": {"input_tokens": 5, "output_tokens": 8, "total_tokens": 13},
        "finish_reason": "completed",
        "request_id": "req_responses",
        "response_id": "resp_123",
        "adapter_retry": DEFAULT_ADAPTER_RETRY,
    }
    assert mc.responses.create.call_args.kwargs == {
        "model": "gpt-5.1",
        "max_output_tokens": 4096,
        "input": [{"role": "user", "content": "p"}],
    }
    assert mc.chat.completions.create.call_count == 0


def test_openai_responses_passes_supported_request_parameters(mocker):
    mc = MagicMock()
    mc.responses.create.return_value.output = [
        MagicMock(
            type="message",
            content=[MagicMock(type="output_text", text="ok")],
        )
    ]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)

    backend = OpenAIBackend(
        model="gpt-5.1",
        api_mode="responses",
        temperature=0.2,
        top_p=0.9,
    )

    assert backend.generate("p") == "ok"
    assert mc.responses.create.call_args.kwargs == {
        "model": "gpt-5.1",
        "max_output_tokens": 4096,
        "input": [{"role": "user", "content": "p"}],
        "temperature": 0.2,
        "top_p": 0.9,
    }


def test_openai_chat_passes_supported_request_parameters(mocker):
    mc = MagicMock()
    mc.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="ok"))
    ]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)

    backend = OpenAIBackend(
        model="gpt-4o-mini",
        temperature=0.2,
        top_p=0.9,
        stop=["END"],
        seed=123,
    )

    assert backend.generate("p") == "ok"
    assert mc.chat.completions.create.call_args.kwargs == {
        "model": "gpt-4o-mini",
        "max_completion_tokens": 4096,
        "messages": [{"role": "user", "content": "p"}],
        "temperature": 0.2,
        "top_p": 0.9,
        "stop": ["END"],
        "seed": 123,
    }


def test_openai_chat_uses_configured_prompt_role_messages(mocker):
    mc = MagicMock()
    mc.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="ok"))
    ]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)

    backend = OpenAIBackend(
        model="gpt-4o-mini",
        prompt_roles={
            "mutation": {
                "system": "System role text",
                "developer": "Developer role text",
            }
        },
    )

    assert backend.generate("p", role="mutation") == "ok"
    assert mc.chat.completions.create.call_args.kwargs["messages"] == [
        {"role": "system", "content": "System role text"},
        {"role": "developer", "content": "Developer role text"},
        {"role": "user", "content": "p"},
    ]
    telemetry = backend.prompt_role_policy_for_role("mutation")
    assert telemetry["policy"] == "configured_structured_messages"
    assert telemetry["message_roles"] == ["system", "developer", "user"]
    assert telemetry["instruction_metadata"]["system"]["chars"] == len("System role text")


def test_openai_responses_uses_configured_prompt_role_input(mocker):
    mc = MagicMock()
    mc.responses.create.return_value.output = [
        MagicMock(type="message", content=[MagicMock(type="output_text", text="ok")])
    ]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)

    backend = OpenAIBackend(
        model="gpt-5.1",
        api_mode="responses",
        prompt_roles={"critique": {"system": "Critique system"}},
    )

    assert backend.generate("p", role="critique") == "ok"
    assert mc.responses.create.call_args.kwargs["input"] == [
        {"role": "system", "content": "Critique system"},
        {"role": "user", "content": "p"},
    ]


def test_openai_auto_api_mode_preserves_legacy_routing(mocker):
    mc = MagicMock()
    mc.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="chat"))
    ]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)

    backend = OpenAIBackend(model="gpt-5.1", api_mode="auto")

    assert backend.api_mode == "chat_completions"
    assert backend.generate("p") == "chat"
    assert mc.chat.completions.create.call_count == 1
    assert mc.responses.create.call_count == 0


def test_anthropic_retries(mocker):
    mc = MagicMock()
    mc.messages.create.side_effect = [Exception("fail"),
                                       MagicMock(content=[MagicMock(text="ok")])]
    mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)
    mocker.patch("libreevolve.llm.anthropic.time.sleep")
    assert AnthropicBackend().generate("p") == "ok"
    assert mc.messages.create.call_count == 2


def test_anthropic_records_configured_provider_retry_metadata(mocker):
    mc = MagicMock()
    msg = MagicMock(content=[MagicMock(text="ok")])
    msg.id = "msg_retry"
    msg.stop_reason = "end_turn"
    mc.messages.create.side_effect = [RuntimeError("temporary"), msg]
    mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)
    mocker.patch("libreevolve.llm.anthropic.time.sleep")

    backend = AnthropicBackend(provider_max_retries=1)

    assert backend.generate("p") == "ok"
    assert mc.messages.create.call_count == 2
    assert backend.provider_response_metadata["adapter_retry"] == {
        "policy": "bounded_provider_internal_retries",
        "max_retries": 1,
        "attempts": 2,
        "failed_attempts": 1,
        "failures": [{"attempt": 0, "error_type": "RuntimeError"}],
    }


def test_anthropic_passes_supported_request_parameters(mocker):
    mc = MagicMock()
    mc.messages.create.return_value.content = [MagicMock(text="ok")]
    mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)

    backend = AnthropicBackend(model="m", temperature=0.2, top_p=0.9, stop=["END"])

    assert backend.generate("p") == "ok"
    assert mc.messages.create.call_args.kwargs == {
        "model": "m",
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": "p"}],
        "temperature": 0.2,
        "top_p": 0.9,
        "stop_sequences": ["END"],
    }


def test_anthropic_uses_configured_prompt_role_system(mocker):
    mc = MagicMock()
    mc.messages.create.return_value.content = [MagicMock(text="ok")]
    mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)

    backend = AnthropicBackend(
        model="m",
        prompt_roles={
            "feedback:grader": {
                "system": "Reviewer system",
                "developer": "Reviewer developer",
            }
        },
    )

    assert backend.generate("p", role="feedback:grader") == "ok"
    assert mc.messages.create.call_args.kwargs["messages"] == [
        {"role": "user", "content": "p"}
    ]
    assert mc.messages.create.call_args.kwargs["system"] == (
        "Reviewer system\n\nReviewer developer"
    )


def test_openai_retries(mocker):
    mc = MagicMock()
    mc.chat.completions.create.side_effect = [
        Exception("fail"),
        MagicMock(choices=[MagicMock(message=MagicMock(content="ok"))]),
    ]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)
    mocker.patch("libreevolve.llm.openai.time.sleep")
    assert OpenAIBackend().generate("p") == "ok"
    assert mc.chat.completions.create.call_count == 2


def test_openai_provider_max_retries_zero_disables_internal_retry(mocker):
    mc = MagicMock()
    mc.chat.completions.create.side_effect = RuntimeError("persistent")
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)
    sleep = mocker.patch("libreevolve.llm.openai.time.sleep")

    backend = OpenAIBackend(provider_max_retries=0)

    with pytest.raises(RuntimeError, match="persistent"):
        backend.generate("p")

    assert mc.chat.completions.create.call_count == 1
    assert sleep.call_count == 0
    assert backend.provider_response_metadata["adapter_retry"] == {
        "policy": "bounded_provider_internal_retries",
        "max_retries": 0,
        "attempts": 1,
        "failed_attempts": 1,
        "failures": [{"attempt": 0, "error_type": "RuntimeError"}],
    }


def test_openai_chat_rejects_non_text_provider_content(mocker):
    mc = MagicMock()
    mc.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=None))
    ]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)
    mocker.patch("libreevolve.llm.openai.time.sleep")

    with pytest.raises(ValueError, match="OpenAI Chat Completions returned non-text"):
        OpenAIBackend().generate("p")

    assert mc.chat.completions.create.call_count == 3


def test_openai_chat_classifies_refusal_without_text(mocker):
    mc = MagicMock()
    mc.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=None, refusal="blocked", tool_calls=None))
    ]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)
    mocker.patch("libreevolve.llm.openai.time.sleep")

    with pytest.raises(ProviderResponseError) as excinfo:
        OpenAIBackend().generate("p")

    assert excinfo.value.category == "refusal"
    assert mc.chat.completions.create.call_count == 3


def test_openai_chat_classifies_tool_calls_without_text(mocker):
    mc = MagicMock()
    mc.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=None, refusal=None, tool_calls=[object()]))
    ]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)
    mocker.patch("libreevolve.llm.openai.time.sleep")

    with pytest.raises(ProviderResponseError) as excinfo:
        OpenAIBackend().generate("p")

    assert excinfo.value.category == "tool_call_only"
    assert mc.chat.completions.create.call_count == 3


def test_openai_responses_rejects_missing_output_text(mocker):
    mc = MagicMock()
    mc.responses.create.return_value.output = [MagicMock(type="message", content=[])]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)
    mocker.patch("libreevolve.llm.openai.time.sleep")

    with pytest.raises(ValueError, match="OpenAI Responses returned empty output"):
        OpenAIBackend(reasoning_effort="high").generate("p")

    assert mc.responses.create.call_count == 3


def test_openai_responses_classifies_refusal_without_text(mocker):
    mc = MagicMock()
    mc.responses.create.return_value.output = [
        MagicMock(
            type="message",
            content=[MagicMock(type="refusal", refusal="blocked")],
        )
    ]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)
    mocker.patch("libreevolve.llm.openai.time.sleep")

    with pytest.raises(ProviderResponseError) as excinfo:
        OpenAIBackend(reasoning_effort="high").generate("p")

    assert excinfo.value.category == "refusal"
    assert mc.responses.create.call_count == 3


def test_openai_responses_classifies_tool_calls_without_text(mocker):
    mc = MagicMock()
    mc.responses.create.return_value.output = [MagicMock(type="function_call")]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)
    mocker.patch("libreevolve.llm.openai.time.sleep")

    with pytest.raises(ProviderResponseError) as excinfo:
        OpenAIBackend(reasoning_effort="high").generate("p")

    assert excinfo.value.category == "tool_call_only"
    assert mc.responses.create.call_count == 3


def test_openai_responses_rejects_empty_output_text(mocker):
    mc = MagicMock()
    mc.responses.create.return_value.output = [
        MagicMock(
            type="message",
            content=[MagicMock(type="output_text", text="   ")],
        )
    ]
    mocker.patch("libreevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)
    mocker.patch("libreevolve.llm.openai.time.sleep")

    with pytest.raises(ValueError, match="OpenAI Responses returned empty output"):
        OpenAIBackend(reasoning_effort="high").generate("p")

    assert mc.responses.create.call_count == 3


def test_ollama_retries(mocker):
    mock_chat = mocker.patch("libreevolve.llm.ollama.ollama_sdk.chat",
        side_effect=[Exception("fail"), {"message": {"content": "ok"}}])
    mocker.patch("libreevolve.llm.ollama.time.sleep")
    assert OllamaBackend().generate("p") == "ok"
    assert mock_chat.call_count == 2


def test_ollama_passes_supported_request_parameters(mocker):
    mock_chat = mocker.patch(
        "libreevolve.llm.ollama.ollama_sdk.chat",
        return_value={"message": {"content": "ok"}},
    )

    backend = OllamaBackend(model="m", temperature=0.2, top_p=0.9, stop=["END"], seed=123)

    assert backend.generate("p") == "ok"
    assert mock_chat.call_args.kwargs == {
        "model": "m",
        "messages": [{"role": "user", "content": "p"}],
        "options": {
            "num_predict": 4096,
            "temperature": 0.2,
            "top_p": 0.9,
            "stop": ["END"],
            "seed": 123,
        },
    }


def test_ollama_uses_configured_prompt_role_system_message(mocker):
    mock_chat = mocker.patch(
        "libreevolve.llm.ollama.ollama_sdk.chat",
        return_value={"message": {"content": "ok"}},
    )

    backend = OllamaBackend(
        model="m",
        prompt_roles={"meta_prompt": {"developer": "Meta prompt developer"}},
    )

    assert backend.generate("p", role="meta_prompt") == "ok"
    assert mock_chat.call_args.kwargs["messages"] == [
        {"role": "system", "content": "Meta prompt developer"},
        {"role": "user", "content": "p"},
    ]


def test_ollama_uses_configured_client_host(mocker):
    module_chat = mocker.patch("libreevolve.llm.ollama.ollama_sdk.chat")
    client = MagicMock()
    client.chat.return_value = {"message": {"content": "ok"}}
    mocker.patch("libreevolve.llm.ollama.ollama_sdk.Client", return_value=client)

    backend = OllamaBackend(model="m", host="http://localhost:11434")

    assert backend.generate("p") == "ok"
    assert client.chat.call_args.kwargs == {
        "model": "m",
        "messages": [{"role": "user", "content": "p"}],
        "options": {"num_predict": 4096},
    }
    assert module_chat.call_count == 0


def test_anthropic_rejects_non_text_provider_content(mocker):
    mc = MagicMock()
    mc.messages.create.return_value.content = [MagicMock(text=7)]
    mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)
    mocker.patch("libreevolve.llm.anthropic.time.sleep")

    with pytest.raises(ValueError, match="Anthropic Messages returned non-text"):
        AnthropicBackend().generate("p")

    assert mc.messages.create.call_count == 3


def test_anthropic_rejects_empty_provider_content(mocker):
    mc = MagicMock()
    mc.messages.create.return_value.content = [MagicMock(text="\n\t")]
    mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)
    mocker.patch("libreevolve.llm.anthropic.time.sleep")

    with pytest.raises(ValueError, match="Anthropic Messages returned empty output"):
        AnthropicBackend().generate("p")

    assert mc.messages.create.call_count == 3


def test_anthropic_classifies_tool_use_without_text(mocker):
    mc = MagicMock()
    mc.messages.create.return_value.content = [MagicMock(type="tool_use")]
    mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)
    mocker.patch("libreevolve.llm.anthropic.time.sleep")

    with pytest.raises(ProviderResponseError) as excinfo:
        AnthropicBackend().generate("p")

    assert excinfo.value.category == "tool_call_only"
    assert mc.messages.create.call_count == 3


def test_ollama_rejects_empty_provider_content(mocker):
    mock_chat = mocker.patch(
        "libreevolve.llm.ollama.ollama_sdk.chat",
        return_value={"message": {"content": "   "}},
    )
    mocker.patch("libreevolve.llm.ollama.time.sleep")

    with pytest.raises(ValueError, match="Ollama Chat returned empty output"):
        OllamaBackend().generate("p")

    assert mock_chat.call_count == 3


def test_ollama_rejects_missing_provider_content(mocker):
    mock_chat = mocker.patch(
        "libreevolve.llm.ollama.ollama_sdk.chat",
        return_value={"message": {}},
    )
    mocker.patch("libreevolve.llm.ollama.time.sleep")

    with pytest.raises(ValueError, match="Ollama Chat returned non-text"):
        OllamaBackend().generate("p")

    assert mock_chat.call_count == 3


def test_anthropic_exhausts_retries(mocker):
    mc = MagicMock()
    mc.messages.create.side_effect = RuntimeError("persistent")
    mocker.patch("libreevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)
    mocker.patch("libreevolve.llm.anthropic.time.sleep")
    with pytest.raises(RuntimeError, match="persistent"):
        AnthropicBackend().generate("p")
    assert mc.messages.create.call_count == 3
