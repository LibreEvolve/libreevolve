from __future__ import annotations
from pathlib import Path
import shutil
from libreevolve.core.config import Config
from libreevolve.core.jsonl import append_strict_jsonl, strict_json_dump
from libreevolve.population.islands import IslandModel
from libreevolve.population.program import Program

RUN_ARTIFACT_NAMES = {
    "history.jsonl",
    "history_invalid.jsonl",
    "failure_history.jsonl",
    "failure_history_invalid.jsonl",
    "prompt_history.jsonl",
    "prompt_history_invalid.jsonl",
    "manifest.json",
    "best.py",
    "best_workspace",
    "evaluator_artifacts",
}


class ProgramDatabase:
    """Facade: IslandModel + append-only history.jsonl.

    This is a small local log/archive facade, not a GigaEvo-style lifecycle
    database.
    """

    def __init__(
        self,
        config: Config,
        perf_bounds: tuple[float, float] = (0.0, 1.0),
        context_sources: list[dict] | None = None,
        evaluator_sources: list[dict] | None = None,
    ):
        self._islands = IslandModel(config, perf_bounds=perf_bounds)
        self._interval = config.migration_interval
        log_dir = Path(config.log_dir) / config.problem_name
        prepare_run_directory(log_dir, config.run_collision_policy)
        log_dir.mkdir(parents=True, exist_ok=True)
        self._jsonl = log_dir / "history.jsonl"
        self._failures = log_dir / "failure_history.jsonl"
        self._quarantine = log_dir / "history_invalid.jsonl"
        self._failure_quarantine = log_dir / "failure_history_invalid.jsonl"
        self._manifest = log_dir / "manifest.json"
        self._all: list[Program] = []
        self._failure_counts: dict[str, int] = {}
        self._write_manifest(config, context_sources or [], evaluator_sources or [])

    def add(self, program: Program) -> dict:
        return self._islands.add(program)

    def admit(self, program: Program, threshold: float = 0.0) -> dict:
        evaluation_is_valid = bool(program.evaluation.get("is_valid", True))
        if not evaluation_is_valid:
            event = {
                "program_id": program.id,
                "admitted": False,
                "reason": "invalid_evaluation",
                "threshold": threshold,
                "evaluation_is_valid": evaluation_is_valid,
                "island_id": None,
                "cell": None,
                "descriptors": {},
                "previous_occupant_id": None,
                "cell_replaced": False,
                "entered_cell": False,
                "entered_elite": False,
                "displaced_elite_ids": [],
            }
        elif program.fitness < threshold:
            event = {
                "program_id": program.id,
                "admitted": False,
                "reason": "below_threshold",
                "threshold": threshold,
                "evaluation_is_valid": evaluation_is_valid,
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
            event["evaluation_is_valid"] = evaluation_is_valid
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

    def log_failure(
        self,
        program: Program,
        parent: Program,
        mutation_text: str,
        diff_error: str | None,
    ) -> dict:
        error = program.evaluation.get("error") if program.evaluation else None
        key = "|".join(
            [
                parent.id,
                str(diff_error or ""),
                str(error or ""),
                _truncate_text(mutation_text, 500),
            ]
        )
        self._failure_counts[key] = self._failure_counts.get(key, 0) + 1
        record = {
            "program_id": program.id,
            "parent_id": parent.id,
            "generation": program.generation,
            "score": program.fitness,
            "is_valid": program.evaluation.get("is_valid") if program.evaluation else None,
            "error": error,
            "diff_error": diff_error,
            "changed_files": _changed_files(parent, program),
            "file_deltas": _file_deltas(parent, program),
            "mutation_text": _truncate_text(mutation_text, 4000),
            "mutation_truncated": len(mutation_text) > 4000,
            "evaluation": _failure_evaluation_summary(program),
            "repetition_count": self._failure_counts[key],
        }
        program.metadata = dict(program.metadata)
        program.metadata["failure_record"] = record
        append_strict_jsonl(
            self._failures,
            record,
            quarantine_path=self._failure_quarantine,
        )
        return record

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

    def _write_manifest(
        self, config: Config, context_sources: list[dict], evaluator_sources: list[dict]
    ) -> None:
        strict_json_dump(
            {
                "config": {
                    "max_generations": config.max_generations,
                    "num_inspirations": config.num_inspirations,
                    "eval_timeout_sec": config.eval_timeout_sec,
                    "validator_env_allowlist": config.validator_env_allowlist,
                    "evaluator_artifact_include": config.evaluator_artifact_include,
                    "evaluator_artifact_exclude": config.evaluator_artifact_exclude,
                    "evaluator_artifact_max_files": config.evaluator_artifact_max_files,
                    "evaluator_artifact_max_bytes": config.evaluator_artifact_max_bytes,
                    "evaluator_artifact_redact_secrets": config.evaluator_artifact_redact_secrets,
                    "explore_ratio": config.explore_ratio,
                    "mutation_mode": config.mutation_mode,
                    "eval_stages": config.eval_stages,
                    "prompt_variants": config.prompt_variants,
                    "meta_prompt_evolution": config.meta_prompt_evolution,
                    "meta_prompt_interval": config.meta_prompt_interval,
                    "prompt_reward_mode": config.prompt_reward_mode,
                    "prompt_reward_bounds": config.prompt_reward_bounds,
                    "prompt_explore_coeff": config.prompt_explore_coeff,
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
                    "run_id": config.run_id,
                    "run_collision_policy": config.run_collision_policy,
                    "seed": config.seed,
                },
                "problem": {
                    "context_sources": context_sources,
                    "evaluator_sources": evaluator_sources,
                },
            },
            self._manifest,
            indent=2,
        )


def prepare_run_directory(run_dir: Path, policy: str) -> None:
    existing = sorted(name for name in RUN_ARTIFACT_NAMES if (run_dir / name).exists())
    if not existing:
        return
    if policy == "overwrite":
        for name in existing:
            path = run_dir / name
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        return
    raise FileExistsError(
        f"Run directory {run_dir} already contains run artifacts {existing}; "
        "use --overwrite or set run_collision_policy: overwrite"
    )


def _changed_files(parent: Program, child: Program) -> list[str]:
    parent_files = parent.workspace().files
    child_files = child.workspace().files
    paths = sorted(set(parent_files) | set(child_files))
    return [path for path in paths if parent_files.get(path) != child_files.get(path)]


def _file_deltas(parent: Program, child: Program) -> list[dict]:
    parent_files = parent.workspace().files
    child_files = child.workspace().files
    deltas = []
    for path in sorted(set(parent_files) | set(child_files)):
        if path not in parent_files:
            change = "added"
        elif path not in child_files:
            change = "deleted"
        elif parent_files[path] != child_files[path]:
            change = "modified"
        else:
            continue
        deltas.append({"path": path, "change": change})
    return deltas


def _failure_evaluation_summary(program: Program) -> dict:
    evaluation = program.evaluation or {}
    return {
        "fitness": evaluation.get("fitness", program.fitness),
        "is_valid": evaluation.get("is_valid"),
        "error": evaluation.get("error"),
        "stdout": _truncate_text(str(evaluation.get("stdout", "")), 1000),
        "stderr": _truncate_text(str(evaluation.get("stderr", "")), 1000),
        "stages": [
            {
                "name": stage.get("name"),
                "passed": stage.get("passed"),
                "score": stage.get("score"),
                "error": stage.get("error"),
            }
            for stage in evaluation.get("stages", [])[-3:]
            if isinstance(stage, dict)
        ],
    }


def _truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    notice = f"\n[truncated {len(text) - max_chars} chars]"
    keep = max(0, max_chars - len(notice))
    return text[:keep] + notice
