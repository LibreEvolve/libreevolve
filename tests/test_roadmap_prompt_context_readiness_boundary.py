from libreevolve.problems.benchmarks.roadmap_prompt_context_readiness_boundary import (
    ROADMAP_PROMPT_CONTEXT_READINESS_BOUNDARY_SCHEMA,
    render_roadmap_prompt_context_readiness_boundary_summary,
    roadmap_prompt_context_readiness_boundary_record,
    validate_roadmap_prompt_context_readiness_boundary,
)


def test_roadmap_prompt_context_readiness_accepts_bounded_matrix():
    boundary = roadmap_prompt_context_readiness_boundary_record()

    validation = validate_roadmap_prompt_context_readiness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_prompt_context_readiness_matrix_without_full_prompt_system_gate"
    )
    assert boundary["schema"] == ROADMAP_PROMPT_CONTEXT_READINESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_prompt_boundary_input"]
        == "papers/roadmap_prompt_context_system_boundary.json"
    )
    assert boundary["source_criterion_count"] == 9
    assert boundary["source_active_todo_ref_count"] == 18
    assert boundary["source_sidecar_ref_count"] == 17
    assert boundary["readiness_criterion_count"] == 8
    assert boundary["sidecar_ref_count"] == 16
    assert boundary["active_todo_ref_count"] == 16
    assert [record["criterion_id"] for record in boundary["readiness_criteria"]] == [
        "prompt_role_capability_matrix",
        "context_selection_and_summarization",
        "all_role_token_section_packing",
        "prompt_format_and_replay_retention",
        "retrieval_and_proposal_memory_integrity",
        "meta_prompt_and_prompt_database_lifecycle",
        "prompt_context_benchmark_evidence",
        "stale_readiness_and_owner_signoff",
    ]
    assert boundary["prompt_context_claim_guard_count"] == 8
    assert [
        record["criterion_id"] for record in boundary["prompt_context_claim_guard"]
    ] == [
        "prompt_role_capability_matrix",
        "context_selection_and_summarization",
        "all_role_token_section_packing",
        "prompt_format_and_replay_retention",
        "retrieval_and_proposal_memory_integrity",
        "meta_prompt_and_prompt_database_lifecycle",
        "prompt_context_benchmark_evidence",
        "stale_readiness_and_owner_signoff",
    ]
    assert all(
        "missing_before_parity_claim" in record
        for record in boundary["prompt_context_claim_guard"]
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
        "prompt_role_capability_matrix": "not_recorded_locally",
        "deterministic_context_summarization": "not_recorded_locally",
        "all_role_provider_token_section_packing": "not_recorded_locally",
        "separate_prompt_format_source_provenance": "not_recorded_locally",
        "full_prompt_replay_retention_policy": "not_recorded_locally",
        "audit_grade_retrieval_source_integrity": "not_recorded_locally",
        "semantic_proposal_memory": "not_recorded_locally",
        "calibrated_meta_prompt_rewards": "not_recorded_locally",
        "prompt_database_archive_lifecycle": "not_recorded_locally",
        "prompt_context_benchmark_evidence": "not_recorded_locally",
        "stale_readiness_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim a prompt-role capability matrix" in boundary["claim_boundary"]
    assert "claim guard for each prompt surface" in boundary["claim_boundary"]


def test_roadmap_prompt_context_readiness_rejects_overclaim_and_drift():
    boundary = roadmap_prompt_context_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_prompt_context_ready"
    boundary["readiness_criterion_count"] = 0
    boundary["readiness_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["prompt_context_claim_guard_count"] = 0
    boundary["missing_evidence"]["semantic_proposal_memory"] = "recorded"
    boundary["required_evidence_fields"] = ["prompt_role_capability_matrix"]

    validation = validate_roadmap_prompt_context_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_readiness_criterion_count" in codes
    assert "invalid_readiness_criteria" in codes
    assert "invalid_prompt_context_claim_guard_count" in codes
    assert "invalid_missing_evidence_semantic_proposal_memory" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_prompt_context_readiness_summary_reports_shape():
    summary = render_roadmap_prompt_context_readiness_boundary_summary(
        roadmap_prompt_context_readiness_boundary_record()
    )

    assert "ROADMAP prompt context readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_prompt_context_readiness_matrix_without_full_prompt_system_gate |"
        in summary
    )
    assert "| readiness_criterion_count | 8 |" in summary
    assert "| sidecar_ref_count | 16 |" in summary
    assert "| active_todo_ref_count | 16 |" in summary
    assert "| missing_evidence_count | 12 |" in summary
