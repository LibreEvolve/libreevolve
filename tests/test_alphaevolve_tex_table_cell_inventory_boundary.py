from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_tex_table_cell_inventory_boundary import (
    ALPHAEVOLVE_TEX_TABLE_CELL_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_tex_table_cell_inventory_boundary_record,
    render_alphaevolve_tex_table_cell_inventory_boundary_summary,
    validate_alphaevolve_tex_table_cell_inventory_boundary,
)


def test_tex_table_cell_inventory_dispositions_are_complete():
    boundary = alphaevolve_tex_table_cell_inventory_boundary_record()

    validation = validate_alphaevolve_tex_table_cell_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_TEX_TABLE_CELL_INVENTORY_BOUNDARY_SCHEMA
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["row_cell_inventory_ready"] is True
    assert boundary["table_cell_semantic_disposition_ready"] is True
    assert boundary["citation_semantic_mapping_ready"] is False
    assert boundary["table_result_reproduction_ready"] is False
    assert boundary["whole_paper_proposition_exhaustiveness_ready"] is False
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert boundary["table_count"] == 3
    assert boundary["tabular_block_count"] == 5
    assert boundary["row_count"] == 83
    assert boundary["data_row_count"] == 78
    assert boundary["header_row_count"] == 5
    assert boundary["cell_count"] == 240
    assert boundary["bounded_claim_component_cell_count"] == 218
    assert boundary["source_context_only_cell_count"] == 8
    assert boundary["structural_header_cell_count"] == 14
    assert boundary["row_claim_ref_count"] == 78
    assert boundary["cell_claim_ref_count"] == 218
    assert boundary["unique_mapped_claim_count"] == 78
    assert boundary["citation_occurrence_count"] == 71
    assert boundary["citation_key_link_count"] == 72
    assert boundary["unmapped_row_count"] == 0
    assert boundary["unmapped_cell_count"] == 0
    assert boundary["unresolved_reference_count"] == 0
    assert boundary["new_claim_count"] == 0
    assert boundary["source_errors"] == []
    assert boundary["parse_errors"] == []


def test_tex_table_cell_inventory_preserves_row_and_cell_semantics():
    boundary = alphaevolve_tex_table_cell_inventory_boundary_record()
    rows = {record["table_row_id"]: record for record in boundary["row_records"]}
    cells = {
        record["table_cell_id"]: record for record in boundary["cell_records"]
    }

    table_1_row = rows["table_1_data_001"]
    table_1_baseline = cells["table_1_data_001_cell_01"]
    table_1_alphaevolve = cells["table_1_data_001_cell_02"]
    table_2_target = cells["table_2_data_003_cell_01"]
    table_3_result = cells["table_3_data_054_cell_03"]

    assert table_1_row["claim_refs"][0]["claim_id"] == "table1_entire_code_file"
    assert table_1_baseline["disposition"] == "source_context_only_baseline_cell"
    assert table_1_baseline["claim_refs"] == []
    assert table_1_alphaevolve["disposition"] == "bounded_claim_component"
    assert table_1_alphaevolve["claim_refs"][0]["claim_id"] == (
        "table1_entire_code_file"
    )
    assert table_2_target["claim_refs"][0]["claim_id"] == (
        "table2_mm_2x4x8_rank51"
    )
    assert table_3_result["claim_refs"][0]["claim_id"] == (
        "table3_mm_6x6x6_rank_result"
    )
    assert all(ref["resolved"] for ref in table_3_result["claim_refs"])


def test_tex_table_cell_inventory_rejects_drift_and_overclaims():
    boundary = deepcopy(alphaevolve_tex_table_cell_inventory_boundary_record())
    boundary["cell_count"] = 239
    boundary["cell_records"][0]["disposition"] = "unmapped"
    boundary["citation_semantic_mapping_ready"] = True
    boundary["table_result_reproduction_ready"] = True
    boundary["whole_paper_proposition_exhaustiveness_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True
    boundary["new_claim_count"] = 1

    validation = validate_alphaevolve_tex_table_cell_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_cell_count" in codes
    assert "invalid_cell_records" in codes
    assert "citation_semantic_overclaim" in codes
    assert "table_reproduction_overclaim" in codes
    assert "proposition_exhaustiveness_overclaim" in codes
    assert "parity_overclaim" in codes
    assert "new_claim_overclaim" in codes


def test_tex_table_cell_inventory_rejects_missing_source_archive(tmp_path):
    boundary = alphaevolve_tex_table_cell_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_tex_table_cell_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["row_cell_inventory_ready"] is False
    assert boundary["table_cell_semantic_disposition_ready"] is False
    assert "source_archive_identity_mismatch" in codes
    assert "source_inventory_incomplete" in codes
    assert "table_cell_parse_incomplete" in codes


def test_render_tex_table_cell_inventory_summary_reports_shape():
    summary = render_alphaevolve_tex_table_cell_inventory_boundary_summary(
        alphaevolve_tex_table_cell_inventory_boundary_record()
    )

    assert "AlphaEvolve TeX table-cell inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| table_count | 3 |" in summary
    assert "| tabular_block_count | 5 |" in summary
    assert "| row_count | 83 |" in summary
    assert "| cell_count | 240 |" in summary
    assert "| unmapped_row_count | 0 |" in summary
    assert "| unmapped_cell_count | 0 |" in summary
    assert "| unresolved_reference_count | 0 |" in summary
