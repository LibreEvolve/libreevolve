"""Pure synchronous contracts used by the run-budget façade.

This module deliberately has no dependency on ``RunBudget``.  It validates
plain snapshot/event records and operates on the small method/attribute
surface needed to apply a validated controller event.  Clock acquisition,
configuration construction, persistence, provider accounting, and async
reservation behavior remain owned by :mod:`libreevolve.core.budget` and its
callers.
"""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from datetime import datetime
import math
import re
from typing import Any

STOP_REASONS = {
    "aborted",
    "completed",
    "max_evaluations",
    "max_evaluator_seconds",
    "max_evaluator_subprocess_attempts",
    "max_evaluator_stage_samples",
    "max_evaluator_retry_attempts",
    "max_evaluator_timeouts",
    "max_evaluator_sample_budget_exhaustions",
    "max_evaluator_stage_budget_exhaustions",
    "max_generations",
    "max_llm_calls",
    "max_llm_provider_attempts",
    "max_llm_tokens",
    "max_llm_cost_microusd",
    "max_llm_seconds",
    "llm_role_call_limits",
    "llm_role_provider_attempt_limits",
    "llm_role_token_limits",
    "llm_role_cost_microusd_limits",
    "llm_role_seconds_limits",
    "max_runtime_seconds",
    "invalid_initial_programs",
    "no_parent",
    "no_valid_programs",
}
CONTROLLER_BUDGET_STATE_SCHEMA = "libreevolve.controller_budget_state.v1"
CONTROLLER_BUDGET_EVENT_SCHEMA = "libreevolve.controller_budget_event.v1"
CONTROLLER_BUDGET_EVENT_KINDS = {
    "seed_evaluation",
    "candidate_evaluation",
    "candidate_evaluation_cache_hit",
    "llm_call",
    "generation_started",
    "generation_completed",
    "stop",
}

_BUDGET_LIMIT_FIELDS = {
    "max_generations": "int",
    "max_evaluations": "optional_int",
    "max_evaluator_seconds": "optional_number",
    "max_evaluator_subprocess_attempts": "optional_int",
    "max_evaluator_stage_samples": "optional_int",
    "max_evaluator_retry_attempts": "optional_int",
    "max_evaluator_timeouts": "optional_int",
    "max_evaluator_sample_budget_exhaustions": "optional_int",
    "max_evaluator_stage_budget_exhaustions": "optional_int",
    "max_llm_calls": "optional_int",
    "max_llm_provider_attempts": "optional_int",
    "max_llm_tokens": "optional_int",
    "max_llm_cost_microusd": "optional_int",
    "max_llm_seconds": "optional_number",
    "llm_role_provider_attempt_limits": "int_mapping",
    "llm_role_token_limits": "int_mapping",
    "llm_role_cost_microusd_limits": "int_mapping",
    "llm_role_seconds_limits": "number_mapping",
    "max_runtime_seconds": "optional_number",
}
_BUDGET_CONSUMED_INT_FIELDS = {
    "evaluations",
    "seed_evaluations",
    "candidate_evaluations",
    "evaluator_subprocess_attempts",
    "evaluator_stage_samples",
    "evaluator_retry_attempts",
    "evaluator_timeouts",
    "evaluator_sample_budget_exhaustions",
    "evaluator_stage_budget_exhaustions",
    "llm_calls",
    "llm_provider_attempts",
    "llm_tokens",
    "llm_cost_microusd",
    "generations_started",
    "generations_completed",
}
_BUDGET_CONSUMED_NUMBER_FIELDS = {
    "evaluator_seconds",
    "llm_seconds",
    "runtime_seconds",
}
_BUDGET_CONSUMED_MAP_FIELDS = {
    "llm_provider_attempts_by_role",
    "llm_tokens_by_role",
    "llm_cost_microusd_by_role",
}
_BUDGET_CONSUMED_NUMBER_MAP_FIELDS = {
    "llm_seconds_by_role",
}
_BUDGET_ROLE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")


class BudgetSnapshotError(ValueError):
    """Raised when a restored run-budget snapshot is malformed."""


def _first_exhausted_budget_limit(
    budget: Any,
    *,
    include_llm: bool = False,
    role: str | None = None,
    runtime_seconds: Callable[[], float] | None = None,
) -> str | None:
    """Return the first exhausted limit using the established precedence.

    ``runtime_seconds`` is a callback so callers can preserve lazy monotonic
    clock acquisition: the clock is consulted only after every earlier
    cumulative counter and role limit has been checked.
    """
    if budget.max_evaluations is not None and budget.evaluations >= budget.max_evaluations:
        return "max_evaluations"
    if (
        budget.max_evaluator_seconds is not None
        and budget.evaluator_seconds >= budget.max_evaluator_seconds
    ):
        return "max_evaluator_seconds"
    if (
        budget.max_evaluator_subprocess_attempts is not None
        and budget.evaluator_subprocess_attempts
        >= budget.max_evaluator_subprocess_attempts
    ):
        return "max_evaluator_subprocess_attempts"
    if (
        budget.max_evaluator_stage_samples is not None
        and budget.evaluator_stage_samples >= budget.max_evaluator_stage_samples
    ):
        return "max_evaluator_stage_samples"
    if (
        budget.max_evaluator_retry_attempts is not None
        and budget.evaluator_retry_attempts >= budget.max_evaluator_retry_attempts
    ):
        return "max_evaluator_retry_attempts"
    if (
        budget.max_evaluator_timeouts is not None
        and budget.evaluator_timeouts >= budget.max_evaluator_timeouts
    ):
        return "max_evaluator_timeouts"
    if (
        budget.max_evaluator_sample_budget_exhaustions is not None
        and budget.evaluator_sample_budget_exhaustions
        >= budget.max_evaluator_sample_budget_exhaustions
    ):
        return "max_evaluator_sample_budget_exhaustions"
    if (
        budget.max_evaluator_stage_budget_exhaustions is not None
        and budget.evaluator_stage_budget_exhaustions
        >= budget.max_evaluator_stage_budget_exhaustions
    ):
        return "max_evaluator_stage_budget_exhaustions"
    if (
        include_llm
        and budget.max_llm_calls is not None
        and budget.llm_calls >= budget.max_llm_calls
    ):
        return "max_llm_calls"
    if (
        include_llm
        and budget.max_llm_provider_attempts is not None
        and budget.llm_provider_attempts >= budget.max_llm_provider_attempts
    ):
        return "max_llm_provider_attempts"
    if (
        include_llm
        and budget.max_llm_tokens is not None
        and budget.llm_tokens >= budget.max_llm_tokens
    ):
        return "max_llm_tokens"
    if (
        include_llm
        and budget.max_llm_cost_microusd is not None
        and budget.llm_cost_microusd >= budget.max_llm_cost_microusd
    ):
        return "max_llm_cost_microusd"
    if (
        include_llm
        and budget.max_llm_seconds is not None
        and budget.llm_seconds >= budget.max_llm_seconds
    ):
        return "max_llm_seconds"
    if include_llm and _role_budget_exhausted(
        budget.llm_role_provider_attempt_limits,
        budget.llm_provider_attempts_by_role,
        role,
    ):
        return "llm_role_provider_attempt_limits"
    if include_llm and _role_budget_exhausted(
        budget.llm_role_token_limits,
        budget.llm_tokens_by_role,
        role,
    ):
        return "llm_role_token_limits"
    if include_llm and _role_budget_exhausted(
        budget.llm_role_cost_microusd_limits,
        budget.llm_cost_microusd_by_role,
        role,
    ):
        return "llm_role_cost_microusd_limits"
    if include_llm and _role_number_budget_exhausted(
        budget.llm_role_seconds_limits,
        budget.llm_seconds_by_role,
        role,
    ):
        return "llm_role_seconds_limits"
    if (
        budget.max_runtime_seconds is not None
        and runtime_seconds is not None
        and runtime_seconds() >= budget.max_runtime_seconds
    ):
        return "max_runtime_seconds"
    return None


def _validate_elapsed_seconds(elapsed_sec: object) -> float:
    if isinstance(elapsed_sec, bool) or not isinstance(elapsed_sec, (int, float)):
        raise ValueError("evaluation elapsed_sec must be a finite non-negative number")
    elapsed = float(elapsed_sec)
    if not math.isfinite(elapsed) or elapsed < 0.0:
        raise ValueError("evaluation elapsed_sec must be a finite non-negative number")
    return elapsed


def _validate_evaluator_accounting(accounting: object) -> dict:
    zero = {
        "subprocess_attempts": 0,
        "configured_stage_samples": 0,
        "retry_attempts": 0,
        "timeout_count": 0,
        "sample_budget_exhaustions": 0,
        "stage_budget_exhaustions": 0,
    }
    if accounting is None:
        return zero
    if not isinstance(accounting, dict):
        raise ValueError("evaluation accounting must be a mapping")
    validated = {}
    for key in zero:
        value = accounting.get(key, 0)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"evaluation accounting {key} must be a non-negative integer")
        validated[key] = value
    return validated


def validate_restored_budget_snapshot(snapshot: object) -> dict:
    """Validate a persisted runtime budget snapshot before future resume use."""
    if not isinstance(snapshot, dict):
        raise BudgetSnapshotError("restored budget snapshot must be a mapping")
    required = {"wall_clock", "limits", "consumed", "stop_reason"}
    missing = required - set(snapshot)
    if missing:
        raise BudgetSnapshotError(
            f"restored budget snapshot missing fields: {sorted(missing)}"
        )
    unsupported = set(snapshot) - required
    if unsupported:
        raise BudgetSnapshotError(
            f"restored budget snapshot has unsupported fields: {sorted(unsupported)}"
        )
    _validate_restored_wall_clock(snapshot["wall_clock"])
    _validate_restored_limits(snapshot["limits"])
    _validate_restored_consumed(snapshot["consumed"])
    try:
        _validate_stop_reason(snapshot["stop_reason"])
    except ValueError as exc:
        raise BudgetSnapshotError(f"restored budget snapshot stop_reason invalid: {exc}") from exc
    return deepcopy(snapshot)


def validate_controller_budget_state(state: object) -> dict:
    """Validate future controller/resume budget state before replay use."""
    if not isinstance(state, dict):
        raise BudgetSnapshotError("controller budget state must be a mapping")
    required = {"schema", "snapshot", "events"}
    missing = required - set(state)
    if missing:
        raise BudgetSnapshotError(
            f"controller budget state missing fields: {sorted(missing)}"
        )
    unsupported = set(state) - required
    if unsupported:
        raise BudgetSnapshotError(
            f"controller budget state has unsupported fields: {sorted(unsupported)}"
        )
    if state["schema"] != CONTROLLER_BUDGET_STATE_SCHEMA:
        raise BudgetSnapshotError("controller budget state schema is unsupported")
    snapshot = validate_restored_budget_snapshot(state["snapshot"])
    events = _validate_controller_budget_events(state["events"])
    return {
        "schema": state["schema"],
        "snapshot": snapshot,
        "events": events,
    }


def validate_controller_budget_event(event: object) -> dict:
    """Validate one durable controller budget event before counter mutation."""
    if not isinstance(event, dict):
        raise BudgetSnapshotError("controller budget event must be a mapping")
    if "schema" not in event:
        raise BudgetSnapshotError("controller budget event missing fields: ['schema']")
    if event["schema"] != CONTROLLER_BUDGET_EVENT_SCHEMA:
        raise BudgetSnapshotError("controller budget event schema is unsupported")
    if "kind" not in event:
        raise BudgetSnapshotError("controller budget event missing fields: ['kind']")
    kind = event["kind"]
    if kind not in CONTROLLER_BUDGET_EVENT_KINDS:
        raise BudgetSnapshotError(
            f"controller budget event kind must be one of {sorted(CONTROLLER_BUDGET_EVENT_KINDS)}"
        )
    if "sequence" not in event:
        raise BudgetSnapshotError("controller budget event missing fields: ['sequence']")
    try:
        sequence = _validate_non_negative_int(event["sequence"], "event.sequence")
    except ValueError as exc:
        raise BudgetSnapshotError(f"controller budget event invalid: {exc}") from exc
    if kind in {"seed_evaluation", "candidate_evaluation"}:
        required = {"schema", "sequence", "kind", "elapsed_sec", "accounting"}
        _validate_controller_event_required_fields(event, required)
        unsupported = set(event) - required
        if unsupported:
            raise BudgetSnapshotError(
                f"controller budget event has unsupported fields: {sorted(unsupported)}"
            )
        elapsed_sec = _validate_controller_event_elapsed(event["elapsed_sec"])
        accounting = _validate_controller_event_accounting(event["accounting"])
        return {
            "schema": event["schema"],
            "sequence": sequence,
            "kind": kind,
            "elapsed_sec": elapsed_sec,
            "accounting": accounting,
        }
    if kind == "candidate_evaluation_cache_hit":
        required = {
            "schema",
            "sequence",
            "kind",
            "cache_key_sha256",
            "workspace_sha256",
            "source_program_id",
        }
        _validate_controller_event_required_fields(event, required)
        unsupported = set(event) - required
        if unsupported:
            raise BudgetSnapshotError(
                f"controller budget event has unsupported fields: {sorted(unsupported)}"
            )
        try:
            cache_key = _validate_sha256(
                event["cache_key_sha256"], "event.cache_key_sha256"
            )
            workspace_hash = _validate_sha256(
                event["workspace_sha256"], "event.workspace_sha256"
            )
            source_program_id = _validate_event_text(
                event["source_program_id"], "event.source_program_id"
            )
        except ValueError as exc:
            raise BudgetSnapshotError(f"controller budget event invalid: {exc}") from exc
        return {
            "schema": event["schema"],
            "sequence": sequence,
            "kind": kind,
            "cache_key_sha256": cache_key,
            "workspace_sha256": workspace_hash,
            "source_program_id": source_program_id,
        }
    if kind == "llm_call":
        required = {"schema", "sequence", "kind"}
        optional = {
            "role",
            "provider_attempts",
            "tokens",
            "cost_microusd",
            "seconds",
        }
        _validate_controller_event_required_fields(event, required)
        unsupported = set(event) - required - optional
        if unsupported:
            raise BudgetSnapshotError(
                f"controller budget event has unsupported fields: {sorted(unsupported)}"
            )
        try:
            role = (
                _validate_role_label(event["role"], "event.role")
                if "role" in event
                else None
            )
            provider_attempts = _validate_non_negative_int(
                event.get("provider_attempts", 0),
                "event.provider_attempts",
            )
            tokens = _validate_non_negative_int(event.get("tokens", 0), "event.tokens")
            cost_microusd = _validate_non_negative_int(
                event.get("cost_microusd", 0),
                "event.cost_microusd",
            )
            seconds = _validate_non_negative_number(
                event.get("seconds", 0.0),
                "event.seconds",
            )
        except ValueError as exc:
            raise BudgetSnapshotError(f"controller budget event invalid: {exc}") from exc
        record = {
            "schema": event["schema"],
            "sequence": sequence,
            "kind": kind,
        }
        if role is not None:
            record["role"] = role
        if provider_attempts:
            record["provider_attempts"] = provider_attempts
        if tokens:
            record["tokens"] = tokens
        if cost_microusd:
            record["cost_microusd"] = cost_microusd
        if seconds:
            record["seconds"] = seconds
        return record
    if kind == "stop":
        required = {"schema", "sequence", "kind", "stop_reason"}
        _validate_controller_event_required_fields(event, required)
        unsupported = set(event) - required
        if unsupported:
            raise BudgetSnapshotError(
                f"controller budget event has unsupported fields: {sorted(unsupported)}"
            )
        try:
            stop_reason = _validate_stop_reason(event["stop_reason"])
        except ValueError as exc:
            raise BudgetSnapshotError(f"controller budget event invalid: {exc}") from exc
        if stop_reason is None:
            raise BudgetSnapshotError(
                "controller budget event invalid: stop_reason must not be null for stop events"
            )
        return {
            "schema": event["schema"],
            "sequence": sequence,
            "kind": kind,
            "stop_reason": stop_reason,
        }
    required = {"schema", "sequence", "kind"}
    _validate_controller_event_required_fields(event, required)
    unsupported = set(event) - required
    if unsupported:
        raise BudgetSnapshotError(
            f"controller budget event has unsupported fields: {sorted(unsupported)}"
        )
    return {
        "schema": event["schema"],
        "sequence": sequence,
        "kind": kind,
    }


def apply_controller_budget_event(budget: Any, event: object) -> dict:
    """Validate and apply one controller event to a synchronous budget object."""
    validated = validate_controller_budget_event(event)
    kind = validated["kind"]
    if kind == "seed_evaluation":
        budget.record_evaluation(
            validated["elapsed_sec"],
            seed=True,
            accounting=validated["accounting"],
        )
    elif kind == "candidate_evaluation":
        budget.record_evaluation(
            validated["elapsed_sec"],
            seed=False,
            accounting=validated["accounting"],
        )
    elif kind == "candidate_evaluation_cache_hit":
        pass
    elif kind == "llm_call":
        budget.record_llm_call()
        role = validated.get("role")
        if not isinstance(role, str):
            role = None
        budget.record_llm_provider_attempts(
            validated.get("provider_attempts", 0),
            role=role,
        )
        budget.record_llm_tokens(validated.get("tokens", 0), role=role)
        budget.record_llm_cost_microusd(
            validated.get("cost_microusd", 0),
            role=role,
        )
        budget.record_llm_seconds(validated.get("seconds", 0.0), role=role)
    elif kind == "generation_started":
        budget.record_generation_start()
    elif kind == "generation_completed":
        budget.record_generation_complete()
    elif kind == "stop":
        budget.stop_reason = validated["stop_reason"]
        _validate_budget_state(budget)
    else:  # pragma: no cover - validate_controller_budget_event guards this.
        raise BudgetSnapshotError(f"unsupported controller budget event kind {kind!r}")
    return validated


def _validate_restored_wall_clock(value: object) -> None:
    if not isinstance(value, dict):
        raise BudgetSnapshotError("restored budget wall_clock must be a mapping")
    required = {
        "schema",
        "started_at",
        "updated_at",
        "runtime_seconds_source",
        "clock",
        "monotonic_budget_clock",
        "resume_segments",
    }
    optional = {"finished_at"}
    missing = required - set(value)
    if missing:
        raise BudgetSnapshotError(
            f"restored budget wall_clock missing fields: {sorted(missing)}"
        )
    unsupported = set(value) - required - optional
    if unsupported:
        raise BudgetSnapshotError(
            f"restored budget wall_clock has unsupported fields: {sorted(unsupported)}"
        )
    if value["schema"] != "utc_run_timestamps_v1":
        raise BudgetSnapshotError("restored budget wall_clock schema is unsupported")
    if value["runtime_seconds_source"] != "consumed.runtime_seconds":
        raise BudgetSnapshotError(
            "restored budget wall_clock runtime_seconds_source is unsupported"
        )
    if value["clock"] != "UTC wall clock":
        raise BudgetSnapshotError("restored budget wall_clock clock is unsupported")
    if value["monotonic_budget_clock"] != "time.monotonic":
        raise BudgetSnapshotError(
            "restored budget wall_clock monotonic_budget_clock is unsupported"
        )
    _validate_restored_utc(value["started_at"], "wall_clock.started_at")
    _validate_restored_utc(value["updated_at"], "wall_clock.updated_at")
    if "finished_at" in value:
        _validate_restored_utc(value["finished_at"], "wall_clock.finished_at")
    segments = value["resume_segments"]
    if not isinstance(segments, list) or not segments:
        raise BudgetSnapshotError("restored budget wall_clock.resume_segments must be a non-empty list")
    for index, segment in enumerate(segments):
        _validate_restored_resume_segment(segment, index)


def _validate_restored_resume_segment(segment: object, index: int) -> None:
    if not isinstance(segment, dict):
        raise BudgetSnapshotError(
            f"restored budget wall_clock.resume_segments[{index}] must be a mapping"
        )
    required = {"segment_index", "kind", "started_at", "updated_at"}
    optional = {"finished_at"}
    missing = required - set(segment)
    if missing:
        raise BudgetSnapshotError(
            "restored budget wall_clock.resume_segments"
            f"[{index}] missing fields: {sorted(missing)}"
        )
    unsupported = set(segment) - required - optional
    if unsupported:
        raise BudgetSnapshotError(
            "restored budget wall_clock.resume_segments"
            f"[{index}] has unsupported fields: {sorted(unsupported)}"
        )
    if segment["segment_index"] != index:
        raise BudgetSnapshotError(
            "restored budget wall_clock.resume_segments"
            f"[{index}].segment_index must equal {index}"
        )
    if not isinstance(segment["kind"], str) or not segment["kind"].strip():
        raise BudgetSnapshotError(
            "restored budget wall_clock.resume_segments"
            f"[{index}].kind must be non-empty text"
        )
    _validate_restored_utc(
        segment["started_at"],
        f"wall_clock.resume_segments[{index}].started_at",
    )
    _validate_restored_utc(
        segment["updated_at"],
        f"wall_clock.resume_segments[{index}].updated_at",
    )
    if "finished_at" in segment:
        _validate_restored_utc(
            segment["finished_at"],
            f"wall_clock.resume_segments[{index}].finished_at",
        )


def _validate_restored_limits(value: object) -> None:
    if not isinstance(value, dict):
        raise BudgetSnapshotError("restored budget limits must be a mapping")
    required = set(_BUDGET_LIMIT_FIELDS)
    missing = required - set(value)
    if missing:
        raise BudgetSnapshotError(f"restored budget limits missing fields: {sorted(missing)}")
    unsupported = set(value) - required
    if unsupported:
        raise BudgetSnapshotError(
            f"restored budget limits has unsupported fields: {sorted(unsupported)}"
        )
    for field, kind in _BUDGET_LIMIT_FIELDS.items():
        try:
            if kind == "int":
                _validate_non_negative_int(value[field], f"limits.{field}")
            elif kind == "optional_int":
                _validate_optional_non_negative_int(value[field], f"limits.{field}")
            elif kind == "int_mapping":
                _validate_role_counter_limit_mapping(value[field], f"limits.{field}")
            elif kind == "number_mapping":
                _validate_role_number_limit_mapping(value[field], f"limits.{field}")
            else:
                _validate_optional_non_negative_number(value[field], f"limits.{field}")
        except ValueError as exc:
            raise BudgetSnapshotError(f"restored budget snapshot invalid: {exc}") from exc


def _validate_restored_consumed(value: object) -> None:
    if not isinstance(value, dict):
        raise BudgetSnapshotError("restored budget consumed must be a mapping")
    required = (
        _BUDGET_CONSUMED_INT_FIELDS
        | _BUDGET_CONSUMED_NUMBER_FIELDS
        | _BUDGET_CONSUMED_MAP_FIELDS
        | _BUDGET_CONSUMED_NUMBER_MAP_FIELDS
    )
    missing = required - set(value)
    if missing:
        raise BudgetSnapshotError(
            f"restored budget consumed missing fields: {sorted(missing)}"
        )
    unsupported = set(value) - required
    if unsupported:
        raise BudgetSnapshotError(
            f"restored budget consumed has unsupported fields: {sorted(unsupported)}"
        )
    for field in sorted(_BUDGET_CONSUMED_INT_FIELDS):
        try:
            _validate_non_negative_int(value[field], f"consumed.{field}")
        except ValueError as exc:
            raise BudgetSnapshotError(f"restored budget snapshot invalid: {exc}") from exc
    for field in sorted(_BUDGET_CONSUMED_NUMBER_FIELDS):
        try:
            _validate_non_negative_number(value[field], f"consumed.{field}")
        except ValueError as exc:
            raise BudgetSnapshotError(f"restored budget snapshot invalid: {exc}") from exc
    for field in sorted(_BUDGET_CONSUMED_MAP_FIELDS):
        try:
            _validate_role_counter_mapping(value[field], f"consumed.{field}")
        except ValueError as exc:
            raise BudgetSnapshotError(f"restored budget snapshot invalid: {exc}") from exc
    for field in sorted(_BUDGET_CONSUMED_NUMBER_MAP_FIELDS):
        try:
            _validate_role_number_mapping(value[field], f"consumed.{field}")
        except ValueError as exc:
            raise BudgetSnapshotError(f"restored budget snapshot invalid: {exc}") from exc
    if value["seed_evaluations"] + value["candidate_evaluations"] != value["evaluations"]:
        raise BudgetSnapshotError(
            "restored budget snapshot invalid: seed and candidate evaluation "
            "counters must sum to consumed.evaluations"
        )
    if value["generations_completed"] > value["generations_started"]:
        raise BudgetSnapshotError(
            "restored budget snapshot invalid: consumed.generations_completed "
            "must be <= consumed.generations_started"
        )


def _validate_controller_budget_events(value: object) -> list[dict]:
    if not isinstance(value, list):
        raise BudgetSnapshotError("controller budget state events must be a list")
    events = []
    for index, event in enumerate(value):
        validated = validate_controller_budget_event(event)
        if validated["sequence"] != index:
            raise BudgetSnapshotError(
                "controller budget state events must have contiguous sequence "
                f"numbers starting at 0; event {index} has sequence {validated['sequence']}"
            )
        events.append(validated)
    return events


def _validate_controller_event_required_fields(
    event: dict, required: set[str]
) -> None:
    missing = required - set(event)
    if missing:
        raise BudgetSnapshotError(
            f"controller budget event missing fields: {sorted(missing)}"
        )


def _validate_controller_event_elapsed(value: object) -> float:
    try:
        return _validate_elapsed_seconds(value)
    except ValueError as exc:
        raise BudgetSnapshotError(f"controller budget event invalid: {exc}") from exc


def _validate_controller_event_accounting(value: object) -> dict:
    try:
        return _validate_evaluator_accounting(value)
    except ValueError as exc:
        raise BudgetSnapshotError(f"controller budget event invalid: {exc}") from exc


def _validate_restored_utc(value: object, field: str) -> None:
    try:
        _validate_utc_timestamp(value, field)
    except ValueError as exc:
        raise BudgetSnapshotError(f"restored budget snapshot invalid: {exc}") from exc


def _validate_budget_state(budget: Any) -> None:
    _validate_non_negative_int(budget.max_generations, "max_generations")
    _validate_optional_non_negative_int(budget.max_evaluations, "max_evaluations")
    _validate_optional_non_negative_number(
        budget.max_evaluator_seconds,
        "max_evaluator_seconds",
    )
    _validate_optional_non_negative_int(
        budget.max_evaluator_subprocess_attempts,
        "max_evaluator_subprocess_attempts",
    )
    _validate_optional_non_negative_int(
        budget.max_evaluator_stage_samples,
        "max_evaluator_stage_samples",
    )
    _validate_optional_non_negative_int(
        budget.max_evaluator_retry_attempts,
        "max_evaluator_retry_attempts",
    )
    _validate_optional_non_negative_int(
        budget.max_evaluator_timeouts,
        "max_evaluator_timeouts",
    )
    _validate_optional_non_negative_int(
        budget.max_evaluator_sample_budget_exhaustions,
        "max_evaluator_sample_budget_exhaustions",
    )
    _validate_optional_non_negative_int(
        budget.max_evaluator_stage_budget_exhaustions,
        "max_evaluator_stage_budget_exhaustions",
    )
    _validate_optional_non_negative_int(budget.max_llm_calls, "max_llm_calls")
    _validate_optional_non_negative_int(
        budget.max_llm_provider_attempts,
        "max_llm_provider_attempts",
    )
    _validate_optional_non_negative_int(budget.max_llm_tokens, "max_llm_tokens")
    _validate_optional_non_negative_int(
        budget.max_llm_cost_microusd,
        "max_llm_cost_microusd",
    )
    _validate_optional_non_negative_number(
        budget.max_llm_seconds,
        "max_llm_seconds",
    )
    _validate_role_counter_limit_mapping(
        budget.llm_role_provider_attempt_limits,
        "llm_role_provider_attempt_limits",
    )
    _validate_role_counter_limit_mapping(
        budget.llm_role_token_limits,
        "llm_role_token_limits",
    )
    _validate_role_counter_limit_mapping(
        budget.llm_role_cost_microusd_limits,
        "llm_role_cost_microusd_limits",
    )
    _validate_role_number_limit_mapping(
        budget.llm_role_seconds_limits,
        "llm_role_seconds_limits",
    )
    _validate_optional_non_negative_number(
        budget.max_runtime_seconds,
        "max_runtime_seconds",
    )
    _validate_non_negative_number(budget.started_at, "started_at")
    _validate_utc_timestamp(budget.started_at_utc, "started_at_utc")
    _validate_non_negative_int(budget.evaluations, "evaluations")
    _validate_non_negative_int(budget.seed_evaluations, "seed_evaluations")
    _validate_non_negative_int(budget.candidate_evaluations, "candidate_evaluations")
    if budget.seed_evaluations + budget.candidate_evaluations != budget.evaluations:
        raise ValueError("seed and candidate evaluation counters must sum to evaluations")
    _validate_non_negative_number(budget.evaluator_seconds, "evaluator_seconds")
    _validate_non_negative_int(
        budget.evaluator_subprocess_attempts,
        "evaluator_subprocess_attempts",
    )
    _validate_non_negative_int(budget.evaluator_stage_samples, "evaluator_stage_samples")
    _validate_non_negative_int(budget.evaluator_retry_attempts, "evaluator_retry_attempts")
    _validate_non_negative_int(budget.evaluator_timeouts, "evaluator_timeouts")
    _validate_non_negative_int(
        budget.evaluator_sample_budget_exhaustions,
        "evaluator_sample_budget_exhaustions",
    )
    _validate_non_negative_int(
        budget.evaluator_stage_budget_exhaustions,
        "evaluator_stage_budget_exhaustions",
    )
    _validate_non_negative_int(budget.llm_calls, "llm_calls")
    _validate_non_negative_int(budget.llm_provider_attempts, "llm_provider_attempts")
    _validate_non_negative_int(budget.llm_tokens, "llm_tokens")
    _validate_non_negative_int(budget.llm_cost_microusd, "llm_cost_microusd")
    _validate_non_negative_number(budget.llm_seconds, "llm_seconds")
    _validate_role_counter_mapping(
        budget.llm_provider_attempts_by_role,
        "llm_provider_attempts_by_role",
    )
    _validate_role_counter_mapping(budget.llm_tokens_by_role, "llm_tokens_by_role")
    _validate_role_counter_mapping(
        budget.llm_cost_microusd_by_role,
        "llm_cost_microusd_by_role",
    )
    _validate_role_number_mapping(budget.llm_seconds_by_role, "llm_seconds_by_role")
    _validate_non_negative_int(budget.generations_started, "generations_started")
    _validate_non_negative_int(budget.generations_completed, "generations_completed")
    if budget.generations_completed > budget.generations_started:
        raise ValueError("generations_completed must be <= generations_started")
    _validate_stop_reason(budget.stop_reason)
    _validate_non_negative_number(budget.prior_runtime_seconds, "prior_runtime_seconds")
    if not isinstance(budget.prior_resume_segments, list):
        raise ValueError("prior_resume_segments must be a list")
    for index, segment in enumerate(budget.prior_resume_segments):
        try:
            _validate_restored_resume_segment(segment, index)
        except BudgetSnapshotError as exc:
            raise ValueError(f"prior_resume_segments invalid: {exc}") from exc
    if budget.run_started_at_utc is not None:
        _validate_utc_timestamp(budget.run_started_at_utc, "run_started_at_utc")


def _validate_non_negative_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _validate_optional_non_negative_int(value: object, field: str) -> int | None:
    if value is None:
        return None
    return _validate_non_negative_int(value, field)


def _validate_role_label(value: object, field: str) -> str:
    if not isinstance(value, str) or _BUDGET_ROLE_RE.fullmatch(value) is None:
        raise ValueError(f"{field} must be a manifest-safe role label")
    return value


def _validate_sha256(value: object, field: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(ch not in "0123456789abcdef" for ch in value)
    ):
        raise ValueError(f"{field} must be a lowercase SHA-256 hex digest")
    return value


def _validate_event_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be non-empty text")
    if len(value) > 256:
        raise ValueError(f"{field} must be <= 256 characters")
    return value


def _validate_role_scope_label(value: object, field: str) -> str:
    if isinstance(value, str) and value.endswith(":*"):
        _validate_role_label(value[:-2], field)
        return value
    return _validate_role_label(value, field)


def _validate_role_counter_mapping(value: object, field: str) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a mapping")
    normalized = {}
    for raw_role, raw_count in value.items():
        role = _validate_role_label(raw_role, f"{field} key")
        normalized[role] = _validate_non_negative_int(raw_count, f"{field}[{role}]")
    return dict(sorted(normalized.items()))


def _validate_role_counter_limit_mapping(value: object, field: str) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a mapping")
    normalized = {}
    for raw_role, raw_count in value.items():
        role = _validate_role_scope_label(raw_role, f"{field} key")
        normalized[role] = _validate_non_negative_int(raw_count, f"{field}[{role}]")
    return dict(sorted(normalized.items()))


def _validate_role_number_mapping(value: object, field: str) -> dict[str, float]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a mapping")
    normalized = {}
    for raw_role, raw_count in value.items():
        role = _validate_role_label(raw_role, f"{field} key")
        normalized[role] = _validate_non_negative_number(
            raw_count,
            f"{field}[{role}]",
        )
    return dict(sorted(normalized.items()))


def _validate_role_number_limit_mapping(value: object, field: str) -> dict[str, float]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a mapping")
    normalized = {}
    for raw_role, raw_count in value.items():
        role = _validate_role_scope_label(raw_role, f"{field} key")
        normalized[role] = _validate_non_negative_number(
            raw_count,
            f"{field}[{role}]",
        )
    return dict(sorted(normalized.items()))


def _role_counter_copy(value: object) -> dict[str, int]:
    return _validate_role_counter_limit_mapping(value, "role counter")


def _role_number_copy(value: object) -> dict[str, float]:
    return _validate_role_number_limit_mapping(value, "role number")


def _increment_role_counter(
    budget: Any,
    field_name: str,
    role: str | None,
    delta: int,
) -> None:
    if role is None or delta <= 0:
        return
    role = _validate_role_label(role, "llm role")
    counters = _validate_role_counter_mapping(getattr(budget, field_name), field_name)
    counters[role] = counters.get(role, 0) + delta
    setattr(budget, field_name, dict(sorted(counters.items())))


def _increment_role_number(
    budget: Any,
    field_name: str,
    role: str | None,
    delta: float,
) -> None:
    if role is None or delta <= 0.0:
        return
    role = _validate_role_label(role, "llm role")
    counters = _validate_role_number_mapping(getattr(budget, field_name), field_name)
    counters[role] = counters.get(role, 0.0) + delta
    setattr(budget, field_name, dict(sorted(counters.items())))


def _role_budget_exhausted(
    limits: object,
    consumed: object,
    role: str | None,
) -> bool:
    if role is not None:
        role = _validate_role_label(role, "llm role")
    limit_map = _validate_role_counter_limit_mapping(limits, "role limits")
    consumed_map = _validate_role_counter_mapping(consumed, "role consumed")
    for scope, limit in limit_map.items():
        if role is not None and not _role_scope_matches(scope, role):
            continue
        if _role_scope_consumed(consumed_map, scope) >= limit:
            return True
    return False


def _role_number_budget_exhausted(
    limits: object,
    consumed: object,
    role: str | None,
) -> bool:
    if role is not None:
        role = _validate_role_label(role, "llm role")
    limit_map = _validate_role_number_limit_mapping(limits, "role limits")
    consumed_map = _validate_role_number_mapping(consumed, "role consumed")
    for scope, limit in limit_map.items():
        if role is not None and not _role_scope_matches(scope, role):
            continue
        if _role_scope_consumed(consumed_map, scope) >= limit:
            return True
    return False


def _role_scope_matches(scope: str, role: str) -> bool:
    if scope.endswith(":*"):
        return role.startswith(scope[:-1])
    return scope == role


def _role_scope_consumed(
    consumed: dict[str, int] | dict[str, float],
    scope: str,
) -> int | float:
    if scope.endswith(":*"):
        return sum(value for role, value in consumed.items() if _role_scope_matches(scope, role))
    return consumed.get(scope, 0)


def _validate_non_negative_number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a finite non-negative number")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0.0:
        raise ValueError(f"{field} must be a finite non-negative number")
    return numeric


def _validate_optional_non_negative_number(value: object, field: str) -> float | None:
    if value is None:
        return None
    return _validate_non_negative_number(value, field)


def _validate_utc_timestamp(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp ending in Z")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(
            f"{field} must be an ISO-8601 UTC timestamp ending in Z"
        ) from exc
    return value


def _validate_stop_reason(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or value not in STOP_REASONS:
        raise ValueError(f"stop_reason must be one of {sorted(STOP_REASONS)}")
    return value
