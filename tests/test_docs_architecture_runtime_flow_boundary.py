from libreevolve.problems.benchmarks.docs_architecture_runtime_flow_boundary import (
    DOCS_ARCHITECTURE_RUNTIME_FLOW_BOUNDARY_SCHEMA,
    docs_architecture_runtime_flow_boundary_record,
    render_docs_architecture_runtime_flow_boundary_summary,
    validate_docs_architecture_runtime_flow_boundary,
)


def test_docs_architecture_runtime_flow_boundary_accepts_current_guide():
    boundary = docs_architecture_runtime_flow_boundary_record()

    validation = validate_docs_architecture_runtime_flow_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "docs_architecture_runtime_flow_recorded_without_semantic_flow_verifier"
    )
    assert boundary["schema"] == DOCS_ARCHITECTURE_RUNTIME_FLOW_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["architecture_path"] == "docs/architecture.md"
    assert boundary["architecture_heading_status"] == "heading_present"
    assert validation.section_record_count == 10
    assert validation.missing_section_record_count == 0
    assert boundary["missing_section_records"] == []
    assert validation.missing_source_path_count == 0
    assert boundary["missing_source_paths"] == []
    assert boundary["route_record_count"] == 3
    assert boundary["missing_route_record_count"] == 0
    assert boundary["missing_route_records"] == []
    assert boundary["known_gap_section_status"] == "section_markers_and_sources_present"
    assert boundary["sync_runtime_boundary_status"] == "sync_runtime_boundary_present"
    assert (
        boundary["alphaevolve_parity_boundary_status"]
        == "alphaevolve_parity_boundary_present"
    )
    assert boundary["missing_evidence"] == {
        "flow_order_semantic_verifier": "not_recorded_locally",
        "source_function_semantic_verifier": "not_recorded_locally",
        "runtime_manifest_field_verifier": "not_recorded_locally",
        "architecture_limitation_freshness_matrix": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "docs/architecture.md section headings" in boundary["claim_boundary"]


def test_docs_architecture_runtime_flow_boundary_rejects_overclaim_and_drift():
    boundary = docs_architecture_runtime_flow_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "docs_architecture_runtime_flow_semantically_verified"
    boundary["architecture_heading_status"] = "heading_missing"
    boundary["missing_section_record_count"] = 1
    boundary["missing_section_records"] = [boundary["section_records"][0]]
    boundary["section_records"][0]["section_status"] = "section_markers_or_sources_missing"
    boundary["missing_source_path_count"] = 1
    boundary["missing_source_paths"] = ["libreevolve/core/loop.py"]
    boundary["missing_route_record_count"] = 1
    boundary["missing_route_records"] = [boundary["route_records"][0]]
    boundary["sync_runtime_boundary_status"] = "sync_runtime_boundary_missing"
    boundary["alphaevolve_parity_boundary_status"] = "alphaevolve_parity_boundary_missing"
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["architecture_section_inventory"]

    validation = validate_docs_architecture_runtime_flow_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_architecture_heading_status" in codes
    assert "missing_architecture_heading" in codes
    assert "invalid_missing_section_record_count" in codes
    assert "invalid_missing_section_records" in codes
    assert "invalid_section_records" in codes
    assert "missing_architecture_section_marker" in codes
    assert "invalid_missing_source_path_count" in codes
    assert "missing_architecture_source_path" in codes
    assert "invalid_missing_route_record_count" in codes
    assert "missing_architecture_route_marker" in codes
    assert "missing_sync_runtime_boundary" in codes
    assert "missing_alphaevolve_parity_boundary" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_docs_architecture_runtime_flow_boundary_summary_reports_shape():
    summary = render_docs_architecture_runtime_flow_boundary_summary(
        docs_architecture_runtime_flow_boundary_record()
    )

    assert "Docs architecture runtime-flow boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | docs_architecture_runtime_flow_recorded_without_semantic_flow_verifier |"
        in summary
    )
    assert "| section_record_count | 10 |" in summary
    assert "| missing_section_record_count | 0 |" in summary
    assert "| missing_source_path_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
