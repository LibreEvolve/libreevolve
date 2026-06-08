import json

from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    CURATION_SCHEMA,
    EXPECTED_TARGET_COUNT,
    TARGET_SUITE,
    appendix_a_matrix_curation_record,
    matrix_target_by_id,
    matrix_target_records,
    render_appendix_a_matrix_curation_summary,
    render_appendix_a_matrix_registry_summary,
    validate_appendix_a_matrix_curation,
    validate_appendix_a_matrix_registry,
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
