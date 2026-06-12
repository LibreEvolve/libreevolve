from libreevolve.problems.benchmarks.fault2flow_boundary import (
    FAULT2FLOW_BOUNDARY_SCHEMA,
    fault2flow_boundary_record,
    render_fault2flow_boundary_summary,
    validate_fault2flow_boundary,
)


def test_fault2flow_boundary_accepts_absence_record():
    boundary = fault2flow_boundary_record()

    validation = validate_fault2flow_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "workflow_automation_context_without_local_fault2flow_benchmark"
    )
    assert validation.component_count == 14
    assert validation.required_evidence_field_count == 24
    assert validation.missing_evidence_count == 20
    assert boundary["schema"] == FAULT2FLOW_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v1"
    assert boundary["source_pdf_date"] == "2025-11-18"
    assert boundary["local_evidence"]["n8n_workflow_builder_ready"] is False
    assert boundary["reported_result"]["success_fault2flow"] == "16/0"
    assert "does not claim regulatory PDF ingestion" in boundary["claim_boundary"]


def test_fault2flow_boundary_rejects_premature_runtime_claims():
    boundary = fault2flow_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][1]["status"] = "verified_local_runtime"
    boundary["framework_components"][8]["local_status"] = "implemented"
    boundary["local_evidence"]["n8n_workflow_builder_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["reported_result"]["dataset_cases"] = 17
    boundary["missing_evidence"]["n8n_workflow_builder"] = "implemented"

    validation = validate_fault2flow_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_n8n_workflow_builder_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "reported_result_dataset_cases_mismatch" in codes
    assert "missing_evidence_mismatch" in codes


def test_render_fault2flow_boundary_summary_reports_shape():
    summary = render_fault2flow_boundary_summary(fault2flow_boundary_record())

    assert "Fault2Flow boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | workflow_automation_context_without_local_fault2flow_benchmark |"
        in summary
    )
    assert "| component_count | 14 |" in summary
