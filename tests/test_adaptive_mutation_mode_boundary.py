from libreevolve.problems.benchmarks.adaptive_mutation_mode_boundary import (
    ADAPTIVE_MUTATION_MODE_BOUNDARY_SCHEMA,
    adaptive_mutation_mode_boundary_record,
    render_adaptive_mutation_mode_boundary_summary,
    validate_adaptive_mutation_mode_boundary,
)


def test_adaptive_mutation_mode_boundary_accepts_partial_record():
    boundary = adaptive_mutation_mode_boundary_record()

    validation = validate_adaptive_mutation_mode_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "adaptive_candidate_shape_selection_partial"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 4
    assert boundary["schema"] == ADAPTIVE_MUTATION_MODE_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.3"]
    assert boundary["supported_modes"] == ["diff", "full"]
    assert boundary["implemented_evidence"]["per_candidate_mode_selection"] == (
        "recorded_in_candidate_history"
    )
    assert "does not claim benchmark-calibrated" in boundary["claim_boundary"]


def test_adaptive_mutation_mode_boundary_rejects_premature_adaptive_claim():
    boundary = adaptive_mutation_mode_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "adaptive_mutation_mode_selection_ready"
    boundary["source_section_ids"] = ["2.4"]
    boundary["missing_evidence"]["benchmark_calibrated_thresholds"] = "recorded"
    boundary["implemented_evidence"]["per_candidate_mode_selection"] = "missing"
    boundary["required_evidence_fields"] = ["run_wide_configured_mode"]

    validation = validate_adaptive_mutation_mode_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_benchmark_calibrated_thresholds" in codes
    assert "invalid_implemented_evidence" in codes
    assert "missing_required_evidence_field" in codes


def test_render_adaptive_mutation_mode_boundary_summary_reports_shape():
    summary = render_adaptive_mutation_mode_boundary_summary(
        adaptive_mutation_mode_boundary_record()
    )

    assert "AlphaEvolve adaptive mutation-mode boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | adaptive_candidate_shape_selection_partial |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
