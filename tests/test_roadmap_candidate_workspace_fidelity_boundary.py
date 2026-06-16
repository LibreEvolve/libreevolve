from libreevolve.problems.benchmarks.roadmap_candidate_workspace_fidelity_boundary import (
    ROADMAP_CANDIDATE_WORKSPACE_FIDELITY_BOUNDARY_SCHEMA,
    render_roadmap_candidate_workspace_fidelity_boundary_summary,
    roadmap_candidate_workspace_fidelity_boundary_record,
    validate_roadmap_candidate_workspace_fidelity_boundary,
)


def test_roadmap_candidate_workspace_fidelity_accepts_bounded_criteria_map():
    boundary = roadmap_candidate_workspace_fidelity_boundary_record()

    validation = validate_roadmap_candidate_workspace_fidelity_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_candidate_workspace_fidelity_matrix_without_alphaevolve_workspace_readiness"
    )
    assert boundary["schema"] == ROADMAP_CANDIDATE_WORKSPACE_FIDELITY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["roadmap_heading_present"] is True
    assert boundary["criterion_count"] == 10
    assert boundary["active_todo_ref_count"] == 20
    assert boundary["sidecar_ref_count"] == 15
    assert [record["criterion_id"] for record in boundary["criterion_records"]] == [
        "language_build_runner_support",
        "candidate_abstraction_api",
        "marker_materialization_policy",
        "embedded_evaluator_boundary",
        "codebase_scale_fixtures",
        "mutation_mode_operator_provenance",
        "prompt_example_copy_guard",
        "cross_file_mutation_consistency",
        "initial_pool_static_binary_handling",
        "workspace_source_integrity_resume",
    ]
    assert all(record["roadmap_phrase_present"] for record in boundary["criterion_records"])
    assert all(
        sidecar["exists"]
        for record in boundary["criterion_records"]
        for sidecar in record["current_sidecar_refs"]
    )
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in boundary["criterion_records"]
        for ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "configured_language_build_runners": "not_recorded_locally",
        "flexible_solution_abstraction_api": "not_recorded_locally",
        "candidate_embedded_evaluator_contracts": "not_recorded_locally",
        "realistic_codebase_fixtures": "not_recorded_locally",
        "adaptive_mutation_mode_selection": "not_recorded_locally",
        "mutation_operator_family_provenance": "not_recorded_locally",
        "semantic_prompt_example_copy_detection": "not_recorded_locally",
        "cross_file_consistency_benchmark_evidence": "not_recorded_locally",
        "initial_pool_divergence_benchmark_evidence": "not_recorded_locally",
        "static_binary_replay_policy": "not_recorded_locally",
        "topology_resume_replay_proof": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim configured language/build runners" in boundary["claim_boundary"]


def test_roadmap_candidate_workspace_fidelity_rejects_overclaim_and_drift():
    boundary = roadmap_candidate_workspace_fidelity_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_candidate_workspace_fidelity_ready"
    boundary["criterion_count"] = 9
    boundary["criterion_records"][0]["roadmap_phrase_present"] = False
    boundary["missing_evidence"]["configured_language_build_runners"] = "recorded"
    boundary["required_evidence_fields"] = ["criterion_records"]

    validation = validate_roadmap_candidate_workspace_fidelity_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_criterion_count" in codes
    assert "invalid_criterion_records" in codes
    assert "invalid_missing_evidence_configured_language_build_runners" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_candidate_workspace_fidelity_summary_reports_shape():
    summary = render_roadmap_candidate_workspace_fidelity_boundary_summary(
        roadmap_candidate_workspace_fidelity_boundary_record()
    )

    assert "ROADMAP candidate workspace fidelity boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_candidate_workspace_fidelity_matrix_without_alphaevolve_workspace_readiness |"
        in summary
    )
    assert "| criterion_count | 10 |" in summary
    assert "| active_todo_ref_count | 20 |" in summary
    assert "| missing_evidence_count | 12 |" in summary
