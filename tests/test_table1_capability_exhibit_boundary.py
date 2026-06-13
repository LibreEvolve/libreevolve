from libreevolve.problems.benchmarks.table1_capability_exhibit_boundary import (
    TABLE1_CAPABILITY_EXHIBIT_BOUNDARY_SCHEMA,
    render_table1_capability_exhibit_boundary_summary,
    table1_capability_exhibit_boundary_record,
    validate_table1_capability_exhibit_boundary,
)


def test_table1_capability_exhibit_boundary_accepts_absence_record():
    boundary = table1_capability_exhibit_boundary_record()

    validation = validate_table1_capability_exhibit_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "table_exhibit_provenance_only"
    assert validation.row_count == 8
    assert validation.required_evidence_field_count == 15
    assert validation.missing_evidence_count == 8
    assert boundary["schema"] == TABLE1_CAPABILITY_EXHIBIT_BOUNDARY_SCHEMA
    assert boundary["table_id"] == "alphaevolve_table_1_capability_comparison"
    assert boundary["row_ids"][0] == "table1.function_vs_file_scope"
    assert boundary["row_ids"][-1] == "table1.metric_optimization_scope"
    assert "does not claim benchmark-backed code-scale parity" in boundary["claim_boundary"]


def test_table1_capability_exhibit_boundary_rejects_parity_overclaim():
    boundary = table1_capability_exhibit_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "table1_parity_ready"
    boundary["row_ids"] = ["table1.function_vs_file_scope"]
    boundary["missing_evidence"]["full_table1_parity"] = "recorded"
    boundary["required_evidence_fields"] = ["stable_table_id"]

    validation = validate_table1_capability_exhibit_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_row_ids" in codes
    assert "invalid_missing_evidence_full_table1_parity" in codes
    assert "missing_required_evidence_field" in codes


def test_render_table1_capability_exhibit_boundary_summary_reports_shape():
    summary = render_table1_capability_exhibit_boundary_summary(
        table1_capability_exhibit_boundary_record()
    )

    assert "AlphaEvolve Table 1 capability-exhibit boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | table_exhibit_provenance_only |" in summary
    assert "| row_count | 8 |" in summary
    assert "| required_evidence_field_count | 15 |" in summary
    assert "| missing_evidence_count | 8 |" in summary
