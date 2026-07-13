from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_math_result_claim_inventory_boundary import (
    ALPHAEVOLVE_MATH_RESULT_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_math_result_claim_inventory_boundary_record,
    render_alphaevolve_math_result_claim_inventory_boundary_summary,
    validate_alphaevolve_math_result_claim_inventory_boundary,
)


def test_math_result_claim_inventory_accepts_pdf_anchored_scope():
    boundary = alphaevolve_math_result_claim_inventory_boundary_record()

    validation = validate_alphaevolve_math_result_claim_inventory_boundary(boundary)

    assert validation.ok is True
    assert (
        boundary["schema"]
        == ALPHAEVOLVE_MATH_RESULT_CLAIM_INVENTORY_BOUNDARY_SCHEMA
    )
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["math_result_claim_inventory_ready"] is True
    assert boundary["alphaevolve_result_reproduction_claim_ready"] is False
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert validation.claim_count == 63
    assert validation.implemented_local_count == 2
    assert validation.implementation_gap_count == 61
    assert validation.missing_anchor_count == 0
    assert validation.missing_reference_count == 0
    assert boundary["todo_owned_gap_count"] == 61
    assert boundary["implementation_status_counts"] == {
        "implemented_local": 2,
        "not_demonstrated": 41,
        "not_implemented": 4,
        "partially_implemented": 16,
    }
    assert boundary["category_counts"] == {
        "artifact_and_collaboration": 7,
        "constructive_math_method": 21,
        "figure_5_domain": 4,
        "figure_5_result_row": 9,
        "math_aggregate_outcome": 8,
        "math_domain_result": 7,
        "math_research_context": 7,
    }
    assert boundary["claim_records"][0]["claim_id"] == (
        "section3_2_optimal_near_optimal_construction_frontier"
    )
    assert boundary["claim_records"][-1]["claim_id"] == (
        "section3_2_ai_human_math_partnership_potential"
    )
    assert all(record["source_anchor_present"] for record in boundary["claim_records"])
    correction = boundary["source_fidelity_correction"]
    assert correction["incorrect_attribution_present_in_pinned_pdf"] is False
    assert correction["actual_source_text_present_in_pinned_pdf"] is True
    assert correction["corrected_boundary_removes_false_attribution"] is True
    assert correction["source_fidelity_correction_ready"] is True
    assert "Appendix B detail exhaustiveness" in boundary["claim_boundary"]


def test_math_result_claim_inventory_gives_every_gap_todo_ownership():
    boundary = alphaevolve_math_result_claim_inventory_boundary_record()

    incomplete = [
        record
        for record in boundary["claim_records"]
        if record["implementation_status"] != "implemented_local"
    ]

    assert len(incomplete) == 61
    assert all(record["active_todo_refs"] for record in incomplete)
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in incomplete
        for ref in record["active_todo_refs"]
    )


def test_math_result_claim_inventory_rejects_record_and_overclaim_drift():
    boundary = deepcopy(alphaevolve_math_result_claim_inventory_boundary_record())
    boundary["claim_records"][0]["implementation_status"] = "implemented_local"
    boundary["claim_count"] = 62
    boundary["alphaevolve_result_reproduction_claim_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True
    boundary["source_fidelity_correction"][
        "corrected_boundary_removes_false_attribution"
    ] = False

    validation = validate_alphaevolve_math_result_claim_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_claim_records" in codes
    assert "invalid_claim_count" in codes
    assert "invalid_source_fidelity_correction" in codes
    assert "result_reproduction_overclaim" in codes
    assert "parity_overclaim" in codes


def test_math_result_claim_inventory_rejects_missing_pinned_source(tmp_path):
    boundary = alphaevolve_math_result_claim_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_math_result_claim_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["math_result_claim_inventory_ready"] is False
    assert "source_pdf_identity_mismatch" in codes
    assert "missing_source_anchor" in codes
    assert "missing_local_reference" in codes
    assert "source_fidelity_correction_incomplete" in codes


def test_render_math_result_claim_inventory_summary_reports_shape():
    summary = render_alphaevolve_math_result_claim_inventory_boundary_summary(
        alphaevolve_math_result_claim_inventory_boundary_record()
    )

    assert "AlphaEvolve math result claim inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| claim_count | 63 |" in summary
    assert "| implemented_local_count | 2 |" in summary
    assert "| implementation_gap_count | 61 |" in summary
    assert "| missing_anchor_count | 0 |" in summary
