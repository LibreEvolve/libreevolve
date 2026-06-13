from libreevolve.problems.benchmarks.collaborator_feedback_provenance_boundary import (
    COLLABORATOR_FEEDBACK_PROVENANCE_BOUNDARY_SCHEMA,
    collaborator_feedback_provenance_boundary_record,
    render_collaborator_feedback_provenance_boundary_summary,
    validate_collaborator_feedback_provenance_boundary,
)


def test_collaborator_feedback_provenance_boundary_accepts_absence_record():
    boundary = collaborator_feedback_provenance_boundary_record()

    validation = validate_collaborator_feedback_provenance_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "metadata_contract_only"
    assert validation.required_evidence_field_count == 26
    assert validation.missing_evidence_count == 15
    assert boundary["schema"] == COLLABORATOR_FEEDBACK_PROVENANCE_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["Acknowledgements"]
    assert "claim_to_feedback_traceability" in boundary["required_evidence_fields"]
    assert boundary["missing_evidence"]["validation_rerun_artifacts"] == (
        "not_recorded_locally"
    )
    assert "does not claim populated representative-fixture" in boundary["claim_boundary"]


def test_collaborator_feedback_provenance_boundary_rejects_premature_parity_claim():
    boundary = collaborator_feedback_provenance_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "collaborator_feedback_ready"
    boundary["source_section_ids"] = ["Contributions"]
    boundary["missing_evidence"]["alphaevolve_collaborator_feedback_parity"] = "recorded"
    boundary["missing_evidence"]["claim_to_feedback_traceability"] = "recorded"
    boundary["required_evidence_fields"] = ["metadata_present"]

    validation = validate_collaborator_feedback_provenance_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_alphaevolve_collaborator_feedback_parity" in codes
    assert "invalid_missing_evidence_claim_to_feedback_traceability" in codes
    assert "missing_required_evidence_field" in codes


def test_render_collaborator_feedback_provenance_boundary_summary_reports_shape():
    summary = render_collaborator_feedback_provenance_boundary_summary(
        collaborator_feedback_provenance_boundary_record()
    )

    assert "AlphaEvolve collaborator-feedback provenance boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | metadata_contract_only |" in summary
    assert "| required_evidence_field_count | 26 |" in summary
    assert "| missing_evidence_count | 15 |" in summary
