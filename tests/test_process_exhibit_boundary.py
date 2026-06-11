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
        "process_mapping_with_text_diagram_artifacts_without_full_parity"
    )
    assert report.required_evidence_field_count == 14
    assert report.missing_evidence_count == 4
    assert "does not claim exact source-diagram reproduction" in record["claim_boundary"]


def test_process_exhibit_boundary_rejects_premature_parity_claim():
    record = process_exhibit_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "rendered_diagram_parity_recorded"
    record["missing_evidence"]["exact_source_diagram_text_reproduction"] = "recorded"
    record["required_evidence_fields"] = ["figure_id"]

    report = validate_process_exhibit_boundary(record)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_exact_source_diagram_text_reproduction" in codes
    assert "missing_required_evidence_field" in codes


def test_process_exhibit_boundary_summary_includes_counts():
    summary = render_process_exhibit_boundary_summary(process_exhibit_boundary_record())

    assert "AlphaEvolve process exhibit boundary" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
