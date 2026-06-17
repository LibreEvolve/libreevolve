from libreevolve.problems.benchmarks.development_workflow_boundary import (
    DEVELOPMENT_WORKFLOW_BOUNDARY_SCHEMA,
    development_workflow_boundary_record,
    render_development_workflow_boundary_summary,
    validate_development_workflow_boundary,
)


def test_development_workflow_boundary_accepts_current_static_inventory():
    boundary = development_workflow_boundary_record()

    validation = validate_development_workflow_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "development_workflow_static_inventory_without_semantic_drift_gate"
    )
    assert boundary["schema"] == DEVELOPMENT_WORKFLOW_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert validation.development_marker_count == 20
    assert validation.runtime_dependency_marker_count == 10
    assert validation.dev_dependency_marker_count == 4
    assert validation.tool_anchor_count == 14
    assert validation.cross_doc_anchor_count == 9
    assert validation.missing_marker_count == 0
    assert validation.missing_evidence_count == 7
    assert boundary["missing_marker_records"] == []
    assert boundary["missing_evidence"] == {
        "per_command_executable_transcripts": "not_recorded_locally",
        "dependency_version_semantic_map": "not_recorded_locally",
        "ci_path_filter_semantic_map": "not_recorded_locally",
        "paper_manifest_fresh_checkout_transcript": "not_recorded_locally",
        "release_smoke_transcript": "not_recorded_locally",
        "repository_convention_source_map": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "static docs/development.md workflow markers" in boundary["claim_boundary"]


def test_development_workflow_boundary_rejects_overclaim_and_drift():
    boundary = development_workflow_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "development_workflow_semantic_drift_gate_ready"
    boundary["development_marker_count"] = 0
    boundary["development_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["runtime_dependency_marker_count"] = 0
    boundary["dev_dependency_marker_count"] = 0
    boundary["tool_anchor_count"] = 0
    boundary["cross_doc_anchor_count"] = 0
    boundary["missing_marker_count"] = 1
    boundary["missing_marker_records"] = [boundary["development_marker_records"][0]]
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["development_doc_workflow_markers"]

    validation = validate_development_workflow_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_development_marker_count" in codes
    assert "invalid_development_marker_records" in codes
    assert "invalid_runtime_dependency_marker_count" in codes
    assert "invalid_dev_dependency_marker_count" in codes
    assert "invalid_tool_anchor_count" in codes
    assert "invalid_cross_doc_anchor_count" in codes
    assert "invalid_missing_marker_count" in codes
    assert "invalid_missing_marker_records" in codes
    assert "missing_development_workflow_marker" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_development_workflow_boundary_summary_reports_shape():
    summary = render_development_workflow_boundary_summary(
        development_workflow_boundary_record()
    )

    assert "Development workflow boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | development_workflow_static_inventory_without_semantic_drift_gate |"
        in summary
    )
    assert "| development_marker_count | 20 |" in summary
    assert "| runtime_dependency_marker_count | 10 |" in summary
    assert "| dev_dependency_marker_count | 4 |" in summary
    assert "| tool_anchor_count | 14 |" in summary
    assert "| cross_doc_anchor_count | 9 |" in summary
    assert "| missing_marker_count | 0 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
