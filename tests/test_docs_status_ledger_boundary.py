from libreevolve.problems.benchmarks.docs_status_ledger_boundary import (
    DOCS_STATUS_LEDGER_BOUNDARY_SCHEMA,
    docs_status_ledger_boundary_record,
    render_docs_status_ledger_boundary_summary,
    validate_docs_status_ledger_boundary,
)


def test_docs_status_ledger_boundary_accepts_current_status_inventory():
    boundary = docs_status_ledger_boundary_record()

    validation = validate_docs_status_ledger_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "docs_status_structural_freshness_inventory_without_semantic_map"
    )
    assert boundary["schema"] == DOCS_STATUS_LEDGER_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["status_ledger_path"] == "docs/status.md"
    assert boundary["status_ledger_heading_status"] == "heading_present"
    assert validation.status_ledger_bullet_count == 268
    assert boundary["status_ledger_section_counts"] == {
        "implemented_today": 10,
        "important_limits": 258,
    }
    assert validation.status_ledger_local_path_ref_count == 278
    assert boundary["status_ledger_missing_local_path_refs"] == []
    assert (
        boundary["status_ledger_local_path_ref_status"]
        == "all_status_ledger_local_path_refs_present"
    )
    assert validation.missing_route_marker_count == 0
    assert boundary["missing_route_marker_records"] == []
    assert boundary["status_claim_inventory_summary"] == {
        "summary_status": "status_claim_inventory_summary_recorded",
        "path": "papers/status_claim_inventory.json",
        "row_count": 53,
        "unique_local_artifact_count": 60,
        "local_artifact_mention_record_count": 60,
        "absence_phrase_count": 87,
        "absence_signal_record_count": 98,
    }
    assert boundary["missing_evidence"] == {
        "per_bullet_source_test_sidecar_todo_map": "not_recorded_locally",
        "stale_status_prose_detector": "not_recorded_locally",
        "orphan_status_bullet_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "paper-index status claim inventory summary fields" in boundary["claim_boundary"]


def test_docs_status_ledger_boundary_rejects_overclaim_and_drift():
    boundary = docs_status_ledger_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "docs_status_semantic_freshness_verified"
    boundary["status_ledger_bullet_count"] = 0
    boundary["status_ledger_heading_status"] = "heading_missing"
    boundary["status_ledger_local_path_ref_status"] = "missing_status_ledger_local_path_refs"
    boundary["missing_route_marker_count"] = 1
    boundary["missing_route_marker_records"] = [boundary["route_marker_records"][0]]
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["status_ledger_heading"]

    validation = validate_docs_status_ledger_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_status_ledger_bullet_count" in codes
    assert "invalid_status_ledger_heading_status" in codes
    assert "missing_status_ledger_heading" in codes
    assert "missing_status_ledger_local_path_ref" in codes
    assert "invalid_missing_route_marker_count" in codes
    assert "invalid_missing_route_marker_records" in codes
    assert "missing_route_marker" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_docs_status_ledger_boundary_summary_reports_shape():
    summary = render_docs_status_ledger_boundary_summary(
        docs_status_ledger_boundary_record()
    )

    assert "Docs status ledger boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | docs_status_structural_freshness_inventory_without_semantic_map |"
        in summary
    )
    assert "| status_ledger_bullet_count | 268 |" in summary
    assert "| status_ledger_local_path_ref_count | 278 |" in summary
    assert "| missing_route_marker_count | 0 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
