from libreevolve.problems.benchmarks.self_improvement_cadence_boundary import (
    SELF_IMPROVEMENT_CADENCE_BOUNDARY_SCHEMA,
    render_self_improvement_cadence_boundary_summary,
    self_improvement_cadence_boundary_record,
    validate_self_improvement_cadence_boundary,
)


def test_self_improvement_cadence_boundary_accepts_absence_record():
    boundary = self_improvement_cadence_boundary_record()

    validation = validate_self_improvement_cadence_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "cadence_environment_roi_not_recorded"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 14
    assert boundary["schema"] == SELF_IMPROVEMENT_CADENCE_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["Discussion"]
    assert boundary["local_pdf_page"] == 21
    assert "months-scale" in boundary["claim_boundary"]
    assert "expected-versus-realized discovery value" in boundary["claim_boundary"]


def test_self_improvement_cadence_boundary_rejects_premature_claim():
    boundary = self_improvement_cadence_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "cadence_roi_ready"
    boundary["source_section_ids"] = ["Section 3"]
    boundary["missing_evidence"]["environment_setup_cost"] = "recorded"
    boundary["required_evidence_fields"] = ["self_improvement_loop_id"]

    validation = validate_self_improvement_cadence_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_environment_setup_cost" in codes
    assert "missing_required_evidence_field" in codes


def test_render_self_improvement_cadence_boundary_summary_reports_shape():
    summary = render_self_improvement_cadence_boundary_summary(
        self_improvement_cadence_boundary_record()
    )

    assert "AlphaEvolve self-improvement cadence boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | cadence_environment_roi_not_recorded |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 14 |" in summary
