from libreevolve.problems.benchmarks.figure6_scheduling_exhibit_boundary import (
    FIGURE6_SCHEDULING_EXHIBIT_BOUNDARY_SCHEMA,
    figure6_scheduling_exhibit_boundary_record,
    render_figure6_scheduling_exhibit_boundary_summary,
    validate_figure6_scheduling_exhibit_boundary,
)


def test_figure6_scheduling_exhibit_boundary_accepts_required_contract():
    boundary = figure6_scheduling_exhibit_boundary_record()

    validation = validate_figure6_scheduling_exhibit_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "required_exhibit_contract_without_artifacts"
    assert validation.required_evidence_field_count == 20
    assert validation.missing_evidence_count == 20
    assert boundary["schema"] == FIGURE6_SCHEDULING_EXHIBIT_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["Figure 6", "3.3.1"]
    assert boundary["claim_ready"] is False
    assert "does not claim a stable exhibit row" in boundary["claim_boundary"]


def test_figure6_scheduling_exhibit_boundary_rejects_artifact_overclaim():
    boundary = figure6_scheduling_exhibit_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "figure6_exhibit_artifacts_ready"
    boundary["missing_evidence"]["rendered_heatmap_artifact_hash"] = "recorded"
    boundary["required_evidence_fields"] = ["stable_exhibit_id"]

    validation = validate_figure6_scheduling_exhibit_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_rendered_heatmap_artifact_hash" in codes
    assert "missing_required_evidence_field" in codes


def test_render_figure6_scheduling_exhibit_boundary_summary_reports_shape():
    summary = render_figure6_scheduling_exhibit_boundary_summary(
        figure6_scheduling_exhibit_boundary_record()
    )

    assert "Figure 6 scheduling exhibit boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | required_exhibit_contract_without_artifacts |" in summary
    assert "| required_evidence_field_count | 20 |" in summary
    assert "| missing_evidence_count | 20 |" in summary
