from __future__ import annotations
import json
from pathlib import Path
from alphaevolve.core.config import Config
from alphaevolve.population.islands import IslandModel
from alphaevolve.population.program import Program


class ProgramDatabase:
    """Facade: IslandModel + append-only history.jsonl."""

    def __init__(self, config: Config):
        self._islands = IslandModel(config)
        self._interval = config.migration_interval
        log_dir = Path(config.log_dir) / config.problem_name
        log_dir.mkdir(parents=True, exist_ok=True)
        self._jsonl = log_dir / "history.jsonl"
        self._all: list[Program] = []

    def add(self, program: Program) -> None:
        self._islands.add(program)

    def log(self, program: Program) -> None:
        self._all.append(program)
        with open(self._jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "id": program.id, "code": program.code, "fitness": program.fitness,
                "generation": program.generation, "parent_id": program.parent_id,
                "lineage": program.lineage, "metadata": program.metadata,
            }) + "\n")

    def sample(self, strategy: str = "exploit") -> Program | None:
        return self._islands.sample(strategy=strategy)

    def sample_diverse(self, k: int) -> list[Program]:
        return self._islands.sample_diverse(k=k)

    def best(self) -> Program | None:
        return self._islands.best()

    def maybe_migrate(self, gen: int) -> None:
        if self._interval > 0 and gen > 0 and gen % self._interval == 0:
            self._islands.migrate()

    def all_programs(self) -> list[Program]:
        return list(self._all)
