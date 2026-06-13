from libreevolve.problems.benchmarks.initial_program_idea_provenance_boundary import (
    INITIAL_PROGRAM_IDEA_PROVENANCE_BOUNDARY_SCHEMA,
    initial_program_idea_provenance_boundary_record,
    render_initial_program_idea_provenance_boundary_summary,
    validate_initial_program_idea_provenance_boundary,
)


def test_initial_program_idea_provenance_boundary_accepts_absence_record():
    boundary = initial_program_idea_provenance_boundary_record()

    validation = validate_initial_program_idea_provenance_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "metadata_contract_only"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 8
    assert boundary["schema"] == INITIAL_PROGRAM_IDEA_PROVENANCE_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.1", "3.1"]
    assert boundary["claim_ready"] is False
    assert "does not claim equal-budget seed-variant result tables" in boundary["claim_boundary"]


def test_initial_program_idea_provenance_boundary_rejects_premature_parity_claim():
    boundary = initial_program_idea_provenance_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "human_seeded_benchmark_ready"
    boundary["source_section_ids"] = ["2.1"]
    boundary["missing_evidence"]["alphaevolve_human_seeded_benchmark_parity"] = "recorded"
    boundary["required_evidence_fields"] = ["seed_source_identity_recorded"]

    validation = validate_initial_program_idea_provenance_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_alphaevolve_human_seeded_benchmark_parity" in codes
    assert "missing_required_evidence_field" in codes


def test_render_initial_program_idea_provenance_boundary_summary_reports_shape():
    summary = render_initial_program_idea_provenance_boundary_summary(
        initial_program_idea_provenance_boundary_record()
    )

    assert "AlphaEvolve initial-program idea provenance boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | metadata_contract_only |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 8 |" in summary
