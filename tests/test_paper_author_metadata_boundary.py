from libreevolve.problems.benchmarks.paper_author_metadata_boundary import (
    PAPER_AUTHOR_METADATA_BOUNDARY_SCHEMA,
    paper_author_metadata_boundary_record,
    render_paper_author_metadata_boundary_summary,
    validate_paper_author_metadata_boundary,
)


def test_paper_author_metadata_boundary_accepts_claim_ready_record():
    boundary = paper_author_metadata_boundary_record()

    validation = validate_paper_author_metadata_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "paper_author_metadata_claim_ready"
    assert validation.required_evidence_field_count == 12
    assert validation.excluded_claim_count == 6
    assert boundary["schema"] == PAPER_AUTHOR_METADATA_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is True
    assert boundary["source_section_ids"] == ["Author information", "Contributions"]
    assert boundary["source_pages"] == [22, 23]
    assert boundary["title_page_marker_linkage"] == "star"
    assert "does not claim technical implementation evidence" in boundary["claim_boundary"]


def test_paper_author_metadata_boundary_rejects_scope_drift():
    boundary = paper_author_metadata_boundary_record()
    boundary["claim_ready"] = False
    boundary["boundary_status"] = "title_page_affiliation_ready"
    boundary["source_section_ids"] = ["Acknowledgements"]
    boundary["excluded_claims"]["title_page_affiliation_metadata"] = "claimed"
    boundary["required_evidence_fields"] = ["metadata_present"]
    boundary["required_role_categories"] = ["equal_contributor"]

    validation = validate_paper_author_metadata_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_underclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_excluded_claim_title_page_affiliation_metadata" in codes
    assert "missing_required_evidence_field" in codes
    assert "missing_required_role_category" in codes


def test_render_paper_author_metadata_boundary_summary_reports_shape():
    summary = render_paper_author_metadata_boundary_summary(
        paper_author_metadata_boundary_record()
    )

    assert "AlphaEvolve paper-author metadata boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | paper_author_metadata_claim_ready |" in summary
    assert "| required_evidence_field_count | 12 |" in summary
    assert "| excluded_claim_count | 6 |" in summary
