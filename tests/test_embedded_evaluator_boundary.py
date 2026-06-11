from libreevolve.problems.benchmarks.embedded_evaluator_boundary import (
    EMBEDDED_EVALUATOR_BOUNDARY_SCHEMA,
    embedded_evaluator_boundary_record,
    render_embedded_evaluator_boundary_summary,
    validate_embedded_evaluator_boundary,
)


def test_embedded_evaluator_boundary_accepts_absence_record():
    boundary = embedded_evaluator_boundary_record()

    validation = validate_embedded_evaluator_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "embedded_entrypoint_without_full_figure3_parity"
    assert validation.required_evidence_field_count == 13
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == EMBEDDED_EVALUATOR_BOUNDARY_SCHEMA
    assert "does not claim full AlphaEvolve Figure 3 evaluator parity" in (
        boundary["claim_boundary"]
    )


def test_embedded_evaluator_boundary_rejects_premature_figure3_claim():
    boundary = embedded_evaluator_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_figure3_parity_recorded"
    boundary["missing_evidence"]["skeleton_to_evolved_block_invocation_trace"] = "recorded"
    boundary["required_evidence_fields"] = ["candidate_primary_file"]

    validation = validate_embedded_evaluator_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_skeleton_to_evolved_block_invocation_trace" in codes
    assert "missing_required_evidence_field" in codes


def test_render_embedded_evaluator_boundary_summary_reports_shape():
    summary = render_embedded_evaluator_boundary_summary(
        embedded_evaluator_boundary_record()
    )

    assert "AlphaEvolve embedded evaluator boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | embedded_entrypoint_without_full_figure3_parity |" in summary
    assert "| required_evidence_field_count | 13 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
