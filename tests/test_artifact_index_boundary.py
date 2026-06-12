from libreevolve.problems.benchmarks.artifact_index_boundary import (
    ARTIFACT_INDEX_BOUNDARY_SCHEMA,
    artifact_index_boundary_record,
    render_artifact_index_boundary_summary,
    validate_artifact_index_boundary,
)


def test_artifact_index_boundary_accepts_bounded_metadata_boundary():
    boundary = artifact_index_boundary_record()

    validation = validate_artifact_index_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "bounded_artifact_metadata_not_full_content_search"
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == ARTIFACT_INDEX_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "does not claim durable artifact query tables" in boundary["claim_boundary"]


def test_artifact_index_boundary_rejects_full_content_search_overclaim():
    boundary = artifact_index_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_content_artifact_search_ready"
    boundary["missing_evidence"]["full_artifact_content_search"] = "recorded"
    boundary["required_evidence_fields"] = ["runtime_artifact_index"]

    validation = validate_artifact_index_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_full_artifact_content_search" in codes
    assert "missing_required_evidence_field" in codes


def test_render_artifact_index_boundary_summary_reports_shape():
    summary = render_artifact_index_boundary_summary(
        artifact_index_boundary_record()
    )

    assert "Artifact index boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | bounded_artifact_metadata_not_full_content_search |" in summary
    assert "| required_evidence_field_count | 16 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
