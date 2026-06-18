from libreevolve.problems.benchmarks.documentation_claim_inventory import (
    DOCUMENTATION_CLAIM_INVENTORY_SCHEMA,
    documentation_claim_inventory_record,
    render_documentation_claim_inventory_summary,
    validate_documentation_claim_inventory,
)


def test_documentation_claim_inventory_accepts_top_level_readme_roadmap_claims():
    inventory = documentation_claim_inventory_record()

    validation = validate_documentation_claim_inventory(inventory)

    assert validation.ok is True
    assert (
        validation.inventory_status
        == "top_level_readme_roadmap_papers_claim_inventory_without_semantic_verifier"
    )
    assert validation.claim_count == 8
    assert validation.readme_claim_count == 3
    assert validation.roadmap_claim_count == 3
    assert validation.papers_claim_count == 2
    assert validation.missing_evidence_count == 9
    assert inventory["schema"] == DOCUMENTATION_CLAIM_INVENTORY_SCHEMA
    assert inventory["claim_ready"] is False
    assert inventory["source_anchor_status"] == "all_claim_source_anchors_recorded"
    assert inventory["source_anchor_missing_claim_ids"] == []
    assert inventory["evidence_ref_status"] == "all_local_evidence_refs_present"
    assert inventory["missing_evidence_ref_records"] == []
    assert inventory["evidence_ref_fragment_status"] == "all_fragment_anchors_resolved"
    assert inventory["fragment_evidence_ref_record_count"] == 7
    assert inventory["missing_fragment_ref_records"] == []
    assert inventory["claim_surface_document_paths"] == [
        "README.md",
        "ROADMAP.md",
        "papers/README.md",
    ]
    assert inventory["claim_surface_heading_status"] == "audited_surface_headings_recorded"
    assert inventory["claim_surface_heading_record_count"] == 34
    assert inventory["missing_claim_surface_document_records"] == []
    assert (
        inventory["claim_surface_heading_claim_status"]
        == "partial_heading_claim_coverage"
    )
    assert inventory["claim_surface_heading_claim_record_count"] == 34
    assert inventory["claim_surface_heading_claim_covered_count"] == 6
    assert inventory["uncovered_claim_surface_heading_count"] == 28
    assert (
        inventory["uncovered_heading_todo_link_status"]
        == "all_uncovered_heading_groups_have_todo_links"
    )
    assert inventory["uncovered_heading_todo_link_record_count"] == 3
    assert inventory["uncovered_heading_todo_link_records"][0][
        "document_path"
    ] == "README.md"
    assert inventory["uncovered_heading_todo_link_records"][0][
        "uncovered_heading_count"
    ] == 12
    assert inventory["uncovered_heading_todo_link_records"][0][
        "todo_path"
    ] == "docs/todo/readme.md"
    assert inventory["uncovered_heading_todo_link_records"][0][
        "todo_anchor_status"
    ] == "todo_anchor_recorded"
    assert inventory["uncovered_heading_todo_link_records"][0]["todo_span"][
        "line_start"
    ] == 195
    assert (
        inventory["status_ledger_inventory_status"]
        == "status_ledger_structural_bullet_inventory_without_semantic_verifier"
    )
    assert inventory["status_ledger_source_path"] == "docs/status.md"
    assert inventory["status_ledger_bullet_count"] == 251
    assert inventory["status_ledger_section_counts"] == {
        "implemented_today": 9,
        "important_limits": 242,
    }
    assert inventory["status_ledger_signal_term_count"] == 11
    assert inventory["status_ledger_signal_record_count"] == 621
    assert inventory["status_ledger_unique_local_path_ref_count"] == 216
    assert inventory["status_ledger_local_path_ref_count"] == 271
    assert inventory["status_ledger_missing_local_path_refs"] == []
    assert "paper_artifacts/..." not in inventory["status_ledger_unique_local_path_refs"]
    assert (
        inventory["status_ledger_local_path_ref_status"]
        == "all_status_ledger_local_path_refs_present"
    )
    assert inventory["run_artifact_documented_count"] == 22
    assert inventory["run_artifact_cleanup_count"] == 23
    assert inventory["run_artifact_documented_without_cleanup_names"] == []
    assert inventory["run_artifact_cleanup_without_documented_names"] == [
        "paper_artifacts",
    ]
    assert inventory["run_artifact_documented_without_cleanup_count"] == 0
    assert inventory["run_artifact_cleanup_without_documented_count"] == 1
    assert (
        inventory["run_artifact_lifecycle_alignment_status"]
        == "cleanup_artifacts_missing_documentation"
    )
    assert inventory["status_ledger_bullet_records"][0] == {
        "bullet_ordinal": 1,
        "section": "implemented_today",
        "line_start": 18,
        "line_end": 18,
        "file_text_char_start": 589,
        "file_text_char_end": 645,
        "text_sha256": "2f52aff907fdb291196e46d2e05f56b5755f2e00aa3260a8235926e93ab261e8",
        "signal_terms": [],
        "signal_term_count": 0,
        "local_path_refs": [],
        "local_path_ref_records": [],
    }
    assert inventory["claim_surface_heading_records"][0] == {
        "path": "README.md",
        "line_start": 1,
        "line_end": 1,
        "level": 1,
        "heading_text": "LibreEvolve",
        "heading_slug": "libreevolve",
    }
    assert {
        "path": "ROADMAP.md",
        "line_start": 831,
        "line_end": 831,
        "level": 3,
        "heading_text": "5. Documentation truthfulness",
        "heading_slug": "5-documentation-truthfulness",
    } in inventory["claim_surface_heading_records"]
    assert inventory["claim_surface_heading_claim_records"][1] == {
        "path": "README.md",
        "line_start": 13,
        "level": 2,
        "heading_text": "Current Status",
        "heading_slug": "current-status",
        "claim_coverage_status": "has_claim_record",
        "claim_ids": [
            "readme_current_status_scope",
            "readme_runnable_today_scope",
            "readme_important_limits_scope",
        ],
    }
    assert inventory["uncovered_claim_surface_heading_records"][0] == {
        "path": "README.md",
        "line_start": 1,
        "heading_text": "LibreEvolve",
        "heading_slug": "libreevolve",
        "reason": "no_claim_record_for_heading",
    }
    assert inventory["evidence_ref_record_count"] == sum(
        len(claim["evidence_refs"]) for claim in inventory["claims"]
    )
    claim_ids = {claim["claim_id"] for claim in inventory["claims"]}
    assert "readme_current_status_scope" in claim_ids
    assert "roadmap_documentation_truthfulness_scope" in claim_ids
    assert "papers_implementation_status_scope" in claim_ids
    readme_claim = next(
        claim for claim in inventory["claims"] if claim["claim_id"] == "readme_current_status_scope"
    )
    assert readme_claim["source_anchor_text"] == "## Current Status"
    assert readme_claim["source_anchor_status"] == "source_anchor_recorded"
    assert readme_claim["source_span"]["path"] == "README.md"
    assert readme_claim["source_span"]["line_start"] == 13
    assert isinstance(readme_claim["source_span"]["file_text_char_start"], int)
    assert readme_claim["evidence_ref_status"] == "all_local_evidence_refs_present"
    assert readme_claim["missing_evidence_refs"] == []
    assert readme_claim["evidence_ref_records"][0] == {
        "ref": "README.md#current-status",
        "path": "README.md",
        "fragment": "current-status",
        "exists": True,
        "kind": "file",
        "fragment_status": "fragment_anchor_resolved",
        "fragment_found": True,
        "matched_heading_text": "Current Status",
        "matched_heading_slug": "current-status",
        "matched_heading_line_start": 13,
    }
    roadmap_doc_claim = next(
        claim
        for claim in inventory["claims"]
        if claim["claim_id"] == "roadmap_documentation_truthfulness_scope"
    )
    assert (
        "ROADMAP.md#5-documentation-truthfulness"
        in roadmap_doc_claim["evidence_refs"]
    )
    assert (
        roadmap_doc_claim["evidence_ref_records"][0]["fragment_status"]
        == "fragment_anchor_resolved"
    )
    assert (
        roadmap_doc_claim["evidence_ref_records"][0]["matched_heading_slug"]
        == "5-documentation-truthfulness"
    )
    assert (
        "does not claim complete README coverage"
        in inventory["claim_boundary"]
    )
    assert "structural docs/status.md ledger inventory" in inventory["claim_boundary"]
    assert "semantic docs/status.md freshness" in inventory["claim_boundary"]
    assert "structural run-artifacts guide inventory" in inventory["claim_boundary"]
    assert "complete run-artifact lifecycle proof" in inventory["claim_boundary"]


def test_documentation_claim_inventory_rejects_semantic_proof_overclaim():
    inventory = documentation_claim_inventory_record()
    inventory["claim_ready"] = True
    inventory["inventory_status"] = "complete_semantic_documentation_truth_ready"
    inventory["claims"] = inventory["claims"][1:]
    inventory["missing_evidence"]["semantic_claim_verifier"] = "recorded"

    validation = validate_documentation_claim_inventory(inventory)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_inventory_status" in codes
    assert "missing_claim_id" in codes
    assert "invalid_missing_evidence_semantic_claim_verifier" in codes


def test_documentation_claim_inventory_rejects_anchor_drift():
    inventory = documentation_claim_inventory_record()
    inventory["claims"][0]["evidence_refs"] = ["README.md"]
    inventory["claims"][0]["source_span"]["line_start"] = -1
    inventory["claims"][0]["evidence_ref_records"][0]["exists"] = False
    inventory["claims"][0]["evidence_ref_records"][0]["fragment_status"] = (
        "fragment_anchor_missing"
    )
    inventory["claim_surface_heading_record_count"] = 0
    inventory["claim_surface_heading_records"] = []
    inventory["claim_surface_heading_claim_status"] = (
        "all_audited_headings_have_claim_records"
    )
    inventory["uncovered_claim_surface_heading_count"] = 0
    inventory["uncovered_claim_surface_heading_records"] = []
    inventory["uncovered_heading_todo_link_status"] = (
        "missing_uncovered_heading_todo_links"
    )
    inventory["uncovered_heading_todo_link_records"] = []
    inventory["source_anchor_status"] = "missing_claim_source_anchors"
    inventory["evidence_ref_status"] = "missing_local_evidence_refs"
    inventory["evidence_ref_fragment_status"] = "missing_fragment_anchors"

    validation = validate_documentation_claim_inventory(inventory)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_readme_current_status_scope_evidence_refs" in codes
    assert "invalid_readme_current_status_scope_source_span" in codes
    assert "invalid_readme_current_status_scope_evidence_ref_records" in codes
    assert "invalid_source_anchor_status" in codes
    assert "invalid_evidence_ref_status" in codes
    assert "invalid_evidence_ref_fragment_status" in codes
    assert "invalid_claim_surface_heading_record_count" in codes
    assert "invalid_claim_surface_heading_records" in codes
    assert "invalid_claim_surface_heading_claim_status" in codes
    assert "invalid_uncovered_claim_surface_heading_count" in codes
    assert "invalid_uncovered_claim_surface_heading_records" in codes
    assert "invalid_uncovered_heading_todo_link_status" in codes
    assert "invalid_uncovered_heading_todo_link_records" in codes


def test_documentation_claim_inventory_rejects_status_ledger_inventory_drift():
    inventory = documentation_claim_inventory_record()
    inventory["status_ledger_bullet_count"] = 0
    inventory["status_ledger_section_counts"] = {}
    inventory["status_ledger_bullet_records"] = []

    validation = validate_documentation_claim_inventory(inventory)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_status_ledger_bullet_count" in codes
    assert "invalid_status_ledger_section_counts" in codes
    assert "invalid_status_ledger_bullet_records" in codes


def test_documentation_claim_inventory_rejects_run_artifact_inventory_drift():
    inventory = documentation_claim_inventory_record()
    inventory["run_artifact_documented_count"] = 0
    inventory["run_artifact_documented_without_cleanup_names"] = ["stale.jsonl"]
    inventory["run_artifact_lifecycle_alignment_status"] = (
        "documented_and_cleanup_artifact_sets_match"
    )

    validation = validate_documentation_claim_inventory(inventory)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_run_artifact_documented_count" in codes
    assert "invalid_run_artifact_documented_without_cleanup_names" in codes
    assert "invalid_run_artifact_lifecycle_alignment_status" in codes


def test_render_documentation_claim_inventory_summary_reports_shape():
    summary = render_documentation_claim_inventory_summary(
        documentation_claim_inventory_record()
    )

    assert "Documentation claim inventory" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| inventory_status | top_level_readme_roadmap_papers_claim_inventory_without_semantic_verifier |"
        in summary
    )
    assert "| claim_count | 8 |" in summary
    assert "| readme_claim_count | 3 |" in summary
    assert "| roadmap_claim_count | 3 |" in summary
    assert "| papers_claim_count | 2 |" in summary
    assert "| missing_evidence_count | 9 |" in summary
    assert "| claim_surface_heading_count | 34 |" in summary
    assert "| uncovered_claim_surface_heading_count | 28 |" in summary
    assert "| uncovered_heading_todo_link_count | 3 |" in summary
    assert "| status_ledger_bullet_count | 251 |" in summary
    assert "| status_ledger_local_path_ref_count | 271 |" in summary
    assert "| run_artifact_documented_count | 22 |" in summary
    assert "| run_artifact_cleanup_count | 23 |" in summary
    assert "| run_artifact_documented_without_cleanup_count | 0 |" in summary
