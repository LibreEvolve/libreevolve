from __future__ import annotations
import math, random
from libreevolve.core.config import Config
from libreevolve.population.map_elites import MAPElites
from libreevolve.population.program import Program


class IslandModel:
    """5 independent MAP-Elites archives with ring-topology migration.

    Sources: ring topology ablations from CodeEvolve (arXiv:2510.14150),
    multi-island elite exchange from GigaEvo (arXiv:2511.17592).
    """

    def __init__(self, config: Config):
        self.n_islands = config.n_islands
        self._migration_ratio = config.migration_ratio
        self.islands: list[MAPElites] = [
            MAPElites(bins=config.map_elites_bins, elite_archive_size=config.elite_archive_size)
            for _ in range(self.n_islands)
        ]
        self._current = 0

    def add(self, program: Program) -> None:
        self.islands[self._current].add(program)
        self._current = (self._current + 1) % self.n_islands

    def sample(self, strategy: str = "exploit") -> Program | None:
        if strategy == "exploit":
            cands = [i.best() for i in self.islands if i.best()]
            return max(cands, key=lambda p: p.fitness) if cands else None
        if strategy == "explore":
            pool = [p for i in self.islands for p in i.occupied_cells()]
            return random.choice(pool) if pool else None
        raise ValueError(f"Unknown strategy: {strategy!r}")

    def sample_diverse(self, k: int) -> list[Program]:
        pool = [p for i in self.islands for p in i.occupied_cells()]
        return random.sample(pool, min(k, len(pool))) if pool else []

    def best(self) -> Program | None:
        cands = [i.best() for i in self.islands if i.best()]
        return max(cands, key=lambda p: p.fitness) if cands else None

    def migrate(self) -> None:
        """Ring: island i copies top migrants to island (i+1) % n.

        Snapshot all elite archives first so that migrants added during this
        round are not themselves propagated in the same step (i.e. island 0
        does not indirectly reach island 2 via island 1 in a single call).
        """
        snapshots = [src.elite_archive() for src in self.islands]
        for i, elites in enumerate(snapshots):
            if not elites:
                continue
            dst = self.islands[(i + 1) % self.n_islands]
            n = max(1, math.ceil(len(elites) * self._migration_ratio))
            for program in elites[:n]:
                dst.add(program)
