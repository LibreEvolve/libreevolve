from libreevolve.problems.benchmarks.parallel_evaluation_readiness_boundary import (
    PARALLEL_EVALUATION_READINESS_BOUNDARY_SCHEMA,
    parallel_evaluation_readiness_boundary_record,
    render_parallel_evaluation_readiness_boundary_summary,
    validate_parallel_evaluation_readiness_boundary,
)


def test_parallel_evaluation_readiness_boundary_accepts_absence_record():
    boundary = parallel_evaluation_readiness_boundary_record()

    validation = validate_parallel_evaluation_readiness_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "local_sample_worker_fanout_only"
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 13
    assert boundary["schema"] == PARALLEL_EVALUATION_READINESS_BOUNDARY_SCHEMA
    assert "hundred_compute_hour_candidate_budget" in boundary["required_evidence_fields"]
    assert "concurrent_llm_sampler_queue" in boundary["required_evidence_fields"]
    assert (
        "deterministic_async_result_merge_order"
        in boundary["required_evidence_fields"]
    )
    assert (
        boundary["missing_evidence"]["generation_cadence_under_slow_feedback_report"]
        == "not_recorded_locally"
    )
    assert (
        boundary["missing_evidence"]["queue_capacity_backpressure_policy"]
        == "not_recorded_locally"
    )
    assert "concurrent LLM sampler queues" in boundary["claim_boundary"]
    assert "does not claim AlphaEvolve-style" in boundary["claim_boundary"]


def test_parallel_evaluation_readiness_boundary_rejects_premature_readiness_claim():
    boundary = parallel_evaluation_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "async_parallel_evaluation_ready"
    boundary["missing_evidence"]["candidate_level_async_evaluation_queue"] = "recorded"
    boundary["required_evidence_fields"] = ["local_stage_sample_worker_fanout"]

    validation = validate_parallel_evaluation_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_candidate_level_async_evaluation_queue" in codes
    assert "missing_required_evidence_field" in codes


def test_render_parallel_evaluation_readiness_boundary_summary_reports_shape():
    summary = render_parallel_evaluation_readiness_boundary_summary(
        parallel_evaluation_readiness_boundary_record()
    )

    assert "AlphaEvolve parallel-evaluation readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | local_sample_worker_fanout_only |" in summary
    assert "| required_evidence_field_count | 16 |" in summary
    assert "| missing_evidence_count | 13 |" in summary
