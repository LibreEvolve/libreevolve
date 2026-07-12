from libreevolve.problems.benchmarks.gemini_provider_parity_boundary import (
    GEMINI_PROVIDER_PARITY_BOUNDARY_SCHEMA,
    gemini_provider_parity_boundary_record,
    render_gemini_provider_parity_boundary_summary,
    validate_gemini_provider_parity_boundary,
)


def test_gemini_provider_parity_boundary_accepts_absence_record():
    boundary = gemini_provider_parity_boundary_record()

    validation = validate_gemini_provider_parity_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "first_class_adapter_without_live_alphaevolve_model_parity"
    )
    assert validation.required_evidence_field_count == 18
    assert validation.missing_evidence_count == 8
    assert boundary["schema"] == GEMINI_PROVIDER_PARITY_BOUNDARY_SCHEMA
    assert "first-class Google Gen AI SDK adapter" in boundary["claim_boundary"]
    assert "live Gemini 2.0 Flash/Pro availability" in boundary["claim_boundary"]
    assert "model-registry snapshots" in boundary["claim_boundary"]
    assert "calibrated AlphaEvolve Flash/Pro scheduling" in boundary["claim_boundary"]


def test_gemini_provider_parity_boundary_rejects_premature_provider_claim():
    boundary = gemini_provider_parity_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "first_class_gemini_provider_ready"
    boundary["missing_evidence"]["built_in_google_gemini_adapter"] = "not_recorded_locally"
    boundary["missing_evidence"]["gemini_flash_lane_identity"] = "not_recorded_locally"
    boundary["required_evidence_fields"] = ["built_in_google_gemini_adapter"]

    validation = validate_gemini_provider_parity_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_built_in_google_gemini_adapter" in codes
    assert "invalid_missing_evidence_gemini_flash_lane_identity" in codes
    assert "missing_required_evidence_field" in codes


def test_render_gemini_provider_parity_boundary_summary_reports_shape():
    summary = render_gemini_provider_parity_boundary_summary(
        gemini_provider_parity_boundary_record()
    )

    assert "AlphaEvolve Gemini provider parity boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | first_class_adapter_without_live_alphaevolve_model_parity |" in summary
    assert "| required_evidence_field_count | 18 |" in summary
    assert "| missing_evidence_count | 8 |" in summary
