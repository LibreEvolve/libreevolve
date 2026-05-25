from __future__ import annotations
import math
from libreevolve.llm.base import LLMBackend


class LLMEnsemble:
    """UCB-style routing layer over one or more LLMBackend instances.

    Sources: UCB1 (Auer, Cesa-Bianchi & Fischer, 2002), applied to LLM
    selection per MadEvolve (arXiv:2602.15951). This implementation is a
    heuristic adaptation over observed fitness improvements, not a canonical
    regret-analyzed UCB1 implementation.
    """

    def __init__(
        self,
        backends: list[LLMBackend],
        explore_coeff: float = 1.0,
        strategy: str = "ucb1",
        backend_metadata: list[dict] | None = None,
    ):
        if not backends:
            raise ValueError("LLMEnsemble requires at least one backend.")
        self.backends = backends
        self.c = explore_coeff
        self.strategy = strategy
        self.backend_metadata = backend_metadata or [{} for _ in backends]
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
        if self.strategy == "throughput_depth":
            return self._throughput_depth_select(scores)
        return best_idx

    def _throughput_depth_select(self, ucb_scores: list[float]) -> int:
        """Cost/depth-aware scheduler layered over UCB scores.

        Metadata keys are optional:
        - `cost`: relative cost, lower is better
        - `latency`: relative latency, lower is better
        - `depth`: relative capability/depth, higher is better
        """
        best_idx = 0
        best_score = float("-inf")
        for i, base_score in enumerate(ucb_scores):
            meta = self.backend_metadata[i] if i < len(self.backend_metadata) else {}
            cost = float(meta.get("cost", 1.0))
            latency = float(meta.get("latency", 1.0))
            depth = float(meta.get("depth", 1.0))
            score = base_score + (0.10 * depth) - (0.05 * cost) - (0.05 * latency)
            if score > best_score:
                best_score = score
                best_idx = i
        return best_idx


def build_llm(config) -> LLMEnsemble:
    """Instantiate LLMEnsemble from config.backends."""
    def _get_backend_cls(t: str):
        if t == "anthropic":
            from libreevolve.llm.anthropic import AnthropicBackend
            return AnthropicBackend
        if t == "openai":
            from libreevolve.llm.openai import OpenAIBackend
            return OpenAIBackend
        if t == "ollama":
            from libreevolve.llm.ollama import OllamaBackend
            return OllamaBackend
        raise ValueError(f"Unknown backend type {t!r}. Valid: ['anthropic', 'openai', 'ollama']")
    backends = []
    ctor_keys = {
        "anthropic": {"model", "max_tokens"},
        "openai": {"model", "max_tokens", "reasoning_effort"},
        "ollama": {"model", "max_tokens"},
    }
    for s in config.backends:
        t = s["type"]
        cls = _get_backend_cls(t)
        allowed = ctor_keys[t]
        backends.append(cls(**{k: v for k, v in s.items() if k in allowed}))
    metadata = [
        {
            "cost": s.get("cost", 1.0),
            "latency": s.get("latency", 1.0),
            "depth": s.get("depth", 1.0),
            "role": s.get("role", "general"),
        }
        for s in config.backends
    ]
    return LLMEnsemble(
        backends,
        explore_coeff=config.ensemble_explore_coeff,
        strategy=config.ensemble_strategy,
        backend_metadata=metadata,
    )
