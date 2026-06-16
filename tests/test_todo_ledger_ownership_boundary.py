from libreevolve.problems.benchmarks.todo_ledger_ownership_boundary import (
    TODO_LEDGER_OWNERSHIP_BOUNDARY_SCHEMA,
    render_todo_ledger_ownership_boundary_summary,
    todo_ledger_ownership_boundary_record,
    validate_todo_ledger_ownership_boundary,
)


def test_todo_ledger_ownership_boundary_accepts_current_ledger_inventory():
    boundary = todo_ledger_ownership_boundary_record()

    validation = validate_todo_ledger_ownership_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "ledger_owner_inventory_without_canonical_gap_deduplication"
    )
    assert boundary["schema"] == TODO_LEDGER_OWNERSHIP_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["owner_record_count"] == 4
    assert boundary["raw_todo_ledger_active_count"] == 506
    assert boundary["raw_todo_ledger_completed_count"] == 4631
    assert boundary["raw_todo_ledger_total_count"] == 5137
    assert boundary["active_ledger_completed_marker_count"] == 0
    assert boundary["completed_ledger_active_marker_count"] == 0
    assert (
        boundary["marker_policy_status"]
        == "active_ledgers_unchecked_completed_ledgers_checked"
    )
    assert boundary["duplicate_detection_policy"] == "exact_normalized_title_only"
    assert boundary["likely_duplicate_title_group_count"] == 122
    assert boundary["canonical_gap_completion_status"] == "not_available_without_gap_ids"
    owner_ids = {record["owner_id"] for record in boundary["owner_records"]}
    assert owner_ids == {"code", "papers", "readme", "roadmap"}
    assert boundary["missing_evidence"] == {
        "canonical_gap_ids": "not_recorded_locally",
        "derivative_relationships": "not_recorded_locally",
        "cross_document_rollup_rules": "not_recorded_locally",
        "source_or_paper_anchor_mapping": "not_recorded_locally",
        "implementation_evidence_links": "not_recorded_locally",
        "stale_duplicate_detector": "not_recorded_locally",
        "canonical_gap_completion_percent": "not_recorded_locally",
    }
    assert "does not claim canonical underlying-gap ids" in boundary["claim_boundary"]


def test_todo_ledger_ownership_boundary_rejects_canonical_gap_overclaim():
    boundary = todo_ledger_ownership_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "canonical_gap_ownership_ready"
    boundary["canonical_gap_completion_status"] = "available"
    boundary["missing_evidence"]["canonical_gap_ids"] = "recorded"
    boundary["owner_records"][0]["active_count"] = 0
    boundary["likely_duplicate_title_groups"] = []
    boundary["required_evidence_fields"] = ["ledger_owner_inventory"]

    validation = validate_todo_ledger_ownership_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_canonical_gap_completion_status" in codes
    assert "invalid_missing_evidence_canonical_gap_ids" in codes
    assert "invalid_owner_records" in codes
    assert "invalid_likely_duplicate_title_groups" in codes
    assert "missing_required_evidence_field" in codes


def test_render_todo_ledger_ownership_boundary_summary_reports_shape():
    summary = render_todo_ledger_ownership_boundary_summary(
        todo_ledger_ownership_boundary_record()
    )

    assert "TODO ledger ownership boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | ledger_owner_inventory_without_canonical_gap_deduplication |"
        in summary
    )
    assert "| owner_record_count | 4 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
