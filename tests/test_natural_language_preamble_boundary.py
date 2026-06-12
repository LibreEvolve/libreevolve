from libreevolve.problems.benchmarks.natural_language_preamble_boundary import (
    NATURAL_LANGUAGE_PREAMBLE_BOUNDARY_SCHEMA,
    natural_language_preamble_boundary_record,
    render_natural_language_preamble_boundary_summary,
    validate_natural_language_preamble_boundary,
)


def test_natural_language_preamble_boundary_accepts_bounded_capture_boundary():
    boundary = natural_language_preamble_boundary_record()

    validation = validate_natural_language_preamble_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "bounded_leading_preamble_capture_only"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == NATURAL_LANGUAGE_PREAMBLE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        "does not claim configurable preamble policy controls"
        in boundary["claim_boundary"]
    )


def test_natural_language_preamble_boundary_rejects_complete_rationale_overclaim():
    boundary = natural_language_preamble_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "complete_alphaevolve_rationale_handling"
    boundary["missing_evidence"]["semantic_rationale_quality_scoring"] = "recorded"
    boundary["required_evidence_fields"] = [
        "bounded_leading_explanatory_preamble_capture"
    ]

    validation = validate_natural_language_preamble_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_semantic_rationale_quality_scoring" in codes
    assert "missing_required_evidence_field" in codes


def test_render_natural_language_preamble_boundary_summary_reports_shape():
    summary = render_natural_language_preamble_boundary_summary(
        natural_language_preamble_boundary_record()
    )

    assert "Natural-language preamble boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | bounded_leading_preamble_capture_only |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
