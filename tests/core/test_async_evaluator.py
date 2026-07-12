from __future__ import annotations

import time

import pytest

from libreevolve.core.async_evaluator import (
    ASYNC_EVALUATION_CONTROLLER_SCHEMA,
    AsyncCandidateEvaluationController,
    AsyncEvaluationJob,
    validate_async_evaluation_controller_report,
)
from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.evaluator import EvaluationResult


def _result(score: float) -> EvaluationResult:
    return EvaluationResult(
        fitness=score,
        metrics={"score": score},
        is_valid=True,
    )


def test_async_controller_runs_workers_and_preserves_admission_order():
    delays = {"candidate-0": 0.06, "candidate-1": 0.01, "candidate-2": 0.03}

    def evaluate(workspace, diff_error):
        assert diff_error is None
        candidate_id = workspace.code
        time.sleep(delays[candidate_id])
        return _result(float(candidate_id[-1]))

    controller = AsyncCandidateEvaluationController(
        evaluate,
        worker_count=2,
        queue_capacity=2,
    )
    futures = [
        controller.submit(
            AsyncEvaluationJob(
                sequence=index,
                candidate_id=f"candidate-{index}",
                workspace=CandidateWorkspace.from_code(f"candidate-{index}"),
                diff_error=None,
            )
        )
        for index in range(3)
    ]

    outcomes = [future.result(timeout=2.0) for future in futures]
    for index, outcome in enumerate(outcomes):
        assert outcome.result.fitness == float(index)
        assert outcome.execution["submission_order"] == index
        controller.record_admission(
            sequence=index,
            source="worker_result",
            task_id=outcome.execution["task_id"],
        )
    report = controller.close()

    assert report["schema"] == ASYNC_EVALUATION_CONTROLLER_SCHEMA
    assert report["status"] == "terminal_async_evaluation_controller_drained"
    assert report["worker_count"] == 2
    assert report["submitted_count"] == 3
    assert report["finished_count"] == 3
    assert report["succeeded_count"] == 3
    assert report["failed_count"] == 0
    assert report["admission_count"] == 3
    assert report["max_running_count"] == 2
    assert report["completion_out_of_order_count"] > 0
    assert [row["submission_order"] for row in report["admission_records"]] == [
        0,
        1,
        2,
    ]
    assert report["pending_work"] == {
        "queued_evaluations": 0,
        "running_evaluations": 0,
        "pending_admissions": 0,
    }
    assert report["validation"]["ok"] is True


def test_async_controller_applies_bounded_queue_backpressure():
    def evaluate(workspace, diff_error):
        time.sleep(0.04)
        return _result(1.0)

    controller = AsyncCandidateEvaluationController(
        evaluate,
        worker_count=1,
        queue_capacity=1,
    )
    futures = [
        controller.submit(
            AsyncEvaluationJob(
                sequence=index,
                candidate_id=f"candidate-{index}",
                workspace=CandidateWorkspace.from_code("x = 1"),
                diff_error=None,
            )
        )
        for index in range(3)
    ]
    for index, future in enumerate(futures):
        outcome = future.result(timeout=2.0)
        controller.record_admission(
            sequence=index,
            source="worker_result",
            task_id=outcome.execution["task_id"],
        )

    report = controller.close()

    assert report["queue"]["capacity"] == 1
    assert report["queue"]["max_observed_depth"] == 1
    assert report["queue"]["backpressure_wait_count"] >= 1
    assert report["validation"]["ok"] is True


def test_async_controller_propagates_evaluator_failure_and_drains():
    def evaluate(workspace, diff_error):
        raise RuntimeError("synthetic evaluator failure")

    controller = AsyncCandidateEvaluationController(
        evaluate,
        worker_count=1,
        queue_capacity=1,
    )
    future = controller.submit(
        AsyncEvaluationJob(
            sequence=0,
            candidate_id="candidate-0",
            workspace=CandidateWorkspace.from_code("x = 1"),
            diff_error=None,
        )
    )

    with pytest.raises(RuntimeError, match="synthetic evaluator failure"):
        future.result(timeout=2.0)
    report = controller.close()

    assert report["submitted_count"] == 1
    assert report["finished_count"] == 1
    assert report["succeeded_count"] == 0
    assert report["failed_count"] == 1
    assert report["task_records"][0]["error_type"] == "RuntimeError"
    assert report["validation"]["ok"] is True


def test_async_controller_rejects_duplicate_submission_and_admission_order():
    controller = AsyncCandidateEvaluationController(
        lambda workspace, diff_error: _result(1.0),
        worker_count=1,
        queue_capacity=1,
    )
    job = AsyncEvaluationJob(
        sequence=1,
        candidate_id="candidate-1",
        workspace=CandidateWorkspace.from_code("x = 1"),
        diff_error=None,
    )
    future = controller.submit(job)

    with pytest.raises(ValueError, match="duplicate async evaluation sequence"):
        controller.submit(job)
    outcome = future.result(timeout=2.0)
    controller.record_admission(
        sequence=1,
        source="worker_result",
        task_id=outcome.execution["task_id"],
    )
    with pytest.raises(ValueError, match="increasing submission order"):
        controller.record_admission(
            sequence=0,
            source="cache_hit",
            task_id=None,
        )
    controller.close()


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"worker_count": 0, "queue_capacity": 1}, "worker_count"),
        ({"worker_count": 1, "queue_capacity": 0}, "queue_capacity"),
        ({"worker_count": True, "queue_capacity": 1}, "worker_count"),
    ],
)
def test_async_controller_rejects_invalid_configuration(kwargs, message):
    with pytest.raises(ValueError, match=message):
        AsyncCandidateEvaluationController(
            lambda workspace, diff_error: _result(1.0),
            **kwargs,
        )


def test_async_controller_report_validator_rejects_overclaim_and_drift():
    controller = AsyncCandidateEvaluationController(
        lambda workspace, diff_error: _result(1.0),
        worker_count=1,
        queue_capacity=1,
    )
    controller.start()
    report = controller.close()
    report["claim_ready"] = True
    report["queue"]["terminal_depth"] = 1
    report["claim_readiness"]["distributed_evaluator_nodes"] = True

    validation = validate_async_evaluation_controller_report(report)
    codes = {issue["code"] for issue in validation["issues"]}

    assert validation["ok"] is False
    assert "queue_not_drained" in codes
    assert "claim_ready_overclaim" in codes
    assert "distributed_evaluator_nodes_overclaim" in codes
