from libreevolve.problems.benchmarks.hardware_rtl_eda_evidence_boundary import (
    HARDWARE_RTL_EDA_EVIDENCE_BOUNDARY_SCHEMA,
    hardware_rtl_eda_evidence_boundary_record,
    render_hardware_rtl_eda_evidence_boundary_summary,
    validate_hardware_rtl_eda_evidence_boundary,
)


def test_hardware_rtl_eda_evidence_boundary_accepts_metadata_only_boundary():
    boundary = hardware_rtl_eda_evidence_boundary_record()

    validation = validate_hardware_rtl_eda_evidence_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "metadata_contract_without_real_rtl_eda_artifacts"
    )
    assert validation.required_evidence_field_count == 21
    assert validation.missing_evidence_count == 17
    assert boundary["schema"] == HARDWARE_RTL_EDA_EVIDENCE_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.3.3"]
    assert boundary["claim_ready"] is False
    assert "optimization objectives were to reduce power and area" in boundary["source_claim"]
    assert "was required to pass robust verification" in boundary["source_claim"]
    assert "passed robust verification" not in boundary["source_claim"]
    assert "does not claim exact RTL module" in boundary["claim_boundary"]


def test_hardware_rtl_eda_evidence_boundary_rejects_artifact_overclaim():
    boundary = hardware_rtl_eda_evidence_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "hardware_rtl_eda_artifacts_ready"
    boundary["missing_evidence"]["source_rtl_or_verilog_artifact"] = "recorded"
    boundary["required_evidence_fields"] = [
        "systems_result_hardware_domain_gate",
    ]

    validation = validate_hardware_rtl_eda_evidence_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert (
        "invalid_missing_evidence_source_rtl_or_verilog_artifact"
        in codes
    )
    assert "missing_required_evidence_field" in codes


def test_render_hardware_rtl_eda_evidence_boundary_summary_reports_shape():
    summary = render_hardware_rtl_eda_evidence_boundary_summary(
        hardware_rtl_eda_evidence_boundary_record()
    )

    assert "Hardware RTL/EDA evidence boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | metadata_contract_without_real_rtl_eda_artifacts |"
        in summary
    )
    assert "| required_evidence_field_count | 21 |" in summary
    assert "| missing_evidence_count | 17 |" in summary
