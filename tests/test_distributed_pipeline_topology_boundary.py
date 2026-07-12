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
    assert validation.boundary_status == "local_candidate_async_evaluation_partial"
    assert validation.required_evidence_field_count == 17
    assert validation.missing_evidence_count == 8
    assert boundary["schema"] == DISTRIBUTED_PIPELINE_TOPOLOGY_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.6"]
    assert "async_task_coroutine_identity" in boundary["required_evidence_fields"]
    assert "scheduler_state_snapshot" in boundary["required_evidence_fields"]
    assert (
        boundary["implemented_evidence"]["deterministic_candidate_admission_order"]
        == "submission_order_merge_recorded"
    )
    assert "bounded queue on a Python asyncio event loop" in boundary["claim_boundary"]
    assert "does not claim concurrent LLM sampler workers" in boundary["claim_boundary"]


def test_distributed_pipeline_topology_boundary_rejects_premature_topology_claim():
    boundary = distributed_pipeline_topology_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "async_distributed_topology_ready"
    boundary["source_section_ids"] = ["2.4"]
    boundary["missing_evidence"]["concurrent_llm_sampler_worker_nodes"] = "recorded"
    boundary["implemented_evidence"]["python_asyncio_runtime"] = "distributed"
    boundary["required_evidence_fields"] = ["controller_node_identity"]

    validation = validate_distributed_pipeline_topology_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_concurrent_llm_sampler_worker_nodes" in codes
    assert "invalid_implemented_evidence" in codes
    assert "missing_required_evidence_field" in codes


def test_render_distributed_pipeline_topology_boundary_summary_reports_shape():
    summary = render_distributed_pipeline_topology_boundary_summary(
        distributed_pipeline_topology_boundary_record()
    )

    assert "AlphaEvolve distributed-pipeline topology boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | local_candidate_async_evaluation_partial |" in summary
    assert "| required_evidence_field_count | 17 |" in summary
    assert "| missing_evidence_count | 8 |" in summary
