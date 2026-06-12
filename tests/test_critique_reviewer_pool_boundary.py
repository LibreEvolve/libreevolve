from libreevolve.problems.benchmarks.critique_reviewer_pool_boundary import (
    CRITIQUE_REVIEWER_POOL_BOUNDARY_SCHEMA,
    critique_reviewer_pool_boundary_record,
    render_critique_reviewer_pool_boundary_summary,
    validate_critique_reviewer_pool_boundary,
)


def test_critique_reviewer_pool_boundary_accepts_synchronous_boundary():
    boundary = critique_reviewer_pool_boundary_record()

    validation = validate_critique_reviewer_pool_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "synchronous_first_last_valid_without_calibrated_reviewers"
    )
    assert validation.required_evidence_field_count == 20
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == CRITIQUE_REVIEWER_POOL_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "does not claim async reviewer overlap" in boundary["claim_boundary"]


def test_critique_reviewer_pool_boundary_rejects_calibrated_overclaim():
    boundary = critique_reviewer_pool_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "calibrated_async_reviewer_pool_ready"
    boundary["missing_evidence"]["calibrated_reviewer_score_report"] = "recorded"
    boundary["required_evidence_fields"] = ["configured_reviewer_specs"]

    validation = validate_critique_reviewer_pool_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_calibrated_reviewer_score_report" in codes
    assert "missing_required_evidence_field" in codes


def test_render_critique_reviewer_pool_boundary_summary_reports_shape():
    summary = render_critique_reviewer_pool_boundary_summary(
        critique_reviewer_pool_boundary_record()
    )

    assert "Critique reviewer pool boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | synchronous_first_last_valid_without_calibrated_reviewers |"
        in summary
    )
    assert "| required_evidence_field_count | 20 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
