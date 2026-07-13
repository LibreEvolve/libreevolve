from libreevolve.problems.benchmarks.distributed_pipeline_topology_boundary import (
    DISTRIBUTED_PIPELINE_TOPOLOGY_BOUNDARY_SCHEMA,
    distributed_pipeline_topology_boundary_record,
    render_distributed_pipeline_topology_boundary_summary,
    validate_distributed_pipeline_topology_boundary,
)


def test_distributed_pipeline_topology_boundary_accepts_local_async_partial_record():
    boundary = distributed_pipeline_topology_boundary_record()

    validation = validate_distributed_pipeline_topology_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "local_cross_generation_async_pipeline_partial"
    )
    assert validation.required_evidence_field_count == 18
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == DISTRIBUTED_PIPELINE_TOPOLOGY_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.6"]
    assert "async_task_coroutine_identity" in boundary["required_evidence_fields"]
    assert "scheduler_state_snapshot" in boundary["required_evidence_fields"]
    assert (
        boundary["implemented_evidence"]["deterministic_candidate_admission_order"]
        == "submission_order_merge_recorded"
    )
    assert "bounded queues on local Python asyncio event loops" in boundary["claim_boundary"]
    assert "Sampler tasks own distinct LLM ensembles" in boundary["claim_boundary"]
    assert (
        boundary["implemented_evidence"][
            "cross_generation_proposal_evaluation_overlap"
        ]
        == "derived_from_exact_merged_task_interval_union_intersection"
    )
    assert boundary["implemented_evidence"][
        "cross_generation_detailed_evaluator_budget_guard"
    ] == "finite_non_evaluation_count_evaluator_limits_retain_generation_barrier"


def test_distributed_pipeline_topology_boundary_rejects_premature_topology_claim():
    boundary = distributed_pipeline_topology_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "async_distributed_topology_ready"
    boundary["source_section_ids"] = ["2.4"]
    boundary["missing_evidence"]["distributed_evaluator_worker_nodes"] = "recorded"
    boundary["implemented_evidence"]["python_asyncio_runtime"] = "distributed"
    boundary["required_evidence_fields"] = ["controller_node_identity"]

    validation = validate_distributed_pipeline_topology_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_distributed_evaluator_worker_nodes" in codes
    assert "invalid_implemented_evidence" in codes
    assert "missing_required_evidence_field" in codes


def test_render_distributed_pipeline_topology_boundary_summary_reports_shape():
    summary = render_distributed_pipeline_topology_boundary_summary(
        distributed_pipeline_topology_boundary_record()
    )

    assert "AlphaEvolve distributed-pipeline topology boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | "
        "local_cross_generation_async_pipeline_partial |"
        in summary
    )
    assert "| required_evidence_field_count | 18 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
