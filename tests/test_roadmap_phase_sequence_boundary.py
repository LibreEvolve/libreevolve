from libreevolve.problems.benchmarks.roadmap_phase_sequence_boundary import (
    ROADMAP_PHASE_SEQUENCE_BOUNDARY_SCHEMA,
    render_roadmap_phase_sequence_boundary_summary,
    roadmap_phase_sequence_boundary_record,
    validate_roadmap_phase_sequence_boundary,
)


def test_roadmap_phase_sequence_accepts_bounded_phase_map():
    boundary = roadmap_phase_sequence_boundary_record()

    validation = validate_roadmap_phase_sequence_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_phase_sequence_map_with_ci_freshness_gate"
    )
    assert boundary["schema"] == ROADMAP_PHASE_SEQUENCE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["phase_order"] == ["near_term", "mid_term", "longer_term"]
    assert boundary["phase_count"] == 3
    assert boundary["phase_section_counts"] == {
        "near_term": 5,
        "mid_term": 3,
        "longer_term": 2,
    }
    assert boundary["section_count"] == 10
    assert boundary["section_sequence_status"] == "roadmap_major_sections_in_expected_order"
    assert boundary["active_blocking_todo_ref_count"] == 10
    assert [record["ordinal"] for record in boundary["section_records"]] == list(range(1, 11))
    assert all(record["roadmap_heading_present"] for record in boundary["section_records"])
    assert all(record["blocking_todo_present"] for record in boundary["section_records"])
    assert boundary["missing_evidence"] == {
        "owner_review_signoff": "not_recorded_locally",
    }
    assert (
        "CI phase freshness gate are recorded separately"
        in boundary["claim_boundary"]
    )


def test_roadmap_phase_sequence_rejects_overclaim_and_reordered_sections():
    boundary = roadmap_phase_sequence_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "phase_dependency_graph_ready"
    boundary["section_sequence_status"] = "roadmap_major_sections_missing_or_reordered"
    boundary["section_records"][0]["roadmap_heading_present"] = False
    boundary["active_blocking_todo_ref_count"] = 9
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["phase_headings"]

    validation = validate_roadmap_phase_sequence_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_section_sequence_status" in codes
    assert "invalid_section_records" in codes
    assert "invalid_active_blocking_todo_ref_count" in codes
    assert "invalid_section_sequence" in codes
    assert "missing_blocking_todo_ref" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_phase_sequence_summary_reports_shape():
    summary = render_roadmap_phase_sequence_boundary_summary(
        roadmap_phase_sequence_boundary_record()
    )

    assert "ROADMAP phase sequence boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_phase_sequence_map_with_ci_freshness_gate |"
        in summary
    )
    assert "| phase_count | 3 |" in summary
    assert "| section_count | 10 |" in summary
    assert "| missing_evidence_count | 1 |" in summary
