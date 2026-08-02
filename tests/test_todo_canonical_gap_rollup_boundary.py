from libreevolve.problems.benchmarks.todo_canonical_gap_rollup_boundary import (
    TODO_CANONICAL_GAP_ROLLUP_BOUNDARY_SCHEMA,
    render_todo_canonical_gap_rollup_boundary_summary,
    todo_canonical_gap_rollup_boundary_record,
    validate_todo_canonical_gap_rollup_boundary,
)


def test_todo_canonical_gap_rollup_accepts_bounded_gate():
    boundary = todo_canonical_gap_rollup_boundary_record()

    validation = validate_todo_canonical_gap_rollup_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_canonical_gap_rollup_gate_with_exact_same_owner_duplicate_report"
    )
    assert boundary["schema"] == TODO_CANONICAL_GAP_ROLLUP_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_canonical_gap_boundary_input"]
        == "papers/todo_canonical_gap_boundary.json"
    )
    assert boundary["source_criterion_count"] == 9
    assert boundary["source_active_todo_ref_count"] == 14
    assert boundary["source_sidecar_ref_count"] == 14
    assert boundary["source_missing_evidence_count"] == 12
    assert boundary["source_canonical_gap_completion_status"] == (
        "not_available_without_gap_ids"
    )
    assert boundary["source_exact_stale_completed_duplicate_group_count"] == 0
    assert (
        boundary["source_exact_stale_completed_duplicate_status"]
        == "no_exact_stale_completed_duplicates_detected"
    )
    assert boundary["source_exact_duplicate_record_count"] == 246
    assert boundary["source_exact_duplicate_inflation_count"] == 123
    assert boundary["source_exact_duplicate_collapsed_total_estimate"] == 5206
    assert boundary["source_exact_duplicate_cross_owner_group_count"] == 122
    assert boundary["source_exact_duplicate_completed_only_group_count"] == 123
    assert boundary["source_exact_duplicate_active_involved_group_count"] == 0
    assert boundary["source_exact_same_owner_completed_duplicate_group_count"] == 1
    assert (
        boundary["source_exact_same_owner_completed_duplicate_status"]
        == "exact_same_owner_completed_duplicates_detected"
    )
    assert boundary["source_exact_duplicate_raw_count_inflation_report"][
        "inflation_percent_of_raw_total"
    ] == 2.308
    assert boundary["source_exact_duplicate_owner_status_report"][
        "canonical_owner_assignments_ready"
    ] is False
    assert boundary["rollup_criterion_count"] == 8
    assert boundary["sidecar_ref_count"] == 16
    assert boundary["active_todo_ref_count"] == 16
    assert (
        boundary["missing_evidence_todo_coverage_status"]
        == "all_missing_evidence_keys_have_active_todo_coverage"
    )
    assert boundary["missing_evidence_todo_coverage_count"] == 12
    assert {
        record["evidence_key"]
        for record in boundary["missing_evidence_todo_coverage_records"]
    } == {
        "canonical_gap_ids",
        "canonical_owner_assignments",
        "derivative_documentation_relationships",
        "source_or_paper_anchor_mapping",
        "implementation_evidence_links",
        "cross_document_rollup_rules",
        "semantic_duplicate_detector",
        "stale_completed_duplicate_detector",
        "orphaned_derivative_detector",
        "canonical_gap_completion_percent",
        "canonical_raw_count_inflation_report",
        "owner_review_signoff",
    }
    assert all(
        record["todo_path"] == "docs/todo/roadmap.md"
        and record["todo_exists"] is True
        and record["required_phrase_present"] is True
        and record["coverage_claim"] == "active_todo_ref_only"
        for record in boundary["missing_evidence_todo_coverage_records"]
    )
    assert [record["criterion_id"] for record in boundary["rollup_criteria"]] == [
        "canonical_gap_registry",
        "canonical_owner_policy",
        "derivative_relationship_policy",
        "source_and_implementation_evidence_links",
        "cross_document_rollup_policy",
        "duplicate_and_orphan_detection",
        "canonical_completion_reporting",
        "publication_and_owner_signoff",
    ]
    assert all(
        sidecar["exists"]
        for record in boundary["rollup_criteria"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in boundary["rollup_criteria"]
        for ref in record["active_todo_refs"]
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
        "canonical_raw_count_inflation_report": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim canonical gap ids" in boundary["claim_boundary"]
    assert "canonical gap completion percent" in boundary["claim_boundary"]
    assert "owner review signoff" in boundary["claim_boundary"]


def test_todo_canonical_gap_rollup_rejects_overclaim_and_drift():
    boundary = todo_canonical_gap_rollup_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "canonical_gap_rollup_ready"
    boundary["rollup_criterion_count"] = 7
    boundary["source_criterion_count"] = 8
    boundary["source_active_todo_ref_count"] = 13
    boundary["source_exact_duplicate_inflation_count"] = 0
    boundary["source_exact_duplicate_cross_owner_group_count"] = 0
    boundary["source_exact_same_owner_completed_duplicate_group_count"] = 0
    boundary["source_exact_stale_completed_duplicate_group_count"] = 1
    boundary["missing_evidence_todo_coverage_count"] = 11
    boundary["rollup_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["rollup_criteria"][0]["active_todo_refs"][0][
        "required_phrase_present"
    ] = False
    boundary["missing_evidence"]["canonical_gap_ids"] = "recorded"
    boundary["required_evidence_fields"] = ["rollup_criteria"]

    validation = validate_todo_canonical_gap_rollup_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_criterion_count" in codes
    assert "invalid_source_active_todo_ref_count" in codes
    assert "invalid_source_exact_duplicate_inflation_count" in codes
    assert "invalid_source_exact_duplicate_cross_owner_group_count" in codes
    assert (
        "invalid_source_exact_same_owner_completed_duplicate_group_count" in codes
    )
    assert "invalid_source_exact_stale_completed_duplicate_group_count" in codes
    assert "invalid_missing_evidence_todo_coverage_count" in codes
    assert "invalid_rollup_criterion_count" in codes
    assert "invalid_rollup_criteria" in codes
    assert "invalid_missing_evidence_canonical_gap_ids" in codes
    assert "missing_required_evidence_field" in codes
    assert "invalid_required_evidence_field_count" in codes


def test_render_todo_canonical_gap_rollup_summary_reports_shape():
    summary = render_todo_canonical_gap_rollup_boundary_summary(
        todo_canonical_gap_rollup_boundary_record()
    )

    assert "TODO canonical gap rollup boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_canonical_gap_rollup_gate_with_exact_same_owner_duplicate_report |"
        in summary
    )
    assert "| rollup_criterion_count | 8 |" in summary
    assert "| sidecar_ref_count | 16 |" in summary
    assert "| active_todo_ref_count | 16 |" in summary
    assert "| missing_evidence_count | 12 |" in summary
