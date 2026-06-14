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
    assert validation.missing_evidence_count == 7
    assert inventory["schema"] == DOCUMENTATION_CLAIM_INVENTORY_SCHEMA
    assert inventory["claim_ready"] is False
    assert inventory["source_anchor_status"] == "all_claim_source_anchors_recorded"
    assert inventory["source_anchor_missing_claim_ids"] == []
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
    assert (
        "does not claim complete README coverage"
        in inventory["claim_boundary"]
    )


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
    inventory["source_anchor_status"] = "missing_claim_source_anchors"

    validation = validate_documentation_claim_inventory(inventory)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_readme_current_status_scope_evidence_refs" in codes
    assert "invalid_readme_current_status_scope_source_span" in codes
    assert "invalid_source_anchor_status" in codes


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
