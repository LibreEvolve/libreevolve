from __future__ import annotations
from pathlib import Path
from libreevolve.core.jsonl import append_strict_jsonl
from libreevolve.plugins.base import PluginBase


class TTTRLPlugin(PluginBase):
    """ThetaEvolve-inspired GRPO training-data export.

    This accumulates examples only; it does not train an RL model.
    Source: arXiv 2511.23473. Hooks: on_evaluated, on_generation_end.
    Writes (prompt, response, reward) triples to grpo_data.jsonl.
    Override _maybe_train() to trigger real GRPO fine-tuning.
    """
    def __init__(self, train_every: int = 50, log_dir: str = "runs/"):
        self._train_every = train_every
        self._log_dir = Path(log_dir)
        self._data: list[dict] = []

    def on_evaluated(self, program, score: float) -> float:
        if program.metadata.get("prompt") and program.metadata.get("diff"):
            self._data.append({"prompt": program.metadata["prompt"],
                               "response": program.metadata["diff"],
                               "reward": max(0.0, score)})
        return score

    def on_generation_end(self, gen: int, best) -> None:
        if gen > 0 and gen % self._train_every == 0:
            self._maybe_train()

    def _maybe_train(self) -> None:
        batch = self._data[-self._train_every:]
        if not batch: return
        out = self._log_dir / "grpo_data.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        quarantine = self._log_dir / "grpo_data_invalid.jsonl"
        for record in batch:
            append_strict_jsonl(out, record, quarantine_path=quarantine)

    def get_training_data(self) -> list[dict]:
        return list(self._data)
