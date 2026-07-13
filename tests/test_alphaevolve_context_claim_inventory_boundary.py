from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_context_claim_inventory_boundary import (
    ALPHAEVOLVE_CONTEXT_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_context_claim_inventory_boundary_record,
    render_alphaevolve_context_claim_inventory_boundary_summary,
    validate_alphaevolve_context_claim_inventory_boundary,
)


def test_context_claim_inventory_accepts_pdf_anchored_scope():
    boundary = alphaevolve_context_claim_inventory_boundary_record()

    validation = validate_alphaevolve_context_claim_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_CONTEXT_CLAIM_INVENTORY_BOUNDARY_SCHEMA
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["context_claim_inventory_ready"] is True
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert validation.claim_count == 41
    assert validation.implemented_local_count == 6
    assert validation.implementation_gap_count == 35
    assert validation.missing_anchor_count == 0
    assert validation.missing_reference_count == 0
    assert boundary["todo_owned_gap_count"] == 35
    assert boundary["implementation_status_counts"] == {
        "implemented_local": 6,
        "not_demonstrated": 20,
        "not_implemented": 4,
        "partially_implemented": 11,
    }
    assert boundary["category_counts"] == {
        "abstract_platform": 4,
        "abstract_results": 6,
        "collaborator_context": 1,
        "discussion_capability": 5,
        "discussion_limitation": 3,
        "discussion_self_improvement": 4,
        "introduction_method": 13,
        "introduction_results": 5,
    }
    assert boundary["claim_records"][0]["claim_id"] == (
        "abstract_substantial_llm_capability_uplift"
    )
    assert boundary["claim_records"][-1]["claim_id"] == (
        "acknowledgements_collaborator_feedback_shaped_tool"
    )
    assert all(record["source_anchor_present"] for record in boundary["claim_records"])
    assert "detailed Results" in boundary["claim_boundary"]


def test_context_claim_inventory_gives_every_incomplete_claim_todo_ownership():
    boundary = alphaevolve_context_claim_inventory_boundary_record()

    incomplete = [
        record
        for record in boundary["claim_records"]
        if record["implementation_status"] != "implemented_local"
    ]

    assert len(incomplete) == 35
    assert all(record["active_todo_refs"] for record in incomplete)
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in incomplete
        for ref in record["active_todo_refs"]
    )


def test_context_claim_inventory_rejects_status_record_and_parity_drift():
    boundary = deepcopy(alphaevolve_context_claim_inventory_boundary_record())
    boundary["claim_records"][0]["implementation_status"] = "implemented_local"
    boundary["claim_count"] = 40
    boundary["alphaevolve_parity_claim_ready"] = True

    validation = validate_alphaevolve_context_claim_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_claim_records" in codes
    assert "invalid_claim_count" in codes
    assert "parity_overclaim" in codes


def test_context_claim_inventory_rejects_missing_pinned_source(tmp_path):
    boundary = alphaevolve_context_claim_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_context_claim_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["context_claim_inventory_ready"] is False
    assert "source_pdf_identity_mismatch" in codes
    assert "missing_source_anchor" in codes
    assert "missing_local_reference" in codes


def test_render_context_claim_inventory_summary_reports_shape():
    summary = render_alphaevolve_context_claim_inventory_boundary_summary(
        alphaevolve_context_claim_inventory_boundary_record()
    )

    assert "AlphaEvolve context claim inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| claim_count | 41 |" in summary
    assert "| implemented_local_count | 6 |" in summary
    assert "| implementation_gap_count | 35 |" in summary
    assert "| missing_anchor_count | 0 |" in summary
