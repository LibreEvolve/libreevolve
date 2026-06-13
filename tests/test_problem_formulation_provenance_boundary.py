from libreevolve.problems.benchmarks.problem_formulation_provenance_boundary import (
    PROBLEM_FORMULATION_PROVENANCE_BOUNDARY_SCHEMA,
    problem_formulation_provenance_boundary_record,
    render_problem_formulation_provenance_boundary_summary,
    validate_problem_formulation_provenance_boundary,
)


def test_problem_formulation_provenance_boundary_accepts_absence_record():
    boundary = problem_formulation_provenance_boundary_record()

    validation = validate_problem_formulation_provenance_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "metadata_contract_only"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == PROBLEM_FORMULATION_PROVENANCE_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.2"]
    assert "does not claim populated expert-reviewed" in boundary["claim_boundary"]


def test_problem_formulation_provenance_boundary_rejects_premature_parity_claim():
    boundary = problem_formulation_provenance_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "expert_guided_formulation_ready"
    boundary["source_section_ids"] = ["2.1"]
    boundary["missing_evidence"]["alphaevolve_expert_guided_formulation_parity"] = "recorded"
    boundary["required_evidence_fields"] = ["metadata_present"]

    validation = validate_problem_formulation_provenance_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_alphaevolve_expert_guided_formulation_parity" in codes
    assert "missing_required_evidence_field" in codes


def test_render_problem_formulation_provenance_boundary_summary_reports_shape():
    summary = render_problem_formulation_provenance_boundary_summary(
        problem_formulation_provenance_boundary_record()
    )

    assert "AlphaEvolve problem-formulation provenance boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | metadata_contract_only |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
