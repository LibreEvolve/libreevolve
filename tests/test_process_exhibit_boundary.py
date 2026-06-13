from __future__ import annotations

from libreevolve.problems.benchmarks.process_exhibit_boundary import (
    PROCESS_EXHIBIT_BOUNDARY_SCHEMA,
    process_exhibit_boundary_record,
    render_process_exhibit_boundary_summary,
    validate_process_exhibit_boundary,
)


def test_process_exhibit_boundary_accepts_absence_record():
    record = process_exhibit_boundary_record()

    report = validate_process_exhibit_boundary(record)

    assert report.ok is True
    assert record["schema"] == PROCESS_EXHIBIT_BOUNDARY_SCHEMA
    assert report.boundary_status == (
        "process_mapping_with_source_text_boundary_without_full_parity"
    )
    assert record["source_section_ids"] == ["2", "2.1"]
    assert report.required_evidence_field_count == 22
    assert report.missing_evidence_count == 8
    assert "does not claim exact source-diagram layout reproduction" in record["claim_boundary"]
    assert "source figure image/crop hashes" in record["claim_boundary"]
    assert "visual node coordinates" in record["claim_boundary"]
    assert "Figure 2 line-level pseudocode alignment" in record["claim_boundary"]
    assert "durable LLM and archive admission stream joins" in record["claim_boundary"]
    assert "hashed source-PDF page text extracts" in record["claim_boundary"]
    assert "validated current synchronous topology boundary" in record["claim_boundary"]
    assert "validated current inline evaluator-pool parallelism boundary" in (
        record["claim_boundary"]
    )
    assert record["missing_evidence"][
        "alphaevolve_async_pipeline_topology_implementation"
    ] == "not_implemented_locally"
    assert record["missing_evidence"][
        "exact_source_diagram_layout_reproduction"
    ] == "not_recorded_locally"
    assert record["missing_evidence"][
        "source_figure_visual_coordinate_map"
    ] == "not_recorded_locally"
    assert record["missing_evidence"][
        "visual_diff_against_source_figure"
    ] == "not_recorded_locally"
    assert record["missing_evidence"][
        "independent_evaluator_pool_parallelism_implementation"
    ] == "not_implemented_locally"


def test_process_exhibit_boundary_rejects_premature_parity_claim():
    record = process_exhibit_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "rendered_diagram_parity_recorded"
    record["source_section_ids"] = ["2.1"]
    record["missing_evidence"]["exact_source_diagram_layout_reproduction"] = "recorded"
    record["missing_evidence"]["visual_diff_against_source_figure"] = "recorded"
    record["missing_evidence"][
        "alphaevolve_async_pipeline_topology_implementation"
    ] = "recorded"
    record["missing_evidence"][
        "independent_evaluator_pool_parallelism_implementation"
    ] = "recorded"
    record["required_evidence_fields"] = ["figure_id"]

    report = validate_process_exhibit_boundary(record)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_exact_source_diagram_layout_reproduction" in codes
    assert "invalid_missing_evidence_visual_diff_against_source_figure" in codes
    assert (
        "invalid_missing_evidence_alphaevolve_async_pipeline_topology_implementation"
        in codes
    )
    assert (
        "invalid_missing_evidence_independent_evaluator_pool_parallelism_implementation"
        in codes
    )
    assert "missing_required_evidence_field" in codes


def test_process_exhibit_boundary_summary_includes_counts():
    summary = render_process_exhibit_boundary_summary(process_exhibit_boundary_record())

    assert "AlphaEvolve process exhibit boundary" in summary
    assert "| required_evidence_field_count | 22 |" in summary
    assert "| missing_evidence_count | 8 |" in summary
