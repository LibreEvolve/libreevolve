from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Callable, Mapping
from concurrent.futures import Future
from dataclasses import dataclass
import math
import platform
import threading
import time
from typing import Any

from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.config import (
    MAX_ASYNC_EVALUATION_QUEUE_CAPACITY,
    MAX_ASYNC_EVALUATOR_WORKERS,
)
from libreevolve.core.evaluator import EvaluationResult


ASYNC_EVALUATION_CONTROLLER_SCHEMA = (
    "libreevolve.async_candidate_evaluation_controller.v1"
)
ASYNC_EVALUATION_EXECUTION_SCHEMA = (
    "libreevolve.async_candidate_evaluation_execution.v1"
)
_STOP = object()


@dataclass(frozen=True)
class AsyncEvaluationJob:
    sequence: int
    candidate_id: str
    workspace: CandidateWorkspace
    diff_error: object | None


@dataclass(frozen=True)
class AsyncEvaluationOutcome:
    result: EvaluationResult
    execution: dict[str, Any]


@dataclass(frozen=True)
class _QueuedEvaluation:
    job: AsyncEvaluationJob
    result_future: Future[AsyncEvaluationOutcome]
    submitted_at: float
    queue_wait_sec: float
    queue_depth_after_submit: int


class AsyncCandidateEvaluationController:
    """Run candidate evaluations on a bounded asyncio worker queue."""

    def __init__(
        self,
        evaluate: Callable[[CandidateWorkspace, object | None], EvaluationResult],
        *,
        worker_count: int,
        queue_capacity: int,
        telemetry_limit: int = 200,
    ) -> None:
        if not callable(evaluate):
            raise ValueError("evaluate must be callable")
        self._worker_count = _positive_int(
            "worker_count",
            worker_count,
            maximum=MAX_ASYNC_EVALUATOR_WORKERS,
        )
        self._queue_capacity = _positive_int(
            "queue_capacity",
            queue_capacity,
            maximum=MAX_ASYNC_EVALUATION_QUEUE_CAPACITY,
        )
        self._telemetry_limit = _positive_int(
            "telemetry_limit",
            telemetry_limit,
            maximum=10_000,
        )
        self._evaluate = evaluate
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._queue: asyncio.Queue[object] | None = None
        self._queue_capacity_sem: asyncio.Semaphore | None = None
        self._workers: list[asyncio.Task[None]] = []
        self._ready = threading.Event()
        self._startup_error: BaseException | None = None
        self._lock = threading.Lock()
        self._closed = False
        self._submitted_sequences: set[int] = set()
        self._submitted_count = 0
        self._finished_count = 0
        self._succeeded_count = 0
        self._failed_count = 0
        self._admission_count = 0
        self._completion_counter = 0
        self._running_count = 0
        self._max_running_count = 0
        self._max_queue_depth = 0
        self._backpressure_wait_count = 0
        self._evaluation_wall_sec_sum = 0.0
        self._started_at: float | None = None
        self._closed_at: float | None = None
        self._last_admission_sequence: int | None = None
        self._completion_sequences: list[int] = []
        self._task_records: deque[dict[str, Any]] = deque(
            maxlen=self._telemetry_limit
        )
        self._admission_records: deque[dict[str, Any]] = deque(
            maxlen=self._telemetry_limit
        )
        self._worker_records: dict[str, dict[str, Any]] = {}

    def start(self) -> None:
        with self._lock:
            if self._thread is not None:
                return
            if self._closed:
                raise RuntimeError("async evaluation controller is closed")
            self._thread = threading.Thread(
                target=self._thread_main,
                name="libreevolve-async-evaluation-controller",
                daemon=False,
            )
            self._thread.start()
        if not self._ready.wait(timeout=10.0):
            raise RuntimeError("async evaluation controller failed to start")
        if self._startup_error is not None:
            raise RuntimeError("async evaluation controller failed to start") from self._startup_error

    def submit(self, job: AsyncEvaluationJob) -> Future[AsyncEvaluationOutcome]:
        self.start()
        _validate_job(job)
        with self._lock:
            if self._closed:
                raise RuntimeError("async evaluation controller is closed")
            if job.sequence in self._submitted_sequences:
                raise ValueError(f"duplicate async evaluation sequence {job.sequence}")
            self._submitted_sequences.add(job.sequence)
            loop = self._loop
        if loop is None:
            raise RuntimeError("async evaluation controller event loop is unavailable")
        result_future: Future[AsyncEvaluationOutcome] = Future()
        enqueue = asyncio.run_coroutine_threadsafe(
            self._enqueue(job, result_future),
            loop,
        )
        try:
            enqueue.result()
        except BaseException:
            with self._lock:
                self._submitted_sequences.discard(job.sequence)
            raise
        return result_future

    def record_admission(
        self,
        *,
        sequence: int,
        source: str,
        task_id: str | None,
    ) -> int:
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
            raise ValueError("admission sequence must be a non-negative integer")
        if source not in {"cache_hit", "inflight_cache_hit", "worker_result"}:
            raise ValueError("unsupported async admission source")
        with self._lock:
            if (
                self._last_admission_sequence is not None
                and sequence <= self._last_admission_sequence
            ):
                raise ValueError(
                    "async candidate admissions must follow increasing submission order"
                )
            admission_order = self._admission_count
            self._admission_count += 1
            self._last_admission_sequence = sequence
            self._admission_records.append(
                {
                    "admission_order": admission_order,
                    "submission_order": sequence,
                    "source": source,
                    "task_id": task_id,
                }
            )
        return admission_order

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
                raise RuntimeError("async evaluation controller event loop is unavailable")
            shutdown = asyncio.run_coroutine_threadsafe(self._shutdown(), loop)
            shutdown.result()
            loop.call_soon_threadsafe(loop.stop)
            thread.join(timeout=10.0)
            if thread.is_alive():
                raise RuntimeError("async evaluation controller did not stop")
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
            report = {
                "schema": ASYNC_EVALUATION_CONTROLLER_SCHEMA,
                "status": (
                    "terminal_async_evaluation_controller_drained"
                    if self._closed
                    else "async_evaluation_controller_running"
                ),
                "controller_model": "single_process_asyncio_candidate_evaluation",
                "runtime_identity": {
                    "library": "asyncio",
                    "python_implementation": platform.python_implementation(),
                    "event_loop_thread": "libreevolve-async-evaluation-controller",
                },
                "queue": {
                    "queue_id": "candidate_evaluation_queue:local",
                    "capacity": self._queue_capacity,
                    "backpressure_policy": "producer_waits_for_bounded_queue_capacity",
                    "max_observed_depth": self._max_queue_depth,
                    "terminal_depth": 0 if self._closed else None,
                    "backpressure_wait_count": self._backpressure_wait_count,
                },
                "worker_count": self._worker_count,
                "worker_records": [
                    dict(self._worker_records[key])
                    for key in sorted(self._worker_records)
                ],
                "submitted_count": self._submitted_count,
                "finished_count": self._finished_count,
                "succeeded_count": self._succeeded_count,
                "failed_count": self._failed_count,
                "admission_count": self._admission_count,
                "max_running_count": self._max_running_count,
                "completion_out_of_order_count": out_of_order,
                "deterministic_admission_policy": "increasing_submission_order",
                "controller_wall_sec": elapsed,
                "evaluation_wall_sec_sum": self._evaluation_wall_sec_sum,
                "observed_wall_clock_compression_ratio": (
                    self._evaluation_wall_sec_sum / elapsed if elapsed > 0 else None
                ),
                "task_record_limit": self._telemetry_limit,
                "task_records": sorted(
                    (dict(record) for record in self._task_records),
                    key=lambda record: record["submission_order"],
                ),
                "task_records_truncated": self._submitted_count > len(self._task_records),
                "admission_records": list(self._admission_records),
                "admission_records_truncated": (
                    self._admission_count > len(self._admission_records)
                ),
                "pending_work": {
                    "queued_evaluations": 0 if self._closed else None,
                    "running_evaluations": 0 if self._closed else self._running_count,
                    "pending_admissions": 0 if self._closed else None,
                },
                "claim_ready": False,
                "claim_readiness": {
                    "python_asyncio_controller": started_at is not None,
                    "bounded_candidate_evaluation_queue": started_at is not None,
                    "candidate_evaluator_worker_identities": (
                        len(self._worker_records) == self._worker_count
                    ),
                    "deterministic_admission_order": self._closed,
                    "concurrent_llm_sampler_workers": False,
                    "distributed_evaluator_nodes": False,
                    "pending_work_resume": False,
                    "remaining_gap": [
                        "concurrent_llm_sampler_queue",
                        "distributed_evaluator_nodes",
                        "pending_work_checkpoint_and_resume",
                        "provider_output_replay",
                        "cross_process_shared_state_coordination",
                    ],
                },
            }
        report["validation"] = validate_async_evaluation_controller_report(report)
        return report

    async def _enqueue(
        self,
        job: AsyncEvaluationJob,
        result_future: Future[AsyncEvaluationOutcome],
    ) -> None:
        queue = self._queue
        capacity = self._queue_capacity_sem
        if queue is None or capacity is None:
            raise RuntimeError("async evaluation queue is unavailable")
        submitted_at = time.perf_counter()
        started_wait = submitted_at
        await capacity.acquire()
        queue_wait_sec = max(0.0, time.perf_counter() - started_wait)
        depth = queue.qsize() + 1
        queue.put_nowait(
            _QueuedEvaluation(
                job=job,
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
        queue = self._queue
        capacity = self._queue_capacity_sem
        if queue is None or capacity is None:
            raise RuntimeError("async evaluation queue is unavailable")
        worker_id = f"candidate_evaluator:local:{worker_index:03d}"
        with self._lock:
            self._worker_records[worker_id] = {
                "worker_id": worker_id,
                "task_name": f"async_evaluator_worker_{worker_index:03d}",
                "runtime": "asyncio_task_with_to_thread_evaluator_call",
                "lifecycle_status": "running",
                "completed_count": 0,
                "failed_count": 0,
            }
        while True:
            item = await queue.get()
            if item is _STOP:
                queue.task_done()
                break
            assert isinstance(item, _QueuedEvaluation)
            capacity.release()
            job = item.job
            task_id = f"candidate_evaluation:{job.sequence:08d}"
            started = time.perf_counter()
            with self._lock:
                self._running_count += 1
                self._max_running_count = max(
                    self._max_running_count,
                    self._running_count,
                )
            status = "succeeded"
            error_type: str | None = None
            try:
                result = await asyncio.to_thread(
                    self._evaluate,
                    job.workspace,
                    job.diff_error,
                )
                if not isinstance(result, EvaluationResult):
                    raise TypeError("async evaluator must return EvaluationResult")
            except BaseException as exc:
                status = "failed"
                error_type = type(exc).__name__
                result = None
                failure = exc
            finished = time.perf_counter()
            evaluation_wall_sec = max(0.0, finished - started)
            with self._lock:
                completion_order = self._completion_counter
                self._completion_counter += 1
                self._finished_count += 1
                self._running_count -= 1
                self._evaluation_wall_sec_sum += evaluation_wall_sec
                self._completion_sequences.append(job.sequence)
                worker = self._worker_records[worker_id]
                worker["completed_count"] += 1
                if status == "succeeded":
                    self._succeeded_count += 1
                else:
                    self._failed_count += 1
                    worker["failed_count"] += 1
                execution = {
                    "schema": ASYNC_EVALUATION_EXECUTION_SCHEMA,
                    "task_id": task_id,
                    "candidate_id": job.candidate_id,
                    "submission_order": job.sequence,
                    "completion_order": completion_order,
                    "worker_id": worker_id,
                    "status": status,
                    "queue_wait_sec": item.queue_wait_sec,
                    "queue_depth_after_submit": item.queue_depth_after_submit,
                    "started_monotonic_sec": started,
                    "finished_monotonic_sec": finished,
                    "evaluation_wall_sec": evaluation_wall_sec,
                    "error_type": error_type,
                }
                self._task_records.append(dict(execution))
            if status == "succeeded":
                assert result is not None
                item.result_future.set_result(
                    AsyncEvaluationOutcome(result=result, execution=execution)
                )
            else:
                item.result_future.set_exception(failure)
            queue.task_done()
        with self._lock:
            self._worker_records[worker_id]["lifecycle_status"] = "stopped"

    async def _shutdown(self) -> None:
        queue = self._queue
        if queue is None:
            return
        await queue.join()
        for _ in self._workers:
            await queue.put(_STOP)
        await asyncio.gather(*self._workers)

    def _thread_main(self) -> None:
        loop: asyncio.AbstractEventLoop | None = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            queue: asyncio.Queue[object] = asyncio.Queue(
                maxsize=self._queue_capacity
            )
            capacity = asyncio.Semaphore(self._queue_capacity)
            workers = [
                loop.create_task(
                    self._worker(index),
                    name=f"async_evaluator_worker_{index:03d}",
                )
                for index in range(self._worker_count)
            ]
            with self._lock:
                self._loop = loop
                self._queue = queue
                self._queue_capacity_sem = capacity
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


def validate_async_evaluation_controller_report(report: object) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    if not isinstance(report, Mapping):
        return {
            "schema": ASYNC_EVALUATION_CONTROLLER_SCHEMA,
            "ok": False,
            "issues": [
                {"code": "invalid_report", "message": "report must be a mapping"}
            ],
        }
    if report.get("schema") != ASYNC_EVALUATION_CONTROLLER_SCHEMA:
        issues.append({"code": "invalid_schema", "message": "unsupported schema"})
    if report.get("status") != "terminal_async_evaluation_controller_drained":
        issues.append(
            {
                "code": "invalid_status",
                "message": "validated controller report must be terminal and drained",
            }
        )
    if report.get("controller_model") != (
        "single_process_asyncio_candidate_evaluation"
    ):
        issues.append(
            {"code": "invalid_controller_model", "message": "unsupported controller model"}
        )
    worker_count = _report_non_negative_int(report.get("worker_count"))
    workers = report.get("worker_records")
    if worker_count is None or worker_count < 1 or not isinstance(workers, list):
        issues.append({"code": "invalid_workers", "message": "worker records are invalid"})
        workers = []
    elif len(workers) != worker_count:
        issues.append({"code": "worker_count_mismatch", "message": "worker count drifted"})
    for worker in workers:
        if not isinstance(worker, Mapping) or worker.get("lifecycle_status") != "stopped":
            issues.append(
                {"code": "worker_not_stopped", "message": "all workers must be stopped"}
            )
    queue = report.get("queue")
    if not isinstance(queue, Mapping):
        issues.append({"code": "invalid_queue", "message": "queue record is invalid"})
    else:
        if _report_non_negative_int(queue.get("capacity")) in {None, 0}:
            issues.append({"code": "invalid_queue_capacity", "message": "queue capacity is invalid"})
        if queue.get("terminal_depth") != 0:
            issues.append({"code": "queue_not_drained", "message": "terminal queue must be empty"})
    submitted = _report_non_negative_int(report.get("submitted_count"))
    finished = _report_non_negative_int(report.get("finished_count"))
    succeeded = _report_non_negative_int(report.get("succeeded_count"))
    failed = _report_non_negative_int(report.get("failed_count"))
    if None in {submitted, finished, succeeded, failed}:
        issues.append({"code": "invalid_counts", "message": "controller counts are invalid"})
    elif submitted != finished or finished != succeeded + failed:
        issues.append({"code": "count_mismatch", "message": "controller counts do not reconcile"})
    _validate_task_timings(report.get("task_records"), issues)
    pending = report.get("pending_work")
    if not isinstance(pending, Mapping) or any(
        pending.get(field) != 0
        for field in (
            "queued_evaluations",
            "running_evaluations",
            "pending_admissions",
        )
    ):
        issues.append({"code": "pending_work_not_drained", "message": "pending work must be zero"})
    admissions = report.get("admission_records")
    if not isinstance(admissions, list):
        issues.append({"code": "invalid_admissions", "message": "admission records are invalid"})
    else:
        sequences = [
            row.get("submission_order")
            for row in admissions
            if isinstance(row, Mapping)
        ]
        if sequences != sorted(sequences) or len(sequences) != len(set(sequences)):
            issues.append(
                {
                    "code": "nondeterministic_admission_order",
                    "message": "admissions must follow increasing submission order",
                }
            )
    if report.get("claim_ready") is not False:
        issues.append({"code": "claim_ready_overclaim", "message": "full async parity is not ready"})
    readiness = report.get("claim_readiness")
    if not isinstance(readiness, Mapping):
        issues.append({"code": "invalid_claim_readiness", "message": "claim readiness is invalid"})
    else:
        for field in (
            "concurrent_llm_sampler_workers",
            "distributed_evaluator_nodes",
            "pending_work_resume",
        ):
            if readiness.get(field) is not False:
                issues.append(
                    {"code": f"{field}_overclaim", "message": f"{field} must remain false"}
                )
    return {
        "schema": ASYNC_EVALUATION_CONTROLLER_SCHEMA,
        "ok": not issues,
        "issues": issues,
    }


def _validate_job(job: object) -> None:
    if not isinstance(job, AsyncEvaluationJob):
        raise ValueError("job must be AsyncEvaluationJob")
    if isinstance(job.sequence, bool) or not isinstance(job.sequence, int) or job.sequence < 0:
        raise ValueError("job.sequence must be a non-negative integer")
    if not isinstance(job.candidate_id, str) or not job.candidate_id:
        raise ValueError("job.candidate_id must be non-empty text")
    if not isinstance(job.workspace, CandidateWorkspace):
        raise ValueError("job.workspace must be CandidateWorkspace")


def _positive_int(name: str, value: object, *, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise ValueError(f"{name} must be an integer between 1 and {maximum}")
    return value


def _report_non_negative_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _validate_task_timings(
    records: object,
    issues: list[dict[str, str]],
) -> None:
    if not isinstance(records, list):
        issues.append(
            {"code": "invalid_task_records", "message": "task records are invalid"}
        )
        return
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            issues.append(
                {
                    "code": "invalid_task_record",
                    "message": f"task record {index} is invalid",
                }
            )
            continue
        started = record.get("started_monotonic_sec")
        finished = record.get("finished_monotonic_sec")
        if (
            isinstance(started, bool)
            or not isinstance(started, (int, float))
            or not math.isfinite(float(started))
            or isinstance(finished, bool)
            or not isinstance(finished, (int, float))
            or not math.isfinite(float(finished))
            or float(finished) < float(started)
        ):
            issues.append(
                {
                    "code": "invalid_task_timing",
                    "message": f"task record {index} timing is invalid",
                }
            )
