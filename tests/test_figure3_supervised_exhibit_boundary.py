from libreevolve.problems.benchmarks.figure3_supervised_exhibit_boundary import (
    FIGURE3_SUPERVISED_EXHIBIT_BOUNDARY_SCHEMA,
    figure3_supervised_exhibit_boundary_record,
    render_figure3_supervised_exhibit_boundary_summary,
    validate_figure3_supervised_exhibit_boundary,
)


def test_figure3_supervised_exhibit_boundary_accepts_absence_record():
    boundary = figure3_supervised_exhibit_boundary_record()

    validation = validate_figure3_supervised_exhibit_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "figure3_supervised_exhibit_not_reproduced"
    assert validation.required_evidence_field_count == 19
    assert validation.missing_evidence_count == 9
    assert boundary["schema"] == FIGURE3_SUPERVISED_EXHIBIT_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.3"]
    assert boundary["source_subfigure_ids"] == ["Figure 3a", "Figure 3b", "Figure 3c"]
    assert "does not claim reproduced Figure 3" in boundary["claim_boundary"]


def test_figure3_supervised_exhibit_boundary_rejects_premature_exhibit_claim():
    boundary = figure3_supervised_exhibit_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "figure3_supervised_exhibit_reproduced"
    boundary["source_section_ids"] = ["2.4"]
    boundary["missing_evidence"]["llm_output_excerpt_artifact"] = "recorded"
    boundary["required_evidence_fields"] = ["figure_id"]

    validation = validate_figure3_supervised_exhibit_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_llm_output_excerpt_artifact" in codes
    assert "missing_required_evidence_field" in codes


def test_render_figure3_supervised_exhibit_boundary_summary_reports_shape():
    summary = render_figure3_supervised_exhibit_boundary_summary(
        figure3_supervised_exhibit_boundary_record()
    )

    assert "AlphaEvolve Figure 3 supervised-learning exhibit boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | figure3_supervised_exhibit_not_reproduced |" in summary
    assert "| required_evidence_field_count | 19 |" in summary
    assert "| missing_evidence_count | 9 |" in summary
