from __future__ import annotations

import time
from dataclasses import dataclass

from libreevolve.core.config import Config


@dataclass
class RunBudget:
    """Synchronous run budget accounting.

    This tracks local loop consumption only. Provider token/cost accounting and
    resumable pending-work queues remain separate runtime concerns.
    """

    max_generations: int
    max_evaluations: int | None
    max_evaluator_seconds: float | None
    max_runtime_seconds: float | None
    started_at: float
    evaluations: int = 0
    seed_evaluations: int = 0
    candidate_evaluations: int = 0
    evaluator_seconds: float = 0.0
    generations_started: int = 0
    generations_completed: int = 0
    stop_reason: str | None = None

    @classmethod
    def from_config(cls, config: Config) -> "RunBudget":
        return cls(
            max_generations=config.max_generations,
            max_evaluations=config.max_evaluations,
            max_evaluator_seconds=config.max_evaluator_seconds,
            max_runtime_seconds=config.max_runtime_seconds,
            started_at=time.monotonic(),
        )

    def check_before_generation(self) -> str | None:
        return self._check_limits()

    def check_before_evaluation(self) -> str | None:
        return self._check_limits()

    def record_generation_start(self) -> None:
        self.generations_started += 1

    def record_generation_complete(self) -> None:
        self.generations_completed += 1

    def record_evaluation(self, elapsed_sec: float, *, seed: bool) -> None:
        self.evaluations += 1
        if seed:
            self.seed_evaluations += 1
        else:
            self.candidate_evaluations += 1
        self.evaluator_seconds += max(0.0, float(elapsed_sec or 0.0))

    def finish(self, best_found: bool) -> dict:
        if self.stop_reason is None:
            self.stop_reason = self._check_limits()
        if self.stop_reason is None:
            if self.generations_completed >= self.max_generations:
                self.stop_reason = "max_generations"
            elif not best_found:
                self.stop_reason = "no_valid_programs"
            else:
                self.stop_reason = "completed"
        return self.snapshot()

    def snapshot(self) -> dict:
        return {
            "limits": {
                "max_generations": self.max_generations,
                "max_evaluations": self.max_evaluations,
                "max_evaluator_seconds": self.max_evaluator_seconds,
                "max_runtime_seconds": self.max_runtime_seconds,
            },
            "consumed": {
                "evaluations": self.evaluations,
                "seed_evaluations": self.seed_evaluations,
                "candidate_evaluations": self.candidate_evaluations,
                "evaluator_seconds": self.evaluator_seconds,
                "runtime_seconds": max(0.0, time.monotonic() - self.started_at),
                "generations_started": self.generations_started,
                "generations_completed": self.generations_completed,
            },
            "stop_reason": self.stop_reason,
        }

    def _check_limits(self) -> str | None:
        if self.stop_reason is not None:
            return self.stop_reason
        if self.max_evaluations is not None and self.evaluations >= self.max_evaluations:
            self.stop_reason = "max_evaluations"
        elif (
            self.max_evaluator_seconds is not None
            and self.evaluator_seconds >= self.max_evaluator_seconds
        ):
            self.stop_reason = "max_evaluator_seconds"
        elif (
            self.max_runtime_seconds is not None
            and time.monotonic() - self.started_at >= self.max_runtime_seconds
        ):
            self.stop_reason = "max_runtime_seconds"
        return self.stop_reason
