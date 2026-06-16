from libreevolve.problems.benchmarks.roadmap_phase_freshness_boundary import (
    ROADMAP_PHASE_FRESHNESS_BOUNDARY_SCHEMA,
    render_roadmap_phase_freshness_boundary_summary,
    roadmap_phase_freshness_boundary_record,
    validate_roadmap_phase_freshness_boundary,
)


def test_roadmap_phase_freshness_accepts_bounded_matrix():
    boundary = roadmap_phase_freshness_boundary_record()

    validation = validate_roadmap_phase_freshness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_phase_freshness_matrix_with_staleness_detector"
    )
    assert boundary["schema"] == ROADMAP_PHASE_FRESHNESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_phase_boundary_input"]
        == "papers/roadmap_phase_sequence_boundary.json"
    )
    assert boundary["source_phase_count"] == 3
    assert boundary["source_section_count"] == 10
    assert boundary["source_section_sequence_status"] == "roadmap_major_sections_in_expected_order"
    assert (
        boundary["phase_dependency_graph_boundary_input"]
        == "papers/roadmap_phase_dependency_graph_boundary.json"
    )
    assert boundary["phase_dependency_graph_status"] == "phase_dependency_graph_recorded"
    assert boundary["phase_dependency_graph_edge_count"] == 22
    assert boundary["phase_dependency_graph_stale_edge_count"] == 0
    assert (
        boundary["phase_staleness_boundary_input"]
        == "papers/roadmap_phase_staleness_boundary.json"
    )
    assert (
        boundary["phase_staleness_detector_status"]
        == "no_stale_phase_records_detected"
    )
    assert boundary["phase_staleness_record_count"] == 10
    assert boundary["stale_phase_record_count"] == 0
    assert boundary["freshness_criterion_count"] == 6
    assert boundary["sidecar_ref_count"] == 14
    assert boundary["active_todo_ref_count"] == 12
    assert [record["criterion_id"] for record in boundary["freshness_criteria"]] == [
        "dependency_graph",
        "phase_staleness_detector",
        "promotion_demotion_workflow",
        "ci_phase_freshness_gate",
        "evidence_status_refresh",
        "owner_review_signoff",
    ]
    assert all(
        sidecar["exists"]
        for record in boundary["freshness_criteria"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        todo_ref["exists"] and todo_ref["required_phrase_present"]
        for record in boundary["freshness_criteria"]
        for todo_ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "promotion_demotion_workflow": "not_recorded_locally",
        "ci_phase_freshness_gate": "not_recorded_locally",
        "evidence_status_refresh": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "phase dependency graph" in boundary["claim_boundary"]


def test_roadmap_phase_freshness_rejects_overclaim_and_drift():
    boundary = roadmap_phase_freshness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "phase_freshness_gate_ready"
    boundary["freshness_criterion_count"] = 0
    boundary["source_section_sequence_status"] = "roadmap_major_sections_missing_or_reordered"
    boundary["freshness_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["missing_evidence"]["promotion_demotion_workflow"] = "recorded"
    boundary["required_evidence_fields"] = ["dependency_graph"]

    validation = validate_roadmap_phase_freshness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_freshness_criterion_count" in codes
    assert "invalid_source_section_sequence_status" in codes
    assert "invalid_freshness_criteria" in codes
    assert "invalid_source_section_sequence" in codes
    assert "invalid_missing_evidence_promotion_demotion_workflow" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_phase_freshness_summary_reports_shape():
    summary = render_roadmap_phase_freshness_boundary_summary(
        roadmap_phase_freshness_boundary_record()
    )

    assert "ROADMAP phase freshness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_phase_freshness_matrix_with_staleness_detector |"
        in summary
    )
    assert "| freshness_criterion_count | 6 |" in summary
    assert "| sidecar_ref_count | 14 |" in summary
    assert "| active_todo_ref_count | 12 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
