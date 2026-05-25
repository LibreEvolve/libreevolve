from __future__ import annotations
import math, random
from libreevolve.core.config import Config
from libreevolve.population.map_elites import MAPElites
from libreevolve.population.program import Program


class IslandModel:
    """5 independent MAP-Elites archives with ring-topology migration.

    Inspired by island population models; this is a synchronous local archive
    rotation and migration policy.
    """

    def __init__(
        self, config: Config, perf_bounds: tuple[float, float] = (0.0, 1.0)
    ):
        self.n_islands = config.n_islands
        self._migration_ratio = config.migration_ratio
        self.islands: list[MAPElites] = [
            MAPElites(
                bins=config.map_elites_bins,
                elite_archive_size=config.elite_archive_size,
                perf_bounds=perf_bounds,
            )
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

    def sample_diverse(
        self, k: int, exclude_ids: set[str] | None = None
    ) -> list[Program]:
        exclude_ids = exclude_ids or set()
        pool: dict[str, Program] = {}
        for island in self.islands:
            for program in island.occupied_cells():
                if program.id not in exclude_ids:
                    pool.setdefault(program.id, program)
        candidates = list(pool.values())
        return random.sample(candidates, min(k, len(candidates))) if candidates else []

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
