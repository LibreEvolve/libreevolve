from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

from libreevolve.core.artifact_schema import (
    ARTIFACT_SCHEMA_VERSION,
    PROMPT_HISTORY_RECORD_SCHEMA,
    versioned_record,
)
from libreevolve.core.jsonl import (
    StrictJsonlError,
    append_quarantine_record,
    append_strict_jsonl,
    iter_strict_jsonl_objects,
    strict_json_dumps,
)
from libreevolve.core.prompt import DEFAULT_TEMPLATE, PromptTemplateError, prompt_context_policy_sha256, validate_configured_prompt_template_semantics, validate_prompt_context_policy, validate_prompt_template, validate_prompt_variant_semantic_policy
from libreevolve.core.redaction import redact_sensitive_text

_PROMPT_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
_PROMPT_REWARD_MODES = {"absolute", "improvement"}
_PROMPT_METADATA_KEY_CHARS = 160
_PROMPT_METADATA_STRING_CHARS = 1000


class PromptHistoryReplayError(ValueError):
    """Raised when prompt_history.jsonl cannot be replayed safely."""


@dataclass
class PromptProgram:
    template: str
    context_policy: dict = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid4().hex)
    parent_id: str | None = None
    generation: int = 0
    uses: int = 0
    reward_sum: float = 0.0
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.context_policy = validate_prompt_context_policy(self.context_policy)
        validate_prompt_program(self)

    @property
    def mean_reward(self) -> float:
        return self.reward_sum / self.uses if self.uses else 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "template": self.template,
            "template_sha256": _template_sha256(self.template),
            "context_policy": deepcopy(validate_prompt_context_policy(self.context_policy)),
            "context_policy_sha256": prompt_context_policy_sha256(self.context_policy),
            "parent_id": self.parent_id,
            "generation": self.generation,
            "uses": self.uses,
            "reward_sum": self.reward_sum,
            "mean_reward": self.mean_reward,
            "metadata": deepcopy(self.metadata),
        }


class PromptDatabase:
    """Small evolutionary database for prompt templates.

    This is intentionally local and deterministic. It gives prompt instructions
    identity, lineage, selection, scoring, and append-only logs so future
    mutation strategies can evolve prompts without changing the rest of the
    loop.
    """

    def __init__(
        self,
        log_dir: str | Path,
        templates: list[str] | None = None,
        reward_bounds: tuple[float, float] = (0.0, 1.0),
        explore_coeff: float = 1.0,
        reward_mode: str = "absolute",
        seed_semantic_policy: str = "compatibility",
        quarantine_snapshot_retention_mode: str = "redacted",
    ):
        self._programs: dict[str, PromptProgram] = {}
        self._log_path = Path(log_dir) / "prompt_history.jsonl"
        self._quarantine_path = Path(log_dir) / "prompt_history_invalid.jsonl"
        self._reward_bounds = _validate_reward_bounds(reward_bounds)
        self._explore_coeff = _validate_explore_coeff(explore_coeff)
        self._reward_mode = _validate_reward_mode(reward_mode)
        self._quarantine_snapshot_retention_mode = quarantine_snapshot_retention_mode
        self._seed_semantic_policy = validate_prompt_variant_semantic_policy(
            seed_semantic_policy
        )
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        if self._log_path.exists() and self._log_path.stat().st_size > 0:
            self._restore_from_history()
        else:
            seed_templates = templates or [DEFAULT_TEMPLATE]
            for index, template in enumerate(seed_templates):
                validate_configured_prompt_template_semantics(
                    template,
                    semantic_policy=self._seed_semantic_policy,
                )
                self.add(
                    PromptProgram(
                        template=template,
                        id=_deterministic_seed_prompt_id(index, template),
                        metadata={"source": "seed", "seed_index": index},
                    )
                )

    def add(self, program: PromptProgram) -> PromptProgram:
        validate_prompt_program(program)
        validate_prompt_template(program.template)
        if program.id in self._programs:
            message = f"duplicate prompt program id: {program.id!r}"
            self._write_reference_error(
                "add",
                program.id,
                message,
                generation=program.generation,
                reward=None,
                template=program.template,
                metadata=program.metadata,
            )
            raise StrictJsonlError(
                f"Duplicate prompt program id for prompt add: {program.id!r}"
            )
        if program.parent_id is not None and program.parent_id not in self._programs:
            message = f"unknown parent prompt program id: {program.parent_id!r}"
            self._write_reference_error(
                "add",
                program.id,
                message,
                generation=program.generation,
                parent_id=program.parent_id,
                reward=None,
                template=program.template,
                metadata=program.metadata,
            )
            raise StrictJsonlError(
                f"Unknown parent prompt program id for prompt add: {program.parent_id!r}"
            )
        snapshot = _copy_prompt_program(program)
        snapshot.context_policy = validate_prompt_context_policy(snapshot.context_policy)
        snapshot.metadata = _validate_prompt_metadata(program.metadata, "prompt program metadata")
        self._write("add", snapshot)
        self._programs[snapshot.id] = snapshot
        return _copy_prompt_program(snapshot)

    def select(self) -> PromptProgram:
        untried = [p for p in self._programs.values() if p.uses == 0]
        if untried:
            return _copy_prompt_program(untried[0])
        total = sum(p.uses for p in self._programs.values())
        return _copy_prompt_program(max(
            self._programs.values(),
            key=lambda p: p.mean_reward
            + self._explore_coeff * math.sqrt(math.log(total + 1) / p.uses),
        ))

    def record_result(self, prompt_id: str, reward: float, metadata: dict | None = None) -> None:
        program = self._get_program(
            prompt_id,
            "score",
            reward=reward,
            metadata=metadata,
        )
        validate_prompt_program(program)
        previous_uses = program.uses
        previous_reward_sum = program.reward_sum
        previous_metadata = dict(program.metadata)
        try:
            normalized = self._normalize_reward(reward)
        except ValueError as exc:
            record = {"event": "score", "prompt_id": prompt_id, "reward": reward}
            if metadata is not None:
                record["metadata"] = metadata
            append_quarantine_record(
                self._quarantine_path,
                record,
                exc,
                retention_mode=self._quarantine_snapshot_retention_mode,
            )
            raise StrictJsonlError(
                f"Could not record prompt reward for {prompt_id}: {exc}"
            ) from exc
        try:
            validated_metadata = (
                _validate_prompt_metadata(metadata, "prompt reward metadata")
                if metadata is not None
                else None
            )
        except ValueError as exc:
            append_quarantine_record(
                self._quarantine_path,
                {
                    "event": "score",
                    "prompt_id": prompt_id,
                    "reward": reward,
                    "metadata": metadata,
                },
                exc,
                retention_mode=self._quarantine_snapshot_retention_mode,
            )
            raise StrictJsonlError(
                f"Could not record prompt reward metadata for {prompt_id}: {exc}"
            ) from exc
        program.uses += 1
        program.reward_sum += normalized
        if validated_metadata:
            program.metadata.update(validated_metadata)
        program.metadata["last_prompt_reward"] = {
            "mode": self._reward_mode,
            "raw": reward,
            "normalized": normalized,
            "bounds": [self._reward_bounds[0], self._reward_bounds[1]],
        }
        try:
            self._write("score", program)
        except Exception:
            program.uses = previous_uses
            program.reward_sum = previous_reward_sum
            program.metadata = previous_metadata
            raise


    def all(self) -> list[PromptProgram]:
        return [_copy_prompt_program(program) for program in self._programs.values()]

    def _restore_from_history(self) -> None:
        restored: dict[str, PromptProgram] = {}
        records = load_prompt_history_records(self._log_path)
        if not records:
            return
        for line_number, record in enumerate(records, start=1):
            event = record.get("event")
            if event not in {"add", "score", "penalty"}:
                raise PromptHistoryReplayError(
                    "Malformed prompt_history.jsonl at line "
                    f"{line_number}: unsupported replay event {event!r}"
                )
            program = _program_from_history_record(record, line_number)
            _validate_prompt_reward_policy_compatibility(
                program,
                line_number,
                reward_mode=self._reward_mode,
                reward_bounds=self._reward_bounds,
            )
            if event == "add":
                if program.id in restored:
                    raise PromptHistoryReplayError(
                        "Malformed prompt_history.jsonl at line "
                        f"{line_number}: duplicate prompt program id {program.id!r}"
                    )
                if program.parent_id is not None and program.parent_id not in restored:
                    raise PromptHistoryReplayError(
                        "Malformed prompt_history.jsonl at line "
                        f"{line_number}: unknown parent prompt program id {program.parent_id!r}"
                    )
                restored[program.id] = program
                continue
            previous = restored.get(program.id)
            if previous is None:
                raise PromptHistoryReplayError(
                    "Malformed prompt_history.jsonl at line "
                    f"{line_number}: {event} references unknown prompt program id {program.id!r}"
                )
            _validate_prompt_history_update(previous, program, line_number, event)
            restored[program.id] = program
        self._programs = restored

    def _get_program(
        self,
        prompt_id: str,
        operation: str,
        *,
        generation: int | None = None,
        reward: float | None = None,
        template: str | None = None,
        metadata: dict | None = None,
    ) -> PromptProgram:
        try:
            safe_prompt_id = _validate_prompt_id(prompt_id, "prompt program id")
        except ValueError as exc:
            self._write_reference_error(
                operation,
                prompt_id,
                str(exc),
                generation=generation,
                reward=reward,
                template=template,
                metadata=metadata,
            )
            raise StrictJsonlError(
                f"Invalid prompt program id for prompt {operation}: {exc}"
            ) from exc
        try:
            return self._programs[safe_prompt_id]
        except KeyError as exc:
            message = f"unknown prompt program id: {safe_prompt_id!r}"
            self._write_reference_error(
                operation,
                safe_prompt_id,
                message,
                generation=generation,
                reward=reward,
                template=template,
                metadata=metadata,
            )
            raise StrictJsonlError(
                f"Unknown prompt program id for prompt {operation}: {safe_prompt_id!r}"
            ) from exc

    def _normalize_reward(self, reward: float) -> float:
        if isinstance(reward, bool) or not isinstance(reward, (int, float)):
            raise ValueError("prompt reward must be numeric")
        value = float(reward)
        if not math.isfinite(value):
            raise ValueError(f"prompt reward must be finite: {reward!r}")
        lo, hi = self._reward_bounds
        normalized = (value - lo) / (hi - lo)
        return max(0.0, min(1.0, normalized))

    def _write(self, event: str, program: PromptProgram) -> None:
        append_strict_jsonl(
            self._log_path,
            versioned_record(
                PROMPT_HISTORY_RECORD_SCHEMA,
                {"event": event, "program": program.to_dict()},
            ),
            quarantine_path=self._quarantine_path,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )

    def _write_reference_error(
        self,
        operation: str,
        prompt_id: object,
        error: str,
        *,
        generation: int | None,
        reward: float | None,
        template: str | None,
        metadata: dict | None,
        parent_id: object | None = None,
    ) -> None:
        record = {
            "event": "prompt_reference_error",
            "operation": operation,
            "prompt_id": _bounded_redacted_repr(prompt_id),
            "error": error,
        }
        if generation is not None:
            record["generation"] = _bounded_redacted_repr(generation)
        if parent_id is not None:
            record["parent_id"] = _bounded_redacted_repr(parent_id)
        if reward is not None:
            record["reward"] = _bounded_redacted_repr(reward)
        if template is not None:
            record["template"] = _bounded_redacted_text(template)
        if metadata is not None:
            record["metadata"] = _bounded_redacted_repr(metadata)
        append_strict_jsonl(
            self._quarantine_path,
            record,
            quarantine_path=self._quarantine_path,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )


def validate_prompt_program(program: PromptProgram) -> None:
    validate_prompt_template(program.template)
    validate_prompt_context_policy(program.context_policy)
    _validate_prompt_id(program.id, "prompt program id")
    if program.parent_id is not None:
        _validate_prompt_id(program.parent_id, "parent prompt program id")
    _validate_generation(program.generation, "prompt program generation")
    _validate_uses(program.uses, "prompt program uses")
    _validate_reward_sum(program.reward_sum, "prompt program reward_sum")
    _validate_prompt_metadata(program.metadata, "prompt program metadata")


def load_prompt_history_records(path: str | Path) -> list[dict]:
    records: list[dict] = []
    try:
        for line_number, record in enumerate(
            iter_strict_jsonl_objects(Path(path), stream_name="prompt_history.jsonl"),
            start=1,
        ):
            _validate_prompt_history_schema(record, line_number)
            records.append(deepcopy(record))
    except StrictJsonlError as exc:
        raise PromptHistoryReplayError(str(exc)) from exc
    return records


def _validate_prompt_history_schema(record: dict, line_number: int) -> None:
    schema_version = record.get("schema_version")
    record_schema = record.get("record_schema")
    if schema_version is None and record_schema is None:
        return
    if schema_version != ARTIFACT_SCHEMA_VERSION:
        raise PromptHistoryReplayError(
            "Malformed prompt_history.jsonl at line "
            f"{line_number}: unsupported schema_version {schema_version!r}"
        )
    if record_schema != PROMPT_HISTORY_RECORD_SCHEMA:
        raise PromptHistoryReplayError(
            "Malformed prompt_history.jsonl at line "
            f"{line_number}: unsupported record_schema {record_schema!r}"
        )


def _program_from_history_record(record: dict, line_number: int) -> PromptProgram:
    raw_program = record.get("program")
    if not isinstance(raw_program, dict):
        raise PromptHistoryReplayError(
            f"Malformed prompt_history.jsonl at line {line_number}: program must be a mapping"
        )
    try:
        program = PromptProgram(
            template=raw_program["template"],
            context_policy=raw_program.get("context_policy", {}),
            id=raw_program["id"],
            parent_id=raw_program.get("parent_id"),
            generation=raw_program.get("generation", 0),
            uses=raw_program.get("uses", 0),
            reward_sum=raw_program.get("reward_sum", 0.0),
            metadata=raw_program.get("metadata", {}),
        )
    except KeyError as exc:
        raise PromptHistoryReplayError(
            f"Malformed prompt_history.jsonl at line {line_number}: program missing {exc.args[0]!r}"
        ) from exc
    except (PromptTemplateError, ValueError) as exc:
        raise PromptHistoryReplayError(
            f"Malformed prompt_history.jsonl at line {line_number}: {exc}"
        ) from exc
    template_hash = raw_program.get("template_sha256")
    if template_hash is not None and template_hash != _template_sha256(program.template):
        raise PromptHistoryReplayError(
            "Malformed prompt_history.jsonl at line "
            f"{line_number}: template_sha256 does not match template"
        )
    context_policy_hash = raw_program.get("context_policy_sha256")
    if (
        context_policy_hash is not None
        and context_policy_hash != prompt_context_policy_sha256(program.context_policy)
    ):
        raise PromptHistoryReplayError(
            "Malformed prompt_history.jsonl at line "
            f"{line_number}: context_policy_sha256 does not match context_policy"
        )
    mean_reward = raw_program.get("mean_reward")
    if mean_reward is not None:
        expected = program.mean_reward
        if (
            isinstance(mean_reward, bool)
            or not isinstance(mean_reward, (int, float))
            or not math.isfinite(float(mean_reward))
            or not math.isclose(float(mean_reward), expected, rel_tol=0.0, abs_tol=1e-12)
        ):
            raise PromptHistoryReplayError(
                "Malformed prompt_history.jsonl at line "
                f"{line_number}: mean_reward is inconsistent"
            )
    return program


def _validate_prompt_history_update(
    previous: PromptProgram,
    current: PromptProgram,
    line_number: int,
    event: str,
) -> None:
    if current.template != previous.template:
        raise PromptHistoryReplayError(
            f"Malformed prompt_history.jsonl at line {line_number}: {event} changed template"
        )
    if current.context_policy != previous.context_policy:
        raise PromptHistoryReplayError(
            "Malformed prompt_history.jsonl at line "
            f"{line_number}: {event} changed context_policy"
        )
    if current.parent_id != previous.parent_id:
        raise PromptHistoryReplayError(
            f"Malformed prompt_history.jsonl at line {line_number}: {event} changed parent_id"
        )
    if current.generation != previous.generation:
        raise PromptHistoryReplayError(
            f"Malformed prompt_history.jsonl at line {line_number}: {event} changed generation"
        )
    if current.uses < previous.uses:
        raise PromptHistoryReplayError(
            f"Malformed prompt_history.jsonl at line {line_number}: {event} decreased uses"
        )
    if current.reward_sum < previous.reward_sum:
        raise PromptHistoryReplayError(
            f"Malformed prompt_history.jsonl at line {line_number}: {event} decreased reward_sum"
        )


def _validate_prompt_reward_policy_compatibility(
    program: PromptProgram,
    line_number: int,
    *,
    reward_mode: str,
    reward_bounds: tuple[float, float],
) -> None:
    metadata = program.metadata
    for field in ("last_prompt_reward", "last_prompt_penalty"):
        policy = metadata.get(field)
        if policy is None:
            continue
        if not isinstance(policy, dict):
            raise PromptHistoryReplayError(
                f"Malformed prompt_history.jsonl at line {line_number}: {field} must be a mapping"
            )
        if policy.get("mode") != reward_mode:
            raise PromptHistoryReplayError(
                "Malformed prompt_history.jsonl at line "
                f"{line_number}: prompt reward mode is incompatible with restored history"
            )
        if policy.get("bounds") != [reward_bounds[0], reward_bounds[1]]:
            raise PromptHistoryReplayError(
                "Malformed prompt_history.jsonl at line "
                f"{line_number}: prompt reward bounds are incompatible with restored history"
            )


def _copy_prompt_program(program: PromptProgram) -> PromptProgram:
    return PromptProgram(
        template=program.template,
        context_policy=deepcopy(program.context_policy),
        id=program.id,
        parent_id=program.parent_id,
        generation=program.generation,
        uses=program.uses,
        reward_sum=program.reward_sum,
        metadata=deepcopy(program.metadata),
    )


def _validate_prompt_id(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a manifest-safe prompt id")
    if redact_sensitive_text(value) != value:
        raise ValueError(f"{label} must be a manifest-safe prompt id")
    if _PROMPT_ID_RE.fullmatch(value) is None:
        raise ValueError(f"{label} must be a manifest-safe prompt id")
    return value


def _validate_generation(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer")
    return value


def _validate_uses(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer")
    return value


def _validate_reward_sum(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{label} must be a finite number")
    return numeric


def _validate_prompt_metadata(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON-safe mapping")
    try:
        normalized = json.loads(strict_json_dumps(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be JSON-safe: {exc}") from exc
    return _sanitize_prompt_metadata_mapping(normalized, label)


def _sanitize_prompt_metadata_mapping(value: dict, label: str) -> dict:
    sanitized: dict = {}
    for key, item in value.items():
        safe_key = _safe_prompt_metadata_key(key)
        if safe_key in sanitized:
            safe_key = _metadata_key_with_hash(key, key, _PROMPT_METADATA_KEY_CHARS)
        sanitized[safe_key] = _sanitize_prompt_metadata_value(item, f"{label}.{safe_key}")
    return sanitized


def _sanitize_prompt_metadata_value(value: object, label: str) -> object:
    if isinstance(value, dict):
        return _sanitize_prompt_metadata_mapping(value, label)
    if isinstance(value, list):
        return [
            _sanitize_prompt_metadata_value(item, f"{label}[{index}]")
            for index, item in enumerate(value)
        ]
    if isinstance(value, str):
        if _has_unicode_format_control(value):
            raise ValueError(f"{label} must be a display-safe metadata value")
        return _bounded_redacted_text(value, _PROMPT_METADATA_STRING_CHARS)
    return value


def _safe_prompt_metadata_key(key: str) -> str:
    if _has_unicode_format_control(key):
        raise ValueError(f"{key!r} must be a display-safe metadata label")
    redacted = redact_sensitive_text(key)
    bounded = _bounded_metadata_key(redacted)
    if bounded != key:
        return _metadata_key_with_hash(redacted, key, _PROMPT_METADATA_KEY_CHARS)
    return bounded


def _has_unicode_format_control(value: str) -> bool:
    return any(unicodedata.category(ch) == "Cf" for ch in value)


def _bounded_metadata_key(key: str) -> str:
    if len(key) <= _PROMPT_METADATA_KEY_CHARS:
        return key
    return key[: _PROMPT_METADATA_KEY_CHARS - 15] + "...<truncated>"


def _metadata_key_with_hash(label: str, hash_source: str, max_length: int) -> str:
    digest = hashlib.sha256(hash_source.encode("utf-8")).hexdigest()[:12]
    suffix = f"#sha256:{digest}"
    base_limit = max(1, max_length - len(suffix))
    base = label if len(label) <= base_limit else label[: base_limit]
    return base + suffix


def _validate_reward_bounds(bounds: object) -> tuple[float, float]:
    if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
        raise ValueError("prompt reward_bounds must be [lo, hi]")
    lo = _validate_reward_bound(bounds[0], "prompt reward_bounds[0]")
    hi = _validate_reward_bound(bounds[1], "prompt reward_bounds[1]")
    if lo >= hi:
        raise ValueError("prompt reward_bounds must be strictly increasing [lo, hi]")
    return (lo, hi)


def _validate_reward_bound(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{label} must be a finite number")
    return numeric


def _validate_explore_coeff(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("prompt explore_coeff must be a finite non-negative number")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0.0:
        raise ValueError("prompt explore_coeff must be a finite non-negative number")
    return numeric


def _validate_reward_mode(value: object) -> str:
    if not isinstance(value, str) or value not in _PROMPT_REWARD_MODES:
        raise ValueError(f"prompt reward_mode must be one of {sorted(_PROMPT_REWARD_MODES)}")
    return value


def _bounded_redacted_repr(value: object, max_length: int = 500) -> str:
    try:
        text = repr(value)
    except Exception as exc:  # pragma: no cover - caller-controlled repr failure
        text = f"<repr failed: {exc.__class__.__name__}>"
    return _bounded_redacted_text(text, max_length=max_length)


def _bounded_redacted_text(value: str, max_length: int = 500) -> str:
    text = redact_sensitive_text(value)
    if len(text) > max_length:
        suffix = "...<truncated>"
        return text[: max_length - len(suffix)] + suffix
    return text


def _template_sha256(template: str) -> str:
    return hashlib.sha256(template.encode("utf-8")).hexdigest()


def _deterministic_seed_prompt_id(index: int, template: str) -> str:
    digest = _template_sha256(template)[:16]
    return f"prompt-seed-{index}-{digest}"
