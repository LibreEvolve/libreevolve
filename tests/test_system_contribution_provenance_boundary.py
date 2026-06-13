from libreevolve.problems.benchmarks.system_contribution_provenance_boundary import (
    SYSTEM_CONTRIBUTION_PROVENANCE_BOUNDARY_SCHEMA,
    render_system_contribution_provenance_boundary_summary,
    system_contribution_provenance_boundary_record,
    validate_system_contribution_provenance_boundary,
)


def test_system_contribution_provenance_boundary_accepts_claim_ready_record():
    boundary = system_contribution_provenance_boundary_record()

    validation = validate_system_contribution_provenance_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "system_contribution_claim_ready"
    assert validation.required_evidence_field_count == 13
    assert validation.excluded_claim_count == 6
    assert boundary["schema"] == SYSTEM_CONTRIBUTION_PROVENANCE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is True
    assert boundary["source_section_ids"] == ["Contributions"]
    assert boundary["source_pages"] == [22, 23]
    assert "does not claim generic git history" in boundary["claim_boundary"]


def test_system_contribution_provenance_boundary_rejects_scope_drift():
    boundary = system_contribution_provenance_boundary_record()
    boundary["claim_ready"] = False
    boundary["boundary_status"] = "git_history_ready"
    boundary["source_section_ids"] = ["Author information"]
    boundary["excluded_claims"]["generic_git_history_or_commit_authorship"] = "claimed"
    boundary["required_evidence_fields"] = ["metadata_present"]
    boundary["required_phases"] = ["initial_design"]

    validation = validate_system_contribution_provenance_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_underclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_excluded_claim_generic_git_history_or_commit_authorship" in codes
    assert "missing_required_evidence_field" in codes
    assert "missing_required_phase" in codes


def test_render_system_contribution_provenance_boundary_summary_reports_shape():
    summary = render_system_contribution_provenance_boundary_summary(
        system_contribution_provenance_boundary_record()
    )

    assert "AlphaEvolve system-contribution provenance boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | system_contribution_claim_ready |" in summary
    assert "| required_evidence_field_count | 13 |" in summary
    assert "| excluded_claim_count | 6 |" in summary
