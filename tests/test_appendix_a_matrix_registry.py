import json

from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    CURATION_SCHEMA,
    EXPECTED_TARGET_COUNT,
    RESOURCE_FRONTIER_SCHEMA,
    ROW_NOTE_SCHEMA,
    SUBSET_SCOPE_SCHEMA,
    TARGET_SUITE,
    appendix_a_matrix_curation_record,
    appendix_a_matrix_resource_frontier_record,
    appendix_a_matrix_row_note_records,
    appendix_a_matrix_subset_scope_record,
    matrix_target_by_id,
    matrix_target_records,
    render_appendix_a_matrix_curation_summary,
    render_appendix_a_matrix_resource_frontier_summary,
    render_appendix_a_matrix_registry_summary,
    render_appendix_a_matrix_row_note_summary,
    render_appendix_a_matrix_subset_scope_summary,
    validate_appendix_a_matrix_curation,
    validate_appendix_a_matrix_resource_frontier,
    validate_appendix_a_matrix_registry,
    validate_appendix_a_matrix_row_notes,
    validate_appendix_a_matrix_subset_scope,
)


def test_appendix_a_matrix_registry_validates_table3_targets():
    report = validate_appendix_a_matrix_registry()

    assert report.ok is True
    assert report.target_count == EXPECTED_TARGET_COUNT == 54
    assert report.matched_count == 38
    assert report.surpassed_count == 14
    assert report.fell_behind_count == 2
    assert report.issues == []


def test_appendix_a_matrix_registry_exposes_target_lookup():
    target = matrix_target_by_id("mm_4x4x4")

    assert target == {
        "id": "mm_4x4x4",
        "dimensions": [4, 4, 4],
        "best_known_rank": 49,
        "alphaevolve_rank": 48,
        "outcome": "surpassed",
        "exact_algorithm": True,
    }
    assert matrix_target_by_id("mm_missing") is None
    assert len(matrix_target_records()) == 54


def test_appendix_a_matrix_registry_rejects_malformed_targets(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": TARGET_SUITE,
                "targets": [
                    {
                        "id": "mm_4x4x4",
                        "dimensions": [4, 4, 4],
                        "best_known_rank": 49,
                        "alphaevolve_rank": 49,
                        "outcome": "surpassed",
                        "exact_algorithm": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    report = validate_appendix_a_matrix_registry(path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_target_count" in codes
    assert "invalid_surpassed_rank" in codes
    assert "missing_exact_algorithm" in codes
    assert "invalid_outcome_counts" in codes


def test_appendix_a_matrix_registry_summary_renders_counts():
    summary = render_appendix_a_matrix_registry_summary()

    assert "AlphaEvolve Appendix A matrix target registry" in summary
    assert "| target_count | 54 |" in summary
    assert "| matched | 38 |" in summary
    assert "| surpassed | 14 |" in summary
    assert "| fell_behind | 2 |" in summary


def test_appendix_a_matrix_curation_validates_selection_and_symmetry_policy():
    record = appendix_a_matrix_curation_record()
    report = validate_appendix_a_matrix_curation(record)

    assert report.ok is True
    assert record["schema"] == CURATION_SCHEMA
    assert report.included_target_count == EXPECTED_TARGET_COUNT == 54
    assert report.outside_rough_rule_count == 1
    assert report.omitted_equivalent_count == 155
    assert report.issues == []
    assert record["selection_policy"]["p_cutoff_policy"] == "reasonable_cutoff_not_numerically_specified_in_paper"
    assert record["symmetry_policy"]["canonical_order"] == "m <= n <= p"


def test_appendix_a_matrix_curation_rejects_policy_drift():
    record = appendix_a_matrix_curation_record()
    record["selection_policy"]["rough_m_max"] = 6
    record["symmetry_policy"]["canonical_order"] = "as_reported"
    record["source_pdf_page"] = 33

    report = validate_appendix_a_matrix_curation(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_selection_rough_m_max" in codes
    assert "invalid_canonical_order" in codes
    assert "invalid_source_pdf_page" in codes


def test_appendix_a_matrix_curation_rejects_missing_target_and_omission():
    record = appendix_a_matrix_curation_record()
    record["included_targets"] = record["included_targets"][:-1]
    record["omitted_equivalent_targets"] = record["omitted_equivalent_targets"][:-1]

    report = validate_appendix_a_matrix_curation(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "missing_included_target" in codes
    assert "missing_omitted_equivalent_target" in codes


def test_appendix_a_matrix_curation_rejects_bad_inclusion_record():
    record = appendix_a_matrix_curation_record()
    record["included_targets"][0]["selection_bucket"] = "reported_outside_rough_rule"
    record["included_targets"][0]["canonical_representative"] = False
    record["included_targets"][0]["dimensions"] = [2, 2, 3]

    report = validate_appendix_a_matrix_curation(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_selection_bucket" in codes
    assert "missing_canonical_representative" in codes
    assert "included_target_dimension_mismatch" in codes


def test_appendix_a_matrix_curation_summary_renders_counts():
    summary = render_appendix_a_matrix_curation_summary()

    assert "AlphaEvolve Appendix A matrix target-suite curation" in summary
    assert "| included_target_count | 54 |" in summary
    assert "| omitted_equivalent_count | 155 |" in summary
    assert "| outside_rough_rule_count | 1 |" in summary


def test_appendix_a_matrix_resource_frontier_validates_paper_oom_boundary():
    record = appendix_a_matrix_resource_frontier_record()
    report = validate_appendix_a_matrix_resource_frontier(record)

    assert report.ok is True
    assert record["schema"] == RESOURCE_FRONTIER_SCHEMA
    assert report.attempted_scope_count == 1
    assert report.local_artifact_count == 0
    assert report.issues == []
    observation = record["frontier_observations"][0]
    assert observation["target_scope"] == "sizes_beyond_5x5x5"
    assert observation["seed_count"] == 1000
    assert observation["accelerator_profile"] == "single_gpu_accelerator"
    assert observation["resource_status"] == "often_out_of_memory"
    assert observation["local_execution_evidence"] is False


def test_appendix_a_matrix_resource_frontier_rejects_overclaimed_local_artifacts():
    record = appendix_a_matrix_resource_frontier_record()
    observation = record["frontier_observations"][0]
    observation["local_execution_evidence"] = True
    observation["local_artifacts"] = [{"path": "runs/matrix_oom.json"}]

    report = validate_appendix_a_matrix_resource_frontier(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert report.local_artifact_count == 1
    assert "local_execution_overclaim" in codes
    assert "unexpected_local_artifacts" in codes


def test_appendix_a_matrix_resource_frontier_rejects_source_drift():
    record = appendix_a_matrix_resource_frontier_record()
    record["source_pdf_page"] = 35
    observation = record["frontier_observations"][0]
    observation["seed_count"] = 100
    observation["source_phrase"] = "larger sizes were expensive"

    report = validate_appendix_a_matrix_resource_frontier(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_source_pdf_page" in codes
    assert "invalid_seed_count" in codes
    assert "missing_source_phrase" in codes


def test_appendix_a_matrix_resource_frontier_summary_renders_counts():
    summary = render_appendix_a_matrix_resource_frontier_summary()

    assert "AlphaEvolve Appendix A matrix resource frontier" in summary
    assert "| attempted_scope_count | 1 |" in summary
    assert "| local_artifact_count | 0 |" in summary


def _subset_by_id(record: dict, subset_id: str) -> dict:
    return next(subset for subset in record["subsets"] if subset["subset_id"] == subset_id)


def test_appendix_a_matrix_subset_scope_validates_table2_and_full_table_boundaries():
    record = appendix_a_matrix_subset_scope_record()
    report = validate_appendix_a_matrix_subset_scope(record)
    full = _subset_by_id(record, "appendix_a_full")
    main_text = _subset_by_id(record, "main_text_mnp_le_5")
    table2 = _subset_by_id(record, "table_2_selected")

    assert report.ok is True
    assert record["schema"] == SUBSET_SCOPE_SCHEMA
    assert report.subset_count == 3
    assert report.main_text_target_count == 20
    assert report.full_table_target_count == EXPECTED_TARGET_COUNT == 54
    assert report.full_table_fell_behind_count == 2
    assert report.issues == []
    assert full["outcome_counts"] == {"matched": 38, "surpassed": 14, "fell_behind": 2}
    assert full["all_matched_or_surpassed"] is False
    assert full["fell_behind_target_ids"] == ["mm_4x4x9", "mm_6x6x6"]
    assert main_text["outcome_counts"] == {"matched": 17, "surpassed": 3, "fell_behind": 0}
    assert main_text["all_matched_or_surpassed"] is True
    assert set(full["fell_behind_target_ids"]).issubset(main_text["out_of_scope_target_ids"])
    assert table2["row_count"] == 16
    assert table2["outcome_counts"] == {"matched": 2, "surpassed": 14, "fell_behind": 0}
    assert table2["target_ids"][0] == "mm_2x4x5"
    assert table2["target_ids"][-1] == "mm_5x5x5"


def test_appendix_a_matrix_subset_scope_rejects_full_table_overclaim():
    record = appendix_a_matrix_subset_scope_record()
    full = _subset_by_id(record, "appendix_a_full")
    full["all_matched_or_surpassed"] = True
    full["fell_behind_target_ids"] = []
    full["outcome_counts"]["fell_behind"] = 0

    report = validate_appendix_a_matrix_subset_scope(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_outcome_counts" in codes
    assert "invalid_all_matched_or_surpassed" in codes
    assert "invalid_fell_behind_target_ids" in codes
    assert "full_table_overclaims_all_matched" in codes


def test_appendix_a_matrix_subset_scope_rejects_main_text_fell_behind_drift():
    record = appendix_a_matrix_subset_scope_record()
    main_text = _subset_by_id(record, "main_text_mnp_le_5")
    main_text["target_ids"].append("mm_4x4x9")
    main_text["row_count"] += 1
    main_text["outcome_counts"]["fell_behind"] = 1
    main_text["all_matched_or_surpassed"] = False
    main_text["fell_behind_target_ids"] = ["mm_4x4x9"]

    report = validate_appendix_a_matrix_subset_scope(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "target_ids_mismatch" in codes
    assert "invalid_row_count" in codes
    assert "invalid_outcome_counts" in codes
    assert "invalid_all_matched_or_surpassed" in codes
    assert "invalid_fell_behind_target_ids" in codes
    assert "main_text_subset_has_fell_behind" in codes


def test_appendix_a_matrix_subset_scope_rejects_table2_membership_and_source_drift():
    record = appendix_a_matrix_subset_scope_record()
    table2 = _subset_by_id(record, "table_2_selected")
    table2["target_ids"][0] = "mm_2x2x2"
    table2["source_pdf_page"] = 10
    table2["source_phrase"] = "selected matrix examples"

    report = validate_appendix_a_matrix_subset_scope(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "target_ids_mismatch" in codes
    assert "invalid_source_pdf_page" in codes
    assert "missing_table2_source_phrase" in codes


def test_appendix_a_matrix_subset_scope_summary_renders_counts():
    summary = render_appendix_a_matrix_subset_scope_summary()

    assert "AlphaEvolve matrix subset-scope evidence" in summary
    assert "| subset_count | 3 |" in summary
    assert "| main_text_target_count | 20 |" in summary
    assert "| full_table_target_count | 54 |" in summary
    assert "| full_table_fell_behind_count | 2 |" in summary


def test_appendix_a_matrix_row_notes_validate_concurrent_work_caveat():
    record = appendix_a_matrix_row_note_records()
    report = validate_appendix_a_matrix_row_notes(record)
    note = record["row_notes"][0]

    assert report.ok is True
    assert record["schema"] == ROW_NOTE_SCHEMA
    assert report.note_count == 1
    assert report.concurrent_work_note_count == 1
    assert report.affected_target_count == 1
    assert report.issues == []
    assert note["target_id"] == "mm_4x5x6"
    assert note["dimensions"] == [4, 5, 6]
    assert note["alphaevolve_rank"] == 90
    assert note["concurrent_rank"] == 90
    assert note["cited_reference_id"] == "49"
    assert note["relationship_to_alphaevolve"] == "independently_matched_alphaevolve_rank"
    assert note["exclusive_priority_claim_safe"] is False


def test_appendix_a_matrix_row_notes_reject_target_rank_and_reference_drift():
    record = appendix_a_matrix_row_note_records()
    note = record["row_notes"][0]
    note["target_id"] = "mm_4x4x4"
    note["dimensions"] = [4, 4, 4]
    note["alphaevolve_rank"] = 91
    note["concurrent_rank"] = 89
    note["cited_reference_id"] = "48"
    note["relationship_to_alphaevolve"] = "superseded_alphaevolve"

    report = validate_appendix_a_matrix_row_notes(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_note_target_id" in codes
    assert "invalid_note_dimensions" in codes
    assert "alphaevolve_rank_mismatch" in codes
    assert "invalid_concurrent_rank" in codes
    assert "invalid_cited_reference_id" in codes
    assert "invalid_relationship" in codes


def test_appendix_a_matrix_row_notes_reject_source_and_text_drift():
    record = appendix_a_matrix_row_note_records()
    note = record["row_notes"][0]
    record["source_pdf_page"] = 33
    note["source_table"] = "Table 2"
    note["source_pdf_page"] = 33
    note["note_text"] = "Another group improved a row."

    report = validate_appendix_a_matrix_row_notes(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_source_pdf_page" in codes
    assert "invalid_source_table" in codes
    assert "invalid_note_source_pdf_page" in codes
    assert "missing_concurrent_note_text" in codes


def test_appendix_a_matrix_row_notes_reject_exclusive_priority_overclaim():
    record = appendix_a_matrix_row_note_records()
    note = record["row_notes"][0]
    note["exclusive_priority_claim_safe"] = True
    note["docs_caveat"] = "AlphaEvolve owns the exclusive SOTA priority."

    report = validate_appendix_a_matrix_row_notes(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_exclusive_priority_flag" in codes
    assert "missing_exclusive_priority_caveat" in codes


def test_appendix_a_matrix_row_note_summary_renders_counts():
    summary = render_appendix_a_matrix_row_note_summary()

    assert "AlphaEvolve Appendix A matrix row-note evidence" in summary
    assert "| note_count | 1 |" in summary
    assert "| concurrent_work_note_count | 1 |" in summary
    assert "| affected_target_count | 1 |" in summary
