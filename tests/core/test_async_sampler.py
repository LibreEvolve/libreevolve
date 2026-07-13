from __future__ import annotations

import time

import pytest

from libreevolve.core.async_sampler import (
    ASYNC_LLM_SAMPLER_CONTROLLER_SCHEMA,
    AsyncLLMSamplerController,
    AsyncLLMSamplerJob,
    validate_async_llm_sampler_controller_report,
)
from libreevolve.llm.ensemble import LLMEnsemble


class _Backend:
    def generate(self, prompt, role="mutation"):
        delay = {"slow": 0.07, "medium": 0.03, "fast": 0.01}.get(prompt, 0.0)
        time.sleep(delay)
        if prompt == "fail":
            raise RuntimeError("sampler failed")
        return f"result:{prompt}"


class _OwnershipLLM:
    def __init__(self):
        self.call_history = []
        self.last_call = None
        self.active = False
        self.events = []

    @property
    def call_history_retention(self):
        return {
            "total_records": len(self.call_history),
            "dropped_records": 0,
        }

    def set_call_id_namespace(self, namespace):
        self.namespace = namespace

    def generate(self, prompt, role="mutation"):
        assert self.active is False
        self.active = True
        self.events.append(f"start:{prompt}")
        time.sleep(0.03)
        call = {
            "id": f"{self.namespace}:{prompt}",
            "sequence_id": len(self.call_history) + 1,
            "role": role,
            "backend_idx": 0,
            "status": "ok",
        }
        self.call_history.append(call)
        self.last_call = call
        self.events.append(f"finish:{prompt}")
        self.active = False
        return f"result:{prompt}", 0

    def record_reward(self, idx, reward, call_id=None):
        assert self.active is False
        self.events.append(f"reward:{call_id}")
        return {
            "record_type": "reward",
            "call_id": call_id,
            "backend_idx": idx,
            "reward": reward,
            "reward_raw": reward,
            "rewarded": True,
        }


def _ensemble():
    return LLMEnsemble([_Backend()], max_retries=0, fallback=False)


def test_async_sampler_overlaps_workers_and_merges_deterministically():
    controller = AsyncLLMSamplerController(
        [_ensemble(), _ensemble()],
        queue_capacity=3,
    )
    jobs = [
        AsyncLLMSamplerJob(sequence=0, request_id="request-0", prompt="slow"),
        AsyncLLMSamplerJob(sequence=1, request_id="request-1", prompt="fast"),
        AsyncLLMSamplerJob(sequence=2, request_id="request-2", prompt="medium"),
    ]
    futures = [controller.submit(job) for job in jobs]
    outcomes = [future.result(timeout=2.0) for future in futures]

    assert [outcome.response for outcome in outcomes] == [
        "result:slow",
        "result:fast",
        "result:medium",
    ]
    assert outcomes[0].execution["worker_id"] == "llm_sampler:local:000"
    assert outcomes[1].execution["worker_id"] == "llm_sampler:local:001"
    assert outcomes[2].execution["worker_id"] == "llm_sampler:local:000"
    assert len({outcome.mutation_call["id"] for outcome in outcomes}) == 3
    for sequence, outcome in enumerate(outcomes):
        controller.record_merge(
            sequence=sequence,
            task_id=outcome.execution["task_id"],
        )
        reward = controller.record_reward(
            task_id=outcome.execution["task_id"],
            reward=0.25,
        )
        assert reward["reward"] == 0.25
        assert reward["call_id"] == outcome.mutation_call["id"]

    report = controller.close()

    assert report["schema"] == ASYNC_LLM_SAMPLER_CONTROLLER_SCHEMA
    assert report["validation"]["ok"] is True
    assert report["submitted_count"] == 3
    assert report["finished_count"] == 3
    assert report["succeeded_count"] == 3
    assert report["failed_count"] == 0
    assert report["merge_count"] == 3
    assert report["reward_count"] == 3
    assert report["max_running_count"] == 2
    assert report["completion_out_of_order_count"] > 0
    assert [row["submission_order"] for row in report["merge_records"]] == [
        0,
        1,
        2,
    ]
    assert all(
        row["scheduler_summary"]["wins"] == [0.25 * row["rewarded_count"]]
        for row in report["worker_records"]
    )


def test_async_sampler_applies_global_bounded_queue_backpressure():
    controller = AsyncLLMSamplerController([_ensemble()], queue_capacity=1)
    futures = [
        controller.submit(
            AsyncLLMSamplerJob(
                sequence=index,
                request_id=f"request-{index}",
                prompt="medium",
            )
        )
        for index in range(3)
    ]
    for index, future in enumerate(futures):
        outcome = future.result(timeout=2.0)
        controller.record_merge(
            sequence=index,
            task_id=outcome.execution["task_id"],
        )
    report = controller.close()

    assert report["queue"]["capacity"] == 1
    assert report["queue"]["max_observed_depth"] == 1
    assert report["queue"]["backpressure_wait_count"] >= 1
    assert report["validation"]["ok"] is True


def test_async_sampler_returns_failure_with_call_telemetry_and_drains():
    controller = AsyncLLMSamplerController([_ensemble()], queue_capacity=1)
    outcome = controller.submit(
        AsyncLLMSamplerJob(sequence=0, request_id="request-0", prompt="fail")
    ).result(timeout=2.0)

    assert isinstance(outcome.error, RuntimeError)
    assert outcome.response is None
    assert outcome.execution["status"] == "failed"
    assert outcome.execution["error_type"] == "RuntimeError"
    assert outcome.call_records[0]["status"] == "error"
    controller.record_merge(sequence=0, task_id=outcome.execution["task_id"])
    report = controller.close()

    assert report["failed_count"] == 1
    assert report["validation"]["ok"] is True


def test_async_sampler_rejects_duplicate_submission_and_merge_order():
    controller = AsyncLLMSamplerController([_ensemble()], queue_capacity=1)
    job = AsyncLLMSamplerJob(sequence=1, request_id="request-1", prompt="fast")
    future = controller.submit(job)
    with pytest.raises(ValueError, match="duplicate async LLM sampler sequence"):
        controller.submit(job)
    outcome = future.result(timeout=2.0)
    controller.record_merge(sequence=1, task_id=outcome.execution["task_id"])
    with pytest.raises(ValueError, match="increasing submission order"):
        controller.record_merge(sequence=0, task_id="llm_sampler_call:00000000")
    controller.close()


@pytest.mark.parametrize(
    ("llms", "capacity", "message"),
    [
        ([], 1, "llms"),
        ([object()], 1, "generate"),
        ([_ensemble()], 0, "queue_capacity"),
    ],
)
def test_async_sampler_rejects_invalid_configuration(llms, capacity, message):
    with pytest.raises(ValueError, match=message):
        AsyncLLMSamplerController(llms, queue_capacity=capacity)


def test_async_sampler_report_validator_rejects_overclaim_and_drift():
    controller = AsyncLLMSamplerController([_ensemble()], queue_capacity=1)
    controller.submit(
        AsyncLLMSamplerJob(
            sequence=0,
            request_id="request-0",
            prompt="fast",
        )
    ).result(timeout=2.0)
    report = controller.close()
    report["claim_ready"] = True
    report["queue"]["terminal_depth"] = 1
    report["claim_readiness"]["distributed_sampler_nodes"] = True
    report["task_records"][0]["finished_monotonic_sec"] = (
        report["task_records"][0]["started_monotonic_sec"] - 1.0
    )

    validation = validate_async_llm_sampler_controller_report(report)
    codes = {issue["code"] for issue in validation["issues"]}

    assert validation["ok"] is False
    assert "queue_not_drained" in codes
    assert "claim_ready_overclaim" in codes
    assert "distributed_sampler_nodes_overclaim" in codes
    assert "invalid_task_timing" in codes


def test_async_sampler_enforces_global_role_limit_across_workers():
    controller = AsyncLLMSamplerController(
        [_ensemble(), _ensemble()],
        queue_capacity=2,
        max_calls_by_role={"mutation": 2},
    )
    assert controller.remaining_role_call_capacity("mutation") == 2
    futures = [
        controller.submit(
            AsyncLLMSamplerJob(
                sequence=index,
                request_id=f"request-{index}",
                prompt="fast",
            )
        )
        for index in range(2)
    ]
    assert controller.remaining_role_call_capacity("mutation") == 0
    with pytest.raises(RuntimeError, match="global llm_role_call_limits"):
        controller.submit(
            AsyncLLMSamplerJob(
                sequence=2,
                request_id="request-2",
                prompt="fast",
            )
        )
    for index, future in enumerate(futures):
        outcome = future.result(timeout=2.0)
        controller.record_merge(
            sequence=index,
            task_id=outcome.execution["task_id"],
        )
    report = controller.close()

    assert report["validation"]["ok"] is True
    assert report["role_call_limits"] == {
        "configured": {"mutation": 2},
        "logical_calls_by_role": {"mutation": 2},
    }


def test_async_sampler_rejects_shared_worker_llm_instance():
    llm = _ensemble()
    with pytest.raises(ValueError, match="distinct LLM"):
        AsyncLLMSamplerController([llm, llm], queue_capacity=2)


def test_async_sampler_rejects_backend_instance_shared_across_workers():
    backend = _Backend()
    first = LLMEnsemble([backend], max_retries=0, fallback=False)
    second = LLMEnsemble([backend], max_retries=0, fallback=False)
    with pytest.raises(ValueError, match="share backend instances"):
        AsyncLLMSamplerController([first, second], queue_capacity=2)


def test_async_sampler_serializes_rewards_with_worker_generation():
    llm = _OwnershipLLM()
    controller = AsyncLLMSamplerController([llm], queue_capacity=2)
    first = controller.submit(
        AsyncLLMSamplerJob(sequence=0, request_id="request-0", prompt="first")
    )
    second = controller.submit(
        AsyncLLMSamplerJob(sequence=1, request_id="request-1", prompt="second")
    )
    first_outcome = first.result(timeout=2.0)
    reward = controller.record_reward(
        task_id=first_outcome.execution["task_id"],
        reward=0.5,
    )
    second_outcome = second.result(timeout=2.0)
    controller.record_merge(sequence=0, task_id=first_outcome.execution["task_id"])
    controller.record_merge(sequence=1, task_id=second_outcome.execution["task_id"])
    report = controller.close()

    assert reward["call_id"] == first_outcome.mutation_call["id"]
    assert llm.events == [
        "start:first",
        "finish:first",
        "start:second",
        "finish:second",
        f"reward:{first_outcome.mutation_call['id']}",
    ]
    assert report["validation"]["ok"] is True
