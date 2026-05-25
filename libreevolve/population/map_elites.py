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

    def _cell_with_descriptors(
        self, p: Program
    ) -> tuple[tuple[int, int, int], dict[str, float]]:
        descriptors = {
            "performance": self._norm_perf(p.fitness),
            "complexity": self._norm_complexity(p.code),
            "diversity": self._diversity(p.code),
        }
        c = lambda x: max(0, min(self.bins - 1, int(x * self.bins)))
        return (
            c(descriptors["performance"]),
            c(descriptors["complexity"]),
            c(descriptors["diversity"]),
        ), descriptors

    def _cell(self, p: Program) -> tuple[int, int, int]:
        return self._cell_with_descriptors(p)[0]

    def add(self, program: Program) -> dict:
        event = {
            "program_id": program.id,
            "admitted": False,
            "reason": "non_finite_fitness",
            "cell": None,
            "descriptors": {},
            "previous_occupant_id": None,
            "cell_replaced": False,
            "entered_cell": False,
            "entered_elite": False,
            "displaced_elite_ids": [],
        }
        if not math.isfinite(program.fitness):
            return event
        cell, descriptors = self._cell_with_descriptors(program)
        event["cell"] = list(cell)
        event["descriptors"] = descriptors
        occ = self._grid.get(cell)
        event["previous_occupant_id"] = occ.id if occ else None
        if occ is None or program.fitness > occ.fitness:
            self._grid[cell] = program
            event["entered_cell"] = True
            event["cell_replaced"] = occ is not None
        self._elite.append(program)
        self._elite.sort(key=lambda p: p.fitness, reverse=True)
        before_trim_ids = [p.id for p in self._elite]
        self._elite = self._elite[:self._elite_size]
        elite_ids = {p.id for p in self._elite}
        event["entered_elite"] = program.id in elite_ids
        event["displaced_elite_ids"] = [
            program_id for program_id in before_trim_ids[self._elite_size :]
        ]
        event["admitted"] = event["entered_cell"] or event["entered_elite"]
        if event["cell_replaced"]:
            event["reason"] = "cell_replaced"
        elif event["entered_cell"]:
            event["reason"] = "empty_cell"
        elif event["entered_elite"]:
            event["reason"] = "elite_only"
        else:
            event["reason"] = "not_improving_cell"
        return event

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
