from __future__ import annotations
import time
import ollama as ollama_sdk

class OllamaBackend:
    def __init__(self, model: str = "llama3", max_tokens: int = 4096):
        self._model = model; self._max_tokens = max_tokens
    @property
    def name(self) -> str: return f"ollama/{self._model}"
    @property
    def api_mode(self) -> str:
        return "chat"
    def generate(self, prompt: str, **kwargs) -> str:
        for attempt in range(3):
            try:
                r = ollama_sdk.chat(model=self._model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"num_predict": self._max_tokens})
                return r["message"]["content"]
            except Exception:
                if attempt == 2: raise
                time.sleep(2 ** attempt)
        raise RuntimeError("unreachable")
