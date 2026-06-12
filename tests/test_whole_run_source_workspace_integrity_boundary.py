from libreevolve.problems.benchmarks.whole_run_source_workspace_integrity_boundary import (
    WHOLE_RUN_SOURCE_WORKSPACE_INTEGRITY_BOUNDARY_SCHEMA,
    render_whole_run_source_workspace_integrity_boundary_summary,
    validate_whole_run_source_workspace_integrity_boundary,
    whole_run_source_workspace_integrity_boundary_record,
)


def test_whole_run_source_workspace_integrity_boundary_accepts_absence_record():
    boundary = whole_run_source_workspace_integrity_boundary_record()

    validation = validate_whole_run_source_workspace_integrity_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "bounded_retained_program_integrity_only"
    assert validation.required_evidence_field_count == 11
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == WHOLE_RUN_SOURCE_WORKSPACE_INTEGRITY_BOUNDARY_SCHEMA
    assert "does not claim a durable whole-run query surface" in boundary["claim_boundary"]


def test_whole_run_source_workspace_integrity_boundary_rejects_premature_database_claim():
    boundary = whole_run_source_workspace_integrity_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "whole_run_database_ready"
    boundary["missing_evidence"]["durable_whole_run_query_surface"] = "recorded"
    boundary["required_evidence_fields"] = ["retained_program_workspace_hashes"]

    validation = validate_whole_run_source_workspace_integrity_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_durable_whole_run_query_surface" in codes
    assert "missing_required_evidence_field" in codes


def test_render_whole_run_source_workspace_integrity_boundary_summary_reports_shape():
    summary = render_whole_run_source_workspace_integrity_boundary_summary(
        whole_run_source_workspace_integrity_boundary_record()
    )

    assert "AlphaEvolve whole-run source/workspace integrity boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | bounded_retained_program_integrity_only |" in summary
    assert "| required_evidence_field_count | 11 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
