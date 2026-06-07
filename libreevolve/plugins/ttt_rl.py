from __future__ import annotations
import copy
import hashlib
import math
from numbers import Real
from pathlib import Path
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.core.jsonl import (
    StrictJsonlError,
    append_strict_jsonl,
    strict_json_loads_object,
)
from libreevolve.plugins.base import PluginBase

DEFAULT_MAX_PAYLOAD_FIELD_CHARS = 20_000
DEFAULT_MAX_PAYLOAD_TOTAL_CHARS = 40_000


class TTTRLPlugin(PluginBase):
    """ThetaEvolve-inspired GRPO training-data export.

    This accumulates examples only; it does not train an RL model.
    Source: arXiv 2511.23473. Hooks: on_evaluated, on_generation_end.
    Writes (prompt, response, reward) triples to grpo_data.jsonl.
    Override _maybe_train() to trigger real GRPO fine-tuning.
    """
    def __init__(
        self,
        train_every: int = 50,
        log_dir: str = "runs/",
        max_retained_examples: int = 500,
        max_payload_field_chars: int = DEFAULT_MAX_PAYLOAD_FIELD_CHARS,
        max_payload_total_chars: int = DEFAULT_MAX_PAYLOAD_TOTAL_CHARS,
    ):
        if isinstance(train_every, bool) or not isinstance(train_every, int) or train_every <= 0:
            raise ValueError("train_every must be a positive integer")
        if (
            isinstance(max_retained_examples, bool)
            or not isinstance(max_retained_examples, int)
            or max_retained_examples <= 0
        ):
            raise ValueError("max_retained_examples must be a positive integer")
        if (
            isinstance(max_payload_field_chars, bool)
            or not isinstance(max_payload_field_chars, int)
            or max_payload_field_chars <= 0
        ):
            raise ValueError("max_payload_field_chars must be a positive integer")
        if (
            isinstance(max_payload_total_chars, bool)
            or not isinstance(max_payload_total_chars, int)
            or max_payload_total_chars <= 0
        ):
            raise ValueError("max_payload_total_chars must be a positive integer")
        self._train_every = train_every
        self._log_dir = Path(log_dir)
        self._max_retained_examples = max_retained_examples
        self._max_payload_field_chars = max_payload_field_chars
        self._max_payload_total_chars = max_payload_total_chars
        self._data: list[dict] = []
        self._export_cursor = 0
        self._export_count = 0
        self._queued_count = 0
        self._skipped_malformed_examples = 0
        self._malformed_example_reasons: dict[str, int] = {}
        self._redacted_payload_examples = 0
        self._truncated_payload_examples = 0
        self._aggregate_truncated_payload_examples = 0
        self._redacted_payload_fields = 0
        self._truncated_payload_fields = 0
        self._payload_original_chars = 0
        self._payload_stored_chars = 0
        self._dropped_retained_examples = 0
        self._restored_export_count = 0
        self._restore_invalid_lines = 0
        self._last_export_path: Path | None = None
        self._last_quarantine_path: Path | None = None
        self._restore_existing_export_state()

    def on_evaluated(self, program, score: float) -> float:
        prompt = program.metadata.get("prompt")
        response = program.metadata.get("diff")
        if prompt or response:
            if not _is_non_empty_text(prompt) or not _is_non_empty_text(response):
                self._record_malformed_example("invalid_prompt_or_response")
                return score
            try:
                raw_score = _validated_score(score)
            except ValueError:
                self._record_malformed_example("invalid_score")
                raise
            payload = _sanitize_payload_pair(
                prompt,
                response,
                max_field_chars=self._max_payload_field_chars,
                max_total_chars=self._max_payload_total_chars,
            )
            self._record_payload_metadata(payload["metadata"])
            shaped_reward = max(0.0, raw_score)
            self._data.append({
                "prompt": payload["prompt"],
                "response": payload["response"],
                "raw_score": raw_score,
                "reward": shaped_reward,
                "reward_policy": "max(0.0, raw_score)",
            })
            self._queued_count += 1
            if self._pending_examples() > self._max_retained_examples:
                self._maybe_train()
        return score

    def on_generation_end(self, gen: int, best) -> None:
        if gen > 0 and gen % self._train_every == 0:
            self._maybe_train()

    def _maybe_train(self) -> None:
        batch = self._data[self._export_cursor:]
        if not batch: return
        out = self._log_dir / "grpo_data.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        quarantine = self._log_dir / "grpo_data_invalid.jsonl"
        self._last_export_path = out
        self._last_quarantine_path = quarantine
        for record in batch:
            append_strict_jsonl(out, record, quarantine_path=quarantine)
            self._export_cursor += 1
            self._export_count += 1
        self._prune_retained_examples()

    def get_training_data(self) -> list[dict]:
        return copy.deepcopy(self._data)

    def run_artifacts_metadata(self) -> dict:
        self._maybe_train()
        metadata = {
            "plugin": self.__class__.__name__,
            "reward_policy": "max(0.0, raw_score)",
            "queued_examples": self._queued_count,
            "retained_examples": len(self._data),
            "pending_examples": self._pending_examples(),
            "exported_examples": self._export_count,
            "skipped_malformed_examples": self._skipped_malformed_examples,
            "malformed_example_reasons": dict(sorted(self._malformed_example_reasons.items())),
            "redacted_payload_examples": self._redacted_payload_examples,
            "truncated_payload_examples": self._truncated_payload_examples,
            "aggregate_truncated_payload_examples": self._aggregate_truncated_payload_examples,
            "redacted_payload_fields": self._redacted_payload_fields,
            "truncated_payload_fields": self._truncated_payload_fields,
            "payload_original_chars": self._payload_original_chars,
            "payload_stored_chars": self._payload_stored_chars,
            "max_payload_field_chars": self._max_payload_field_chars,
            "max_payload_total_chars": self._max_payload_total_chars,
            "payload_policy": "redact_sensitive_text_then_truncate_field_and_total_chars",
            "max_retained_examples": self._max_retained_examples,
            "dropped_retained_examples": self._dropped_retained_examples,
            "retention_policy": "auto_export_pending_overflow_then_prune_exported_records",
            "finalization_policy": "flush_pending_examples_before_artifact_metadata",
            "restored_exported_examples": self._restored_export_count,
            "restore_invalid_lines": self._restore_invalid_lines,
            "restore_policy": "count_existing_grpo_jsonl_rows_without_reexport",
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

    def _pending_examples(self) -> int:
        return len(self._data) - self._export_cursor

    def _record_malformed_example(self, reason: str) -> None:
        self._skipped_malformed_examples += 1
        self._malformed_example_reasons[reason] = self._malformed_example_reasons.get(reason, 0) + 1

    def _record_payload_metadata(self, metadata: dict) -> None:
        redacted_fields = int(metadata["redacted_fields"])
        truncated_fields = int(metadata["truncated_fields"])
        self._redacted_payload_fields += redacted_fields
        self._truncated_payload_fields += truncated_fields
        self._payload_original_chars += int(metadata["original_chars"])
        self._payload_stored_chars += int(metadata["stored_chars"])
        if redacted_fields:
            self._redacted_payload_examples += 1
        if truncated_fields:
            self._truncated_payload_examples += 1
        if metadata["aggregate_truncated"]:
            self._aggregate_truncated_payload_examples += 1

    def _prune_retained_examples(self) -> None:
        excess = len(self._data) - self._max_retained_examples
        if excess <= 0:
            return
        removable = min(excess, self._export_cursor)
        if removable <= 0:
            return
        del self._data[:removable]
        self._export_cursor -= removable
        self._dropped_retained_examples += removable

    def _restore_existing_export_state(self) -> None:
        out = self._log_dir / "grpo_data.jsonl"
        quarantine = self._log_dir / "grpo_data_invalid.jsonl"
        if quarantine.exists():
            self._last_quarantine_path = quarantine
        if not out.exists():
            return
        self._last_export_path = out
        valid_rows = 0
        invalid_rows = 0
        with out.open("rb") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                try:
                    line = raw_line.decode("utf-8")
                except UnicodeDecodeError:
                    invalid_rows += 1
                    continue
                if not line.strip():
                    continue
                try:
                    record = strict_json_loads_object(
                        line,
                        source=f"grpo_data.jsonl at line {line_number}",
                    )
                except StrictJsonlError:
                    invalid_rows += 1
                    continue
                if _is_export_record(record):
                    valid_rows += 1
                else:
                    invalid_rows += 1
        self._restored_export_count = valid_rows
        self._restore_invalid_lines = invalid_rows
        self._export_count = valid_rows


def _is_non_empty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validated_score(score: object) -> float:
    if isinstance(score, bool) or not isinstance(score, Real):
        raise ValueError("TTTRLPlugin score must be a finite non-boolean number")
    numeric = float(score)
    if not math.isfinite(numeric):
        raise ValueError("TTTRLPlugin score must be a finite non-boolean number")
    return numeric


def _is_export_record(record: object) -> bool:
    if not isinstance(record, dict):
        return False
    if not isinstance(record.get("prompt"), str):
        return False
    if not isinstance(record.get("response"), str):
        return False
    if record.get("reward_policy") != "max(0.0, raw_score)":
        return False
    try:
        _validated_score(record.get("raw_score"))
        _validated_score(record.get("reward"))
    except ValueError:
        return False
    return True


def _sanitize_payload_pair(
    prompt: str,
    response: str,
    *,
    max_field_chars: int,
    max_total_chars: int,
) -> dict:
    original_prompt_chars = len(prompt)
    original_response_chars = len(response)
    sanitized_prompt, prompt_redacted = _redact_payload_field(prompt)
    sanitized_response, response_redacted = _redact_payload_field(response)
    sanitized_prompt, prompt_truncated = _truncate_text(sanitized_prompt, max_field_chars)
    sanitized_response, response_truncated = _truncate_text(sanitized_response, max_field_chars)

    combined = len(sanitized_prompt) + len(sanitized_response)
    aggregate_truncated = False
    if combined > max_total_chars:
        response_budget = max(0, max_total_chars - len(sanitized_prompt))
        if len(sanitized_response) > response_budget:
            sanitized_response, _ = _truncate_text(sanitized_response, response_budget)
            response_truncated = True
            aggregate_truncated = True
        combined = len(sanitized_prompt) + len(sanitized_response)
    if combined > max_total_chars:
        prompt_budget = max_total_chars
        sanitized_prompt, _ = _truncate_text(sanitized_prompt, prompt_budget)
        prompt_truncated = True
        aggregate_truncated = True
        response_budget = max(0, max_total_chars - len(sanitized_prompt))
        sanitized_response, _ = _truncate_text(sanitized_response, response_budget)
        response_truncated = True

    return {
        "prompt": sanitized_prompt,
        "response": sanitized_response,
        "metadata": {
            "redacted_fields": int(prompt_redacted) + int(response_redacted),
            "truncated_fields": int(prompt_truncated) + int(response_truncated),
            "aggregate_truncated": aggregate_truncated,
            "original_chars": original_prompt_chars + original_response_chars,
            "stored_chars": len(sanitized_prompt) + len(sanitized_response),
        },
    }


def _redact_payload_field(text: str) -> tuple[str, bool]:
    redacted = redact_sensitive_text(text)
    return redacted, redacted != text or "[REDACTED]" in redacted


def _truncate_text(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    marker = "...[truncated]"
    if limit <= len(marker):
        return text[:limit], True
    return text[: limit - len(marker)] + marker, True


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
