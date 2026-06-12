from libreevolve.problems.benchmarks.initial_program_validity_boundary import (
    INITIAL_PROGRAM_VALIDITY_BOUNDARY_SCHEMA,
    initial_program_validity_boundary_record,
    render_initial_program_validity_boundary_summary,
    validate_initial_program_validity_boundary,
)


def test_initial_program_validity_boundary_accepts_strict_policy_boundary():
    boundary = initial_program_validity_boundary_record()

    validation = validate_initial_program_validity_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "strict_policy_available"
    assert validation.required_evidence_field_count == 11
    assert validation.missing_evidence_count == 4
    assert boundary["schema"] == INITIAL_PROGRAM_VALIDITY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["strict_policy"] == "alphaevolve_strict"
    assert boundary["default_policy"] == "permissive_baseline"
    assert "does not claim AlphaEvolve complete initial-program parity" in (
        boundary["claim_boundary"]
    )


def test_initial_program_validity_boundary_rejects_default_parity_overclaim():
    boundary = initial_program_validity_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "complete_initial_program_ready"
    boundary["missing_evidence"][
        "alphaevolve_complete_initial_program_parity_default_run"
    ] = "recorded"
    boundary["required_evidence_fields"] = ["initial_program_validity_policy_recorded"]

    validation = validate_initial_program_validity_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert (
        "invalid_missing_evidence_alphaevolve_complete_initial_program_parity_default_run"
        in codes
    )
    assert "missing_required_evidence_field" in codes


def test_render_initial_program_validity_boundary_summary_reports_shape():
    summary = render_initial_program_validity_boundary_summary(
        initial_program_validity_boundary_record()
    )

    assert "AlphaEvolve initial-program validity boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | strict_policy_available |" in summary
    assert "| required_evidence_field_count | 11 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
