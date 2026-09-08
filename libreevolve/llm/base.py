from typing import Protocol, runtime_checkable

@runtime_checkable
class LLMBackend(Protocol):
    """Per-backend interface. Returns raw text (str), not a tuple."""
    def generate(self, prompt: str, **kwargs) -> str: ...
    @property
    def name(self) -> str: ...
