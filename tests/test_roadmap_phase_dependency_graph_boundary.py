from libreevolve.problems.benchmarks.roadmap_phase_dependency_graph_boundary import (
    ROADMAP_PHASE_DEPENDENCY_GRAPH_BOUNDARY_SCHEMA,
    render_roadmap_phase_dependency_graph_boundary_summary,
    roadmap_phase_dependency_graph_boundary_record,
    validate_roadmap_phase_dependency_graph_boundary,
)


def test_roadmap_phase_dependency_graph_accepts_bounded_graph():
    boundary = roadmap_phase_dependency_graph_boundary_record()

    validation = validate_roadmap_phase_dependency_graph_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_phase_dependency_graph_recorded_with_phase_workflow"
    )
    assert boundary["schema"] == ROADMAP_PHASE_DEPENDENCY_GRAPH_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_phase_boundary_input"]
        == "papers/roadmap_phase_sequence_boundary.json"
    )
    assert boundary["source_phase_count"] == 3
    assert boundary["source_section_count"] == 10
    assert boundary["source_section_sequence_status"] == (
        "roadmap_major_sections_in_expected_order"
    )
    assert boundary["node_count"] == 10
    assert boundary["edge_count"] == 22
    assert boundary["dependency_record_count"] == 9
    assert boundary["stale_dependency_edge_count"] == 0
    assert boundary["stale_dependency_edges"] == []
    assert boundary["dependency_graph_status"] == "phase_dependency_graph_recorded"
    assert [node["section_id"] for node in boundary["phase_dependency_nodes"]] == [
        "candidate_workspace_fidelity",
        "multi_objective_search",
        "evaluation_cascades",
        "prompt_context",
        "documentation_truthfulness",
        "async_resumable_runtime",
        "backend_scheduling_and_critique",
        "plugin_extensibility",
        "representative_benchmarks",
        "operational_maturity",
    ]
    assert all(
        node["node_status"] == "phase_dependency_node_current"
        for node in boundary["phase_dependency_nodes"]
    )
    assert all(
        sidecar["exists"]
        for node in boundary["phase_dependency_nodes"]
        for sidecar in node["section_sidecar_refs"]
    )
    assert all(
        edge["dependency_edge_status"] == "dependency_edge_current"
        for edge in boundary["phase_dependency_edges"]
    )
    assert boundary["missing_evidence"] == {
        "ci_phase_freshness_gate": "not_recorded_locally",
        "evidence_status_refresh": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "bounded ROADMAP phase dependency graph" in boundary["claim_boundary"]
    assert "phase promotion/demotion workflow are recorded separately" in boundary["claim_boundary"]


def test_roadmap_phase_dependency_graph_rejects_overclaim_and_stale_edges():
    boundary = roadmap_phase_dependency_graph_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "phase_freshness_gate_ready"
    boundary["stale_dependency_edge_count"] = 1
    boundary["dependency_graph_status"] = "phase_dependency_graph_stale_or_incomplete"
    boundary["phase_dependency_edges"][0]["dependency_edge_status"] = (
        "dependency_edge_stale_or_incomplete"
    )
    boundary["missing_evidence"]["ci_phase_freshness_gate"] = "recorded"
    boundary["required_evidence_fields"] = ["source_phase_sequence"]

    validation = validate_roadmap_phase_dependency_graph_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_stale_dependency_edge_count" in codes
    assert "invalid_dependency_graph_status" in codes
    assert "invalid_phase_dependency_edges" in codes
    assert "stale_dependency_edge" in codes
    assert "invalid_missing_evidence_ci_phase_freshness_gate" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_phase_dependency_graph_summary_reports_shape():
    summary = render_roadmap_phase_dependency_graph_boundary_summary(
        roadmap_phase_dependency_graph_boundary_record()
    )

    assert "ROADMAP phase dependency graph boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_phase_dependency_graph_recorded_with_phase_workflow |"
        in summary
    )
    assert "| node_count | 10 |" in summary
    assert "| edge_count | 22 |" in summary
    assert "| stale_dependency_edge_count | 0 |" in summary
    assert "| missing_evidence_count | 3 |" in summary
