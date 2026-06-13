from libreevolve.problems.benchmarks.automated_evaluator_scope_boundary import (
    AUTOMATED_EVALUATOR_SCOPE_BOUNDARY_SCHEMA,
    automated_evaluator_scope_boundary_record,
    render_automated_evaluator_scope_boundary_summary,
    validate_automated_evaluator_scope_boundary,
)


def test_automated_evaluator_scope_boundary_accepts_machine_gradeable_scope():
    boundary = automated_evaluator_scope_boundary_record()

    validation = validate_automated_evaluator_scope_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "machine_gradeable_scope_without_robust_environment_fixtures"
    )
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == AUTOMATED_EVALUATOR_SCOPE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["source_section_ids"] == [
        "front_matter_overview",
        "2.1",
        "2.4",
        "Discussion",
    ]
    assert (
        "does not claim robust evaluator-environment fixtures"
        in boundary["claim_boundary"]
    )


def test_automated_evaluator_scope_boundary_rejects_environment_overclaim():
    boundary = automated_evaluator_scope_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "robust_evaluator_environment_ready"
    boundary["source_section_ids"] = ["2.1"]
    boundary["missing_evidence"]["robust_evaluator_environment_fixture"] = "recorded"
    boundary["required_evidence_fields"] = ["automated_evaluator_available"]

    validation = validate_automated_evaluator_scope_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert (
        "invalid_missing_evidence_robust_evaluator_environment_fixture"
        in codes
    )
    assert "missing_required_evidence_field" in codes


def test_render_automated_evaluator_scope_boundary_summary_reports_shape():
    summary = render_automated_evaluator_scope_boundary_summary(
        automated_evaluator_scope_boundary_record()
    )

    assert "Automated evaluator scope boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | machine_gradeable_scope_without_robust_environment_fixtures |"
        in summary
    )
    assert "| required_evidence_field_count | 16 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
