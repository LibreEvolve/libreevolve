from libreevolve.problems.benchmarks.roadmap_phase_staleness_boundary import (
    ROADMAP_PHASE_STALENESS_BOUNDARY_SCHEMA,
    render_roadmap_phase_staleness_boundary_summary,
    roadmap_phase_staleness_boundary_record,
    validate_roadmap_phase_staleness_boundary,
)


def test_roadmap_phase_staleness_accepts_current_phase_records():
    boundary = roadmap_phase_staleness_boundary_record()

    validation = validate_roadmap_phase_staleness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_phase_staleness_detector_without_workflow_gate"
    )
    assert boundary["schema"] == ROADMAP_PHASE_STALENESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_phase_boundary_input"]
        == "papers/roadmap_phase_sequence_boundary.json"
    )
    assert (
        boundary["source_dependency_graph_input"]
        == "papers/roadmap_phase_dependency_graph_boundary.json"
    )
    assert boundary["source_phase_count"] == 3
    assert boundary["source_section_count"] == 10
    assert boundary["source_section_sequence_status"] == (
        "roadmap_major_sections_in_expected_order"
    )
    assert boundary["dependency_graph_status"] == "phase_dependency_graph_recorded"
    assert boundary["dependency_edge_count"] == 22
    assert boundary["dependency_graph_stale_edge_count"] == 0
    assert boundary["phase_detector_status"] == "no_stale_phase_records_detected"
    assert boundary["phase_record_count"] == 10
    assert boundary["stale_phase_record_count"] == 0
    assert boundary["stale_phase_records"] == []
    assert [record["ordinal"] for record in boundary["detector_records"]] == list(
        range(1, 11)
    )
    assert all(
        record["phase_detector_status"] == "phase_current"
        for record in boundary["detector_records"]
    )
    assert all(
        record["missing_sidecar_ref_count"] == 0
        for record in boundary["detector_records"]
    )
    assert boundary["missing_evidence"] == {
        "promotion_demotion_workflow": "not_recorded_locally",
        "ci_phase_freshness_gate": "not_recorded_locally",
        "evidence_status_refresh": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "bounded stale-phase detector" in boundary["claim_boundary"]


def test_roadmap_phase_staleness_rejects_overclaim_and_stale_record():
    boundary = roadmap_phase_staleness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "phase_freshness_gate_ready"
    boundary["phase_detector_status"] = "stale_phase_records_detected"
    boundary["stale_phase_record_count"] = 1
    boundary["detector_records"][0]["phase_detector_status"] = "stale_phase_detected"
    boundary["detector_records"][0]["stale_reasons"] = ["roadmap_heading_missing"]
    boundary["stale_phase_records"] = [boundary["detector_records"][0]]
    boundary["missing_evidence"]["promotion_demotion_workflow"] = "recorded"
    boundary["required_evidence_fields"] = ["source_phase_sequence"]

    validation = validate_roadmap_phase_staleness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_phase_detector_status" in codes
    assert "invalid_stale_phase_record_count" in codes
    assert "invalid_stale_phase_records" in codes
    assert "invalid_detector_records" in codes
    assert "stale_phase_record_detected" in codes
    assert "invalid_missing_evidence_promotion_demotion_workflow" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_phase_staleness_summary_reports_shape():
    summary = render_roadmap_phase_staleness_boundary_summary(
        roadmap_phase_staleness_boundary_record()
    )

    assert "ROADMAP phase staleness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_phase_staleness_detector_without_workflow_gate |"
        in summary
    )
    assert "| phase_record_count | 10 |" in summary
    assert "| dependency_edge_count | 22 |" in summary
    assert "| stale_phase_record_count | 0 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
