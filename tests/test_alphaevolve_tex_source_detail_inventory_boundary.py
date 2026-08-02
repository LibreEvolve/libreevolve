from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_tex_source_detail_inventory_boundary import (
    ALPHAEVOLVE_TEX_SOURCE_DETAIL_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_tex_source_detail_inventory_boundary_record,
    render_alphaevolve_tex_source_detail_inventory_boundary_summary,
    validate_alphaevolve_tex_source_detail_inventory_boundary,
)


def test_tex_source_detail_inventory_dispositions_are_complete():
    boundary = alphaevolve_tex_source_detail_inventory_boundary_record()

    validation = validate_alphaevolve_tex_source_detail_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_TEX_SOURCE_DETAIL_INVENTORY_BOUNDARY_SCHEMA
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["construct_inventory_ready"] is True
    assert boundary["construct_disposition_ready"] is True
    assert boundary["proposition_level_semantic_exhaustiveness_ready"] is False
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert boundary["caption_count"] == 22
    assert boundary["equation_count"] == 5
    assert boundary["footnote_count"] == 3
    assert boundary["excluded_footnote_macro_template_count"] == 1
    assert boundary["source_detail_count"] == 30
    assert boundary["mapped_bounded_claim_construct_count"] == 24
    assert boundary["metadata_boundary_construct_count"] == 1
    assert boundary["named_span_locator_count"] == 2
    assert boundary["decorative_marker_count"] == 3
    assert boundary["unmapped_construct_count"] == 0
    assert boundary["mapped_claim_ref_count"] == 80
    assert boundary["unresolved_reference_count"] == 0
    assert boundary["new_claim_count"] == 0
    assert boundary["parse_errors"] == []


def test_tex_source_detail_inventory_preserves_semantic_dispositions():
    boundary = alphaevolve_tex_source_detail_inventory_boundary_record()
    records = {
        record["construct_id"]: record
        for record in boundary["source_detail_records"]
    }

    figure_7 = records["caption_figure_7"]
    equation_4 = records["equation_b11_inner_product"]
    title_footnote = records["footnote_title_equal_contribution"]
    decorative = [
        record
        for record in records.values()
        if record["disposition"] == "decorative_marker"
    ]

    assert figure_7["source_label"] == "fig:tiling_heuristic"
    assert figure_7["source_page"] == 15
    assert len(figure_7["claim_refs"]) == 8
    assert all(ref["resolved"] for ref in figure_7["claim_refs"])
    assert equation_4["source_label"] == "eq:abi"
    assert equation_4["tex_environment"] == "equation"
    assert equation_4["claim_refs"][0]["claim_id"] == (
        "b11_proof_inner_product_equation_4"
    )
    assert title_footnote["disposition"] == "publication_metadata_boundary"
    assert len(title_footnote["supporting_boundary_refs"]) == 2
    assert all(ref["resolved"] for ref in title_footnote["supporting_boundary_refs"])
    assert len(decorative) == 3
    assert {record["source_label"] for record in decorative} == {
        "fig:grounding-api",
        "fig:grounding-llm",
        "fig:grounding-prompt",
    }


def test_tex_source_detail_inventory_rejects_drift_and_overclaims():
    boundary = deepcopy(alphaevolve_tex_source_detail_inventory_boundary_record())
    boundary["source_detail_count"] = 29
    boundary["source_detail_records"][0]["disposition"] = "unmapped"
    boundary["proposition_level_semantic_exhaustiveness_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True
    boundary["new_claim_count"] = 1

    validation = validate_alphaevolve_tex_source_detail_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_source_detail_count" in codes
    assert "invalid_source_detail_records" in codes
    assert "semantic_exhaustiveness_overclaim" in codes
    assert "parity_overclaim" in codes
    assert "new_claim_overclaim" in codes


def test_tex_source_detail_inventory_rejects_missing_source_archive(tmp_path):
    boundary = alphaevolve_tex_source_detail_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_tex_source_detail_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["construct_inventory_ready"] is False
    assert boundary["construct_disposition_ready"] is False
    assert "source_archive_identity_mismatch" in codes
    assert "source_inventory_incomplete" in codes
    assert "source_detail_parse_incomplete" in codes


def test_render_tex_source_detail_inventory_summary_reports_shape():
    summary = render_alphaevolve_tex_source_detail_inventory_boundary_summary(
        alphaevolve_tex_source_detail_inventory_boundary_record()
    )

    assert "AlphaEvolve TeX source-detail inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| source_detail_count | 30 |" in summary
    assert "| caption_count | 22 |" in summary
    assert "| equation_count | 5 |" in summary
    assert "| footnote_count | 3 |" in summary
    assert "| unmapped_construct_count | 0 |" in summary
    assert "| unresolved_reference_count | 0 |" in summary
