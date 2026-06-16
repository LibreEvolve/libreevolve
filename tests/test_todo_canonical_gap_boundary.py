from libreevolve.problems.benchmarks.todo_canonical_gap_boundary import (
    TODO_CANONICAL_GAP_BOUNDARY_SCHEMA,
    render_todo_canonical_gap_boundary_summary,
    todo_canonical_gap_boundary_record,
    validate_todo_canonical_gap_boundary,
)


def test_todo_canonical_gap_boundary_accepts_bounded_matrix():
    boundary = todo_canonical_gap_boundary_record()

    validation = validate_todo_canonical_gap_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_todo_canonical_gap_matrix_without_underlying_gap_rollup"
    )
    assert boundary["schema"] == TODO_CANONICAL_GAP_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["raw_todo_ledger_active_count"] == 506
    assert boundary["raw_todo_ledger_completed_count"] == 4669
    assert boundary["raw_todo_ledger_total_count"] == 5175
    assert boundary["exact_duplicate_group_count"] == 123
    assert boundary["duplicate_detection_policy"] == "exact_normalized_title_only"
    assert boundary["canonical_gap_completion_status"] == "not_available_without_gap_ids"
    assert boundary["criterion_count"] == 9
    assert boundary["active_todo_ref_count"] == 13
    assert boundary["sidecar_ref_count"] == 14
    assert [record["criterion_id"] for record in boundary["criterion_records"]] == [
        "canonical_gap_ids",
        "canonical_owner_ledgers",
        "derivative_relationships",
        "source_paper_anchor_mapping",
        "implementation_evidence_links",
        "cross_document_rollup_rules",
        "semantic_duplicate_detection",
        "stale_duplicate_and_orphan_detection",
        "raw_count_inflation_reporting",
    ]
    assert all(
        sidecar["exists"]
        for record in boundary["criterion_records"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        todo_ref["exists"] and todo_ref["required_phrase_present"]
        for record in boundary["criterion_records"]
        for todo_ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "canonical_gap_ids": "not_recorded_locally",
        "canonical_owner_assignments": "not_recorded_locally",
        "derivative_documentation_relationships": "not_recorded_locally",
        "source_or_paper_anchor_mapping": "not_recorded_locally",
        "implementation_evidence_links": "not_recorded_locally",
        "cross_document_rollup_rules": "not_recorded_locally",
        "semantic_duplicate_detector": "not_recorded_locally",
        "stale_completed_duplicate_detector": "not_recorded_locally",
        "orphaned_derivative_detector": "not_recorded_locally",
        "canonical_gap_completion_percent": "not_recorded_locally",
        "raw_count_inflation_report": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim canonical gap ids" in boundary["claim_boundary"]


def test_todo_canonical_gap_boundary_rejects_overclaim_and_drift():
    boundary = todo_canonical_gap_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "canonical_gap_rollup_ready"
    boundary["criterion_count"] = 8
    boundary["criterion_records"][0]["readiness_status"] = "ready"
    boundary["missing_evidence"]["canonical_gap_ids"] = "recorded"
    boundary["required_evidence_fields"] = ["canonical_gap_criteria"]

    validation = validate_todo_canonical_gap_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_criterion_count" in codes
    assert "invalid_criterion_records" in codes
    assert "invalid_missing_evidence_canonical_gap_ids" in codes
    assert "missing_required_evidence_field" in codes


def test_render_todo_canonical_gap_boundary_summary_reports_shape():
    summary = render_todo_canonical_gap_boundary_summary(
        todo_canonical_gap_boundary_record()
    )

    assert "TODO canonical gap boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_todo_canonical_gap_matrix_without_underlying_gap_rollup |"
        in summary
    )
    assert "| criterion_count | 9 |" in summary
    assert "| active_todo_ref_count | 13 |" in summary
    assert "| missing_evidence_count | 12 |" in summary
