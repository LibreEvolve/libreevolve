from libreevolve.problems.benchmarks.task_specification_boundary import (
    TASK_SPECIFICATION_BOUNDARY_SCHEMA,
    render_task_specification_boundary_summary,
    task_specification_boundary_record,
    validate_task_specification_boundary,
)


def test_task_specification_boundary_accepts_artifact_resolution_record():
    boundary = task_specification_boundary_record()

    validation = validate_task_specification_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "runtime_artifact_resolution_only"
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 4
    assert boundary["schema"] == TASK_SPECIFICATION_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.1"]
    assert boundary["source_figure_ids"] == ["Figure 2"]
    assert boundary["claim_ready"] is False
    assert "does not claim external-validator score causality" in (
        boundary["claim_boundary"]
    )


def test_task_specification_boundary_rejects_full_parity_overclaim():
    boundary = task_specification_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_task_spec_parity_ready"
    boundary["source_section_ids"] = ["2.2"]
    boundary["source_figure_ids"] = ["Figure 1"]
    boundary["missing_evidence"]["full_alphaevolve_task_spec_parity"] = "recorded"
    boundary["required_evidence_fields"] = ["startup_task_spec_bundle_recorded"]

    validation = validate_task_specification_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_source_figure_ids" in codes
    assert "invalid_missing_evidence_full_alphaevolve_task_spec_parity" in codes
    assert "missing_required_evidence_field" in codes


def test_render_task_specification_boundary_summary_reports_shape():
    summary = render_task_specification_boundary_summary(
        task_specification_boundary_record()
    )

    assert "AlphaEvolve task-specification boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | runtime_artifact_resolution_only |" in summary
    assert "| required_evidence_field_count | 16 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
