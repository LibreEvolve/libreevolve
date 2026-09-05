from __future__ import annotations

from collections.abc import Mapping
import time
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone

from libreevolve.core.budget_contract import (
    CONTROLLER_BUDGET_EVENT_KINDS as _CONTRACT_CONTROLLER_BUDGET_EVENT_KINDS,
    CONTROLLER_BUDGET_EVENT_SCHEMA as _CONTRACT_CONTROLLER_BUDGET_EVENT_SCHEMA,
    CONTROLLER_BUDGET_STATE_SCHEMA as _CONTRACT_CONTROLLER_BUDGET_STATE_SCHEMA,
    STOP_REASONS as _CONTRACT_STOP_REASONS,
    BudgetSnapshotError as _ContractBudgetSnapshotError,
    _BUDGET_CONSUMED_INT_FIELDS as _CONTRACT_BUDGET_CONSUMED_INT_FIELDS,
    _BUDGET_CONSUMED_MAP_FIELDS as _CONTRACT_BUDGET_CONSUMED_MAP_FIELDS,
    _BUDGET_CONSUMED_NUMBER_FIELDS as _CONTRACT_BUDGET_CONSUMED_NUMBER_FIELDS,
    _BUDGET_CONSUMED_NUMBER_MAP_FIELDS as _CONTRACT_BUDGET_CONSUMED_NUMBER_MAP_FIELDS,
    _BUDGET_LIMIT_FIELDS as _CONTRACT_BUDGET_LIMIT_FIELDS,
    _BUDGET_ROLE_RE as _CONTRACT_BUDGET_ROLE_RE,
    apply_controller_budget_event as _contract_apply_controller_budget_event,
    _first_exhausted_budget_limit as _first_exhausted_budget_limit,
    _increment_role_counter as _increment_role_counter,
    _increment_role_number as _increment_role_number,
    _role_budget_exhausted as _role_budget_exhausted,
    _role_counter_copy as _role_counter_copy,
    _role_number_budget_exhausted as _role_number_budget_exhausted,
    _role_number_copy as _role_number_copy,
    _role_scope_consumed as _role_scope_consumed,
    _role_scope_matches as _role_scope_matches,
    _validate_budget_state as _validate_budget_state,
    _validate_controller_budget_events as _validate_controller_budget_events,
    _validate_controller_event_accounting as _validate_controller_event_accounting,
    _validate_controller_event_elapsed as _validate_controller_event_elapsed,
    _validate_controller_event_required_fields as _validate_controller_event_required_fields,
    _validate_elapsed_seconds as _validate_elapsed_seconds,
    _validate_evaluator_accounting as _validate_evaluator_accounting,
    _validate_event_text as _validate_event_text,
    _validate_non_negative_int as _validate_non_negative_int,
    _validate_non_negative_number as _validate_non_negative_number,
    _validate_optional_non_negative_int as _validate_optional_non_negative_int,
    _validate_optional_non_negative_number as _validate_optional_non_negative_number,
    _validate_restored_resume_segment as _validate_restored_resume_segment,
    _validate_restored_consumed as _validate_restored_consumed,
    _validate_restored_limits as _validate_restored_limits,
    _validate_restored_utc as _validate_restored_utc,
    _validate_restored_wall_clock as _validate_restored_wall_clock,
    _validate_role_counter_limit_mapping as _validate_role_counter_limit_mapping,
    _validate_role_counter_mapping as _validate_role_counter_mapping,
    _validate_role_label as _validate_role_label,
    _validate_role_number_limit_mapping as _validate_role_number_limit_mapping,
    _validate_role_number_mapping as _validate_role_number_mapping,
    _validate_role_scope_label as _validate_role_scope_label,
    _validate_sha256 as _validate_sha256,
    _validate_stop_reason as _validate_stop_reason,
    _validate_utc_timestamp as _validate_utc_timestamp,
    validate_controller_budget_event as _contract_validate_controller_budget_event,
    validate_controller_budget_state as _contract_validate_controller_budget_state,
    validate_restored_budget_snapshot as _contract_validate_restored_budget_snapshot,
)

from libreevolve.core.config import Config

STOP_REASONS = _CONTRACT_STOP_REASONS
CONTROLLER_BUDGET_STATE_SCHEMA = _CONTRACT_CONTROLLER_BUDGET_STATE_SCHEMA
CONTROLLER_BUDGET_EVENT_SCHEMA = _CONTRACT_CONTROLLER_BUDGET_EVENT_SCHEMA
CONTROLLER_BUDGET_EVENT_KINDS = _CONTRACT_CONTROLLER_BUDGET_EVENT_KINDS
_BUDGET_LIMIT_FIELDS = _CONTRACT_BUDGET_LIMIT_FIELDS
_BUDGET_CONSUMED_INT_FIELDS = _CONTRACT_BUDGET_CONSUMED_INT_FIELDS
_BUDGET_CONSUMED_NUMBER_FIELDS = _CONTRACT_BUDGET_CONSUMED_NUMBER_FIELDS
_BUDGET_CONSUMED_MAP_FIELDS = _CONTRACT_BUDGET_CONSUMED_MAP_FIELDS
_BUDGET_CONSUMED_NUMBER_MAP_FIELDS = _CONTRACT_BUDGET_CONSUMED_NUMBER_MAP_FIELDS
_BUDGET_ROLE_RE = _CONTRACT_BUDGET_ROLE_RE
BudgetSnapshotError = _ContractBudgetSnapshotError


@dataclass
class RunBudget:
    """Synchronous run budget accounting.

    This tracks local loop consumption only. Resumable pending-work queues
    remain a separate runtime concern.
    """

    max_generations: int
    max_evaluations: int | None
    max_evaluator_seconds: float | None
    max_runtime_seconds: float | None
    started_at: float
    started_at_utc: str
    max_evaluator_subprocess_attempts: int | None = None
    max_evaluator_stage_samples: int | None = None
    max_evaluator_retry_attempts: int | None = None
    max_evaluator_timeouts: int | None = None
    max_evaluator_sample_budget_exhaustions: int | None = None
    max_evaluator_stage_budget_exhaustions: int | None = None
    max_llm_calls: int | None = None
    max_llm_provider_attempts: int | None = None
    max_llm_tokens: int | None = None
    max_llm_cost_microusd: int | None = None
    max_llm_seconds: float | None = None
    llm_role_provider_attempt_limits: dict[str, int] = field(default_factory=dict)
    llm_role_token_limits: dict[str, int] = field(default_factory=dict)
    llm_role_cost_microusd_limits: dict[str, int] = field(default_factory=dict)
    llm_role_seconds_limits: dict[str, float] = field(default_factory=dict)
    evaluations: int = 0
    seed_evaluations: int = 0
    candidate_evaluations: int = 0
    evaluator_seconds: float = 0.0
    evaluator_subprocess_attempts: int = 0
    evaluator_stage_samples: int = 0
    evaluator_retry_attempts: int = 0
    evaluator_timeouts: int = 0
    evaluator_sample_budget_exhaustions: int = 0
    evaluator_stage_budget_exhaustions: int = 0
    llm_calls: int = 0
    llm_provider_attempts: int = 0
    llm_tokens: int = 0
    llm_cost_microusd: int = 0
    llm_seconds: float = 0.0
    llm_provider_attempts_by_role: dict[str, int] = field(default_factory=dict)
    llm_tokens_by_role: dict[str, int] = field(default_factory=dict)
    llm_cost_microusd_by_role: dict[str, int] = field(default_factory=dict)
    llm_seconds_by_role: dict[str, float] = field(default_factory=dict)
    generations_started: int = 0
    generations_completed: int = 0
    stop_reason: str | None = None
    prior_runtime_seconds: float = 0.0
    prior_resume_segments: list[dict] = field(default_factory=list)
    run_started_at_utc: str | None = None

    @classmethod
    def from_config(cls, config: Config) -> "RunBudget":
        return cls(
            max_generations=config.max_generations,
            max_evaluations=config.max_evaluations,
            max_evaluator_seconds=config.max_evaluator_seconds,
            max_runtime_seconds=config.max_runtime_seconds,
            started_at=time.monotonic(),
            started_at_utc=_utc_timestamp(),
            max_evaluator_subprocess_attempts=config.max_evaluator_subprocess_attempts,
            max_evaluator_stage_samples=config.max_evaluator_stage_samples,
            max_evaluator_retry_attempts=config.max_evaluator_retry_attempts,
            max_evaluator_timeouts=config.max_evaluator_timeouts,
            max_evaluator_sample_budget_exhaustions=(
                config.max_evaluator_sample_budget_exhaustions
            ),
            max_evaluator_stage_budget_exhaustions=(
                config.max_evaluator_stage_budget_exhaustions
            ),
            max_llm_calls=config.max_llm_calls,
            max_llm_provider_attempts=config.max_llm_provider_attempts,
            max_llm_tokens=config.max_llm_tokens,
            max_llm_cost_microusd=config.max_llm_cost_microusd,
            max_llm_seconds=config.max_llm_seconds,
            llm_role_provider_attempt_limits=dict(
                config.llm_role_provider_attempt_limits
            ),
            llm_role_token_limits=dict(config.llm_role_token_limits),
            llm_role_cost_microusd_limits=dict(
                config.llm_role_cost_microusd_limits
            ),
            llm_role_seconds_limits=dict(config.llm_role_seconds_limits),
        )

    @classmethod
    def from_restored_snapshot(cls, config: Config, snapshot: object) -> "RunBudget":
        restored = validate_restored_budget_snapshot(snapshot)
        budget = cls.from_config(config)
        restored_limits = restored["limits"]
        current_limits = budget.snapshot()["limits"]
        if restored_limits != current_limits:
            raise BudgetSnapshotError(
                "restored budget limits must match the effective run configuration"
            )
        consumed = restored["consumed"]
        budget.evaluations = consumed["evaluations"]
        budget.seed_evaluations = consumed["seed_evaluations"]
        budget.candidate_evaluations = consumed["candidate_evaluations"]
        budget.evaluator_seconds = consumed["evaluator_seconds"]
        budget.evaluator_subprocess_attempts = consumed["evaluator_subprocess_attempts"]
        budget.evaluator_stage_samples = consumed["evaluator_stage_samples"]
        budget.evaluator_retry_attempts = consumed["evaluator_retry_attempts"]
        budget.evaluator_timeouts = consumed["evaluator_timeouts"]
        budget.evaluator_sample_budget_exhaustions = consumed[
            "evaluator_sample_budget_exhaustions"
        ]
        budget.evaluator_stage_budget_exhaustions = consumed[
            "evaluator_stage_budget_exhaustions"
        ]
        budget.llm_calls = consumed["llm_calls"]
        budget.llm_provider_attempts = consumed["llm_provider_attempts"]
        budget.llm_tokens = consumed["llm_tokens"]
        budget.llm_cost_microusd = consumed["llm_cost_microusd"]
        budget.llm_seconds = consumed["llm_seconds"]
        budget.llm_provider_attempts_by_role = dict(
            consumed["llm_provider_attempts_by_role"]
        )
        budget.llm_tokens_by_role = dict(consumed["llm_tokens_by_role"])
        budget.llm_cost_microusd_by_role = dict(
            consumed["llm_cost_microusd_by_role"]
        )
        budget.llm_seconds_by_role = dict(consumed["llm_seconds_by_role"])
        budget.generations_started = consumed["generations_started"]
        budget.generations_completed = consumed["generations_completed"]
        budget.prior_runtime_seconds = consumed["runtime_seconds"]
        budget.prior_resume_segments = deepcopy(
            restored["wall_clock"]["resume_segments"]
        )
        budget.run_started_at_utc = restored["wall_clock"]["started_at"]
        budget.stop_reason = None
        _validate_budget_state(budget)
        return budget

    def check_before_generation(self) -> str | None:
        return self._check_limits()

    def check_before_evaluation(self) -> str | None:
        return self._check_limits()

    def check_before_llm_call(self, *, role: str | None = None) -> str | None:
        return self._check_limits(include_llm=True, role=role)

    def remaining_runtime_seconds(self) -> float | None:
        _validate_budget_state(self)
        if self.max_runtime_seconds is None:
            return None
        return max(0.0, self.max_runtime_seconds - self._runtime_seconds())

    def record_generation_start(self) -> None:
        _validate_non_negative_int(self.generations_started, "generations_started")
        self.generations_started += 1

    def record_generation_complete(self) -> None:
        _validate_non_negative_int(self.generations_completed, "generations_completed")
        self.generations_completed += 1

    def record_llm_call(self) -> None:
        _validate_non_negative_int(self.llm_calls, "llm_calls")
        self.llm_calls += 1

    def record_llm_provider_attempts(self, attempts: int, *, role: str | None = None) -> None:
        _validate_non_negative_int(self.llm_provider_attempts, "llm_provider_attempts")
        delta = _validate_non_negative_int(
            attempts,
            "llm_provider_attempts",
        )
        self.llm_provider_attempts += delta
        _increment_role_counter(
            self,
            "llm_provider_attempts_by_role",
            role,
            delta,
        )

    def record_llm_tokens(self, tokens: int, *, role: str | None = None) -> None:
        _validate_non_negative_int(self.llm_tokens, "llm_tokens")
        delta = _validate_non_negative_int(tokens, "llm_tokens")
        self.llm_tokens += delta
        _increment_role_counter(self, "llm_tokens_by_role", role, delta)

    def record_llm_cost_microusd(
        self,
        cost_microusd: int,
        *,
        role: str | None = None,
    ) -> None:
        _validate_non_negative_int(self.llm_cost_microusd, "llm_cost_microusd")
        delta = _validate_non_negative_int(
            cost_microusd,
            "llm_cost_microusd",
        )
        self.llm_cost_microusd += delta
        _increment_role_counter(self, "llm_cost_microusd_by_role", role, delta)

    def record_llm_seconds(
        self,
        seconds: float,
        *,
        role: str | None = None,
    ) -> None:
        _validate_non_negative_number(self.llm_seconds, "llm_seconds")
        delta = _validate_non_negative_number(seconds, "llm_seconds")
        self.llm_seconds += delta
        _increment_role_number(self, "llm_seconds_by_role", role, delta)

    def record_evaluation(
        self,
        elapsed_sec: float,
        *,
        seed: bool,
        accounting: dict | None = None,
    ) -> None:
        if not isinstance(seed, bool):
            raise ValueError("evaluation seed flag must be boolean")
        elapsed = _validate_elapsed_seconds(elapsed_sec)
        evaluator_accounting = _validate_evaluator_accounting(accounting)
        self.evaluations += 1
        if seed:
            self.seed_evaluations += 1
        else:
            self.candidate_evaluations += 1
        self.evaluator_seconds += elapsed
        self.evaluator_subprocess_attempts += evaluator_accounting["subprocess_attempts"]
        self.evaluator_stage_samples += evaluator_accounting["configured_stage_samples"]
        self.evaluator_retry_attempts += evaluator_accounting["retry_attempts"]
        self.evaluator_timeouts += evaluator_accounting["timeout_count"]
        self.evaluator_sample_budget_exhaustions += evaluator_accounting[
            "sample_budget_exhaustions"
        ]
        self.evaluator_stage_budget_exhaustions += evaluator_accounting[
            "stage_budget_exhaustions"
        ]

    def finish(self, best_found: bool) -> dict:
        _validate_budget_state(self)
        if self.stop_reason is None:
            self.stop_reason = self._check_limits(include_llm=True)
        if self.stop_reason is None:
            if not best_found:
                self.stop_reason = "no_valid_programs"
            elif self.generations_completed >= self.max_generations:
                self.stop_reason = "max_generations"
            else:
                self.stop_reason = "completed"
        return self.snapshot()

    def snapshot(self) -> dict:
        _validate_budget_state(self)
        updated_at = _utc_timestamp()
        segments = deepcopy(self.prior_resume_segments)
        current_segment_index = len(segments)
        current_segment = {
            "segment_index": current_segment_index,
            "kind": "resumed_process" if segments else "initial_process",
            "started_at": self.started_at_utc,
            "updated_at": updated_at,
        }
        if self.stop_reason is not None:
            current_segment["finished_at"] = updated_at
        segments.append(current_segment)
        wall_clock = {
            "schema": "utc_run_timestamps_v1",
            "started_at": self.run_started_at_utc or self.started_at_utc,
            "updated_at": updated_at,
            "runtime_seconds_source": "consumed.runtime_seconds",
            "clock": "UTC wall clock",
            "monotonic_budget_clock": "time.monotonic",
            "resume_segments": segments,
        }
        if self.stop_reason is not None:
            wall_clock["finished_at"] = updated_at
        return {
            "wall_clock": wall_clock,
            "limits": {
                "max_generations": self.max_generations,
                "max_evaluations": self.max_evaluations,
                "max_evaluator_seconds": self.max_evaluator_seconds,
                "max_evaluator_subprocess_attempts": (
                    self.max_evaluator_subprocess_attempts
                ),
                "max_evaluator_stage_samples": self.max_evaluator_stage_samples,
                "max_evaluator_retry_attempts": self.max_evaluator_retry_attempts,
                "max_evaluator_timeouts": self.max_evaluator_timeouts,
                "max_evaluator_sample_budget_exhaustions": (
                    self.max_evaluator_sample_budget_exhaustions
                ),
                "max_evaluator_stage_budget_exhaustions": (
                    self.max_evaluator_stage_budget_exhaustions
                ),
                "max_llm_calls": self.max_llm_calls,
                "max_llm_provider_attempts": self.max_llm_provider_attempts,
                "max_llm_tokens": self.max_llm_tokens,
                "max_llm_cost_microusd": self.max_llm_cost_microusd,
                "max_llm_seconds": self.max_llm_seconds,
                "llm_role_provider_attempt_limits": _role_counter_copy(
                    self.llm_role_provider_attempt_limits
                ),
                "llm_role_token_limits": _role_counter_copy(
                    self.llm_role_token_limits
                ),
                "llm_role_cost_microusd_limits": _role_counter_copy(
                    self.llm_role_cost_microusd_limits
                ),
                "llm_role_seconds_limits": _role_number_copy(
                    self.llm_role_seconds_limits
                ),
                "max_runtime_seconds": self.max_runtime_seconds,
            },
            "consumed": {
                "evaluations": self.evaluations,
                "seed_evaluations": self.seed_evaluations,
                "candidate_evaluations": self.candidate_evaluations,
                "evaluator_seconds": self.evaluator_seconds,
                "evaluator_subprocess_attempts": self.evaluator_subprocess_attempts,
                "evaluator_stage_samples": self.evaluator_stage_samples,
                "evaluator_retry_attempts": self.evaluator_retry_attempts,
                "evaluator_timeouts": self.evaluator_timeouts,
                "evaluator_sample_budget_exhaustions": (
                    self.evaluator_sample_budget_exhaustions
                ),
                "evaluator_stage_budget_exhaustions": (
                    self.evaluator_stage_budget_exhaustions
                ),
                "llm_calls": self.llm_calls,
                "llm_provider_attempts": self.llm_provider_attempts,
                "llm_tokens": self.llm_tokens,
                "llm_cost_microusd": self.llm_cost_microusd,
                "llm_seconds": self.llm_seconds,
                "llm_provider_attempts_by_role": _role_counter_copy(
                    self.llm_provider_attempts_by_role
                ),
                "llm_tokens_by_role": _role_counter_copy(self.llm_tokens_by_role),
                "llm_cost_microusd_by_role": _role_counter_copy(
                    self.llm_cost_microusd_by_role
                ),
                "llm_seconds_by_role": _role_number_copy(self.llm_seconds_by_role),
                "runtime_seconds": self._runtime_seconds(),
                "generations_started": self.generations_started,
                "generations_completed": self.generations_completed,
            },
            "stop_reason": self.stop_reason,
        }

    def _runtime_seconds(self) -> float:
        return self.prior_runtime_seconds + max(0.0, time.monotonic() - self.started_at)

    def _check_limits(
        self,
        *,
        include_llm: bool = False,
        role: str | None = None,
    ) -> str | None:
        _validate_budget_state(self)
        if self.stop_reason is not None:
            return self.stop_reason
        reason = _first_exhausted_budget_limit(
            self,
            include_llm=include_llm,
            role=role,
            runtime_seconds=self._runtime_seconds,
        )
        if reason is not None:
            self.stop_reason = reason
        return self.stop_reason


def validate_controller_budget_replay_state(state: object) -> dict:
    """Validate that controller budget events replay to the persisted snapshot."""
    validated = validate_controller_budget_state(state)
    snapshot = validated["snapshot"]
    budget = _budget_for_controller_event_replay(snapshot)
    for event in validated["events"]:
        apply_controller_budget_event(budget, event)
    replayed_snapshot = budget.snapshot()
    _validate_controller_budget_replay_matches_snapshot(replayed_snapshot, snapshot)
    return {
        "schema": validated["schema"],
        "snapshot": snapshot,
        "events": validated["events"],
        "replay": {
            "status": "matched_snapshot",
            "event_count": len(validated["events"]),
            "runtime_seconds_policy": "manifest_snapshot_authoritative",
        },
    }

def _budget_for_controller_event_replay(snapshot: Mapping[str, object]) -> RunBudget:
    limits = snapshot["limits"]
    wall_clock = snapshot["wall_clock"]
    if not isinstance(limits, Mapping) or not isinstance(wall_clock, Mapping):
        raise BudgetSnapshotError("controller budget replay snapshot is malformed")
    started_at_utc = wall_clock["started_at"]
    if not isinstance(started_at_utc, str):
        raise BudgetSnapshotError("controller budget replay started_at is malformed")
    return RunBudget(
        max_generations=limits["max_generations"],
        max_evaluations=limits["max_evaluations"],
        max_evaluator_seconds=limits["max_evaluator_seconds"],
        max_runtime_seconds=limits["max_runtime_seconds"],
        started_at=0.0,
        started_at_utc=started_at_utc,
        max_evaluator_subprocess_attempts=limits["max_evaluator_subprocess_attempts"],
        max_evaluator_stage_samples=limits["max_evaluator_stage_samples"],
        max_evaluator_retry_attempts=limits["max_evaluator_retry_attempts"],
        max_evaluator_timeouts=limits["max_evaluator_timeouts"],
        max_evaluator_sample_budget_exhaustions=(
            limits["max_evaluator_sample_budget_exhaustions"]
        ),
        max_evaluator_stage_budget_exhaustions=(
            limits["max_evaluator_stage_budget_exhaustions"]
        ),
        max_llm_calls=limits["max_llm_calls"],
        max_llm_provider_attempts=limits["max_llm_provider_attempts"],
        max_llm_tokens=limits["max_llm_tokens"],
        max_llm_cost_microusd=limits["max_llm_cost_microusd"],
        max_llm_seconds=limits["max_llm_seconds"],
        llm_role_provider_attempt_limits=dict(
            limits["llm_role_provider_attempt_limits"]
        ),
        llm_role_token_limits=dict(limits["llm_role_token_limits"]),
        llm_role_cost_microusd_limits=dict(
            limits["llm_role_cost_microusd_limits"]
        ),
        llm_role_seconds_limits=dict(limits["llm_role_seconds_limits"]),
    )

def _validate_controller_budget_replay_matches_snapshot(
    replayed_snapshot: Mapping[str, object],
    snapshot: Mapping[str, object],
) -> None:
    if replayed_snapshot["limits"] != snapshot["limits"]:
        raise BudgetSnapshotError(
            "controller budget replay limits do not match budget snapshot"
        )
    if replayed_snapshot["stop_reason"] != snapshot["stop_reason"]:
        raise BudgetSnapshotError(
            "controller budget replay stop_reason does not match budget snapshot"
        )
    replayed_consumed = dict(replayed_snapshot["consumed"])
    snapshot_consumed = dict(snapshot["consumed"])
    replayed_consumed.pop("runtime_seconds", None)
    snapshot_consumed.pop("runtime_seconds", None)
    if replayed_consumed != snapshot_consumed:
        raise BudgetSnapshotError(
            "controller budget replay consumption does not match budget snapshot"
        )

def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00",
        "Z",
    )

def validate_restored_budget_snapshot(snapshot: object) -> dict:
    return _contract_validate_restored_budget_snapshot(snapshot)


def validate_controller_budget_state(state: object) -> dict:
    return _contract_validate_controller_budget_state(state)


def validate_controller_budget_event(event: object) -> dict:
    return _contract_validate_controller_budget_event(event)


def apply_controller_budget_event(budget: RunBudget, event: object) -> dict:
    return _contract_apply_controller_budget_event(budget, event)
