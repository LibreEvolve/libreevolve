from libreevolve.problems.benchmarks.sample_efficiency_boundary import (
    SAMPLE_EFFICIENCY_BOUNDARY_SCHEMA,
    sample_efficiency_boundary_record,
    render_sample_efficiency_boundary_summary,
    validate_sample_efficiency_boundary,
)


def test_sample_efficiency_boundary_accepts_absence_record():
    boundary = sample_efficiency_boundary_record()

    validation = validate_sample_efficiency_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "single_run_counts_only"
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == SAMPLE_EFFICIENCY_BOUNDARY_SCHEMA
    assert "does not claim AlphaEvolve-style target-hit" in boundary["claim_boundary"]


def test_sample_efficiency_boundary_rejects_premature_efficiency_claim():
    boundary = sample_efficiency_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "benchmark_sample_efficiency_ready"
    boundary["missing_evidence"]["target_hit_sample_index"] = "recorded"
    boundary["required_evidence_fields"] = ["run_id"]

    validation = validate_sample_efficiency_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_target_hit_sample_index" in codes
    assert "missing_required_evidence_field" in codes


def test_render_sample_efficiency_boundary_summary_reports_shape():
    summary = render_sample_efficiency_boundary_summary(
        sample_efficiency_boundary_record()
    )

    assert "AlphaEvolve sample-efficiency boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | single_run_counts_only |" in summary
    assert "| required_evidence_field_count | 16 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
