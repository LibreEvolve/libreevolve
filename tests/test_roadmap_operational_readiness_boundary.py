from libreevolve.problems.benchmarks.roadmap_operational_readiness_boundary import (
    ROADMAP_OPERATIONAL_READINESS_BOUNDARY_SCHEMA,
    render_roadmap_operational_readiness_boundary_summary,
    roadmap_operational_readiness_boundary_record,
    validate_roadmap_operational_readiness_boundary,
)


def test_roadmap_operational_readiness_accepts_bounded_matrix():
    boundary = roadmap_operational_readiness_boundary_record()

    validation = validate_roadmap_operational_readiness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_operational_readiness_matrix_without_global_maturity_gate"
    )
    assert boundary["schema"] == ROADMAP_OPERATIONAL_READINESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_operational_boundary_input"]
        == "papers/roadmap_operational_maturity_boundary.json"
    )
    assert boundary["source_criterion_count"] == 6
    assert boundary["source_active_todo_ref_count"] == 10
    assert boundary["readiness_criterion_count"] == 6
    assert boundary["sidecar_ref_count"] == 12
    assert boundary["active_todo_ref_count"] == 12
    assert [record["criterion_id"] for record in boundary["readiness_criteria"]] == [
        "global_acceptance_threshold",
        "unified_generated_artifact_lifecycle_inventory",
        "semantic_docs_verification",
        "signed_release_provenance",
        "cross_platform_ci_policy",
        "owner_review_signoff",
    ]
    assert boundary["operational_claim_guard_count"] == 6
    assert [record["criterion_id"] for record in boundary["operational_claim_guard"]] == [
        "global_acceptance_threshold",
        "unified_generated_artifact_lifecycle_inventory",
        "semantic_docs_verification",
        "signed_release_provenance",
        "cross_platform_ci_policy",
        "owner_review_signoff",
    ]
    assert all(
        "missing_before_maturity_claim" in record
        for record in boundary["operational_claim_guard"]
    )
    assert all(
        sidecar["exists"]
        for record in boundary["readiness_criteria"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        todo_ref["exists"] and todo_ref["required_phrase_present"]
        for record in boundary["readiness_criteria"]
        for todo_ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "global_acceptance_threshold": "not_recorded_locally",
        "unified_generated_artifact_lifecycle_inventory": "not_recorded_locally",
        "semantic_docs_verification": "not_recorded_locally",
        "signed_release_provenance": "not_recorded_locally",
        "cross_platform_ci_policy": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim a global acceptance threshold" in boundary["claim_boundary"]
    assert "claim guard for each maturity surface" in boundary["claim_boundary"]


def test_roadmap_operational_readiness_rejects_overclaim_and_drift():
    boundary = roadmap_operational_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "operational_maturity_gate_ready"
    boundary["readiness_criterion_count"] = 0
    boundary["readiness_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["operational_claim_guard_count"] = 0
    boundary["missing_evidence"]["global_acceptance_threshold"] = "recorded"
    boundary["required_evidence_fields"] = ["global_acceptance_threshold"]

    validation = validate_roadmap_operational_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_readiness_criterion_count" in codes
    assert "invalid_readiness_criteria" in codes
    assert "invalid_operational_claim_guard_count" in codes
    assert "invalid_missing_evidence_global_acceptance_threshold" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_operational_readiness_summary_reports_shape():
    summary = render_roadmap_operational_readiness_boundary_summary(
        roadmap_operational_readiness_boundary_record()
    )

    assert "ROADMAP operational readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_operational_readiness_matrix_without_global_maturity_gate |"
        in summary
    )
    assert "| readiness_criterion_count | 6 |" in summary
    assert "| sidecar_ref_count | 12 |" in summary
    assert "| active_todo_ref_count | 12 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
