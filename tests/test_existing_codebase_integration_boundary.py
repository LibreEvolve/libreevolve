from libreevolve.problems.benchmarks.existing_codebase_integration import (
    EXISTING_CODEBASE_INTEGRATION_BOUNDARY_SCHEMA,
    existing_codebase_integration_boundary_record,
    render_existing_codebase_integration_boundary_summary,
    validate_existing_codebase_integration_boundary,
)


def test_existing_codebase_integration_boundary_accepts_absence_record():
    boundary = existing_codebase_integration_boundary_record()

    validation = validate_existing_codebase_integration_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "not_recorded_at_source_setup_level"
    assert validation.required_evidence_field_count == 10
    assert validation.missing_evidence_count == 9
    assert boundary["schema"] == EXISTING_CODEBASE_INTEGRATION_BOUNDARY_SCHEMA
    assert "does not claim AlphaEvolve-style minimal-change integration" in boundary["claim_boundary"]


def test_existing_codebase_integration_boundary_rejects_premature_claim():
    boundary = existing_codebase_integration_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "recorded"
    boundary["missing_evidence"]["pre_marker_source_hashes"] = "recorded"
    boundary["required_evidence_fields"] = ["original_codebase_id"]

    validation = validate_existing_codebase_integration_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_pre_marker_source_hashes" in codes
    assert "missing_required_evidence_field" in codes


def test_render_existing_codebase_integration_boundary_summary_reports_shape():
    summary = render_existing_codebase_integration_boundary_summary(
        existing_codebase_integration_boundary_record()
    )

    assert "AlphaEvolve existing-codebase integration boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | not_recorded_at_source_setup_level |" in summary
    assert "| required_evidence_field_count | 10 |" in summary
    assert "| missing_evidence_count | 9 |" in summary
