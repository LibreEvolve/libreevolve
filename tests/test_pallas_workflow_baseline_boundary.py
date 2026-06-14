from libreevolve.problems.benchmarks.pallas_workflow_baseline_boundary import (
    PALLAS_WORKFLOW_BASELINE_BOUNDARY_SCHEMA,
    pallas_workflow_baseline_boundary_record,
    render_pallas_workflow_baseline_boundary_summary,
    validate_pallas_workflow_baseline_boundary,
)


def test_pallas_workflow_baseline_boundary_accepts_runtime_only_boundary():
    boundary = pallas_workflow_baseline_boundary_record()

    validation = validate_pallas_workflow_baseline_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "pallas_runtime_without_workflow_baseline_evidence"
    )
    assert validation.required_evidence_field_count == 18
    assert validation.missing_evidence_count == 16
    assert boundary["schema"] == PALLAS_WORKFLOW_BASELINE_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.3.2"]
    assert boundary["claim_ready"] is False
    assert "does not claim baseline workflow class records" in boundary["claim_boundary"]


def test_pallas_workflow_baseline_boundary_rejects_workflow_overclaim():
    boundary = pallas_workflow_baseline_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "pallas_workflow_baseline_ready"
    boundary["missing_evidence"]["baseline_workflow_class"] = "recorded"
    boundary["required_evidence_fields"] = ["kernel_shape_corpus_boundary"]

    validation = validate_pallas_workflow_baseline_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_baseline_workflow_class" in codes
    assert "missing_required_evidence_field" in codes


def test_render_pallas_workflow_baseline_boundary_summary_reports_shape():
    summary = render_pallas_workflow_baseline_boundary_summary(
        pallas_workflow_baseline_boundary_record()
    )

    assert "Pallas workflow baseline boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | pallas_runtime_without_workflow_baseline_evidence |"
        in summary
    )
    assert "| required_evidence_field_count | 18 |" in summary
    assert "| missing_evidence_count | 16 |" in summary
