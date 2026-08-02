from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_tex_math_inventory_boundary import (
    ALPHAEVOLVE_TEX_MATH_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_tex_math_inventory_boundary_record,
    render_alphaevolve_tex_math_inventory_boundary_summary,
    validate_alphaevolve_tex_math_inventory_boundary,
)


def test_tex_math_inventory_accepts_complete_explicit_delimiter_scope():
    boundary = alphaevolve_tex_math_inventory_boundary_record()

    validation = validate_alphaevolve_tex_math_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_TEX_MATH_INVENTORY_BOUNDARY_SCHEMA
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["math_construct_inventory_ready"] is True
    assert boundary["math_construct_disposition_ready"] is True
    assert validation.math_construct_count == 309
    assert validation.inline_construct_count == 291
    assert validation.display_construct_count == 18
    assert boundary["delimiter_kind_counts"] == {
        "bracket": 1,
        "double_dollar": 11,
        "environment": 5,
        "paren": 1,
        "single_dollar": 291,
    }
    assert boundary["source_detail_overlap_count"] == 34
    assert boundary["table_cell_overlap_count"] == 75
    assert boundary["direct_claim_mapping_count"] == 200
    assert boundary["new_claim_count"] == 0


def test_tex_math_inventory_resolves_every_construct_disposition():
    boundary = alphaevolve_tex_math_inventory_boundary_record()
    records = boundary["math_construct_records"]

    assert len({record["math_construct_id"] for record in records}) == 309
    assert boundary["unmapped_construct_count"] == 0
    assert boundary["unresolved_reference_count"] == 0
    assert all(
        record["claim_refs"]
        or record["named_span_refs"]
        or record["supporting_boundary_refs"]
        or record["supporting_unit_refs"]
        for record in records
    )
    assert any(
        record["delimiter_kind"] == "single_dollar"
        and record["render_mode"] == "display"
        and record["source_file"] == "appendix.tex"
        and record["source_line"] == 153
        for record in records
    )
    mapped_ids = {
        ref["claim_id"]
        for record in records
        for ref in record["claim_refs"]
    }
    assert "introduction_complex_4x4_matrix_48_multiplications" in mapped_ids
    assert "introduction_seventy_five_percent_math_best_known" in mapped_ids
    assert "introduction_kissing_number_d11_improvement" in mapped_ids
    assert "section3_1_3x3_minimum_rank_unknown" in mapped_ids


def test_tex_math_inventory_rejects_record_count_and_parity_drift():
    boundary = deepcopy(alphaevolve_tex_math_inventory_boundary_record())
    boundary["math_construct_records"][0]["normalized_body"] = "drift"
    boundary["math_construct_count"] = 308
    boundary["alphaevolve_parity_claim_ready"] = True

    validation = validate_alphaevolve_tex_math_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_math_construct_records" in codes
    assert "invalid_math_construct_count" in codes
    assert "alphaevolve_parity_claim_ready_overclaim" in codes


def test_tex_math_inventory_rejects_missing_pinned_source(tmp_path):
    boundary = alphaevolve_tex_math_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_tex_math_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["math_construct_inventory_ready"] is False
    assert "source_archive_identity_mismatch" in codes
    assert "source_inventory_incomplete" in codes


def test_render_tex_math_inventory_summary_reports_shape():
    summary = render_alphaevolve_tex_math_inventory_boundary_summary(
        alphaevolve_tex_math_inventory_boundary_record()
    )

    assert "AlphaEvolve TeX math inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| math_construct_count | 309 |" in summary
    assert "| inline_construct_count | 291 |" in summary
    assert "| display_construct_count | 18 |" in summary
    assert "| unmapped_construct_count | 0 |" in summary
