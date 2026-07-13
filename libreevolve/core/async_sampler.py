from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Mapping
from concurrent.futures import Future
from copy import deepcopy
from dataclasses import dataclass
import platform
import threading
import time
from typing import Any

from libreevolve.core.config import (
    MAX_ASYNC_LLM_QUEUE_CAPACITY,
    MAX_ASYNC_LLM_SAMPLER_WORKERS,
)


ASYNC_LLM_SAMPLER_CONTROLLER_SCHEMA = (
    "libreevolve.async_llm_sampler_controller.v1"
)
ASYNC_LLM_SAMPLER_EXECUTION_SCHEMA = (
    "libreevolve.async_llm_sampler_execution.v1"
)
_STOP = object()


@dataclass(frozen=True)
class AsyncLLMSamplerJob:
    sequence: int
    request_id: str
    prompt: str
    role: str = "mutation"
    max_call_attempts: int | None = None
    runtime_deadline_sec: float | None = None


@dataclass(frozen=True)
class AsyncLLMSamplerOutcome:
    response: str | None
    backend_idx: int | None
    call_records: list[dict[str, Any]]
    mutation_call: dict[str, Any] | None
    execution: dict[str, Any]
    error: BaseException | None = None


@dataclass(frozen=True)
class _QueuedSamplerJob:
    job: AsyncLLMSamplerJob
    worker_index: int
    result_future: Future[AsyncLLMSamplerOutcome]
    submitted_at: float
    queue_wait_sec: float
    queue_depth_after_submit: int


@dataclass(frozen=True)
class _QueuedSamplerReward:
    owner: dict[str, Any]
    reward: float
    result_future: Future[dict | None]


class AsyncLLMSamplerController:
    """Run mutation requests on bounded, worker-owned LLM ensembles."""

    def __init__(
        self,
        llms: list[object],
        *,
        queue_capacity: int,
        max_calls_by_role: Mapping[str, int] | None = None,
        telemetry_limit: int = 200,
    ) -> None:
        if not isinstance(llms, list) or not llms:
            raise ValueError("llms must contain at least one sampler")
        if len(llms) > MAX_ASYNC_LLM_SAMPLER_WORKERS:
            raise ValueError(
                "llms must contain at most "
                f"{MAX_ASYNC_LLM_SAMPLER_WORKERS} samplers"
            )
        for index, llm in enumerate(llms):
            if not callable(getattr(llm, "generate", None)):
                raise ValueError(f"llms[{index}] must provide generate()")
            setter = getattr(llm, "set_call_id_namespace", None)
            if callable(setter):
                setter(f"async_sampler_{index:03d}")
        if len({id(llm) for llm in llms}) != len(llms):
            raise ValueError("each async LLM sampler worker must own a distinct LLM")
        backend_owners: dict[int, int] = {}
        for worker_index, llm in enumerate(llms):
            backends = getattr(llm, "backends", None)
            if not isinstance(backends, list):
                continue
            for backend in backends:
                backend_id = id(backend)
                previous_owner = backend_owners.get(backend_id)
                if previous_owner is not None and previous_owner != worker_index:
                    raise ValueError(
                        "async LLM sampler workers must not share backend instances"
                    )
                backend_owners[backend_id] = worker_index
        self._llms = list(llms)
        self._worker_count = len(llms)
        self._queue_capacity = _positive_int(
            "queue_capacity",
            queue_capacity,
            maximum=MAX_ASYNC_LLM_QUEUE_CAPACITY,
        )
        self._telemetry_limit = _positive_int(
            "telemetry_limit",
            telemetry_limit,
            maximum=10_000,
        )
        self._max_calls_by_role = _validate_role_call_limits(max_calls_by_role)
        self._logical_calls_by_role: dict[str, int] = {}
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._queues: list[asyncio.Queue[object]] = []
        self._queue_capacity_sem: asyncio.Semaphore | None = None
        self._workers: list[asyncio.Task[None]] = []
        self._ready = threading.Event()
        self._startup_error: BaseException | None = None
        self._lock = threading.Lock()
        self._closed = False
        self._submitted_sequences: set[int] = set()
        self._task_owners: dict[str, dict[str, Any]] = {}
        self._submitted_count = 0
        self._finished_count = 0
        self._succeeded_count = 0
        self._failed_count = 0
        self._merge_count = 0
        self._reward_count = 0
        self._completion_counter = 0
        self._running_count = 0
        self._max_running_count = 0
        self._max_queue_depth = 0
        self._backpressure_wait_count = 0
        self._provider_wall_sec_sum = 0.0
        self._started_at: float | None = None
        self._closed_at: float | None = None
        self._last_merge_sequence: int | None = None
        self._completion_sequences: list[int] = []
        self._task_records: deque[dict[str, Any]] = deque(
            maxlen=self._telemetry_limit
        )
        self._merge_records: deque[dict[str, Any]] = deque(
            maxlen=self._telemetry_limit
        )
        self._worker_records: dict[str, dict[str, Any]] = {}

    def start(self) -> None:
        with self._lock:
            if self._thread is not None:
                return
            if self._closed:
                raise RuntimeError("async LLM sampler controller is closed")
            self._thread = threading.Thread(
                target=self._thread_main,
                name="libreevolve-async-llm-sampler-controller",
                daemon=False,
            )
            self._thread.start()
        if not self._ready.wait(timeout=10.0):
            raise RuntimeError("async LLM sampler controller failed to start")
        if self._startup_error is not None:
            raise RuntimeError(
                "async LLM sampler controller failed to start"
            ) from self._startup_error

    def submit(self, job: AsyncLLMSamplerJob) -> Future[AsyncLLMSamplerOutcome]:
        self.start()
        _validate_job(job)
        with self._lock:
            if self._closed:
                raise RuntimeError("async LLM sampler controller is closed")
            if job.sequence in self._submitted_sequences:
                raise ValueError(f"duplicate async LLM sampler sequence {job.sequence}")
            remaining = self._remaining_role_call_capacity_locked(job.role)
            if remaining is not None and remaining <= 0:
                raise RuntimeError(
                    f"LLM call budget exhausted before {job.role}: "
                    "async sampler global llm_role_call_limits"
                )
            self._submitted_sequences.add(job.sequence)
            self._logical_calls_by_role[job.role] = (
                self._logical_calls_by_role.get(job.role, 0) + 1
            )
            loop = self._loop
        if loop is None:
            raise RuntimeError("async LLM sampler event loop is unavailable")
        result_future: Future[AsyncLLMSamplerOutcome] = Future()
        worker_index = job.sequence % self._worker_count
        enqueue = asyncio.run_coroutine_threadsafe(
            self._enqueue(job, worker_index, result_future),
            loop,
        )
        try:
            enqueue.result()
        except BaseException:
            with self._lock:
                self._submitted_sequences.discard(job.sequence)
                retained = self._logical_calls_by_role.get(job.role, 0) - 1
                if retained > 0:
                    self._logical_calls_by_role[job.role] = retained
                else:
                    self._logical_calls_by_role.pop(job.role, None)
            raise
        return result_future

    def remaining_role_call_capacity(self, role: str) -> int | None:
        if not isinstance(role, str) or not role:
            raise ValueError("role must be non-empty text")
        with self._lock:
            return self._remaining_role_call_capacity_locked(role)

    def record_merge(self, *, sequence: int, task_id: str) -> int:
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
            raise ValueError("merge sequence must be a non-negative integer")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("merge task_id must be non-empty text")
        with self._lock:
            if (
                self._last_merge_sequence is not None
                and sequence <= self._last_merge_sequence
            ):
                raise ValueError(
                    "async LLM sampler merges must follow increasing submission order"
                )
            merge_order = self._merge_count
            self._merge_count += 1
            self._last_merge_sequence = sequence
            self._merge_records.append(
                {
                    "merge_order": merge_order,
                    "submission_order": sequence,
                    "task_id": task_id,
                }
            )
        return merge_order

    def record_reward(self, *, task_id: str, reward: float) -> dict | None:
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("reward task_id must be non-empty text")
        with self._lock:
            if self._closed:
                raise RuntimeError("async LLM sampler controller is closed")
            stored_owner = self._task_owners.get(task_id)
            if stored_owner is None:
                raise ValueError(f"unknown async LLM sampler task {task_id!r}")
            if (
                stored_owner.get("rewarded") is True
                or stored_owner.get("reward_pending") is True
            ):
                raise ValueError(
                    f"async LLM sampler task {task_id!r} is already rewarded"
                )
            loop = self._loop
            if loop is None:
                raise RuntimeError("async LLM sampler event loop is unavailable")
            stored_owner["reward_pending"] = True
            owner = deepcopy(stored_owner)
        result_future: Future[dict | None] = Future()
        try:
            reward_future = asyncio.run_coroutine_threadsafe(
                self._enqueue_reward(owner, reward, result_future),
                loop,
            )
            reward_future.result()
            event = result_future.result()
        except BaseException:
            with self._lock:
                self._task_owners[task_id]["reward_pending"] = False
            raise
        with self._lock:
            self._task_owners[task_id]["rewarded"] = True
            self._task_owners[task_id]["reward_pending"] = False
            self._reward_count += 1
            worker_id = self._task_owners[task_id]["worker_id"]
            self._worker_records[worker_id]["rewarded_count"] += 1
        return event

    def close(self) -> dict[str, Any]:
        with self._lock:
            thread = self._thread
            loop = self._loop
            already_closed = self._closed
        if thread is None:
            with self._lock:
                self._closed = True
                self._closed_at = time.perf_counter()
            return self.snapshot()
        if not already_closed:
            if loop is None:
                raise RuntimeError("async LLM sampler event loop is unavailable")
            shutdown = asyncio.run_coroutine_threadsafe(self._shutdown(), loop)
            shutdown.result()
            loop.call_soon_threadsafe(loop.stop)
            thread.join(timeout=10.0)
            if thread.is_alive():
                raise RuntimeError("async LLM sampler controller did not stop")
            with self._lock:
                self._closed = True
                self._closed_at = time.perf_counter()
        return self.snapshot()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            started_at = self._started_at
            closed_at = self._closed_at
            elapsed = (
                max(0.0, (closed_at or time.perf_counter()) - started_at)
                if started_at is not None
                else 0.0
            )
            completion_sequences = list(self._completion_sequences)
            sorted_completion_sequences = sorted(completion_sequences)
            out_of_order = sum(
                1
                for observed, expected in zip(
                    completion_sequences,
                    sorted_completion_sequences,
                )
                if observed != expected
            )
            workers = []
            for index, llm in enumerate(self._llms):
                worker_id = f"llm_sampler:local:{index:03d}"
                record = dict(self._worker_records.get(worker_id, {}))
                record["scheduler_summary"] = _scheduler_summary(llm)
                workers.append(record)
            report = {
                "schema": ASYNC_LLM_SAMPLER_CONTROLLER_SCHEMA,
                "status": (
                    "terminal_async_llm_sampler_controller_drained"
                    if self._closed
                    else "async_llm_sampler_controller_running"
                ),
                "controller_model": "single_process_asyncio_llm_sampler_workers",
                "runtime_identity": {
                    "library": "asyncio",
                    "python_implementation": platform.python_implementation(),
                    "event_loop_thread": (
                        "libreevolve-async-llm-sampler-controller"
                    ),
                    "worker_ownership": "one_llm_ensemble_per_worker",
                },
                "queue": {
                    "queue_id": "llm_proposal_queue:local",
                    "capacity": self._queue_capacity,
                    "dispatch_policy": "submission_order_modulo_worker_count",
                    "backpressure_policy": (
                        "producer_waits_for_bounded_queue_capacity"
                    ),
                    "max_observed_depth": self._max_queue_depth,
                    "terminal_depth": 0 if self._closed else None,
                    "backpressure_wait_count": self._backpressure_wait_count,
                },
                "worker_count": self._worker_count,
                "worker_records": workers,
                "submitted_count": self._submitted_count,
                "finished_count": self._finished_count,
                "succeeded_count": self._succeeded_count,
                "failed_count": self._failed_count,
                "merge_count": self._merge_count,
                "reward_count": self._reward_count,
                "role_call_limits": {
                    "configured": dict(sorted(self._max_calls_by_role.items())),
                    "logical_calls_by_role": dict(
                        sorted(self._logical_calls_by_role.items())
                    ),
                },
                "budget_policy": {
                    "logical_role_calls": "globally_reserved_before_queue_submit",
                    "job_attempt_limit": "optional_per_submitted_job",
                    "runtime_deadline": "optional_per_submitted_job",
                    "provider_usage_caps": (
                        "cooperative_after_already_dispatched_batch"
                    ),
                    "queue_wait_budget": "not_implemented",
                    "worker_lease_budget": "not_implemented",
                },
                "cancellation_policy": (
                    "drain_inflight_provider_threads_before_terminal_close"
                ),
                "max_running_count": self._max_running_count,
                "completion_out_of_order_count": out_of_order,
                "deterministic_merge_policy": "increasing_submission_order",
                "controller_wall_sec": elapsed,
                "provider_wall_sec_sum": self._provider_wall_sec_sum,
                "observed_wall_clock_compression_ratio": (
                    self._provider_wall_sec_sum / elapsed if elapsed > 0 else None
                ),
                "task_record_limit": self._telemetry_limit,
                "task_records": sorted(
                    (dict(record) for record in self._task_records),
                    key=lambda record: record["submission_order"],
                ),
                "task_records_truncated": (
                    self._submitted_count > len(self._task_records)
                ),
                "merge_records": list(self._merge_records),
                "merge_records_truncated": self._merge_count > len(self._merge_records),
                "pending_work": {
                    "queued_llm_calls": 0 if self._closed else None,
                    "running_llm_calls": 0 if self._closed else self._running_count,
                    "pending_merges": 0 if self._closed else None,
                },
                "claim_ready": False,
                "claim_readiness": {
                    "python_asyncio_sampler_controller": started_at is not None,
                    "bounded_llm_proposal_queue": started_at is not None,
                    "worker_owned_llm_ensembles": (
                        len(workers) == self._worker_count
                    ),
                    "deterministic_result_merge": self._closed,
                    "candidate_evaluator_queue": False,
                    "distributed_sampler_nodes": False,
                    "pending_work_resume": False,
                    "remaining_gap": [
                        "distributed_sampler_processes_or_hosts",
                        "cross_generation_dependency_graph",
                        "pending_work_checkpoint_and_resume",
                        "provider_output_replay",
                        "worker_lease_and_queue_wait_budgets",
                    ],
                },
            }
        report["validation"] = validate_async_llm_sampler_controller_report(report)
        return report

    def _remaining_role_call_capacity_locked(self, role: str) -> int | None:
        matching = [
            limit - _role_scope_consumed(self._logical_calls_by_role, scope)
            for scope, limit in self._max_calls_by_role.items()
            if _role_scope_matches(scope, role)
        ]
        return max(0, min(matching)) if matching else None

    async def _enqueue(
        self,
        job: AsyncLLMSamplerJob,
        worker_index: int,
        result_future: Future[AsyncLLMSamplerOutcome],
    ) -> None:
        capacity = self._queue_capacity_sem
        if capacity is None or not self._queues:
            raise RuntimeError("async LLM sampler queues are unavailable")
        submitted_at = time.perf_counter()
        started_wait = submitted_at
        await capacity.acquire()
        queue_wait_sec = max(0.0, time.perf_counter() - started_wait)
        depth = sum(queue.qsize() for queue in self._queues) + 1
        self._queues[worker_index].put_nowait(
            _QueuedSamplerJob(
                job=job,
                worker_index=worker_index,
                result_future=result_future,
                submitted_at=submitted_at,
                queue_wait_sec=queue_wait_sec,
                queue_depth_after_submit=depth,
            )
        )
        with self._lock:
            self._submitted_count += 1
            self._max_queue_depth = max(self._max_queue_depth, depth)
            if queue_wait_sec >= 0.001:
                self._backpressure_wait_count += 1

    async def _worker(self, worker_index: int) -> None:
        queue = self._queues[worker_index]
        capacity = self._queue_capacity_sem
        if capacity is None:
            raise RuntimeError("async LLM sampler capacity is unavailable")
        llm = self._llms[worker_index]
        worker_id = f"llm_sampler:local:{worker_index:03d}"
        with self._lock:
            self._worker_records[worker_id] = {
                "worker_id": worker_id,
                "task_name": f"async_llm_sampler_worker_{worker_index:03d}",
                "runtime": "asyncio_task_with_to_thread_worker_owned_llm",
                "ownership": "dedicated_llm_ensemble",
                "lifecycle_status": "running",
                "completed_count": 0,
                "failed_count": 0,
                "rewarded_count": 0,
            }
        while True:
            item = await queue.get()
            if item is _STOP:
                queue.task_done()
                break
            if isinstance(item, _QueuedSamplerReward):
                try:
                    event = await asyncio.to_thread(
                        _record_worker_reward,
                        llm,
                        item.owner,
                        item.reward,
                    )
                except BaseException as exc:
                    item.result_future.set_exception(exc)
                else:
                    item.result_future.set_result(event)
                queue.task_done()
                continue
            assert isinstance(item, _QueuedSamplerJob)
            capacity.release()
            job = item.job
            task_id = f"llm_sampler_call:{job.sequence:08d}"
            started = time.perf_counter()
            with self._lock:
                self._running_count += 1
                self._max_running_count = max(
                    self._max_running_count,
                    self._running_count,
                )
            call_start = _llm_call_count(llm)
            status = "succeeded"
            error: BaseException | None = None
            response: str | None = None
            backend_idx: int | None = None
            original_attempts = getattr(llm, "max_call_attempts", None)
            original_timeout = getattr(llm, "call_timeout_sec", None)
            try:
                if job.max_call_attempts is not None and isinstance(
                    original_attempts, int
                ):
                    setattr(
                        llm,
                        "max_call_attempts",
                        min(original_attempts, job.max_call_attempts),
                    )
                if job.runtime_deadline_sec is not None and "call_timeout_sec" in getattr(
                    llm, "__dict__", {}
                ):
                    effective_timeout = job.runtime_deadline_sec
                    if original_timeout is not None:
                        effective_timeout = min(
                            float(original_timeout),
                            job.runtime_deadline_sec,
                        )
                    setattr(llm, "call_timeout_sec", effective_timeout)
                response, backend_idx = await asyncio.to_thread(
                    _generate,
                    llm,
                    job.prompt,
                    job.role,
                )
                if not isinstance(response, str) or not isinstance(backend_idx, int):
                    raise TypeError("async LLM sampler must return (text, backend_index)")
            except BaseException as exc:
                status = "failed"
                error = exc
            finally:
                if isinstance(original_attempts, int):
                    setattr(llm, "max_call_attempts", original_attempts)
                if "call_timeout_sec" in getattr(llm, "__dict__", {}):
                    setattr(llm, "call_timeout_sec", original_timeout)
            call_records = _llm_call_span(llm, call_start)
            mutation_call = (
                dict(call_records[-1]) if call_records else None
            )
            provider_wall_sec = max(0.0, time.perf_counter() - started)
            with self._lock:
                completion_order = self._completion_counter
                self._completion_counter += 1
                self._finished_count += 1
                self._running_count -= 1
                self._provider_wall_sec_sum += provider_wall_sec
                self._completion_sequences.append(job.sequence)
                worker = self._worker_records[worker_id]
                worker["completed_count"] += 1
                if status == "succeeded":
                    self._succeeded_count += 1
                else:
                    self._failed_count += 1
                    worker["failed_count"] += 1
                execution = {
                    "schema": ASYNC_LLM_SAMPLER_EXECUTION_SCHEMA,
                    "task_id": task_id,
                    "request_id": job.request_id,
                    "submission_order": job.sequence,
                    "completion_order": completion_order,
                    "worker_id": worker_id,
                    "status": status,
                    "queue_wait_sec": item.queue_wait_sec,
                    "queue_depth_after_submit": item.queue_depth_after_submit,
                    "provider_wall_sec": provider_wall_sec,
                    "call_record_count": len(call_records),
                    "error_type": type(error).__name__ if error is not None else None,
                }
                self._task_records.append(dict(execution))
                if status == "succeeded" and backend_idx is not None:
                    self._task_owners[task_id] = {
                        "task_id": task_id,
                        "worker_id": worker_id,
                        "worker_index": worker_index,
                        "backend_idx": backend_idx,
                        "call_id": (
                            mutation_call.get("id")
                            if isinstance(mutation_call, Mapping)
                            else None
                        ),
                        "rewarded": False,
                        "reward_pending": False,
                    }
            item.result_future.set_result(
                AsyncLLMSamplerOutcome(
                    response=response,
                    backend_idx=backend_idx,
                    call_records=call_records,
                    mutation_call=(
                        dict(mutation_call)
                        if isinstance(mutation_call, Mapping)
                        else None
                    ),
                    execution=execution,
                    error=error,
                )
            )
            queue.task_done()
        with self._lock:
            self._worker_records[worker_id]["lifecycle_status"] = "stopped"

    async def _enqueue_reward(
        self,
        owner: dict[str, Any],
        reward: float,
        result_future: Future[dict | None],
    ) -> None:
        worker_index = owner.get("worker_index")
        if (
            isinstance(worker_index, bool)
            or not isinstance(worker_index, int)
            or not 0 <= worker_index < self._worker_count
        ):
            raise RuntimeError("async LLM sampler reward ownership is invalid")
        await self._queues[worker_index].put(
            _QueuedSamplerReward(
                owner=owner,
                reward=reward,
                result_future=result_future,
            )
        )

    async def _shutdown(self) -> None:
        if not self._queues:
            return
        await asyncio.gather(*(queue.join() for queue in self._queues))
        for queue in self._queues:
            await queue.put(_STOP)
        await asyncio.gather(*self._workers)

    def _thread_main(self) -> None:
        loop: asyncio.AbstractEventLoop | None = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            queues = [
                asyncio.Queue(maxsize=self._queue_capacity)
                for _ in range(self._worker_count)
            ]
            capacity = asyncio.Semaphore(self._queue_capacity)
            self._queues = queues
            self._queue_capacity_sem = capacity
            workers = [
                loop.create_task(
                    self._worker(index),
                    name=f"async_llm_sampler_worker_{index:03d}",
                )
                for index in range(self._worker_count)
            ]
            with self._lock:
                self._loop = loop
                self._workers = workers
                self._started_at = time.perf_counter()
            self._ready.set()
            loop.run_forever()
        except BaseException as exc:
            self._startup_error = exc
            self._ready.set()
        finally:
            if loop is not None:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                if pending:
                    loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
                loop.close()


def validate_async_llm_sampler_controller_report(report: object) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    if not isinstance(report, Mapping):
        return {
            "schema": ASYNC_LLM_SAMPLER_CONTROLLER_SCHEMA,
            "ok": False,
            "issues": [
                {"code": "invalid_report", "message": "report must be a mapping"}
            ],
        }
    if report.get("schema") != ASYNC_LLM_SAMPLER_CONTROLLER_SCHEMA:
        issues.append({"code": "invalid_schema", "message": "unsupported schema"})
    if report.get("status") != "terminal_async_llm_sampler_controller_drained":
        issues.append(
            {
                "code": "invalid_status",
                "message": "validated sampler report must be terminal and drained",
            }
        )
    if report.get("controller_model") != (
        "single_process_asyncio_llm_sampler_workers"
    ):
        issues.append(
            {"code": "invalid_controller_model", "message": "unsupported model"}
        )
    worker_count = _report_non_negative_int(report.get("worker_count"))
    workers = report.get("worker_records")
    if worker_count is None or worker_count < 1 or not isinstance(workers, list):
        issues.append({"code": "invalid_workers", "message": "workers are invalid"})
        workers = []
    elif len(workers) != worker_count:
        issues.append({"code": "worker_count_mismatch", "message": "worker count drifted"})
    for worker in workers:
        if not isinstance(worker, Mapping) or worker.get("lifecycle_status") != "stopped":
            issues.append(
                {"code": "worker_not_stopped", "message": "all workers must stop"}
            )
    queue = report.get("queue")
    if not isinstance(queue, Mapping):
        issues.append({"code": "invalid_queue", "message": "queue is invalid"})
    else:
        if _report_non_negative_int(queue.get("capacity")) in {None, 0}:
            issues.append({"code": "invalid_queue_capacity", "message": "capacity is invalid"})
        if queue.get("terminal_depth") != 0:
            issues.append({"code": "queue_not_drained", "message": "queue must be empty"})
    submitted = _report_non_negative_int(report.get("submitted_count"))
    finished = _report_non_negative_int(report.get("finished_count"))
    succeeded = _report_non_negative_int(report.get("succeeded_count"))
    failed = _report_non_negative_int(report.get("failed_count"))
    if None in {submitted, finished, succeeded, failed}:
        issues.append({"code": "invalid_counts", "message": "counts are invalid"})
    elif submitted != finished or finished != succeeded + failed:
        issues.append({"code": "count_mismatch", "message": "counts do not reconcile"})
    pending = report.get("pending_work")
    if not isinstance(pending, Mapping) or any(
        pending.get(field) != 0
        for field in ("queued_llm_calls", "running_llm_calls", "pending_merges")
    ):
        issues.append({"code": "pending_work_not_drained", "message": "pending work must be zero"})
    merges = report.get("merge_records")
    if not isinstance(merges, list):
        issues.append({"code": "invalid_merges", "message": "merge records are invalid"})
    else:
        sequences = [
            row.get("submission_order")
            for row in merges
            if isinstance(row, Mapping)
        ]
        if sequences != sorted(sequences) or len(sequences) != len(set(sequences)):
            issues.append(
                {
                    "code": "nondeterministic_merge_order",
                    "message": "merges must follow increasing submission order",
                }
            )
    if report.get("claim_ready") is not False:
        issues.append({"code": "claim_ready_overclaim", "message": "full parity is not ready"})
    readiness = report.get("claim_readiness")
    if not isinstance(readiness, Mapping):
        issues.append({"code": "invalid_claim_readiness", "message": "readiness is invalid"})
    else:
        for field in ("distributed_sampler_nodes", "pending_work_resume"):
            if readiness.get(field) is not False:
                issues.append(
                    {"code": f"{field}_overclaim", "message": f"{field} must remain false"}
                )
    return {
        "schema": ASYNC_LLM_SAMPLER_CONTROLLER_SCHEMA,
        "ok": not issues,
        "issues": issues,
    }


def _generate(llm: object, prompt: str, role: str) -> tuple[str, int]:
    return llm.generate(prompt, role=role)


def _record_worker_reward(
    llm: object,
    owner: Mapping[str, object],
    reward: float,
) -> dict | None:
    backend_idx = owner.get("backend_idx")
    if isinstance(backend_idx, bool) or not isinstance(backend_idx, int):
        raise RuntimeError("async LLM sampler reward backend ownership is invalid")
    recorder = getattr(llm, "record_reward", None)
    if not callable(recorder):
        return None
    event = recorder(backend_idx, reward, owner.get("call_id"))
    return dict(event) if isinstance(event, Mapping) else None


def _llm_call_count(llm: object) -> int | None:
    retention = getattr(llm, "call_history_retention", None)
    if isinstance(retention, Mapping):
        total = retention.get("total_records")
        if isinstance(total, int) and not isinstance(total, bool) and total >= 0:
            return total
    history = getattr(llm, "call_history", None)
    return len(history) if isinstance(history, list) else None


def _llm_call_span(llm: object, start: int | None) -> list[dict[str, Any]]:
    if start is None:
        return []
    history = getattr(llm, "call_history", None)
    if not isinstance(history, list) or start < 0:
        return []
    retention = getattr(llm, "call_history_retention", None)
    dropped = 0
    if isinstance(retention, Mapping):
        raw_dropped = retention.get("dropped_records")
        if isinstance(raw_dropped, int) and not isinstance(raw_dropped, bool):
            dropped = max(0, raw_dropped)
    retained_start = max(0, start - dropped)
    return [dict(record) for record in history[retained_start:] if isinstance(record, Mapping)]


def _scheduler_summary(llm: object) -> dict[str, Any]:
    state = getattr(llm, "scheduler_state", None)
    if not isinstance(state, Mapping):
        return {"available": False}
    return {
        "available": True,
        "counts": deepcopy(state.get("counts")),
        "wins": deepcopy(state.get("wins")),
        "total": state.get("total"),
        "role_accounting": deepcopy(state.get("role_accounting")),
        "role_scheduler_state": deepcopy(state.get("role_scheduler_state")),
        "role_call_limits": deepcopy(state.get("role_call_limits")),
        "provider_failure_policy_state": deepcopy(
            state.get("provider_failure_policy_state")
        ),
    }


def _validate_job(job: object) -> None:
    if not isinstance(job, AsyncLLMSamplerJob):
        raise ValueError("job must be AsyncLLMSamplerJob")
    if isinstance(job.sequence, bool) or not isinstance(job.sequence, int) or job.sequence < 0:
        raise ValueError("job.sequence must be a non-negative integer")
    if not isinstance(job.request_id, str) or not job.request_id:
        raise ValueError("job.request_id must be non-empty text")
    if not isinstance(job.prompt, str) or not job.prompt:
        raise ValueError("job.prompt must be non-empty text")
    if not isinstance(job.role, str) or not job.role:
        raise ValueError("job.role must be non-empty text")
    if job.max_call_attempts is not None and (
        isinstance(job.max_call_attempts, bool)
        or not isinstance(job.max_call_attempts, int)
        or job.max_call_attempts < 1
    ):
        raise ValueError("job.max_call_attempts must be a positive integer or None")
    if job.runtime_deadline_sec is not None and (
        isinstance(job.runtime_deadline_sec, bool)
        or not isinstance(job.runtime_deadline_sec, (int, float))
        or float(job.runtime_deadline_sec) <= 0.0
    ):
        raise ValueError("job.runtime_deadline_sec must be positive or None")


def _positive_int(name: str, value: object, *, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise ValueError(f"{name} must be an integer between 1 and {maximum}")
    return value


def _report_non_negative_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _validate_role_call_limits(value: object) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("max_calls_by_role must be a mapping")
    normalized: dict[str, int] = {}
    for scope, limit in value.items():
        if not isinstance(scope, str) or not scope:
            raise ValueError("max_calls_by_role keys must be non-empty text")
        if scope.endswith(":*"):
            if not scope[:-2]:
                raise ValueError("max_calls_by_role wildcard scopes require a prefix")
        elif "*" in scope:
            raise ValueError("max_calls_by_role only supports :* suffix wildcards")
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("max_calls_by_role values must be positive integers")
        normalized[scope] = limit
    return dict(sorted(normalized.items()))


def _role_scope_matches(scope: str, role: str) -> bool:
    if scope.endswith(":*"):
        return role.startswith(scope[:-1])
    return scope == role


def _role_scope_consumed(consumed: Mapping[str, int], scope: str) -> int:
    if scope.endswith(":*"):
        return sum(
            value
            for role, value in consumed.items()
            if _role_scope_matches(scope, role)
        )
    return consumed.get(scope, 0)
