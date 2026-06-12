from libreevolve.problems.benchmarks.codebase_scale_benchmark_boundary import (
    CODEBASE_SCALE_BENCHMARK_BOUNDARY_SCHEMA,
    codebase_scale_benchmark_boundary_record,
    render_codebase_scale_benchmark_boundary_summary,
    validate_codebase_scale_benchmark_boundary,
)


def test_codebase_scale_benchmark_boundary_accepts_absence_record():
    boundary = codebase_scale_benchmark_boundary_record()

    validation = validate_codebase_scale_benchmark_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "runtime_scale_telemetry_only"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == CODEBASE_SCALE_BENCHMARK_BOUNDARY_SCHEMA
    assert "does not claim realistic codebase fixtures" in boundary["claim_boundary"]


def test_codebase_scale_benchmark_boundary_rejects_premature_table1_claim():
    boundary = codebase_scale_benchmark_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "table1_code_scale_ready"
    boundary["missing_evidence"]["large_multi_component_benchmark_fixture"] = "recorded"
    boundary["required_evidence_fields"] = ["retained_program_file_line_scale"]

    validation = validate_codebase_scale_benchmark_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_large_multi_component_benchmark_fixture" in codes
    assert "missing_required_evidence_field" in codes


def test_render_codebase_scale_benchmark_boundary_summary_reports_shape():
    summary = render_codebase_scale_benchmark_boundary_summary(
        codebase_scale_benchmark_boundary_record()
    )

    assert "AlphaEvolve codebase-scale benchmark boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | runtime_scale_telemetry_only |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
