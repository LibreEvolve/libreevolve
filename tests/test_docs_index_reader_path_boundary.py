from libreevolve.problems.benchmarks.docs_index_reader_path_boundary import (
    DOCS_INDEX_READER_PATH_BOUNDARY_SCHEMA,
    docs_index_reader_path_boundary_record,
    render_docs_index_reader_path_boundary_summary,
    validate_docs_index_reader_path_boundary,
)


def test_docs_index_reader_path_boundary_accepts_current_routes():
    boundary = docs_index_reader_path_boundary_record()

    validation = validate_docs_index_reader_path_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "docs_index_routes_recorded_without_semantic_scope_verifier"
    )
    assert boundary["schema"] == DOCS_INDEX_READER_PATH_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["docs_readme_path"] == "docs/README.md"
    assert validation.route_record_count == 14
    assert boundary["route_group_counts"] == {
        "intro": 1,
        "operational_guide": 3,
        "reader_path": 10,
    }
    assert validation.missing_route_record_count == 0
    assert boundary["missing_route_records"] == []
    assert validation.boundary_marker_count == 7
    assert boundary["missing_boundary_marker_records"] == []
    assert boundary["whole_documentation_cleanup_status"] == "marker_present"
    assert (
        boundary["docs_index_marker_status"]
        == "docs_index_routes_and_boundary_markers_present"
    )
    assert boundary["missing_evidence"] == {
        "route_purpose_semantic_verifier": "not_recorded_locally",
        "target_scope_agreement_verifier": "not_recorded_locally",
        "new_major_doc_detector": "not_recorded_locally",
        "misplaced_claim_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "docs/README reader paths" in boundary["claim_boundary"]


def test_docs_index_reader_path_boundary_rejects_overclaim_and_missing_route():
    boundary = docs_index_reader_path_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "docs_index_semantic_scope_verified"
    boundary["missing_route_record_count"] = 1
    boundary["missing_route_records"] = [boundary["route_records"][0]]
    boundary["route_records"][0]["route_status"] = "route_target_or_markers_missing"
    boundary["missing_boundary_marker_count"] = 1
    boundary["missing_boundary_marker_records"] = [boundary["boundary_marker_records"][0]]
    boundary["boundary_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["whole_documentation_cleanup_status"] = "marker_missing"
    boundary["docs_index_marker_status"] = "docs_index_routes_or_boundary_markers_incomplete"
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["docs_index_reader_path_inventory"]

    validation = validate_docs_index_reader_path_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_route_record_count" in codes
    assert "invalid_missing_route_records" in codes
    assert "invalid_route_records" in codes
    assert "invalid_missing_boundary_marker_count" in codes
    assert "invalid_missing_boundary_marker_records" in codes
    assert "invalid_boundary_marker_records" in codes
    assert "missing_docs_index_route" in codes
    assert "missing_docs_index_boundary_marker" in codes
    assert "missing_whole_documentation_cleanup_marker" in codes
    assert "invalid_docs_index_marker_status" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_docs_index_reader_path_boundary_summary_reports_shape():
    summary = render_docs_index_reader_path_boundary_summary(
        docs_index_reader_path_boundary_record()
    )

    assert "Docs index reader-path boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | docs_index_routes_recorded_without_semantic_scope_verifier |"
        in summary
    )
    assert "| route_record_count | 14 |" in summary
    assert "| missing_route_record_count | 0 |" in summary
    assert "| boundary_marker_count | 7 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
