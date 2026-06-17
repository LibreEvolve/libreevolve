from libreevolve.problems.benchmarks.alphaevolve_impact_claim_policy_boundary import (
    ALPHAEVOLVE_IMPACT_CLAIM_POLICY_BOUNDARY_SCHEMA,
    alphaevolve_impact_claim_policy_boundary_record,
    render_alphaevolve_impact_claim_policy_boundary_summary,
    validate_alphaevolve_impact_claim_policy_boundary,
)


def test_alphaevolve_impact_claim_policy_boundary_accepts_source_scoped_rows():
    boundary = alphaevolve_impact_claim_policy_boundary_record()

    validation = validate_alphaevolve_impact_claim_policy_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "normalized_source_claim_rows_without_release_note_promotion_eligibility"
    )
    assert validation.normalized_claim_count == 22
    assert validation.release_note_eligible_count == 0
    assert validation.required_evidence_field_count == 20
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == ALPHAEVOLVE_IMPACT_CLAIM_POLICY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert len(boundary["normalized_claim_rows"]) == 22
    assert boundary["normalized_claim_rows"][0]["claim_id"] == "deepconsensus_variant_error_reduction"
    assert boundary["normalized_claim_rows"][-1]["claim_id"] == "schrodinger_mlff_speedup"
    assert all(row["release_note_eligible"] is False for row in boundary["normalized_claim_rows"])


def test_alphaevolve_impact_claim_policy_boundary_rejects_promotion_overclaim():
    boundary = alphaevolve_impact_claim_policy_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "impact_claims_release_note_ready"
    boundary["policy"]["release_note_gate_status"] = "implemented"
    row = boundary["normalized_claim_rows"][0]
    row["release_note_eligible"] = True
    row["local_fixture_status"] = "implemented"
    row["independent_verification_status"] = "verified"
    row["reproduction_artifact_links"] = ["runs/example/report.json"]
    row["unsupported_local_evidence_flag"] = False
    boundary["required_evidence_fields"] = ["canonical_claim_id"]
    boundary["missing_evidence"]["release_note_promotion_gate"] = "implemented"

    validation = validate_alphaevolve_impact_claim_policy_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_release_note_gate_status" in codes
    assert "release_note_eligibility_overclaim" in codes
    assert "claim_local_fixture_overclaim" in codes
    assert "claim_independent_verification_overclaim" in codes
    assert "reproduction_artifact_link_overclaim" in codes
    assert "missing_unsupported_local_evidence_flag" in codes
    assert "missing_required_evidence_field" in codes
    assert "invalid_missing_evidence_release_note_promotion_gate" in codes


def test_render_alphaevolve_impact_claim_policy_boundary_summary_reports_shape():
    summary = render_alphaevolve_impact_claim_policy_boundary_summary(
        alphaevolve_impact_claim_policy_boundary_record()
    )

    assert "AlphaEvolve impact claim policy boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| normalized_claim_count | 22 |" in summary
    assert "| release_note_eligible_count | 0 |" in summary
    assert "| required_evidence_field_count | 20 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
