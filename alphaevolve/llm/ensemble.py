from __future__ import annotations
import math
from alphaevolve.llm.base import LLMBackend


class LLMEnsemble:
    """UCB1-bandit routing layer over one or more LLMBackend instances."""

    def __init__(self, backends: list[LLMBackend], explore_coeff: float = 1.0):
        if not backends:
            raise ValueError("LLMEnsemble requires at least one backend.")
        self.backends = backends
        self.c = explore_coeff
        self.counts: list[int]   = [0]   * len(backends)
        self.wins:   list[float] = [0.0] * len(backends)
        self.total:  int         = 0

    def generate(self, prompt: str) -> tuple[str, int]:
        """Returns (diff_text, backend_index)."""
        idx = self._ucb1_select()
        response = self.backends[idx].generate(prompt)
        self.counts[idx] += 1
        return response, idx

    def record_reward(self, idx: int, reward: float) -> None:
        """Caller is responsible for clamping reward >= 0."""
        self.wins[idx] += reward

    def _ucb1_select(self) -> int:
        self.total += 1
        # Note: log(1)=0 on first call — initial exploration is guaranteed by the
        # (score, -count) tiebreaker which prefers unexplored arms when scores tie.
        scores = [
            (self.wins[i] / max(self.counts[i], 1))
            + self.c * math.sqrt(math.log(self.total) / max(self.counts[i], 1))
            for i in range(len(self.backends))
        ]
        # Tiebreaker: prefer arms with fewer pulls (argmax breaks ties by first index,
        # so we use a tuple (score, -count) to prefer lower counts on ties)
        best_idx = 0
        best_score = (scores[0], -self.counts[0])
        for i in range(1, len(self.backends)):
            current_score = (scores[i], -self.counts[i])
            if current_score > best_score:
                best_score = current_score
                best_idx = i
        return best_idx


def build_llm(config) -> LLMEnsemble:
    """Instantiate LLMEnsemble from config.backends."""
    from alphaevolve.llm.anthropic import AnthropicBackend
    from alphaevolve.llm.openai    import OpenAIBackend
    from alphaevolve.llm.ollama    import OllamaBackend
    _REG = {"anthropic": AnthropicBackend, "openai": OpenAIBackend, "ollama": OllamaBackend}
    backends = []
    for s in config.backends:
        t = s["type"]
        if t not in _REG:
            raise ValueError(f"Unknown backend type {t!r}. Valid: {list(_REG)}")
        backends.append(_REG[t](**{k: v for k, v in s.items() if k != "type"}))
    return LLMEnsemble(backends, explore_coeff=config.ensemble_explore_coeff)
