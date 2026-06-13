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
    assert validation.boundary_status == "missing_first_class_gemini_provider"
    assert validation.required_evidence_field_count == 15
    assert validation.missing_evidence_count == 15
    assert boundary["schema"] == GEMINI_PROVIDER_PARITY_BOUNDARY_SCHEMA
    assert "does not claim a first-class Google/Gemini adapter" in boundary["claim_boundary"]
    assert "Gemini client-context configuration" in boundary["claim_boundary"]
    assert "Gemini request-parameter mapping" in boundary["claim_boundary"]
    assert "Flash and Pro lane identity" in boundary["claim_boundary"]


def test_gemini_provider_parity_boundary_rejects_premature_provider_claim():
    boundary = gemini_provider_parity_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "first_class_gemini_provider_ready"
    boundary["missing_evidence"]["built_in_google_gemini_adapter"] = "recorded"
    boundary["missing_evidence"]["gemini_flash_lane_identity"] = "recorded"
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
    assert "| boundary_status | missing_first_class_gemini_provider |" in summary
    assert "| required_evidence_field_count | 15 |" in summary
    assert "| missing_evidence_count | 15 |" in summary
