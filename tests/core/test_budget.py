import math
from datetime import datetime

import pytest

from libreevolve.core.budget import (
    BudgetSnapshotError,
    CONTROLLER_BUDGET_EVENT_SCHEMA,
    CONTROLLER_BUDGET_STATE_SCHEMA,
    RunBudget,
    apply_controller_budget_event,
    validate_controller_budget_event,
    validate_controller_budget_state,
    validate_restored_budget_snapshot,
)
from libreevolve.core.config import Config


def _budget():
    return RunBudget(
        max_generations=10,
        max_evaluations=None,
        max_evaluator_seconds=None,
        max_runtime_seconds=None,
        started_at=0.0,
        started_at_utc="2000-01-01T00:00:00.000Z",
    )


def _parse_utc_timestamp(value: str) -> datetime:
    assert value.endswith("Z")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def test_record_evaluation_counts_exact_seed_and_candidate_events():
    budget = _budget()

    budget.record_evaluation(
        0.25,
        seed=True,
        accounting={
            "subprocess_attempts": 2,
            "configured_stage_samples": 1,
            "retry_attempts": 1,
            "timeout_count": 0,
            "sample_budget_exhaustions": 0,
            "stage_budget_exhaustions": 0,
        },
    )
    budget.record_evaluation(
        0.50,
        seed=False,
        accounting={
            "subprocess_attempts": 3,
            "configured_stage_samples": 2,
            "retry_attempts": 1,
            "timeout_count": 1,
            "sample_budget_exhaustions": 1,
            "stage_budget_exhaustions": 0,
        },
    )

    snapshot = budget.snapshot()["consumed"]
    assert snapshot["evaluations"] == 2
    assert snapshot["seed_evaluations"] == 1
    assert snapshot["candidate_evaluations"] == 1
    assert snapshot["evaluator_seconds"] == 0.75
    assert snapshot["evaluator_subprocess_attempts"] == 5
    assert snapshot["evaluator_stage_samples"] == 3
    assert snapshot["evaluator_retry_attempts"] == 2
    assert snapshot["evaluator_timeouts"] == 1
    assert snapshot["evaluator_sample_budget_exhaustions"] == 1
    assert snapshot["evaluator_stage_budget_exhaustions"] == 0
    assert snapshot["llm_provider_attempts"] == 0
    assert snapshot["llm_tokens"] == 0
    assert snapshot["llm_cost_microusd"] == 0


def test_llm_provider_attempt_limit_stops_after_recorded_attempts():
    budget = _budget()
    budget.max_llm_provider_attempts = 3

    assert budget.check_before_llm_call() is None
    budget.record_llm_provider_attempts(3)

    assert budget.check_before_llm_call() == "max_llm_provider_attempts"
    snapshot = budget.snapshot()
    assert snapshot["limits"]["max_llm_provider_attempts"] == 3
    assert snapshot["consumed"]["llm_provider_attempts"] == 3
    assert snapshot["stop_reason"] == "max_llm_provider_attempts"


def test_llm_token_limit_stops_after_recorded_tokens():
    budget = _budget()
    budget.max_llm_tokens = 2000

    assert budget.check_before_llm_call() is None
    budget.record_llm_tokens(2000)

    assert budget.check_before_llm_call() == "max_llm_tokens"
    snapshot = budget.snapshot()
    assert snapshot["limits"]["max_llm_tokens"] == 2000
    assert snapshot["consumed"]["llm_tokens"] == 2000
    assert snapshot["stop_reason"] == "max_llm_tokens"


def test_llm_cost_limit_stops_after_recorded_cost():
    budget = _budget()
    budget.max_llm_cost_microusd = 5000

    assert budget.check_before_llm_call() is None
    budget.record_llm_cost_microusd(5000)

    assert budget.check_before_llm_call() == "max_llm_cost_microusd"
    snapshot = budget.snapshot()
    assert snapshot["limits"]["max_llm_cost_microusd"] == 5000
    assert snapshot["consumed"]["llm_cost_microusd"] == 5000
    assert snapshot["stop_reason"] == "max_llm_cost_microusd"


def test_llm_seconds_limit_stops_after_recorded_latency():
    budget = _budget()
    budget.max_llm_seconds = 1.5

    assert budget.check_before_llm_call() is None
    budget.record_llm_seconds(1.5)

    assert budget.check_before_llm_call() == "max_llm_seconds"
    snapshot = budget.snapshot()
    assert snapshot["limits"]["max_llm_seconds"] == 1.5
    assert snapshot["consumed"]["llm_seconds"] == 1.5
    assert snapshot["stop_reason"] == "max_llm_seconds"


@pytest.mark.parametrize(
    ("limit_field", "record_method", "consumed_field", "stop_reason"),
    [
        (
            "llm_role_provider_attempt_limits",
            "record_llm_provider_attempts",
            "llm_provider_attempts_by_role",
            "llm_role_provider_attempt_limits",
        ),
        (
            "llm_role_token_limits",
            "record_llm_tokens",
            "llm_tokens_by_role",
            "llm_role_token_limits",
        ),
        (
            "llm_role_cost_microusd_limits",
            "record_llm_cost_microusd",
            "llm_cost_microusd_by_role",
            "llm_role_cost_microusd_limits",
        ),
        (
            "llm_role_seconds_limits",
            "record_llm_seconds",
            "llm_seconds_by_role",
            "llm_role_seconds_limits",
        ),
    ],
)
def test_llm_role_budget_limits_stop_matching_role_only(
    limit_field,
    record_method,
    consumed_field,
    stop_reason,
):
    budget = _budget()
    setattr(budget, limit_field, {"critique": 3})

    getattr(budget, record_method)(3, role="mutation")
    assert budget.check_before_llm_call(role="mutation") is None
    assert budget.check_before_llm_call(role="critique") is None
    getattr(budget, record_method)(3, role="critique")

    assert budget.check_before_llm_call(role="critique") == stop_reason
    snapshot = budget.snapshot()
    assert snapshot["limits"][limit_field] == {"critique": 3}
    assert snapshot["consumed"][consumed_field] == {"critique": 3, "mutation": 3}
    assert snapshot["stop_reason"] == stop_reason


@pytest.mark.parametrize("attempts", [-1, True, "1", 1.5, None])
def test_record_llm_provider_attempts_rejects_invalid_attempts_before_mutation(
    attempts,
):
    budget = _budget()

    with pytest.raises(ValueError, match="llm_provider_attempts"):
        budget.record_llm_provider_attempts(attempts)

    assert budget.snapshot()["consumed"]["llm_provider_attempts"] == 0


@pytest.mark.parametrize(
    ("method", "field", "value"),
    [
        ("record_llm_tokens", "llm_tokens", -1),
        ("record_llm_tokens", "llm_tokens", True),
        ("record_llm_tokens", "llm_tokens", "1"),
        ("record_llm_cost_microusd", "llm_cost_microusd", -1),
        ("record_llm_cost_microusd", "llm_cost_microusd", True),
        ("record_llm_cost_microusd", "llm_cost_microusd", "1"),
        ("record_llm_seconds", "llm_seconds", -1.0),
        ("record_llm_seconds", "llm_seconds", True),
        ("record_llm_seconds", "llm_seconds", "1"),
    ],
)
def test_record_llm_token_and_cost_reject_invalid_values_before_mutation(
    method,
    field,
    value,
):
    budget = _budget()

    with pytest.raises(ValueError, match=field):
        getattr(budget, method)(value)

    assert budget.snapshot()["consumed"][field] == 0


def test_snapshot_includes_utc_wall_clock_timestamps():
    budget = _budget()

    snapshot = budget.snapshot()
    wall_clock = snapshot["wall_clock"]

    assert wall_clock["schema"] == "utc_run_timestamps_v1"
    assert wall_clock["started_at"] == "2000-01-01T00:00:00.000Z"
    assert wall_clock["runtime_seconds_source"] == "consumed.runtime_seconds"
    assert wall_clock["monotonic_budget_clock"] == "time.monotonic"
    assert _parse_utc_timestamp(wall_clock["updated_at"]) >= _parse_utc_timestamp(
        wall_clock["started_at"]
    )
    assert "finished_at" not in wall_clock
    assert wall_clock["resume_segments"] == [
        {
            "segment_index": 0,
            "kind": "initial_process",
            "started_at": "2000-01-01T00:00:00.000Z",
            "updated_at": wall_clock["updated_at"],
        }
    ]


def test_finished_snapshot_includes_wall_clock_finish_timestamp():
    budget = _budget()
    budget.stop_reason = "completed"

    wall_clock = budget.snapshot()["wall_clock"]

    assert wall_clock["finished_at"] == wall_clock["updated_at"]
    assert wall_clock["resume_segments"][0]["finished_at"] == wall_clock["finished_at"]


@pytest.mark.parametrize(
    ("limit_field", "accounting_key", "stop_reason"),
    [
        (
            "max_evaluator_subprocess_attempts",
            "subprocess_attempts",
            "max_evaluator_subprocess_attempts",
        ),
        (
            "max_evaluator_stage_samples",
            "configured_stage_samples",
            "max_evaluator_stage_samples",
        ),
        (
            "max_evaluator_retry_attempts",
            "retry_attempts",
            "max_evaluator_retry_attempts",
        ),
        ("max_evaluator_timeouts", "timeout_count", "max_evaluator_timeouts"),
        (
            "max_evaluator_sample_budget_exhaustions",
            "sample_budget_exhaustions",
            "max_evaluator_sample_budget_exhaustions",
        ),
        (
            "max_evaluator_stage_budget_exhaustions",
            "stage_budget_exhaustions",
            "max_evaluator_stage_budget_exhaustions",
        ),
    ],
)
def test_detailed_evaluator_accounting_limits_stop_after_recorded_evaluation(
    limit_field,
    accounting_key,
    stop_reason,
):
    budget = _budget()
    setattr(budget, limit_field, 2)

    assert budget.check_before_evaluation() is None
    budget.record_evaluation(0.25, seed=False, accounting={accounting_key: 2})

    assert budget.check_before_evaluation() == stop_reason
    snapshot = budget.snapshot()
    assert snapshot["limits"][limit_field] == 2
    assert snapshot["stop_reason"] == stop_reason


@pytest.mark.parametrize(
    "accounting",
    [
        "bad",
        {"subprocess_attempts": -1},
        {"configured_stage_samples": True},
        {"retry_attempts": "1"},
        {"timeout_count": -1},
        {"sample_budget_exhaustions": -1},
        {"stage_budget_exhaustions": -1},
    ],
)
def test_record_evaluation_rejects_invalid_accounting_before_counter_mutation(accounting):
    budget = _budget()

    with pytest.raises(ValueError, match="accounting"):
        budget.record_evaluation(0.25, seed=False, accounting=accounting)

    snapshot = budget.snapshot()["consumed"]
    assert snapshot["evaluations"] == 0
    assert snapshot["evaluator_subprocess_attempts"] == 0


@pytest.mark.parametrize("seed", ["false", 1, 0, None, [], object()])
def test_record_evaluation_rejects_non_boolean_seed_kind_before_counter_mutation(seed):
    budget = _budget()

    with pytest.raises(ValueError, match="seed flag"):
        budget.record_evaluation(0.25, seed=seed)

    snapshot = budget.snapshot()["consumed"]
    assert snapshot["evaluations"] == 0
    assert snapshot["seed_evaluations"] == 0
    assert snapshot["candidate_evaluations"] == 0
    assert snapshot["evaluator_seconds"] == 0.0


@pytest.mark.parametrize("elapsed_sec", [math.inf, -math.inf, math.nan, -0.01, True, "1", None])
def test_record_evaluation_rejects_invalid_elapsed_time_before_counter_mutation(elapsed_sec):
    budget = _budget()

    with pytest.raises(ValueError, match="elapsed_sec"):
        budget.record_evaluation(elapsed_sec, seed=False)

    snapshot = budget.snapshot()["consumed"]
    assert snapshot["evaluations"] == 0
    assert snapshot["seed_evaluations"] == 0
    assert snapshot["candidate_evaluations"] == 0
    assert snapshot["evaluator_seconds"] == 0.0


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda b: setattr(b, "generations_started", "api_key=secret"), "generations_started"),
        (lambda b: setattr(b, "generations_completed", -3), "generations_completed"),
        (lambda b: setattr(b, "generations_started", 1) or setattr(b, "generations_completed", 2), "<="),
        (lambda b: setattr(b, "stop_reason", {"bad": "reason"}), "stop_reason"),
        (lambda b: setattr(b, "stop_reason", "api_key=secret"), "stop_reason"),
        (lambda b: setattr(b, "evaluations", 3), "sum to evaluations"),
        (lambda b: setattr(b, "evaluator_seconds", math.inf), "evaluator_seconds"),
        (lambda b: setattr(b, "evaluator_subprocess_attempts", -1), "evaluator_subprocess_attempts"),
        (lambda b: setattr(b, "evaluator_stage_samples", -1), "evaluator_stage_samples"),
        (lambda b: setattr(b, "evaluator_retry_attempts", -1), "evaluator_retry_attempts"),
        (lambda b: setattr(b, "evaluator_timeouts", -1), "evaluator_timeouts"),
        (
            lambda b: setattr(b, "evaluator_sample_budget_exhaustions", -1),
            "evaluator_sample_budget_exhaustions",
        ),
        (
            lambda b: setattr(b, "evaluator_stage_budget_exhaustions", -1),
            "evaluator_stage_budget_exhaustions",
        ),
        (lambda b: setattr(b, "max_generations", True), "max_generations"),
        (lambda b: setattr(b, "max_evaluator_seconds", math.nan), "max_evaluator_seconds"),
        (
            lambda b: setattr(b, "started_at_utc", "2026-01-01T00:00:00+00:00"),
            "started_at_utc",
        ),
        (
            lambda b: setattr(b, "max_evaluator_subprocess_attempts", -1),
            "max_evaluator_subprocess_attempts",
        ),
        (
            lambda b: setattr(b, "max_evaluator_stage_samples", True),
            "max_evaluator_stage_samples",
        ),
        (
            lambda b: setattr(b, "max_evaluator_retry_attempts", -1),
            "max_evaluator_retry_attempts",
        ),
        (
            lambda b: setattr(b, "max_evaluator_timeouts", True),
            "max_evaluator_timeouts",
        ),
        (
            lambda b: setattr(b, "max_evaluator_sample_budget_exhaustions", -1),
            "max_evaluator_sample_budget_exhaustions",
        ),
        (
            lambda b: setattr(b, "max_evaluator_stage_budget_exhaustions", True),
            "max_evaluator_stage_budget_exhaustions",
        ),
        (
            lambda b: setattr(b, "max_llm_provider_attempts", -1),
            "max_llm_provider_attempts",
        ),
        (
            lambda b: setattr(b, "llm_provider_attempts", True),
            "llm_provider_attempts",
        ),
        (lambda b: setattr(b, "max_llm_tokens", -1), "max_llm_tokens"),
        (lambda b: setattr(b, "max_llm_cost_microusd", True), "max_llm_cost_microusd"),
        (lambda b: setattr(b, "llm_tokens", -1), "llm_tokens"),
        (lambda b: setattr(b, "llm_cost_microusd", True), "llm_cost_microusd"),
        (
            lambda b: setattr(b, "llm_role_token_limits", {"bad role": 1}),
            "llm_role_token_limits",
        ),
        (
            lambda b: setattr(b, "llm_tokens_by_role", {"critique": -1}),
            "llm_tokens_by_role",
        ),
    ],
)
def test_snapshot_rejects_malformed_budget_state(mutate, message):
    budget = _budget()
    mutate(budget)

    with pytest.raises(ValueError, match=message):
        budget.snapshot()


def test_check_limits_rejects_malformed_existing_stop_reason():
    budget = _budget()
    budget.stop_reason = {"bad": "reason"}

    with pytest.raises(ValueError, match="stop_reason"):
        budget.check_before_generation()


def test_finish_rejects_malformed_budget_state_before_returning_runtime_snapshot():
    budget = _budget()
    budget.generations_started = 0
    budget.generations_completed = 1

    with pytest.raises(ValueError, match="<="):
        budget.finish(best_found=True)


def _restored_snapshot():
    budget = _budget()
    budget.record_generation_start()
    budget.record_evaluation(0.25, seed=True)
    return budget.snapshot()


def test_validate_restored_budget_snapshot_returns_defensive_copy():
    snapshot = _restored_snapshot()

    restored = validate_restored_budget_snapshot(snapshot)

    assert restored == snapshot
    restored["consumed"]["evaluations"] = 99
    assert validate_restored_budget_snapshot(snapshot)["consumed"]["evaluations"] == 1


def test_run_budget_restores_consumed_counters_and_resume_segments():
    config = Config(
        max_generations=10,
        max_llm_tokens=2000,
        llm_role_token_limits={"mutation": 2000},
    )
    original = RunBudget.from_config(config)
    original.record_evaluation(0.25, seed=True)
    original.record_llm_call()
    original.record_llm_tokens(1200, role="mutation")
    snapshot = original.snapshot()

    restored = RunBudget.from_restored_snapshot(config, snapshot)

    consumed = restored.snapshot()["consumed"]
    assert consumed["evaluations"] == 1
    assert consumed["seed_evaluations"] == 1
    assert consumed["llm_calls"] == 1
    assert consumed["llm_tokens"] == 1200
    assert consumed["llm_tokens_by_role"] == {"mutation": 1200}
    assert consumed["runtime_seconds"] >= snapshot["consumed"]["runtime_seconds"]
    segments = restored.snapshot()["wall_clock"]["resume_segments"]
    assert segments[0]["kind"] == "initial_process"
    assert segments[1]["kind"] == "resumed_process"


def test_run_budget_restore_rejects_limit_mismatch():
    snapshot = RunBudget.from_config(Config(max_generations=10)).snapshot()

    with pytest.raises(BudgetSnapshotError, match="limits must match"):
        RunBudget.from_restored_snapshot(Config(max_generations=11), snapshot)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda s: s.update({"extra": {}}), "unsupported fields"),
        (lambda s: s.pop("consumed"), "missing fields"),
        (lambda s: s["limits"].update({"max_generations": True}), "limits.max_generations"),
        (lambda s: s["limits"].update({"max_evaluator_seconds": math.inf}), "limits.max_evaluator_seconds"),
        (
            lambda s: s["limits"].update({"max_llm_provider_attempts": -1}),
            "limits.max_llm_provider_attempts",
        ),
        (
            lambda s: s["limits"].update({"max_llm_tokens": -1}),
            "limits.max_llm_tokens",
        ),
        (
            lambda s: s["limits"].update({"max_llm_cost_microusd": True}),
            "limits.max_llm_cost_microusd",
        ),
        (
            lambda s: s["limits"].update({"llm_role_token_limits": {"bad role": 1}}),
            "limits.llm_role_token_limits",
        ),
        (lambda s: s["consumed"].update({"evaluations": -1}), "consumed.evaluations"),
        (lambda s: s["consumed"].update({"evaluator_seconds": math.nan}), "consumed.evaluator_seconds"),
        (
            lambda s: s["consumed"].update({"llm_provider_attempts": True}),
            "consumed.llm_provider_attempts",
        ),
        (
            lambda s: s["consumed"].update({"llm_tokens": -1}),
            "consumed.llm_tokens",
        ),
        (
            lambda s: s["consumed"].update({"llm_cost_microusd": True}),
            "consumed.llm_cost_microusd",
        ),
        (
            lambda s: s["consumed"].update({"llm_tokens_by_role": {"critique": -1}}),
            "consumed.llm_tokens_by_role",
        ),
        (lambda s: s["consumed"].update({"runtime_seconds": -0.1}), "consumed.runtime_seconds"),
        (lambda s: s["consumed"].update({"seed_evaluations": 2}), "sum to consumed.evaluations"),
        (
            lambda s: s["consumed"].update(
                {"generations_started": 0, "generations_completed": 1}
            ),
            "generations_completed",
        ),
        (lambda s: s.update({"stop_reason": "bad"}), "stop_reason"),
        (lambda s: s["wall_clock"].update({"schema": "v0"}), "wall_clock schema"),
        (
            lambda s: s["wall_clock"].update({"started_at": "2026-01-01T00:00:00+00:00"}),
            "wall_clock.started_at",
        ),
        (lambda s: s["wall_clock"].update({"resume_segments": []}), "resume_segments"),
        (
            lambda s: s["wall_clock"]["resume_segments"][0].update({"segment_index": 7}),
            "segment_index must equal 0",
        ),
        (
            lambda s: s["wall_clock"]["resume_segments"][0].update({"kind": ""}),
            "kind",
        ),
    ],
)
def test_validate_restored_budget_snapshot_rejects_malformed_state(mutate, message):
    snapshot = _restored_snapshot()
    mutate(snapshot)

    with pytest.raises(BudgetSnapshotError, match=message):
        validate_restored_budget_snapshot(snapshot)


def _controller_event(kind: str, sequence: int = 0, **extra):
    event = {
        "schema": CONTROLLER_BUDGET_EVENT_SCHEMA,
        "sequence": sequence,
        "kind": kind,
    }
    if kind in {"seed_evaluation", "candidate_evaluation"}:
        event.update(
            {
                "elapsed_sec": 0.25,
                "accounting": {
                    "subprocess_attempts": 1,
                    "configured_stage_samples": 2,
                    "retry_attempts": 0,
                    "timeout_count": 0,
                    "sample_budget_exhaustions": 0,
                    "stage_budget_exhaustions": 0,
                },
            }
        )
    if kind == "stop":
        event["stop_reason"] = "completed"
    event.update(extra)
    return event


def test_controller_budget_events_validate_and_apply_before_counter_mutation():
    budget = _budget()

    seed = apply_controller_budget_event(budget, _controller_event("seed_evaluation"))
    candidate = apply_controller_budget_event(
        budget, _controller_event("candidate_evaluation", sequence=1)
    )
    llm_call = apply_controller_budget_event(
        budget, _controller_event("llm_call", sequence=2)
    )
    apply_controller_budget_event(budget, _controller_event("generation_started", sequence=3))
    apply_controller_budget_event(budget, _controller_event("generation_completed", sequence=4))
    stop = apply_controller_budget_event(
        budget, _controller_event("stop", sequence=5, stop_reason="completed")
    )

    consumed = budget.snapshot()["consumed"]
    assert seed["kind"] == "seed_evaluation"
    assert candidate["kind"] == "candidate_evaluation"
    assert llm_call["kind"] == "llm_call"
    assert stop["stop_reason"] == "completed"
    assert consumed["evaluations"] == 2
    assert consumed["seed_evaluations"] == 1
    assert consumed["candidate_evaluations"] == 1
    assert consumed["evaluator_seconds"] == 0.5
    assert consumed["evaluator_subprocess_attempts"] == 2
    assert consumed["evaluator_stage_samples"] == 4
    assert consumed["llm_calls"] == 1
    assert consumed["generations_started"] == 1
    assert consumed["generations_completed"] == 1


def test_controller_llm_call_event_replays_usage_budget_consumption_by_role():
    budget = _budget()
    budget.max_llm_provider_attempts = 3
    budget.max_llm_tokens = 2000
    budget.max_llm_cost_microusd = 10000
    budget.max_llm_seconds = 1.5
    budget.llm_role_provider_attempt_limits = {"mutation": 3}
    budget.llm_role_token_limits = {"mutation": 2000}
    budget.llm_role_cost_microusd_limits = {"mutation": 10000}
    budget.llm_role_seconds_limits = {"mutation": 1.5}

    llm_call = apply_controller_budget_event(
        budget,
        _controller_event(
            "llm_call",
            role="mutation",
            provider_attempts=3,
            tokens=2000,
            cost_microusd=10000,
            seconds=1.5,
        ),
    )

    assert llm_call == {
        "schema": CONTROLLER_BUDGET_EVENT_SCHEMA,
        "sequence": 0,
        "kind": "llm_call",
        "role": "mutation",
        "provider_attempts": 3,
        "tokens": 2000,
        "cost_microusd": 10000,
        "seconds": 1.5,
    }
    consumed = budget.snapshot()["consumed"]
    assert consumed["llm_calls"] == 1
    assert consumed["llm_provider_attempts"] == 3
    assert consumed["llm_tokens"] == 2000
    assert consumed["llm_cost_microusd"] == 10000
    assert consumed["llm_seconds"] == 1.5
    assert consumed["llm_provider_attempts_by_role"] == {"mutation": 3}
    assert consumed["llm_tokens_by_role"] == {"mutation": 2000}
    assert consumed["llm_cost_microusd_by_role"] == {"mutation": 10000}
    assert consumed["llm_seconds_by_role"] == {"mutation": 1.5}
    assert budget.check_before_llm_call(role="mutation") == (
        "max_llm_provider_attempts"
    )


@pytest.mark.parametrize(
    ("event", "message"),
    [
        ([], "must be a mapping"),
        ({}, "missing fields"),
        (_controller_event("seed_evaluation", schema="wrong"), "schema is unsupported"),
        (_controller_event("bogus"), "kind must be one of"),
        (_controller_event("seed_evaluation", sequence=True), "event.sequence"),
        (_controller_event("seed_evaluation", elapsed_sec=math.nan), "elapsed_sec"),
        (_controller_event("candidate_evaluation", elapsed_sec=-1.0), "elapsed_sec"),
        (
            {
                "schema": CONTROLLER_BUDGET_EVENT_SCHEMA,
                "sequence": 0,
                "kind": "candidate_evaluation",
            },
            "missing fields",
        ),
        (
            _controller_event("seed_evaluation", accounting={"subprocess_attempts": -1}),
            "accounting subprocess_attempts",
        ),
        (_controller_event("stop", stop_reason=None), "stop_reason must not be null"),
        (_controller_event("stop", stop_reason="bad"), "stop_reason"),
        (_controller_event("generation_started", elapsed_sec=0.1), "unsupported fields"),
        (_controller_event("llm_call", role="bad role"), "event.role"),
        (_controller_event("llm_call", provider_attempts=-1), "event.provider_attempts"),
        (_controller_event("llm_call", tokens=True), "event.tokens"),
        (_controller_event("llm_call", cost_microusd="1"), "event.cost_microusd"),
        (_controller_event("llm_call", seconds=math.inf), "event.seconds"),
    ],
)
def test_validate_controller_budget_event_rejects_malformed_events(event, message):
    with pytest.raises(BudgetSnapshotError, match=message):
        validate_controller_budget_event(event)


def test_apply_controller_budget_event_rejects_malformed_event_before_mutation():
    budget = _budget()

    with pytest.raises(BudgetSnapshotError, match="elapsed_sec"):
        apply_controller_budget_event(
            budget, _controller_event("candidate_evaluation", elapsed_sec=math.inf)
        )

    consumed = budget.snapshot()["consumed"]
    assert consumed["evaluations"] == 0
    assert consumed["seed_evaluations"] == 0
    assert consumed["candidate_evaluations"] == 0
    assert consumed["evaluator_seconds"] == 0.0


def test_validate_controller_budget_state_validates_snapshot_and_event_sequence():
    snapshot = _restored_snapshot()
    state = {
        "schema": CONTROLLER_BUDGET_STATE_SCHEMA,
        "snapshot": snapshot,
        "events": [
            _controller_event("seed_evaluation", sequence=0),
            _controller_event("candidate_evaluation", sequence=1),
        ],
    }

    restored = validate_controller_budget_state(state)

    assert restored["schema"] == CONTROLLER_BUDGET_STATE_SCHEMA
    assert restored["snapshot"] == snapshot
    assert [event["kind"] for event in restored["events"]] == [
        "seed_evaluation",
        "candidate_evaluation",
    ]
    restored["snapshot"]["consumed"]["evaluations"] = 99
    assert validate_controller_budget_state(state)["snapshot"]["consumed"]["evaluations"] == 1


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda state: state.update({"schema": "wrong"}), "schema is unsupported"),
        (lambda state: state.pop("snapshot"), "missing fields"),
        (
            lambda state: state["snapshot"]["consumed"].update({"runtime_seconds": math.nan}),
            "consumed.runtime_seconds",
        ),
        (lambda state: state.update({"events": "bad"}), "events must be a list"),
        (
            lambda state: state["events"][1].update({"sequence": 7}),
            "contiguous sequence",
        ),
        (
            lambda state: state["events"][0].update({"kind": "bad"}),
            "kind must be one of",
        ),
    ],
)
def test_validate_controller_budget_state_rejects_malformed_state(mutate, message):
    state = {
        "schema": CONTROLLER_BUDGET_STATE_SCHEMA,
        "snapshot": _restored_snapshot(),
        "events": [
            _controller_event("seed_evaluation", sequence=0),
            _controller_event("candidate_evaluation", sequence=1),
        ],
    }
    mutate(state)

    with pytest.raises(BudgetSnapshotError, match=message):
        validate_controller_budget_state(state)
