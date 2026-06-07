import json

from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    EXPECTED_TARGET_COUNT,
    TARGET_SUITE,
    matrix_target_by_id,
    matrix_target_records,
    render_appendix_a_matrix_registry_summary,
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
