from libreevolve.problems.benchmarks.title_page_affiliation_boundary import (
    TITLE_PAGE_AFFILIATION_BOUNDARY_SCHEMA,
    render_title_page_affiliation_boundary_summary,
    title_page_affiliation_boundary_record,
    validate_title_page_affiliation_boundary,
)


def test_title_page_affiliation_boundary_accepts_claim_ready_record():
    boundary = title_page_affiliation_boundary_record()

    validation = validate_title_page_affiliation_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "title_page_affiliation_claim_ready"
    assert validation.required_evidence_field_count == 14
    assert validation.excluded_claim_count == 6
    assert boundary["schema"] == TITLE_PAGE_AFFILIATION_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is True
    assert boundary["source_pages"] == [1]
    assert boundary["affiliation_organization"] == "Google DeepMind"
    assert "does not claim local LibreEvolve affiliation" in boundary["claim_boundary"]


def test_title_page_affiliation_boundary_rejects_scope_drift():
    boundary = title_page_affiliation_boundary_record()
    boundary["claim_ready"] = False
    boundary["boundary_status"] = "local_affiliation_ready"
    boundary["excluded_claims"]["local_libreevolve_affiliation_or_endorsement"] = "claimed"
    boundary["required_evidence_fields"] = ["metadata_present"]
    boundary["required_marker_kinds"] = ["affiliation"]

    validation = validate_title_page_affiliation_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_underclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_excluded_claim_local_libreevolve_affiliation_or_endorsement" in codes
    assert "missing_required_evidence_field" in codes
    assert "invalid_required_marker_kinds" in codes


def test_render_title_page_affiliation_boundary_summary_reports_shape():
    summary = render_title_page_affiliation_boundary_summary(
        title_page_affiliation_boundary_record()
    )

    assert "AlphaEvolve title-page affiliation boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | title_page_affiliation_claim_ready |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| excluded_claim_count | 6 |" in summary
