from __future__ import annotations
import time
import openai as openai_sdk

class OpenAIBackend:
    def __init__(self, model: str = "gpt-4o", max_tokens: int = 4096):
        self._client = openai_sdk.OpenAI()
        self._model = model; self._max_tokens = max_tokens
    @property
    def name(self) -> str: return f"openai/{self._model}"
    def generate(self, prompt: str, **kwargs) -> str:
        for attempt in range(3):
            try:
                r = self._client.chat.completions.create(
                    model=self._model, max_tokens=self._max_tokens,
                    messages=[{"role": "user", "content": prompt}])
                return r.choices[0].message.content
            except Exception:
                if attempt == 2: raise
                time.sleep(2 ** attempt)
        raise RuntimeError("unreachable")
