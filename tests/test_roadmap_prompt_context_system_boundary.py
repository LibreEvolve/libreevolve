from libreevolve.problems.benchmarks.roadmap_prompt_context_system_boundary import (
    ROADMAP_PROMPT_CONTEXT_SYSTEM_BOUNDARY_SCHEMA,
    render_roadmap_prompt_context_system_boundary_summary,
    roadmap_prompt_context_system_boundary_record,
    validate_roadmap_prompt_context_system_boundary,
)


def test_roadmap_prompt_context_system_accepts_bounded_criteria_map():
    boundary = roadmap_prompt_context_system_boundary_record()

    validation = validate_roadmap_prompt_context_system_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_prompt_context_system_matrix_without_full_prompt_system_readiness"
    )
    assert boundary["schema"] == ROADMAP_PROMPT_CONTEXT_SYSTEM_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["roadmap_heading_present"] is True
    assert boundary["criterion_count"] == 9
    assert boundary["active_todo_ref_count"] == 18
    assert boundary["sidecar_ref_count"] == 17
    assert [record["criterion_id"] for record in boundary["criterion_records"]] == [
        "role_template_compatibility",
        "context_source_selection",
        "token_section_packing",
        "stochastic_prompt_format_provenance",
        "retention_replay_context_policy",
        "retrieval_integrity",
        "proposal_memory_semantics",
        "meta_prompt_reward_evidence",
        "prompt_database_lifecycle",
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
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim a prompt-role capability matrix" in boundary["claim_boundary"]


def test_roadmap_prompt_context_system_rejects_overclaim_and_drift():
    boundary = roadmap_prompt_context_system_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_prompt_context_system_ready"
    boundary["criterion_count"] = 8
    boundary["criterion_records"][0]["roadmap_phrase_present"] = False
    boundary["missing_evidence"]["semantic_proposal_memory"] = "recorded"
    boundary["required_evidence_fields"] = ["criterion_records"]

    validation = validate_roadmap_prompt_context_system_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_criterion_count" in codes
    assert "invalid_criterion_records" in codes
    assert "invalid_missing_evidence_semantic_proposal_memory" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_prompt_context_system_summary_reports_shape():
    summary = render_roadmap_prompt_context_system_boundary_summary(
        roadmap_prompt_context_system_boundary_record()
    )

    assert "ROADMAP prompt context system boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_prompt_context_system_matrix_without_full_prompt_system_readiness |"
        in summary
    )
    assert "| criterion_count | 9 |" in summary
    assert "| active_todo_ref_count | 18 |" in summary
    assert "| missing_evidence_count | 11 |" in summary
