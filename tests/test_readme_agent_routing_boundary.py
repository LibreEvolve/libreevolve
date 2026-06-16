from libreevolve.problems.benchmarks.readme_agent_routing_boundary import (
    README_AGENT_ROUTING_BOUNDARY_SCHEMA,
    readme_agent_routing_boundary_record,
    render_readme_agent_routing_boundary_summary,
    validate_readme_agent_routing_boundary,
)


def test_readme_agent_routing_boundary_accepts_current_routes():
    boundary = readme_agent_routing_boundary_record()

    validation = validate_readme_agent_routing_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "agent_operating_contract_routed_without_full_instruction_drift_map"
    )
    assert boundary["schema"] == README_AGENT_ROUTING_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["readme_path"] == "README.md"
    assert boundary["docs_readme_path"] == "docs/README.md"
    assert boundary["agents_path"] == "AGENTS.md"
    assert boundary["agents_test_path"] == "tests/test_agents_docs.py"
    assert validation.route_record_count == 6
    assert validation.missing_route_count == 0
    assert validation.instruction_link_record_count == 5
    assert validation.missing_instruction_link_count == 0
    assert boundary["routing_status"] == "agents_operating_contract_routed"
    assert all(
        record["record_status"] == "all_markers_present"
        for record in boundary["route_records"]
    )
    assert all(
        record["record_status"] == "all_markers_present"
        for record in boundary["instruction_link_records"]
    )
    assert boundary["missing_evidence"] == {
        "complete_instruction_drift_map": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "README/docs routing for AGENTS.md" in boundary["claim_boundary"]


def test_readme_agent_routing_boundary_rejects_overclaim_and_missing_route():
    boundary = readme_agent_routing_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "agents_instruction_drift_map_complete"
    boundary["missing_route_count"] = 1
    boundary["missing_route_records"] = [boundary["route_records"][0]]
    boundary["route_records"][0]["record_status"] = "markers_missing"
    boundary["missing_instruction_link_count"] = 1
    boundary["missing_instruction_link_records"] = [
        boundary["instruction_link_records"][0]
    ]
    boundary["instruction_link_records"][0]["record_status"] = "markers_missing"
    boundary["routing_status"] = "agents_operating_contract_routing_incomplete"
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_documentation_map_route"]

    validation = validate_readme_agent_routing_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_route_count" in codes
    assert "invalid_missing_route_records" in codes
    assert "invalid_route_records" in codes
    assert "invalid_missing_instruction_link_count" in codes
    assert "invalid_instruction_link_records" in codes
    assert "missing_agent_route" in codes
    assert "missing_instruction_link" in codes
    assert "invalid_routing_status" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_agent_routing_boundary_summary_reports_shape():
    summary = render_readme_agent_routing_boundary_summary(
        readme_agent_routing_boundary_record()
    )

    assert "README AGENTS routing boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | agent_operating_contract_routed_without_full_instruction_drift_map |"
        in summary
    )
    assert "| route_record_count | 6 |" in summary
    assert "| missing_route_count | 0 |" in summary
    assert "| instruction_link_record_count | 5 |" in summary
    assert "| missing_instruction_link_count | 0 |" in summary
    assert "| missing_evidence_count | 2 |" in summary
