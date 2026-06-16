from libreevolve.problems.benchmarks.readme_documentation_map_boundary import (
    README_DOCUMENTATION_MAP_BOUNDARY_SCHEMA,
    readme_documentation_map_boundary_record,
    render_readme_documentation_map_boundary_summary,
    validate_readme_documentation_map_boundary,
)


def test_readme_documentation_map_boundary_accepts_current_routes():
    boundary = readme_documentation_map_boundary_record()

    validation = validate_readme_documentation_map_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_documentation_map_routes_recorded_without_semantic_purpose_verifier"
    )
    assert boundary["schema"] == README_DOCUMENTATION_MAP_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["readme_path"] == "README.md"
    assert validation.route_record_count == 11
    assert validation.missing_route_record_count == 0
    assert boundary["missing_route_records"] == []
    assert boundary["docs_index_delegation_status"] == (
        "route_target_and_markers_present"
    )
    assert boundary["archival_old_route_status"] == "archival_route_present"
    assert boundary["agent_contract_route_status"] == (
        "route_target_and_markers_present"
    )
    assert all(
        record["route_status"] == "route_target_and_markers_present"
        for record in boundary["route_records"]
    )
    assert boundary["missing_evidence"] == {
        "route_purpose_semantic_verifier": "not_recorded_locally",
        "new_major_doc_detector": "not_recorded_locally",
        "misplaced_claim_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "README Documentation Map route inventory" in boundary["claim_boundary"]


def test_readme_documentation_map_boundary_rejects_overclaim_and_missing_route():
    boundary = readme_documentation_map_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "readme_documentation_map_semantically_verified"
    boundary["missing_route_record_count"] = 1
    boundary["missing_route_records"] = [boundary["route_records"][0]]
    boundary["route_records"][0]["route_status"] = "route_target_or_markers_missing"
    boundary["docs_index_delegation_status"] = "route_target_or_markers_missing"
    boundary["archival_old_route_status"] = "archival_route_missing"
    boundary["agent_contract_route_status"] = "route_target_or_markers_missing"
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = [
        "readme_documentation_map_route_inventory"
    ]

    validation = validate_readme_documentation_map_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_route_record_count" in codes
    assert "invalid_missing_route_records" in codes
    assert "invalid_route_records" in codes
    assert "missing_documentation_map_route" in codes
    assert "invalid_docs_index_delegation_status" in codes
    assert "invalid_archival_old_route_status" in codes
    assert "invalid_agent_contract_route_status" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_documentation_map_boundary_summary_reports_shape():
    summary = render_readme_documentation_map_boundary_summary(
        readme_documentation_map_boundary_record()
    )

    assert "README Documentation Map boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_documentation_map_routes_recorded_without_semantic_purpose_verifier |"
        in summary
    )
    assert "| route_record_count | 11 |" in summary
    assert "| missing_route_record_count | 0 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
