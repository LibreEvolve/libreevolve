from libreevolve.problems.benchmarks.objective_archive_boundary import (
    OBJECTIVE_ARCHIVE_BOUNDARY_SCHEMA,
    objective_archive_boundary_record,
    render_objective_archive_boundary_summary,
    validate_objective_archive_boundary,
)


def test_objective_archive_boundary_accepts_retained_overlay_boundary():
    boundary = objective_archive_boundary_record()

    validation = validate_objective_archive_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "bounded_retained_overlays_not_primary_pareto_archive"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == OBJECTIVE_ARCHIVE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        "does not claim primary Pareto archive replacement"
        in boundary["claim_boundary"]
    )


def test_objective_archive_boundary_rejects_primary_archive_overclaim():
    boundary = objective_archive_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "primary_pareto_archive_replacement_ready"
    boundary["missing_evidence"]["primary_pareto_archive_replacement"] = "recorded"
    boundary["required_evidence_fields"] = ["diagnostic_objective_frontier"]

    validation = validate_objective_archive_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_primary_pareto_archive_replacement" in codes
    assert "missing_required_evidence_field" in codes


def test_render_objective_archive_boundary_summary_reports_shape():
    summary = render_objective_archive_boundary_summary(
        objective_archive_boundary_record()
    )

    assert "Objective archive boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | bounded_retained_overlays_not_primary_pareto_archive |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
