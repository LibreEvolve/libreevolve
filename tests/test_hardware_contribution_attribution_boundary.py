from libreevolve.problems.benchmarks.hardware_contribution_attribution_boundary import (
    HARDWARE_CONTRIBUTION_ATTRIBUTION_BOUNDARY_SCHEMA,
    hardware_contribution_attribution_boundary_record,
    render_hardware_contribution_attribution_boundary_summary,
    validate_hardware_contribution_attribution_boundary,
)


def test_hardware_contribution_attribution_boundary_accepts_metadata_boundary():
    boundary = hardware_contribution_attribution_boundary_record()

    validation = validate_hardware_contribution_attribution_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "metadata_contract_without_gemini_tpu_attribution_artifacts"
    )
    assert validation.required_evidence_field_count == 19
    assert validation.missing_evidence_count == 15
    assert boundary["schema"] == HARDWARE_CONTRIBUTION_ATTRIBUTION_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.3.3"]
    assert boundary["claim_ready"] is False
    assert "does not claim Gemini model-family identity" in boundary["claim_boundary"]


def test_hardware_contribution_attribution_boundary_rejects_overclaim():
    boundary = hardware_contribution_attribution_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "gemini_tpu_attribution_artifacts_ready"
    boundary["missing_evidence"]["gemini_model_family_identity"] = "recorded"
    boundary["required_evidence_fields"] = [
        "systems_result_hardware_domain_gate",
    ]

    validation = validate_hardware_contribution_attribution_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_gemini_model_family_identity" in codes
    assert "missing_required_evidence_field" in codes


def test_render_hardware_contribution_attribution_boundary_summary_reports_shape():
    summary = render_hardware_contribution_attribution_boundary_summary(
        hardware_contribution_attribution_boundary_record()
    )

    assert "Hardware contribution attribution boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | metadata_contract_without_gemini_tpu_attribution_artifacts |"
        in summary
    )
    assert "| required_evidence_field_count | 19 |" in summary
    assert "| missing_evidence_count | 15 |" in summary
