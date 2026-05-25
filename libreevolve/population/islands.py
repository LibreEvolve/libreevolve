from __future__ import annotations
import math, random
from libreevolve.core.config import Config
from libreevolve.population.map_elites import MAPElites, _selection_key
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

    def add(self, program: Program) -> dict:
        island_id = self._current
        event = self.islands[island_id].add(program)
        event["island_id"] = island_id
        self._current = (self._current + 1) % self.n_islands
        return event

    def sample(self, strategy: str = "exploit") -> Program | None:
        if strategy == "exploit":
            cands = [i.best() for i in self.islands if i.best()]
            return max(cands, key=_selection_key) if cands else None
        if strategy == "explore":
            pool = [p for i in self.islands for p in i.occupied_cells()]
            return random.choice(pool) if pool else None
        if strategy == "metric":
            leaders = _metric_leaders(self._occupied_programs())
            return random.choice(leaders) if leaders else self.sample("exploit")
        if strategy == "novelty":
            pool = self._occupied_programs()
            return max(pool, key=_novelty_key) if pool else None
        if strategy == "recency":
            pool = self._occupied_programs()
            return max(pool, key=_recency_key) if pool else None
        raise ValueError(f"Unknown strategy: {strategy!r}")

    def sample_diverse(
        self, k: int, exclude_ids: set[str] | None = None, strategy: str = "mixed"
    ) -> list[Program]:
        candidates = self._occupied_programs(exclude_ids)
        if k <= 0 or not candidates:
            return []
        if strategy == "random":
            return random.sample(candidates, min(k, len(candidates)))
        if strategy == "selection":
            return sorted(candidates, key=_selection_key, reverse=True)[:k]
        if strategy == "metric":
            return _first_unique(
                _metric_leaders(candidates)
                + sorted(candidates, key=_selection_key, reverse=True),
                k,
            )
        if strategy == "novelty":
            return sorted(candidates, key=_novelty_key, reverse=True)[:k]
        if strategy == "recency":
            return sorted(candidates, key=_recency_key, reverse=True)[:k]
        if strategy == "mixed":
            random_tail = random.sample(candidates, len(candidates))
            return _first_unique(
                _metric_leaders(candidates)
                + sorted(candidates, key=_novelty_key, reverse=True)
                + sorted(candidates, key=_selection_key, reverse=True)
                + random_tail,
                k,
            )
        raise ValueError(f"Unknown inspiration strategy: {strategy!r}")

    def _occupied_programs(
        self, exclude_ids: set[str] | None = None
    ) -> list[Program]:
        exclude_ids = exclude_ids or set()
        pool: dict[str, Program] = {}
        for island in self.islands:
            for program in island.occupied_cells():
                if program.id not in exclude_ids:
                    pool.setdefault(program.id, program)
        return list(pool.values())

    def best(self) -> Program | None:
        cands = [i.best() for i in self.islands if i.best()]
        return max(cands, key=_selection_key) if cands else None

    def migrate(self) -> None:
        """Ring: island i copies top migrants to island (i+1) % n.

        Snapshot all elite archives first so that migrants added during this
        round are not themselves propagated in the same step (i.e. island 0
        does not indirectly reach island 2 via island 1 in a single call).
        """
        if self._migration_ratio <= 0:
            return
        snapshots = [src.elite_archive() for src in self.islands]
        for i, elites in enumerate(snapshots):
            if not elites:
                continue
            dst = self.islands[(i + 1) % self.n_islands]
            n = max(1, math.ceil(len(elites) * self._migration_ratio))
            for program in elites[:n]:
                dst.add(program)


def _metric_leaders(candidates: list[Program]) -> list[Program]:
    names = sorted(
        {
            name
            for program in candidates
            for name, value in _normalized_metrics(program).items()
            if _is_finite_number(value)
        }
    )
    leaders: list[Program] = []
    for name in names:
        eligible = [
            program
            for program in candidates
            if _is_finite_number(_normalized_metrics(program).get(name))
        ]
        if eligible:
            leaders.append(
                max(
                    eligible,
                    key=lambda program: (
                        float(_normalized_metrics(program)[name]),
                        *_selection_key(program),
                    ),
                )
            )
    return _first_unique(leaders, len(leaders))


def _normalized_metrics(program: Program) -> dict:
    raw = program.metadata.get("normalized_metrics")
    return raw if isinstance(raw, dict) else {}


def _novelty_key(program: Program) -> tuple[float, float, float]:
    return (_descriptor_value(program, "diversity"), *_selection_key(program))


def _recency_key(program: Program) -> tuple[int, float, float]:
    return (program.generation, *_selection_key(program))


def _descriptor_value(program: Program, name: str) -> float:
    admission = program.metadata.get("archive_admission")
    if not isinstance(admission, dict):
        return 0.0
    descriptors = admission.get("descriptors")
    if not isinstance(descriptors, dict):
        return 0.0
    raw = descriptors.get(name)
    return float(raw) if _is_finite_number(raw) else 0.0


def _is_finite_number(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )


def _first_unique(programs: list[Program], k: int) -> list[Program]:
    result: list[Program] = []
    seen: set[str] = set()
    for program in programs:
        if program.id in seen:
            continue
        seen.add(program.id)
        result.append(program)
        if len(result) >= k:
            break
    return result
