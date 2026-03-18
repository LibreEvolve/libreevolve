from unittest.mock import MagicMock
from alphaevolve.llm.anthropic import AnthropicBackend
from alphaevolve.llm.openai    import OpenAIBackend
from alphaevolve.llm.ollama    import OllamaBackend
from alphaevolve.llm.base      import LLMBackend

def test_names():
    for cls, prefix, m in [(AnthropicBackend, "anthropic", "m"),
                           (OpenAIBackend, "openai", "m2"),
                           (OllamaBackend, "ollama", "m3")]:
        b = cls.__new__(cls); b._model = m
        assert b.name == f"{prefix}/{m}"

def test_anthropic_generate(mocker):
    mc = MagicMock()
    mc.messages.create.return_value.content = [MagicMock(text="diff")]
    mocker.patch("alphaevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)
    assert AnthropicBackend(model="m").generate("p") == "diff"

def test_openai_generate(mocker):
    mc = MagicMock()
    mc.chat.completions.create.return_value.choices = [MagicMock(message=MagicMock(content="d"))]
    mocker.patch("alphaevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)
    assert OpenAIBackend(model="m").generate("p") == "d"

def test_ollama_generate(mocker):
    mocker.patch("alphaevolve.llm.ollama.ollama_sdk.chat",
                 return_value={"message": {"content": "out"}})
    assert OllamaBackend(model="m").generate("p") == "out"

def test_anthropic_retries(mocker):
    mc = MagicMock()
    mc.messages.create.side_effect = [Exception("fail"),
                                       MagicMock(content=[MagicMock(text="ok")])]
    mocker.patch("alphaevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)
    mocker.patch("alphaevolve.llm.anthropic.time.sleep")
    assert AnthropicBackend().generate("p") == "ok"
    assert mc.messages.create.call_count == 2
