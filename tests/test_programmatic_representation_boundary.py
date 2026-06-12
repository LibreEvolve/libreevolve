from libreevolve.problems.benchmarks.programmatic_representation_boundary import (
    PROGRAMMATIC_REPRESENTATION_BOUNDARY_SCHEMA,
    programmatic_representation_boundary_record,
    render_programmatic_representation_boundary_summary,
    validate_programmatic_representation_boundary,
)


def test_programmatic_representation_boundary_accepts_structural_boundary():
    boundary = programmatic_representation_boundary_record()

    validation = validate_programmatic_representation_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "executable_code_representation_without_hallucination_or_bridge_evidence"
    )
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == PROGRAMMATIC_REPRESENTATION_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "does not claim hallucination-risk measurement" in boundary["claim_boundary"]


def test_programmatic_representation_boundary_rejects_bridge_overclaim():
    boundary = programmatic_representation_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "ai_coscientist_bridge_ready"
    boundary["missing_evidence"]["natural_language_to_programmatic_bridge_status"] = (
        "recorded"
    )
    boundary["required_evidence_fields"] = [
        "executable_code_workspace_candidate_representation"
    ]

    validation = validate_programmatic_representation_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert (
        "invalid_missing_evidence_natural_language_to_programmatic_bridge_status"
        in codes
    )
    assert "missing_required_evidence_field" in codes


def test_render_programmatic_representation_boundary_summary_reports_shape():
    summary = render_programmatic_representation_boundary_summary(
        programmatic_representation_boundary_record()
    )

    assert "Programmatic representation boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | executable_code_representation_without_hallucination_or_bridge_evidence |"
        in summary
    )
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
