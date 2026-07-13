from libreevolve.problems.benchmarks.roadmap_source_span_disposition_boundary import (
    ROADMAP_SOURCE_SPAN_DISPOSITION_BOUNDARY_SCHEMA,
    render_roadmap_source_span_disposition_boundary_summary,
    roadmap_source_span_disposition_boundary_record,
    validate_roadmap_source_span_disposition_boundary,
)


def test_roadmap_source_span_disposition_accepts_core_anchor_boundary():
    boundary = roadmap_source_span_disposition_boundary_record()

    validation = validate_roadmap_source_span_disposition_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "named_source_span_dispositions_without_claim_level_exhaustiveness"
    )
    assert boundary["schema"] == ROADMAP_SOURCE_SPAN_DISPOSITION_BOUNDARY_SCHEMA
    assert boundary["source_paper_id"] == "2506.13131"
    assert boundary["claim_ready"] is False
    assert boundary["disposition_record_count"] == 55
    assert boundary["disposition_source_ref_count"] == 55
    assert boundary["paper_status_row_count"] == 53
    assert boundary["paper_status_row_dispositioned_count"] == 1
    assert (
        boundary["paper_status_row_disposition_status"]
        == "paper_index_rows_not_exhaustively_roadmapped"
    )
    first_record = boundary["disposition_records"][0]
    assert first_record == {
        "span_id": "abstract",
        "source_kind": "structure",
        "source_label": "Abstract",
        "source_refs": ["2506.13131:pages 1"],
        "source_ref_count": 1,
        "source_anchor_count": 1,
        "source_anchors_verified": True,
        "local_claim_status": "background_only",
        "roadmap_section_id": "documentation_truthfulness",
        "roadmap_phase": "near_term",
        "coverage_scope": "named_structure_span",
        "sidecar_refs": ["papers/documentation_truthfulness_boundary.json"],
        "todo_refs": [],
        "disposition_status": "named_structure_disposition_only",
    }
    assert boundary["missing_evidence"] == {
        "claim_level_requirement_inventory": "not_recorded_locally",
        "application_result_claim_matrix": "not_recorded_locally",
        "status_row_to_roadmap_disposition_map": "not_recorded_locally",
        "missing_partial_todo_proof": "not_recorded_locally",
        "ci_source_span_exhaustiveness_gate": "not_recorded_locally",
    }
    assert "all 55 PDF-verified named AlphaEvolve structural spans" in boundary["claim_boundary"]
    assert "requirement-level exhaustiveness" in boundary["claim_boundary"]


def test_roadmap_source_span_disposition_rejects_exhaustive_overclaim():
    boundary = roadmap_source_span_disposition_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "exhaustive_source_span_matrix_ready"
    boundary["paper_status_row_disposition_status"] = "all_rows_dispositioned"
    boundary["disposition_records"][0]["coverage_scope"] = "exhaustive"
    boundary["missing_evidence"]["claim_level_requirement_inventory"] = "recorded"
    boundary["required_evidence_fields"] = ["core_requirement_anchor_dispositions"]

    validation = validate_roadmap_source_span_disposition_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_paper_status_row_disposition_status" in codes
    assert "invalid_disposition_records" in codes
    assert "invalid_missing_evidence_claim_level_requirement_inventory" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_source_span_disposition_summary_reports_shape():
    summary = render_roadmap_source_span_disposition_boundary_summary(
        roadmap_source_span_disposition_boundary_record()
    )

    assert "ROADMAP source-span disposition boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | named_source_span_dispositions_without_claim_level_exhaustiveness |"
        in summary
    )
    assert "| disposition_record_count | 55 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
