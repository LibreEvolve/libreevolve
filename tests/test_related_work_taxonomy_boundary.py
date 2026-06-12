from libreevolve.problems.benchmarks.related_work_taxonomy_boundary import (
    RELATED_WORK_TAXONOMY_BOUNDARY_SCHEMA,
    related_work_taxonomy_boundary_record,
    render_related_work_taxonomy_boundary_summary,
    validate_related_work_taxonomy_boundary,
)


def test_related_work_taxonomy_boundary_accepts_flat_inventory_boundary():
    boundary = related_work_taxonomy_boundary_record()

    validation = validate_related_work_taxonomy_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "paper_index_rows_without_related_work_taxonomy"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 11
    assert boundary["schema"] == RELATED_WORK_TAXONOMY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "does not claim a Related Work taxonomy" in boundary["claim_boundary"]


def test_related_work_taxonomy_boundary_rejects_positioning_overclaim():
    boundary = related_work_taxonomy_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "related_work_taxonomy_ready"
    boundary["missing_evidence"]["method_family_taxonomy"] = "recorded"
    boundary["required_evidence_fields"] = ["source_paper_inventory"]

    validation = validate_related_work_taxonomy_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_method_family_taxonomy" in codes
    assert "missing_required_evidence_field" in codes


def test_render_related_work_taxonomy_boundary_summary_reports_shape():
    summary = render_related_work_taxonomy_boundary_summary(
        related_work_taxonomy_boundary_record()
    )

    assert "Related Work taxonomy boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | paper_index_rows_without_related_work_taxonomy |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 11 |" in summary
