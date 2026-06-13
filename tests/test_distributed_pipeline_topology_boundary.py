from libreevolve.problems.benchmarks.distributed_pipeline_topology_boundary import (
    DISTRIBUTED_PIPELINE_TOPOLOGY_BOUNDARY_SCHEMA,
    distributed_pipeline_topology_boundary_record,
    render_distributed_pipeline_topology_boundary_summary,
    validate_distributed_pipeline_topology_boundary,
)


def test_distributed_pipeline_topology_boundary_accepts_absence_record():
    boundary = distributed_pipeline_topology_boundary_record()

    validation = validate_distributed_pipeline_topology_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "single_process_synchronous_topology"
    assert validation.required_evidence_field_count == 11
    assert validation.missing_evidence_count == 8
    assert boundary["schema"] == DISTRIBUTED_PIPELINE_TOPOLOGY_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.6"]
    assert "does not claim AlphaEvolve-style Python asyncio" in boundary["claim_boundary"]


def test_distributed_pipeline_topology_boundary_rejects_premature_topology_claim():
    boundary = distributed_pipeline_topology_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "async_distributed_topology_ready"
    boundary["source_section_ids"] = ["2.4"]
    boundary["missing_evidence"]["async_controller_queues"] = "recorded"
    boundary["required_evidence_fields"] = ["controller_node_identity"]

    validation = validate_distributed_pipeline_topology_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_async_controller_queues" in codes
    assert "missing_required_evidence_field" in codes


def test_render_distributed_pipeline_topology_boundary_summary_reports_shape():
    summary = render_distributed_pipeline_topology_boundary_summary(
        distributed_pipeline_topology_boundary_record()
    )

    assert "AlphaEvolve distributed-pipeline topology boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | single_process_synchronous_topology |" in summary
    assert "| required_evidence_field_count | 11 |" in summary
    assert "| missing_evidence_count | 8 |" in summary
