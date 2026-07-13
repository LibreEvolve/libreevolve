from libreevolve.problems.benchmarks.parallel_evaluation_readiness_boundary import (
    PARALLEL_EVALUATION_READINESS_BOUNDARY_SCHEMA,
    parallel_evaluation_readiness_boundary_record,
    render_parallel_evaluation_readiness_boundary_summary,
    validate_parallel_evaluation_readiness_boundary,
)


def test_parallel_evaluation_readiness_boundary_accepts_local_async_partial_record():
    boundary = parallel_evaluation_readiness_boundary_record()

    validation = validate_parallel_evaluation_readiness_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "local_cross_generation_async_pipeline_partial"
    )
    assert validation.required_evidence_field_count == 17
    assert validation.missing_evidence_count == 9
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
        boundary["implemented_evidence"]["candidate_level_async_evaluation_queue"]
        == "bounded_local_asyncio_queue"
    )
    assert (
        boundary["implemented_evidence"]["concurrent_llm_sampler_queue"]
        == "bounded_local_asyncio_queue"
    )
    assert "bounded local asyncio LLM proposal queue" in boundary["claim_boundary"]
    assert "does not claim AlphaEvolve-style" in boundary["claim_boundary"]
    assert (
        boundary["implemented_evidence"]["cross_generation_overlap_telemetry"]
        == "process_local_exact_merged_sampler_evaluator_task_interval_union_intersection"
    )
    assert boundary["implemented_evidence"][
        "cross_generation_detailed_evaluator_budget_guard"
    ] == "finite_non_evaluation_count_evaluator_limits_retain_generation_barrier"


def test_parallel_evaluation_readiness_boundary_rejects_premature_readiness_claim():
    boundary = parallel_evaluation_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "async_parallel_evaluation_ready"
    boundary["missing_evidence"]["distributed_evaluator_worker_nodes"] = "recorded"
    boundary["implemented_evidence"]["shared_state_mutation_policy"] = "parallel"
    boundary["required_evidence_fields"] = ["local_stage_sample_worker_fanout"]

    validation = validate_parallel_evaluation_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_distributed_evaluator_worker_nodes" in codes
    assert "invalid_implemented_evidence" in codes
    assert "missing_required_evidence_field" in codes


def test_render_parallel_evaluation_readiness_boundary_summary_reports_shape():
    summary = render_parallel_evaluation_readiness_boundary_summary(
        parallel_evaluation_readiness_boundary_record()
    )

    assert "AlphaEvolve parallel-evaluation readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | "
        "local_cross_generation_async_pipeline_partial |"
        in summary
    )
    assert "| required_evidence_field_count | 17 |" in summary
    assert "| missing_evidence_count | 9 |" in summary
