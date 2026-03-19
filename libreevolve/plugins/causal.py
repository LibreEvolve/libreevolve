from __future__ import annotations
import math, random, re
from collections import defaultdict
from libreevolve.core.diff import DIFF_PATTERN
from libreevolve.plugins.base import PluginBase

# Heuristic patterns for classifying which code dimension a diff changed.
# Checked against tokens that differ between SEARCH and REPLACE blocks.
_FACTOR_PATTERNS: dict[str, re.Pattern] = {
    "loop_structure":   re.compile(r'\b(for|while|break|continue|range|enumerate)\b'),
    "data_types":       re.compile(r'\b(int|float|str|list|dict|set|tuple|bool|bytes|array)\b'
                                   r'|\.astype\b'),
    "constants":        re.compile(r'\b\d+\.?\d*\b|["\'][^"\']*["\']'),
    "helper_functions": re.compile(r'\bdef\s+\w+|\bclass\s+\w+|\blambda\b'),
    "algorithm_choice": re.compile(r'\b(import|sorted|\.sort\(|heapq|bisect|itertools'
                                   r'|collections|functools|math\.|numpy|np\.)\b'),
}


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
        lines = "\n".join(f"  - Changed {h['factors']}: delta={h['delta']:+.4f}"
                         for h in self._history[-5:])
        return f"[CAUSAL GUIDANCE]\nMost promising dimension: {f}\nRecent outcomes:\n{lines}\n"

    def on_evaluated(self, program, score: float) -> float:
        prev = self._history[-1]["score"] if self._history else 0.0
        delta = score - prev
        diff_text = program.metadata.get("diff", "")
        factors = self._detect_factors(diff_text)
        reward = max(0.0, delta) / len(factors)
        for factor in factors:
            self._wins[factor] += reward
            self._counts[factor] += 1
        self._total += 1
        self._history.append({"factors": factors, "delta": delta, "score": score})
        return score

    def _detect_factors(self, diff_text: str) -> list[str]:
        """Classify which code dimensions a SEARCH/REPLACE diff changed.

        Extracts tokens that differ between SEARCH and REPLACE blocks,
        then matches against keyword patterns for each factor. Falls back
        to random when the diff is empty or no patterns match.
        """
        blocks = DIFF_PATTERN.findall(diff_text)
        if not blocks:
            return [random.choice(self.FACTORS)]
        factors: set[str] = set()
        for search, replace in blocks:
            old_tokens = set(re.findall(r'\S+', search))
            new_tokens = set(re.findall(r'\S+', replace))
            changed = " ".join((new_tokens - old_tokens) | (old_tokens - new_tokens))
            for factor, pattern in _FACTOR_PATTERNS.items():
                if pattern.search(changed):
                    factors.add(factor)
        return list(factors) if factors else [random.choice(self.FACTORS)]

    def _ucb1_factor(self) -> str:
        if self._total == 0: return random.choice(self.FACTORS)
        scores = [(self._wins[f]/max(self._counts[f],1)
                   + math.sqrt(math.log(max(self._total,1))/max(self._counts[f],1)), f)
                  for f in self.FACTORS]
        return max(scores)[1]
