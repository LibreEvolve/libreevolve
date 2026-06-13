from libreevolve.problems.benchmarks.acknowledgement_role_provenance_boundary import (
    ACKNOWLEDGEMENT_ROLE_PROVENANCE_BOUNDARY_SCHEMA,
    acknowledgement_role_provenance_boundary_record,
    render_acknowledgement_role_provenance_boundary_summary,
    validate_acknowledgement_role_provenance_boundary,
)


def test_acknowledgement_role_provenance_boundary_accepts_claim_ready_record():
    boundary = acknowledgement_role_provenance_boundary_record()

    validation = validate_acknowledgement_role_provenance_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "acknowledgement_role_claim_ready"
    assert validation.required_evidence_field_count == 10
    assert validation.excluded_claim_count == 6
    assert boundary["schema"] == ACKNOWLEDGEMENT_ROLE_PROVENANCE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is True
    assert boundary["source_section_ids"] == ["Acknowledgements"]
    assert boundary["source_pages"] == [21, 22]
    assert "does not claim benchmark success" in boundary["claim_boundary"]


def test_acknowledgement_role_provenance_boundary_rejects_scope_drift():
    boundary = acknowledgement_role_provenance_boundary_record()
    boundary["claim_ready"] = False
    boundary["boundary_status"] = "publication_author_ready"
    boundary["source_section_ids"] = ["Contributions"]
    boundary["excluded_claims"]["publication_author_metadata"] = "claimed"
    boundary["required_evidence_fields"] = ["metadata_present"]
    boundary["required_role_categories"] = ["white_paper_review"]

    validation = validate_acknowledgement_role_provenance_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_underclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_excluded_claim_publication_author_metadata" in codes
    assert "missing_required_evidence_field" in codes
    assert "missing_required_role_category" in codes


def test_render_acknowledgement_role_provenance_boundary_summary_reports_shape():
    summary = render_acknowledgement_role_provenance_boundary_summary(
        acknowledgement_role_provenance_boundary_record()
    )

    assert "AlphaEvolve acknowledgement-role provenance boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | acknowledgement_role_claim_ready |" in summary
    assert "| required_evidence_field_count | 10 |" in summary
    assert "| excluded_claim_count | 6 |" in summary
