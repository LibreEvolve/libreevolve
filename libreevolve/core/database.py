from __future__ import annotations
from pathlib import Path
from libreevolve.core.config import Config
from libreevolve.core.jsonl import append_strict_jsonl, strict_json_dump
from libreevolve.population.islands import IslandModel
from libreevolve.population.program import Program


class ProgramDatabase:
    """Facade: IslandModel + append-only history.jsonl.

    This is a small local log/archive facade, not a GigaEvo-style lifecycle
    database.
    """

    def __init__(self, config: Config, perf_bounds: tuple[float, float] = (0.0, 1.0)):
        self._islands = IslandModel(config, perf_bounds=perf_bounds)
        self._interval = config.migration_interval
        log_dir = Path(config.log_dir) / config.problem_name
        log_dir.mkdir(parents=True, exist_ok=True)
        self._jsonl = log_dir / "history.jsonl"
        self._quarantine = log_dir / "history_invalid.jsonl"
        self._manifest = log_dir / "manifest.json"
        self._all: list[Program] = []
        self._write_manifest(config)

    def add(self, program: Program) -> dict:
        return self._islands.add(program)

    def admit(self, program: Program, threshold: float = 0.0) -> dict:
        if program.fitness < threshold:
            event = {
                "program_id": program.id,
                "admitted": False,
                "reason": "below_threshold",
                "threshold": threshold,
                "island_id": None,
                "cell": None,
                "descriptors": {},
                "previous_occupant_id": None,
                "cell_replaced": False,
                "entered_cell": False,
                "entered_elite": False,
                "displaced_elite_ids": [],
            }
        else:
            event = self.add(program)
            event["threshold"] = threshold
        program.metadata = dict(program.metadata)
        program.metadata["archive_admission"] = event
        return event

    def log(self, program: Program) -> None:
        append_strict_jsonl(
            self._jsonl,
            {
                "id": program.id, "code": program.code, "fitness": program.fitness,
                "files": program.files, "primary_file": program.primary_file,
                "generation": program.generation, "parent_id": program.parent_id,
                "lineage": program.lineage, "metadata": program.metadata,
                "metrics": program.metrics, "evaluation": program.evaluation,
            },
            quarantine_path=self._quarantine,
        )
        self._all.append(program)

    def sample(self, strategy: str = "exploit") -> Program | None:
        return self._islands.sample(strategy=strategy)

    def sample_diverse(
        self, k: int, exclude_ids: set[str] | None = None
    ) -> list[Program]:
        return self._islands.sample_diverse(k=k, exclude_ids=exclude_ids)

    def best(self) -> Program | None:
        return self._islands.best()

    def maybe_migrate(self, gen: int) -> None:
        if self._interval > 0 and gen > 0 and gen % self._interval == 0:
            self._islands.migrate()

    def all_programs(self) -> list[Program]:
        return list(self._all)

    def _write_manifest(self, config: Config) -> None:
        strict_json_dump(
            {
                "config": {
                    "max_generations": config.max_generations,
                    "num_inspirations": config.num_inspirations,
                    "eval_timeout_sec": config.eval_timeout_sec,
                    "explore_ratio": config.explore_ratio,
                    "mutation_mode": config.mutation_mode,
                    "eval_stages": config.eval_stages,
                    "prompt_variants": config.prompt_variants,
                    "meta_prompt_evolution": config.meta_prompt_evolution,
                    "meta_prompt_interval": config.meta_prompt_interval,
                    "critique_enabled": config.critique_enabled,
                    "critique_prompt": config.critique_prompt,
                    "llm_feedback": config.llm_feedback,
                    "n_islands": config.n_islands,
                    "migration_interval": config.migration_interval,
                    "migration_ratio": config.migration_ratio,
                    "map_elites_bins": config.map_elites_bins,
                    "elite_archive_size": config.elite_archive_size,
                    "backends": config.backends,
                    "ensemble_explore_coeff": config.ensemble_explore_coeff,
                    "ensemble_strategy": config.ensemble_strategy,
                    "plugins": config.plugins,
                    "log_dir": config.log_dir,
                    "problem_name": config.problem_name,
                    "seed": config.seed,
                }
            },
            self._manifest,
            indent=2,
        )
