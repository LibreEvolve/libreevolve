from libreevolve.problems.benchmarks.release_checklist_documentation_boundary import (
    RELEASE_CHECKLIST_DOCUMENTATION_BOUNDARY_SCHEMA,
    release_checklist_documentation_boundary_record,
    render_release_checklist_documentation_boundary_summary,
    validate_release_checklist_documentation_boundary,
)


def test_release_checklist_documentation_boundary_accepts_current_static_record():
    boundary = release_checklist_documentation_boundary_record()

    validation = validate_release_checklist_documentation_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "release_checklist_static_drift_record_without_signed_release_proof"
    )
    assert boundary["schema"] == RELEASE_CHECKLIST_DOCUMENTATION_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert validation.required_local_evidence_count == 6
    assert validation.outside_scope_count == 3
    assert validation.workflow_marker_count == 14
    assert validation.provenance_tool_marker_count == 8
    assert validation.evidence_anchor_count == 8
    assert validation.missing_marker_count == 0
    assert validation.missing_evidence_count == 6
    assert boundary["missing_marker_records"] == []
    assert boundary["missing_evidence"] == {
        "per_checklist_bullet_to_workflow_step_map": "not_recorded_locally",
        "provenance_schema_field_map": "not_recorded_locally",
        "signed_release_provenance": "not_recorded_locally",
        "published_index_verification": "not_recorded_locally",
        "maintainer_release_event": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "Build exactly one wheel" in boundary["required_local_evidence_bullets"][0]
    assert "Signed release provenance" in boundary["outside_scope_bullets"][0]
    assert "static release-checklist documentation evidence" in boundary["claim_boundary"]
    assert "signed release provenance" in boundary["claim_boundary"]


def test_release_checklist_documentation_boundary_rejects_overclaim_and_drift():
    boundary = release_checklist_documentation_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "release_checklist_signed_release_ready"
    boundary["required_local_evidence_count"] = 0
    boundary["required_local_evidence_bullets"] = []
    boundary["outside_scope_count"] = 0
    boundary["workflow_marker_count"] = 0
    boundary["workflow_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["missing_marker_count"] = 1
    boundary["missing_marker_records"] = [boundary["workflow_marker_records"][0]]
    boundary["missing_evidence"]["signed_release_provenance"] = "recorded"
    boundary["required_evidence_fields"] = ["release_checklist_required_local_evidence_bullets"]

    validation = validate_release_checklist_documentation_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_required_local_evidence_count" in codes
    assert "invalid_required_local_evidence_bullets" in codes
    assert "invalid_outside_scope_count" in codes
    assert "invalid_workflow_marker_count" in codes
    assert "invalid_workflow_marker_records" in codes
    assert "invalid_missing_marker_count" in codes
    assert "invalid_missing_marker_records" in codes
    assert "missing_release_checklist_marker" in codes
    assert "invalid_missing_evidence_signed_release_provenance" in codes
    assert "missing_required_evidence_field" in codes


def test_render_release_checklist_documentation_boundary_summary_reports_shape():
    summary = render_release_checklist_documentation_boundary_summary(
        release_checklist_documentation_boundary_record()
    )

    assert "Release checklist documentation boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | release_checklist_static_drift_record_without_signed_release_proof |"
        in summary
    )
    assert "| required_local_evidence_count | 6 |" in summary
    assert "| outside_scope_count | 3 |" in summary
    assert "| workflow_marker_count | 14 |" in summary
    assert "| provenance_tool_marker_count | 8 |" in summary
    assert "| evidence_anchor_count | 8 |" in summary
    assert "| missing_marker_count | 0 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
