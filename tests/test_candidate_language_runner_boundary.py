from libreevolve.problems.benchmarks.candidate_language_runner_boundary import (
    CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_SCHEMA,
    candidate_language_runner_boundary_record,
    render_candidate_language_runner_boundary_summary,
    validate_candidate_language_runner_boundary,
)


def test_candidate_language_runner_boundary_accepts_partial_record():
    boundary = candidate_language_runner_boundary_record()

    validation = validate_candidate_language_runner_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "digest_pinned_oci_candidate_execution_partial"
    )
    assert validation.required_evidence_field_count == 28
    assert validation.missing_evidence_count == 10
    assert boundary["schema"] == CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_SCHEMA
    assert "does not claim AlphaEvolve-style arbitrary language" in (
        boundary["claim_boundary"]
    )


def test_candidate_language_runner_boundary_rejects_premature_runner_claim():
    boundary = candidate_language_runner_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "arbitrary_language_runner_evidence_recorded"
    boundary["missing_evidence"]["configured_non_python_language_runners"] = "recorded"
    boundary["required_evidence_fields"] = ["candidate_language"]

    validation = validate_candidate_language_runner_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_configured_non_python_language_runners" in codes
    assert "missing_required_evidence_field" in codes


def test_render_candidate_language_runner_boundary_summary_reports_shape():
    summary = render_candidate_language_runner_boundary_summary(
        candidate_language_runner_boundary_record()
    )

    assert "AlphaEvolve candidate language runner boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | digest_pinned_oci_candidate_execution_partial |"
        in summary
    )
    assert "| required_evidence_field_count | 28 |" in summary
    assert "| missing_evidence_count | 10 |" in summary
