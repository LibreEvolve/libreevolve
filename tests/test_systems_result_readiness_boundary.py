from libreevolve.problems.benchmarks.systems_result_readiness_boundary import (
    SYSTEMS_RESULT_READINESS_BOUNDARY_SCHEMA,
    render_systems_result_readiness_boundary_summary,
    systems_result_readiness_boundary_record,
    validate_systems_result_readiness_boundary,
)


def test_systems_result_readiness_boundary_accepts_absence_record():
    boundary = systems_result_readiness_boundary_record()

    validation = validate_systems_result_readiness_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "report_contract_without_real_systems_fixtures"
    assert validation.required_evidence_field_count == 25
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == SYSTEMS_RESULT_READINESS_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.3"]
    assert "does not claim real scheduling" in boundary["claim_boundary"]


def test_systems_result_readiness_boundary_rejects_premature_ready_claim():
    boundary = systems_result_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "real_systems_fixtures_ready"
    boundary["source_section_ids"] = ["3.2"]
    boundary["missing_evidence"]["real_kernel_fixture_runs"] = "recorded"
    boundary["required_evidence_fields"] = ["systems_result_report_schema"]

    validation = validate_systems_result_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_real_kernel_fixture_runs" in codes
    assert "missing_required_evidence_field" in codes


def test_render_systems_result_readiness_boundary_summary_reports_shape():
    summary = render_systems_result_readiness_boundary_summary(
        systems_result_readiness_boundary_record()
    )

    assert "AlphaEvolve systems-result readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | report_contract_without_real_systems_fixtures |" in summary
    assert "| required_evidence_field_count | 25 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
