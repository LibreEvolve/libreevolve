from libreevolve.problems.benchmarks.ucb1_boundary import (
    UCB1_BOUNDARY_SCHEMA,
    render_ucb1_boundary_summary,
    ucb1_boundary_record,
    validate_ucb1_boundary,
)


def test_ucb1_boundary_accepts_heuristic_absence_record():
    boundary = ucb1_boundary_record()

    validation = validate_ucb1_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "ucb1_foundational_source_without_canonical_regret_scheduler_claim"
    )
    assert validation.component_count == 14
    assert validation.required_evidence_field_count == 24
    assert validation.missing_evidence_count == 20
    assert boundary["schema"] == UCB1_BOUNDARY_SCHEMA
    assert boundary["source_year"] == 2002
    assert boundary["source_bytes"] == 207956
    assert boundary["local_evidence"]["default_strategy"] == "ucb1"
    assert boundary["local_evidence"]["reward_cap"] == 1.0
    assert boundary["local_evidence"]["regret_report_ready"] is False
    assert (
        boundary["reported_theorem_scope"]["canonical_index_confidence_term"]
        == "sqrt(2 ln(t) / T_i(t))"
    )
    assert boundary["variant_support"]["UCB1_TUNED"] == (
        "not_implemented_no_proof_claim"
    )
    assert "does not claim canonical UCB1 finite-time regret" in (
        boundary["claim_boundary"]
    )


def test_ucb1_boundary_rejects_premature_regret_claims():
    boundary = ucb1_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][0]["status"] = "verified_license_and_source"
    boundary["framework_components"][1]["local_status"] = "validated"
    boundary["local_evidence"]["regret_report_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["reported_theorem_scope"]["reward_support"] = "unbounded"
    boundary["variant_support"]["UCB2"] = "implemented"
    boundary["missing_evidence"]["regret_baseline_reports"] = "implemented"

    validation = validate_ucb1_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_regret_report_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "reported_theorem_scope_reward_support_mismatch" in codes
    assert "variant_support_mismatch" in codes
    assert "missing_evidence_mismatch" in codes


def test_render_ucb1_boundary_summary_reports_shape():
    summary = render_ucb1_boundary_summary(ucb1_boundary_record())

    assert "UCB1 boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | ucb1_foundational_source_without_canonical_regret_scheduler_claim |"
        in summary
    )
    assert "| component_count | 14 |" in summary
