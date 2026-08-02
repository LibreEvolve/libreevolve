from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_appendix_b_claim_inventory_boundary import (
    ALPHAEVOLVE_APPENDIX_B_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_appendix_b_claim_inventory_boundary_record,
    render_alphaevolve_appendix_b_claim_inventory_boundary_summary,
    validate_alphaevolve_appendix_b_claim_inventory_boundary,
)


def test_appendix_b_claim_inventory_accepts_pdf_and_visual_scope():
    boundary = alphaevolve_appendix_b_claim_inventory_boundary_record()

    validation = validate_alphaevolve_appendix_b_claim_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_APPENDIX_B_CLAIM_INVENTORY_BOUNDARY_SCHEMA
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["appendix_b_claim_inventory_ready"] is True
    assert boundary["alphaevolve_result_reproduction_claim_ready"] is False
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert validation.claim_count == 188
    assert validation.implemented_local_count == 0
    assert validation.implementation_gap_count == 188
    assert validation.missing_anchor_count == 0
    assert validation.missing_reference_count == 0
    assert boundary["todo_owned_gap_count"] == 188
    assert boundary["implementation_status_counts"] == {
        "not_demonstrated": 69,
        "not_implemented": 24,
        "partially_implemented": 95,
    }
    assert boundary["category_counts"] == {
        "figure_caption": 15,
        "figure_visual": 12,
        "known_bound": 21,
        "known_construction": 1,
        "mathematical_definition": 18,
        "mathematical_reasoning": 1,
        "mathematical_relation": 2,
        "method_derivation": 15,
        "metric_convention": 1,
        "problem_context": 3,
        "problem_definition": 30,
        "proof_statement": 5,
        "proof_step": 6,
        "publication_artifact": 2,
        "qualitative_result": 2,
        "reported_construction": 18,
        "reported_method": 2,
        "reported_result": 20,
        "revision_provenance": 2,
        "rounding_provenance": 2,
        "source_attribution": 10,
    }
    assert boundary["claim_records"][0]["claim_id"] == (
        "appendix_b_colab_data_and_verification_code"
    )
    assert boundary["claim_records"][-1]["claim_id"] == (
        "figure14_circle_counts_visible"
    )
    assert all(record["source_anchor_present"] for record in boundary["claim_records"])
    figure_claims = [
        record
        for record in boundary["claim_records"]
        if record["category"] in {"figure_caption", "figure_visual"}
    ]
    assert len(figure_claims) == 27
    assert "all 19 named result instances" in boundary["claim_boundary"]


def test_appendix_b_claim_inventory_gives_every_gap_dual_todo_ownership():
    boundary = alphaevolve_appendix_b_claim_inventory_boundary_record()

    incomplete = [
        record
        for record in boundary["claim_records"]
        if record["implementation_status"] != "implemented_local"
    ]

    assert len(incomplete) == 188
    for record in incomplete:
        paths = {ref["path"] for ref in record["active_todo_refs"]}
        assert "docs/todo/code.md" in paths
        assert "docs/todo/papers.md" in paths
        assert all(
            ref["exists"] and ref["required_phrase_present"]
            for ref in record["active_todo_refs"]
        )


def test_appendix_b_claim_inventory_rejects_record_and_overclaim_drift():
    boundary = deepcopy(alphaevolve_appendix_b_claim_inventory_boundary_record())
    boundary["claim_records"][0]["implementation_status"] = "implemented_local"
    boundary["claim_count"] = 187
    boundary["alphaevolve_result_reproduction_claim_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True

    validation = validate_alphaevolve_appendix_b_claim_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_claim_records" in codes
    assert "invalid_claim_count" in codes
    assert "result_reproduction_overclaim" in codes
    assert "parity_overclaim" in codes


def test_appendix_b_claim_inventory_rejects_missing_pinned_source(tmp_path):
    boundary = alphaevolve_appendix_b_claim_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_appendix_b_claim_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["appendix_b_claim_inventory_ready"] is False
    assert "source_pdf_identity_mismatch" in codes
    assert "missing_source_anchor" in codes
    assert "missing_local_reference" in codes


def test_render_appendix_b_claim_inventory_summary_reports_shape():
    summary = render_alphaevolve_appendix_b_claim_inventory_boundary_summary(
        alphaevolve_appendix_b_claim_inventory_boundary_record()
    )

    assert "AlphaEvolve Appendix B claim inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| claim_count | 188 |" in summary
    assert "| implemented_local_count | 0 |" in summary
    assert "| implementation_gap_count | 188 |" in summary
    assert "| missing_anchor_count | 0 |" in summary
