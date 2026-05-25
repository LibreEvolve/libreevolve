from __future__ import annotations
import time
import anthropic as anthropic_sdk

class AnthropicBackend:
    def __init__(self, model: str = "claude-sonnet-4-6", max_tokens: int = 4096):
        self._client = anthropic_sdk.Anthropic()
        self._model = model; self._max_tokens = max_tokens
    @property
    def name(self) -> str: return f"anthropic/{self._model}"
    @property
    def api_mode(self) -> str:
        return "messages"
    def generate(self, prompt: str, **kwargs) -> str:
        for attempt in range(3):
            try:
                msg = self._client.messages.create(
                    model=self._model, max_tokens=self._max_tokens,
                    messages=[{"role": "user", "content": prompt}])
                return msg.content[0].text
            except Exception:
                if attempt == 2: raise
                time.sleep(2 ** attempt)
        raise RuntimeError("unreachable")
