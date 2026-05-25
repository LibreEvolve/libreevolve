from __future__ import annotations
import random
import math
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from libreevolve.population.program import Program


class MAPElites:
    """3D MAP-Elites: performance x complexity x diversity.

    This is a fixed local quality-diversity heuristic, not a canonical
    user-defined behavior descriptor implementation.
    """

    def __init__(self, bins: int = 10, elite_archive_size: int = 50,
                 perf_bounds: tuple[float, float] = (0.0, 1.0)):
        self.bins = bins
        self._perf_min, self._perf_max = perf_bounds
        self._grid: dict[tuple[int, int, int], Program] = {}
        self._max_complexity: int = 1
        self._elite: list[Program] = []
        self._elite_size = elite_archive_size

    def _norm_perf(self, fitness: float) -> float:
        rng = self._perf_max - self._perf_min
        if rng == 0: return 0.5
        return max(0.0, min(1.0, (fitness - self._perf_min) / rng))

    def _norm_complexity(self, code: str) -> float:
        n = len(code)
        self._max_complexity = max(self._max_complexity, n)
        return n / self._max_complexity

    def _diversity(self, code: str) -> float:
        """Mean TF-IDF char-4gram cosine distance to global elite archive."""
        if not self._elite: return 0.5
        corpus = [p.code for p in self._elite] + [code]
        try:
            mat = TfidfVectorizer(analyzer="char", ngram_range=(4, 4)).fit_transform(corpus)
        except ValueError:
            return 0.5
        sims = cosine_similarity(mat[-1], mat[:-1])[0]
        return float(np.mean(1.0 - sims))

    def _cell(self, p: Program) -> tuple[int, int, int]:
        c = lambda x: max(0, min(self.bins - 1, int(x * self.bins)))
        return (c(self._norm_perf(p.fitness)),
                c(self._norm_complexity(p.code)),
                c(self._diversity(p.code)))

    def add(self, program: Program) -> None:
        if not math.isfinite(program.fitness):
            return
        cell = self._cell(program)
        occ = self._grid.get(cell)
        if occ is None or program.fitness > occ.fitness:
            self._grid[cell] = program
        self._elite.append(program)
        self._elite.sort(key=lambda p: p.fitness, reverse=True)
        self._elite = self._elite[:self._elite_size]

    def best(self) -> Program | None:
        return self._elite[0] if self._elite else None

    def sample_diverse(
        self, k: int, exclude_ids: set[str] | None = None
    ) -> list[Program]:
        exclude_ids = exclude_ids or set()
        cells = [p for p in self._grid.values() if p.id not in exclude_ids]
        return random.sample(cells, min(k, len(cells))) if cells else []

    def occupied_cells(self) -> list[Program]:
        return list(self._grid.values())

    def elite_archive(self) -> list[Program]:
        return list(self._elite)
