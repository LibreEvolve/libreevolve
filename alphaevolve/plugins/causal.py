from __future__ import annotations
import math, random
from collections import defaultdict
from alphaevolve.plugins.base import PluginBase


class CausalPlugin(PluginBase):
    """CausalEvolve: causal scratchpad + MAB outcome-factor guidance.
    Source: arXiv 2603.14575. Hooks: build_extra_context, on_evaluated.
    """
    FACTORS = ["loop_structure", "data_types", "algorithm_choice",
               "constants", "helper_functions"]

    def __init__(self):
        self._wins:   dict[str, float] = defaultdict(float)
        self._counts: dict[str, int]   = defaultdict(int)
        self._total = 0
        self._history: list[dict] = []

    def build_extra_context(self, parent, inspirations) -> str:
        if not self._history: return ""
        f = self._ucb1_factor()
        lines = "\n".join(f"  - Changed {h['factor']}: delta={h['delta']:+.4f}"
                         for h in self._history[-5:])
        return f"[CAUSAL GUIDANCE]\nMost promising dimension: {f}\nRecent outcomes:\n{lines}\n"

    def on_evaluated(self, program, score: float) -> float:
        prev = self._history[-1]["score"] if self._history else 0.0
        delta = score - prev
        factor = random.choice(self.FACTORS)
        self._wins[factor] += max(0.0, delta)
        self._counts[factor] += 1
        self._total += 1
        self._history.append({"factor": factor, "delta": delta, "score": score})
        return score

    def _ucb1_factor(self) -> str:
        if self._total == 0: return random.choice(self.FACTORS)
        scores = [(self._wins[f]/max(self._counts[f],1)
                   + math.sqrt(math.log(max(self._total,1))/max(self._counts[f],1)), f)
                  for f in self.FACTORS]
        return max(scores)[1]
