from libreevolve.problems.benchmarks.roadmap_candidate_workspace_readiness_boundary import (
    ROADMAP_CANDIDATE_WORKSPACE_READINESS_BOUNDARY_SCHEMA,
    render_roadmap_candidate_workspace_readiness_boundary_summary,
    roadmap_candidate_workspace_readiness_boundary_record,
    validate_roadmap_candidate_workspace_readiness_boundary,
)


def test_roadmap_candidate_workspace_readiness_accepts_bounded_matrix():
    boundary = roadmap_candidate_workspace_readiness_boundary_record()

    validation = validate_roadmap_candidate_workspace_readiness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_candidate_workspace_readiness_matrix_without_alphaevolve_workspace_gate"
    )
    assert boundary["schema"] == ROADMAP_CANDIDATE_WORKSPACE_READINESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_candidate_workspace_boundary_input"]
        == "papers/roadmap_candidate_workspace_fidelity_boundary.json"
    )
    assert boundary["source_criterion_count"] == 10
    assert boundary["source_active_todo_ref_count"] == 20
    assert boundary["source_sidecar_ref_count"] == 15
    assert boundary["source_missing_evidence_count"] == 12
    assert boundary["readiness_criterion_count"] == 8
    assert boundary["sidecar_ref_count"] == 16
    assert boundary["active_todo_ref_count"] == 16
    assert [record["criterion_id"] for record in boundary["readiness_criteria"]] == [
        "language_build_and_candidate_api",
        "embedded_evaluator_and_codebase_scale",
        "materialization_marker_and_topology",
        "mutation_mode_operator_provenance",
        "prompt_copy_and_cross_file_consistency",
        "initial_pool_static_binary_policy",
        "resume_replay_and_manifest_policy",
        "stale_readiness_and_owner_signoff",
    ]
    assert boundary["candidate_workspace_claim_guard_count"] == 8
    assert [
        record["criterion_id"] for record in boundary["candidate_workspace_claim_guard"]
    ] == [
        "language_build_and_candidate_api",
        "embedded_evaluator_and_codebase_scale",
        "materialization_marker_and_topology",
        "mutation_mode_operator_provenance",
        "prompt_copy_and_cross_file_consistency",
        "initial_pool_static_binary_policy",
        "resume_replay_and_manifest_policy",
        "stale_readiness_and_owner_signoff",
    ]
    assert all(
        "missing_before_parity_claim" in record
        for record in boundary["candidate_workspace_claim_guard"]
    )
    assert all(
        sidecar["exists"]
        for record in boundary["readiness_criteria"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in boundary["readiness_criteria"]
        for ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "configured_language_build_runners": "not_recorded_locally",
        "flexible_solution_abstraction_api": "not_recorded_locally",
        "candidate_embedded_evaluator_contracts": "not_recorded_locally",
        "realistic_codebase_fixtures": "not_recorded_locally",
        "benchmark_calibrated_adaptive_mutation_mode_policy": "not_recorded_locally",
        "mutation_operator_family_provenance": "not_recorded_locally",
        "semantic_prompt_example_copy_detection": "not_recorded_locally",
        "cross_file_consistency_benchmark_evidence": "not_recorded_locally",
        "initial_pool_divergence_benchmark_evidence": "not_recorded_locally",
        "static_binary_replay_policy": "not_recorded_locally",
        "topology_resume_replay_proof": "not_recorded_locally",
        "stale_readiness_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim configured language/build runners" in boundary["claim_boundary"]
    assert "claim guard for each workspace surface" in boundary["claim_boundary"]
    assert "topology resume replay proof" in boundary["claim_boundary"]
    assert "stale-readiness detector" in boundary["claim_boundary"]


def test_roadmap_candidate_workspace_readiness_rejects_overclaim_and_drift():
    boundary = roadmap_candidate_workspace_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_candidate_workspace_readiness_ready"
    boundary["readiness_criterion_count"] = 7
    boundary["source_criterion_count"] = 9
    boundary["readiness_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["candidate_workspace_claim_guard_count"] = 0
    boundary["readiness_criteria"][0]["active_todo_refs"][0][
        "required_phrase_present"
    ] = False
    boundary["missing_evidence"]["configured_language_build_runners"] = "recorded"
    boundary["required_evidence_fields"] = ["readiness_criteria"]

    validation = validate_roadmap_candidate_workspace_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_criterion_count" in codes
    assert "invalid_readiness_criterion_count" in codes
    assert "invalid_readiness_criteria" in codes
    assert "invalid_candidate_workspace_claim_guard_count" in codes
    assert "invalid_missing_evidence_configured_language_build_runners" in codes
    assert "missing_required_evidence_field" in codes
    assert "invalid_required_evidence_field_count" in codes


def test_render_roadmap_candidate_workspace_readiness_summary_reports_shape():
    summary = render_roadmap_candidate_workspace_readiness_boundary_summary(
        roadmap_candidate_workspace_readiness_boundary_record()
    )

    assert "ROADMAP candidate workspace readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_candidate_workspace_readiness_matrix_without_alphaevolve_workspace_gate |"
        in summary
    )
    assert "| readiness_criterion_count | 8 |" in summary
    assert "| sidecar_ref_count | 16 |" in summary
    assert "| active_todo_ref_count | 16 |" in summary
    assert "| missing_evidence_count | 13 |" in summary
