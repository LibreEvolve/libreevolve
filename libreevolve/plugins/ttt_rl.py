from __future__ import annotations
import hashlib
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
        self._export_count = 0
        self._last_export_path: Path | None = None
        self._last_quarantine_path: Path | None = None

    def on_evaluated(self, program, score: float) -> float:
        if program.metadata.get("prompt") and program.metadata.get("diff"):
            raw_score = score
            shaped_reward = max(0.0, score)
            self._data.append({
                "prompt": program.metadata["prompt"],
                "response": program.metadata["diff"],
                "raw_score": raw_score,
                "reward": shaped_reward,
                "reward_policy": "max(0.0, raw_score)",
            })
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
            self._export_count += 1
        self._last_export_path = out
        self._last_quarantine_path = quarantine

    def get_training_data(self) -> list[dict]:
        return list(self._data)

    def run_artifacts_metadata(self) -> dict:
        metadata = {
            "plugin": self.__class__.__name__,
            "reward_policy": "max(0.0, raw_score)",
            "queued_examples": len(self._data),
            "exported_examples": self._export_count,
            "log_dir": str(self._log_dir),
        }
        if self._last_export_path is not None:
            metadata["path"] = str(self._last_export_path)
            if self._last_export_path.exists():
                metadata["sha256"] = _file_sha256(self._last_export_path)
                metadata["bytes"] = self._last_export_path.stat().st_size
        if self._last_quarantine_path is not None:
            metadata["quarantine_path"] = str(self._last_quarantine_path)
            metadata["quarantine_exists"] = self._last_quarantine_path.exists()
        return metadata


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
