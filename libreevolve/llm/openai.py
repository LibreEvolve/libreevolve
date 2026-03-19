from __future__ import annotations
import time
import openai as openai_sdk

class OpenAIBackend:
    def __init__(self, model: str = "gpt-4o", max_tokens: int = 4096,
                 reasoning_effort: str | None = None):
        self._client = openai_sdk.OpenAI()
        self._model = model
        self._max_tokens = max_tokens
        self._reasoning_effort = reasoning_effort
    @property
    def name(self) -> str: return f"openai/{self._model}"
    def generate(self, prompt: str, **kwargs) -> str:
        for attempt in range(3):
            try:
                if self._reasoning_effort:
                    return self._generate_responses(prompt)
                return self._generate_chat(prompt)
            except Exception:
                if attempt == 2: raise
                time.sleep(2 ** attempt)
        raise RuntimeError("unreachable")

    def _generate_chat(self, prompt: str) -> str:
        r = self._client.chat.completions.create(
            model=self._model, max_tokens=self._max_tokens,
            messages=[{"role": "user", "content": prompt}])
        return r.choices[0].message.content

    def _generate_responses(self, prompt: str) -> str:
        r = self._client.responses.create(
            model=self._model,
            max_output_tokens=self._max_tokens,
            reasoning={"effort": self._reasoning_effort},
            input=[{"role": "user", "content": prompt}])
        # Extract text from response output items
        for item in r.output:
            if item.type == "message":
                for part in item.content:
                    if part.type == "output_text":
                        return part.text
        return ""
