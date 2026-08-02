from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_tex_prose_inventory_boundary import (
    ALPHAEVOLVE_TEX_PROSE_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_tex_prose_inventory_boundary_record,
    render_alphaevolve_tex_prose_inventory_boundary_summary,
    validate_alphaevolve_tex_prose_inventory_boundary,
)


def test_tex_prose_inventory_accepts_complete_sentence_disposition_scope():
    boundary = alphaevolve_tex_prose_inventory_boundary_record()

    validation = validate_alphaevolve_tex_prose_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_TEX_PROSE_INVENTORY_BOUNDARY_SCHEMA
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["prose_inventory_ready"] is True
    assert boundary["prose_disposition_ready"] is True
    assert boundary["whole_paper_semantic_exhaustiveness_claim_ready"] is False
    assert boundary["mathematical_correctness_claim_ready"] is False
    assert boundary["result_reproduction_claim_ready"] is False
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert validation.paragraph_count == 128
    assert validation.sentence_count == 402
    assert boundary["disposition_counts"] == {
        "existing_bounded_claim_mapping": 372,
        "reviewed_nonclaim": 30,
    }
    assert boundary["excluded_range_count"] == 37


def test_tex_prose_inventory_preserves_file_counts_and_resolved_dispositions():
    boundary = alphaevolve_tex_prose_inventory_boundary_record()

    assert boundary["paragraph_counts_by_file"] == {
        "ablations.tex": 7,
        "acknowledgement.tex": 6,
        "appendix.tex": 34,
        "discussion.tex": 5,
        "introduction.tex": 8,
        "main.tex": 1,
        "methods.tex": 24,
        "related_work.tex": 11,
        "results.tex": 32,
    }
    assert boundary["sentence_counts_by_file"] == {
        "ablations.tex": 24,
        "acknowledgement.tex": 7,
        "appendix.tex": 96,
        "discussion.tex": 14,
        "introduction.tex": 29,
        "main.tex": 8,
        "methods.tex": 61,
        "related_work.tex": 41,
        "results.tex": 122,
    }
    assert boundary["unmapped_sentence_count"] == 0
    assert boundary["unresolved_reference_count"] == 0
    assert all(
        record["claim_refs"] or record["nonclaim_disposition"]
        for record in boundary["sentence_records"]
    )
    assert all(
        ref["resolved"]
        for record in boundary["sentence_records"]
        for ref in record["claim_refs"]
    )


def test_tex_prose_inventory_maps_new_claims_and_disambiguates_repeated_anchors():
    boundary = alphaevolve_tex_prose_inventory_boundary_record()
    records = {
        (
            record["source_file"],
            record["source_line"],
            record["line_ordinal"],
        ): record
        for record in boundary["sentence_records"]
    }
    mapped_ids = {
        ref["claim_id"]
        for record in boundary["sentence_records"]
        for ref in record["claim_refs"]
    }

    assert {
        "task_metric_maximization_convention",
        "task_problem_specific_abstraction_choice",
        "task_symmetry_guided_abstraction_bias",
        "evaluation_order_hundred_compute_hours_per_candidate",
        "evaluation_multi_metric_single_target_uplift",
        "section3_1_tensor_decomposition_algorithm_representation",
        "section3_1_low_rank_decomposition_search_objective",
    } <= mapped_ids
    assert [
        ref["claim_id"] for ref in records[("ablations.tex", 8, 3)]["claim_refs"]
    ] == ["no_context_variant_name"]
    assert "already_highly_optimized_baseline" not in {
        ref["claim_id"] for ref in records[("results.tex", 168, 0)]["claim_refs"]
    }
    assert "b8_3d_prior_sqrt_4_168" not in {
        ref["claim_id"] for ref in records[("appendix.tex", 209, 0)]["claim_refs"]
    }
    assert "b8_2d_prior_sqrt_12_890" not in {
        ref["claim_id"] for ref in records[("appendix.tex", 212, 0)]["claim_refs"]
    }


def test_tex_prose_inventory_rejects_record_count_and_overclaim_drift():
    boundary = deepcopy(alphaevolve_tex_prose_inventory_boundary_record())
    boundary["sentence_records"][0]["rendered_text"] = "drift"
    boundary["sentence_count"] = 401
    boundary["whole_paper_semantic_exhaustiveness_claim_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True

    validation = validate_alphaevolve_tex_prose_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_sentence_records" in codes
    assert "invalid_sentence_count" in codes
    assert "whole_paper_semantic_exhaustiveness_claim_ready_overclaim" in codes
    assert "alphaevolve_parity_claim_ready_overclaim" in codes


def test_tex_prose_inventory_rejects_missing_pinned_source(tmp_path):
    boundary = alphaevolve_tex_prose_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_tex_prose_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["prose_inventory_ready"] is False
    assert boundary["prose_disposition_ready"] is False
    assert "source_archive_identity_mismatch" in codes
    assert "source_inventory_incomplete" in codes


def test_render_tex_prose_inventory_summary_reports_shape():
    summary = render_alphaevolve_tex_prose_inventory_boundary_summary(
        alphaevolve_tex_prose_inventory_boundary_record()
    )

    assert "AlphaEvolve TeX prose inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| paragraph_count | 128 |" in summary
    assert "| sentence_count | 402 |" in summary
    assert "| unmapped_sentence_count | 0 |" in summary
    assert "| unresolved_reference_count | 0 |" in summary
