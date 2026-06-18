from libreevolve.problems.benchmarks.roadmap_plugin_readiness_boundary import (
    ROADMAP_PLUGIN_READINESS_BOUNDARY_SCHEMA,
    render_roadmap_plugin_readiness_boundary_summary,
    roadmap_plugin_readiness_boundary_record,
    validate_roadmap_plugin_readiness_boundary,
)


def test_roadmap_plugin_readiness_accepts_bounded_matrix():
    boundary = roadmap_plugin_readiness_boundary_record()

    validation = validate_roadmap_plugin_readiness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_plugin_readiness_matrix_without_external_plugin_gate"
    )
    assert boundary["schema"] == ROADMAP_PLUGIN_READINESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_plugin_boundary_input"]
        == "papers/roadmap_plugin_extensibility_boundary.json"
    )
    assert boundary["source_surface_count"] == 6
    assert boundary["source_active_todo_ref_count"] == 10
    assert boundary["source_sidecar_ref_count"] == 14
    assert boundary["source_code_ref_count"] == 11
    assert boundary["readiness_criterion_count"] == 7
    assert boundary["sidecar_ref_count"] == 14
    assert boundary["active_todo_ref_count"] == 14
    assert [record["criterion_id"] for record in boundary["readiness_criteria"]] == [
        "plugin_trust_boundary_matrix",
        "plugin_admission_checklist",
        "direct_constructor_value_schema_registry",
        "versioned_custom_plugin_registry",
        "artifact_lifecycle_hash_policy",
        "runtime_isolation_policy",
        "paper_scope_attribution_and_staleness",
    ]
    assert boundary["plugin_claim_guard_count"] == 7
    assert [record["criterion_id"] for record in boundary["plugin_claim_guard"]] == [
        "plugin_trust_boundary_matrix",
        "plugin_admission_checklist",
        "direct_constructor_value_schema_registry",
        "versioned_custom_plugin_registry",
        "artifact_lifecycle_hash_policy",
        "runtime_isolation_policy",
        "paper_scope_attribution_and_staleness",
    ]
    assert all(
        "missing_before_external_plugin_claim" in record
        for record in boundary["plugin_claim_guard"]
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
        "plugin_trust_boundary_matrix": "not_recorded_locally",
        "plugin_admission_checklist": "not_recorded_locally",
        "direct_constructor_value_schema_registry": "not_recorded_locally",
        "versioned_custom_plugin_registry": "not_recorded_locally",
        "artifact_lifecycle_hash_policy": "not_recorded_locally",
        "runtime_isolation_policy": "not_recorded_locally",
        "paper_scope_attribution_and_staleness": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim a plugin trust-boundary matrix" in boundary["claim_boundary"]
    assert "claim guard for each plugin surface" in boundary["claim_boundary"]


def test_roadmap_plugin_readiness_rejects_overclaim_and_drift():
    boundary = roadmap_plugin_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "external_plugin_gate_ready"
    boundary["readiness_criterion_count"] = 0
    boundary["readiness_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["plugin_claim_guard_count"] = 0
    boundary["missing_evidence"]["plugin_admission_checklist"] = "recorded"
    boundary["required_evidence_fields"] = ["plugin_trust_boundary_matrix"]

    validation = validate_roadmap_plugin_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_readiness_criterion_count" in codes
    assert "invalid_readiness_criteria" in codes
    assert "invalid_plugin_claim_guard_count" in codes
    assert "invalid_missing_evidence_plugin_admission_checklist" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_plugin_readiness_summary_reports_shape():
    summary = render_roadmap_plugin_readiness_boundary_summary(
        roadmap_plugin_readiness_boundary_record()
    )

    assert "ROADMAP plugin readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_plugin_readiness_matrix_without_external_plugin_gate |"
        in summary
    )
    assert "| readiness_criterion_count | 7 |" in summary
    assert "| sidecar_ref_count | 14 |" in summary
    assert "| active_todo_ref_count | 14 |" in summary
    assert "| missing_evidence_count | 8 |" in summary
