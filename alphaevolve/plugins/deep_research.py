from __future__ import annotations
from alphaevolve.plugins.base import PluginBase


class DeepResearchPlugin(PluginBase):
    """DeepEvolve: web search + hypothesis synthesis before generation.
    Source: arXiv 2510.06056. Hook: on_generation_start.
    Pass search_fn=callable(query)->str to activate; default is a no-op stub.
    """
    def __init__(self, search_fn=None, search_every: int = 10):
        self._search_fn    = search_fn or self._default_search
        self._search_every = search_every
        self._synthesis    = ""

    def on_generation_start(self, gen: int, db) -> None:
        if gen % self._search_every != 0: return
        best = db.best()
        if best is None: return
        result = self._search_fn(f"evolutionary algorithm optimization fitness~{best.fitness:.3f}")
        if result: self._synthesis = result

    def build_extra_context(self, parent, inspirations) -> str:
        return f"[DEEP RESEARCH]\n{self._synthesis}\n" if self._synthesis else ""

    @staticmethod
    def _default_search(query: str) -> str | None:
        """No-op stub. Replace with a real search function for production use."""
        return None
