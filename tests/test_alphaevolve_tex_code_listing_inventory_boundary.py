from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_tex_code_listing_inventory_boundary import (
    ALPHAEVOLVE_TEX_CODE_LISTING_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_tex_code_listing_inventory_boundary_record,
    render_alphaevolve_tex_code_listing_inventory_boundary_summary,
    validate_alphaevolve_tex_code_listing_inventory_boundary,
)


def test_tex_code_listing_inventory_dispositions_are_complete():
    boundary = alphaevolve_tex_code_listing_inventory_boundary_record()

    validation = validate_alphaevolve_tex_code_listing_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_TEX_CODE_LISTING_INVENTORY_BOUNDARY_SCHEMA
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["retained_listing_inventory_ready"] is True
    assert boundary["listing_line_disposition_ready"] is True
    assert boundary["listing_execution_ready"] is False
    assert boundary["figure_result_reproduction_ready"] is False
    assert boundary["whole_paper_proposition_exhaustiveness_ready"] is False
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert boundary["listing_environment_count"] == 8
    assert boundary["minted_count"] == 4
    assert boundary["lstlisting_count"] == 3
    assert boundary["verbatim_count"] == 1
    assert boundary["line_count"] == 305
    assert boundary["nonblank_line_count"] == 273
    assert boundary["blank_line_count"] == 32
    assert boundary["bounded_claim_component_line_count"] == 214
    assert boundary["source_context_only_line_count"] == 21
    assert boundary["abbreviation_line_count"] == 10
    assert boundary["structural_diff_hunk_line_count"] == 4
    assert boundary["structural_blank_line_count"] == 32
    assert boundary["structural_diff_blank_line_count"] == 24
    assert boundary["listing_claim_ref_count"] == 66
    assert boundary["line_claim_ref_count"] == 344
    assert boundary["unique_mapped_claim_count"] == 60
    assert boundary["unmapped_line_count"] == 0
    assert boundary["unresolved_reference_count"] == 0
    assert boundary["new_claim_count"] == 0
    assert boundary["source_errors"] == []
    assert boundary["parse_errors"] == []


def test_tex_code_listing_inventory_preserves_line_semantics():
    boundary = alphaevolve_tex_code_listing_inventory_boundary_record()
    lines = {
        (record["listing_id"], record["source_line"]): record
        for record in boundary["line_records"]
    }

    diff_fence = lines[("methods_canonical_diff_format", 84)]
    marker = lines[("figure3_marked_program", 8)]
    abbreviation = lines[("figure3_marked_program", 30)]
    schedule_ratio = lines[("figure6_scheduling_heuristic", 134)]
    adamw_weight = lines[("figure9_program_diff_part_1", 12)]
    removed_real_loss = lines[("figure9_program_diff_part_2", 140)]
    unchanged_context = lines[("figure9_program_diff_part_2", 102)]
    diff_blank = lines[("figure9_program_diff_part_1", 53)]
    sweep_floor = lines[("figure9_program_diff_part_3", 225)]

    assert diff_fence["claim_refs"][0]["claim_id"] == (
        "generation_search_replace_blocks"
    )
    assert {ref["claim_id"] for ref in marker["claim_refs"]} == {
        "figure3_supervised_pipeline_exhibit",
        "task_evolved_blocks_and_skeleton",
        "task_multiple_marked_components",
        "task_minimal_marker_integration",
    }
    assert abbreviation["disposition"] == (
        "source_context_only_abbreviation_line"
    )
    assert abbreviation["claim_refs"] == []
    assert schedule_ratio["claim_refs"][0]["claim_id"] == (
        "figure6_memory_over_cpu_cross_ratio"
    )
    assert {ref["claim_id"] for ref in adamw_weight["claim_refs"]} == {
        "figure9_adam_to_adamw",
        "figure9_adamw_weight_decay",
    }
    assert removed_real_loss["claim_refs"][0]["claim_id"] == (
        "figure9_real_total_loss"
    )
    assert unchanged_context["disposition"] == (
        "source_context_only_baseline_line"
    )
    assert diff_blank["disposition"] == "structural_diff_blank_line"
    assert sweep_floor["claim_refs"][0]["claim_id"] == (
        "figure9_sweep_half_integer_start"
    )
    assert all(ref["resolved"] for ref in sweep_floor["claim_refs"])


def test_tex_code_listing_inventory_rejects_drift_and_overclaims():
    boundary = deepcopy(alphaevolve_tex_code_listing_inventory_boundary_record())
    boundary["line_count"] = 304
    boundary["line_records"][0]["disposition"] = "unmapped"
    boundary["listing_execution_ready"] = True
    boundary["figure_result_reproduction_ready"] = True
    boundary["whole_paper_proposition_exhaustiveness_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True
    boundary["new_claim_count"] = 1

    validation = validate_alphaevolve_tex_code_listing_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_line_count" in codes
    assert "invalid_line_records" in codes
    assert "listing_execution_overclaim" in codes
    assert "figure_reproduction_overclaim" in codes
    assert "proposition_exhaustiveness_overclaim" in codes
    assert "parity_overclaim" in codes
    assert "new_claim_overclaim" in codes


def test_tex_code_listing_inventory_rejects_missing_source_archive(tmp_path):
    boundary = alphaevolve_tex_code_listing_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_tex_code_listing_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["retained_listing_inventory_ready"] is False
    assert boundary["listing_line_disposition_ready"] is False
    assert "source_archive_identity_mismatch" in codes
    assert "source_inventory_incomplete" in codes
    assert "listing_line_parse_incomplete" in codes
    assert "listing_inventory_incomplete" in codes


def test_render_tex_code_listing_inventory_summary_reports_shape():
    summary = render_alphaevolve_tex_code_listing_inventory_boundary_summary(
        alphaevolve_tex_code_listing_inventory_boundary_record()
    )

    assert "AlphaEvolve TeX code-listing inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| listing_environment_count | 8 |" in summary
    assert "| line_count | 305 |" in summary
    assert "| unmapped_line_count | 0 |" in summary
    assert "| unresolved_reference_count | 0 |" in summary
