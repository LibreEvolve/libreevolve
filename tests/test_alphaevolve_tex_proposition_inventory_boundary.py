from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_tex_proposition_inventory_boundary import (
    ALPHAEVOLVE_TEX_PROPOSITION_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_tex_proposition_inventory_boundary_record,
    render_alphaevolve_tex_proposition_inventory_boundary_summary,
    validate_alphaevolve_tex_proposition_inventory_boundary,
)


def test_tex_proposition_inventory_accepts_abstract_and_introduction_scope():
    boundary = alphaevolve_tex_proposition_inventory_boundary_record()

    validation = validate_alphaevolve_tex_proposition_inventory_boundary(boundary)

    assert validation.ok is True
    assert (
        boundary["schema"]
        == ALPHAEVOLVE_TEX_PROPOSITION_INVENTORY_BOUNDARY_SCHEMA
    )
    assert boundary["source_prose_ready"] is True
    assert boundary["proposition_inventory_ready"] is True
    assert boundary["review_scope_complete"] is True
    assert boundary["whole_paper_semantic_exhaustiveness_claim_ready"] is False
    assert boundary["independent_semantic_review_ready"] is False
    assert validation.reviewed_sentence_count == 37
    assert validation.proposition_count == 93
    assert validation.remaining_sentence_count == 365
    assert validation.unmapped_proposition_count == 0
    assert validation.unresolved_reference_count == 0
    assert boundary["reviewed_sentence_fraction"] == 37 / 402
    assert boundary["reviewed_source_files"] == ["introduction.tex", "main.tex"]
    assert boundary["disposition_counts"] == {
        "author_interpretation": 1,
        "author_outlook": 2,
        "existing_bounded_claim_mapping": 81,
        "source_context_only": 9,
    }
    assert boundary["claim_reference_count"] == 94
    assert boundary["unique_claim_reference_count"] == 62
    assert boundary["implementation_relevant_proposition_count"] == 71


def test_tex_proposition_inventory_resolves_every_reviewed_record():
    boundary = alphaevolve_tex_proposition_inventory_boundary_record()

    assert len(boundary["reviewed_sentence_records"]) == 37
    assert len(boundary["proposition_records"]) == 93
    assert all(
        record["review_status"]
        == "manual_static_semantic_decomposition_complete"
        for record in boundary["reviewed_sentence_records"]
    )
    assert all(
        ref["resolved"]
        for record in boundary["proposition_records"]
        for ref in record["claim_refs"]
    )
    assert all(
        record["source_quote_start"] >= 0
        and record["source_quote_end"] > record["source_quote_start"]
        for record in boundary["proposition_records"]
    )


def test_tex_proposition_inventory_records_new_and_repaired_claims():
    boundary = alphaevolve_tex_proposition_inventory_boundary_record()
    mapped_ids = {
        ref["claim_id"]
        for record in boundary["proposition_records"]
        for ref in record["claim_refs"]
    }

    assert boundary["new_bounded_claim_ids"] == [
        "introduction_algorithm_search_outperforms_direct_solution_search"
    ]
    assert set(boundary["repaired_sentence_claim_ids"]) == {
        "abstract_complex_4x4_matrix_48_multiplications",
        "introduction_complex_4x4_matrix_48_multiplications",
        "introduction_erdos_minimum_overlap_result",
        "introduction_seventy_five_percent_math_best_known",
    }
    assert set(boundary["new_bounded_claim_ids"]) <= mapped_ids
    assert set(boundary["repaired_sentence_claim_ids"]) <= mapped_ids


def test_tex_proposition_inventory_rejects_record_and_overclaim_drift():
    boundary = deepcopy(alphaevolve_tex_proposition_inventory_boundary_record())
    boundary["proposition_records"][0]["statement"] = "drift"
    boundary["proposition_count"] = 92
    boundary["reviewed_source_files"] = []
    boundary["parse_errors"] = ["fabricated_error"]
    boundary["whole_paper_semantic_exhaustiveness_claim_ready"] = True
    boundary["independent_semantic_review_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True

    validation = validate_alphaevolve_tex_proposition_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_proposition_records" in codes
    assert "invalid_proposition_count" in codes
    assert "invalid_reviewed_source_files" in codes
    assert "invalid_parse_errors" in codes
    assert "whole_paper_semantic_exhaustiveness_claim_ready_overclaim" in codes
    assert "independent_semantic_review_ready_overclaim" in codes
    assert "alphaevolve_parity_claim_ready_overclaim" in codes


def test_tex_proposition_inventory_rejects_missing_pinned_source(tmp_path):
    boundary = alphaevolve_tex_proposition_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_tex_proposition_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["source_prose_ready"] is False
    assert boundary["proposition_inventory_ready"] is False
    assert "source_prose_incomplete" in codes
    assert "proposition_inventory_incomplete" in codes


def test_render_tex_proposition_inventory_summary_reports_shape():
    summary = render_alphaevolve_tex_proposition_inventory_boundary_summary(
        alphaevolve_tex_proposition_inventory_boundary_record()
    )

    assert "AlphaEvolve TeX proposition inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| reviewed_sentence_count | 37 |" in summary
    assert "| proposition_count | 93 |" in summary
    assert "| remaining_sentence_count | 365 |" in summary
    assert "| validation_status | ok |" in summary
