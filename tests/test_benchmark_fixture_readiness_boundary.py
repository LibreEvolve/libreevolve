from libreevolve.problems.benchmarks.benchmark_fixture_readiness_boundary import (
    BENCHMARK_FIXTURE_READINESS_BOUNDARY_SCHEMA,
    benchmark_fixture_readiness_boundary_record,
    render_benchmark_fixture_readiness_boundary_summary,
    validate_benchmark_fixture_readiness_boundary,
)


def test_benchmark_fixture_readiness_boundary_accepts_absence_record():
    boundary = benchmark_fixture_readiness_boundary_record()

    validation = validate_benchmark_fixture_readiness_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "smoke_scope_with_deterministic_matrix_calibration_only"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 4
    assert boundary["schema"] == BENCHMARK_FIXTURE_READINESS_BOUNDARY_SCHEMA
    assert "does not claim non-smoke AlphaEvolve-comparable fixture" in (
        boundary["claim_boundary"]
    )


def test_benchmark_fixture_readiness_boundary_rejects_premature_paper_claim():
    boundary = benchmark_fixture_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "paper_claim_ready"
    boundary["missing_evidence"]["anti_gaming_negative_fixtures_passed"] = "recorded"
    boundary["required_evidence_fields"] = ["example_scope_record_present"]

    validation = validate_benchmark_fixture_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_anti_gaming_negative_fixtures_passed" in codes
    assert "missing_required_evidence_field" in codes


def test_render_benchmark_fixture_readiness_boundary_summary_reports_shape():
    summary = render_benchmark_fixture_readiness_boundary_summary(
        benchmark_fixture_readiness_boundary_record()
    )

    assert "AlphaEvolve benchmark-fixture readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | smoke_scope_with_deterministic_matrix_calibration_only |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
