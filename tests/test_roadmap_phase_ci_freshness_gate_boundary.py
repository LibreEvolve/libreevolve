from libreevolve.problems.benchmarks.roadmap_phase_ci_freshness_gate_boundary import (
    ROADMAP_PHASE_CI_FRESHNESS_GATE_BOUNDARY_SCHEMA,
    render_roadmap_phase_ci_freshness_gate_boundary_summary,
    roadmap_phase_ci_freshness_gate_boundary_record,
    validate_roadmap_phase_ci_freshness_gate_boundary,
)


def test_roadmap_phase_ci_freshness_gate_accepts_current_gate():
    boundary = roadmap_phase_ci_freshness_gate_boundary_record()

    validation = validate_roadmap_phase_ci_freshness_gate_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "phase_ci_freshness_gate_recorded_without_evidence_refresh_or_signoff"
    )
    assert boundary["schema"] == ROADMAP_PHASE_CI_FRESHNESS_GATE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["workflow_path"] == ".github/workflows/tests.yml"
    assert boundary["paper_manifest_path"] == "libreevolve/tools/paper_manifest.py"
    assert boundary["source_phase_count"] == 3
    assert boundary["source_section_count"] == 10
    assert boundary["dependency_edge_count"] == 22
    assert boundary["stale_phase_record_count"] == 0
    assert boundary["promotion_workflow_phrase_count"] == 9
    assert boundary["freshness_criterion_count"] == 6
    assert validation.gate_record_count == 16
    assert validation.missing_gate_record_count == 0
    assert boundary["missing_gate_records"] == []
    assert boundary["ci_gate_status"] == "phase_freshness_gate_present"
    assert all(
        record["gate_status"] == "gate_marker_present"
        for record in boundary["gate_records"]
    )
    assert boundary["missing_evidence"] == {
        "evidence_status_refresh": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "GitHub Actions workflow" in boundary["claim_boundary"]


def test_roadmap_phase_ci_freshness_gate_rejects_overclaim_and_missing_gate():
    boundary = roadmap_phase_ci_freshness_gate_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "phase_evidence_refresh_ready"
    boundary["missing_gate_record_count"] = 1
    boundary["ci_gate_status"] = "phase_freshness_gate_incomplete"
    boundary["missing_gate_records"] = [
        {
            "gate_kind": "paper_manifest_gate",
            "path": "libreevolve/tools/paper_manifest.py",
            "required_marker": "_validate_roadmap_phase_freshness_boundary",
            "gate_status": "gate_marker_missing",
        }
    ]
    boundary["gate_records"][0]["gate_status"] = "gate_marker_missing"
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["phase_sequence_boundary"]

    validation = validate_roadmap_phase_ci_freshness_gate_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_gate_record_count" in codes
    assert "invalid_ci_gate_status" in codes
    assert "invalid_missing_gate_records" in codes
    assert "invalid_gate_records" in codes
    assert "missing_gate_record" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_phase_ci_freshness_gate_summary_reports_shape():
    summary = render_roadmap_phase_ci_freshness_gate_boundary_summary(
        roadmap_phase_ci_freshness_gate_boundary_record()
    )

    assert "ROADMAP phase CI freshness gate boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | phase_ci_freshness_gate_recorded_without_evidence_refresh_or_signoff |"
        in summary
    )
    assert "| gate_record_count | 16 |" in summary
    assert "| missing_gate_record_count | 0 |" in summary
    assert "| missing_evidence_count | 2 |" in summary
