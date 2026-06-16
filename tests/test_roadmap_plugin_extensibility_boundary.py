from libreevolve.problems.benchmarks.roadmap_plugin_extensibility_boundary import (
    ROADMAP_PLUGIN_EXTENSIBILITY_BOUNDARY_SCHEMA,
    render_roadmap_plugin_extensibility_boundary_summary,
    roadmap_plugin_extensibility_boundary_record,
    validate_roadmap_plugin_extensibility_boundary,
)


def test_roadmap_plugin_extensibility_accepts_bounded_matrix():
    boundary = roadmap_plugin_extensibility_boundary_record()

    validation = validate_roadmap_plugin_extensibility_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_plugin_extensibility_matrix_without_external_plugin_readiness"
    )
    assert boundary["schema"] == ROADMAP_PLUGIN_EXTENSIBILITY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["roadmap_heading_present"] is True
    assert boundary["surface_count"] == 6
    assert boundary["active_todo_ref_count"] == 10
    assert boundary["sidecar_ref_count"] == 14
    assert boundary["code_ref_count"] == 11
    assert [record["surface_id"] for record in boundary["surface_records"]] == [
        "builtin_plugin_catalog",
        "entry_point_plugins",
        "direct_instance_plugins",
        "future_custom_registry",
        "plugin_hook_isolation",
        "plugin_artifact_lifecycle",
    ]
    assert all(record["roadmap_phrase_present"] for record in boundary["surface_records"])
    assert all(
        sidecar["exists"]
        for record in boundary["surface_records"]
        for sidecar in record["current_sidecar_refs"]
    )
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in boundary["surface_records"]
        for ref in record["current_code_refs"]
    )
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in boundary["surface_records"]
        for ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "plugin_trust_boundary_matrix": "not_recorded_locally",
        "plugin_admission_checklist": "not_recorded_locally",
        "direct_constructor_value_schema_registry": "not_recorded_locally",
        "versioned_custom_plugin_registry": "not_recorded_locally",
        "artifact_lifecycle_hash_policy": "not_recorded_locally",
        "runtime_isolation_policy": "not_recorded_locally",
        "paper_scope_attribution_policy": "not_recorded_locally",
        "stale_readiness_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim a plugin trust-boundary matrix" in boundary["claim_boundary"]


def test_roadmap_plugin_extensibility_rejects_external_plugin_overclaim_and_drift():
    boundary = roadmap_plugin_extensibility_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "external_plugin_readiness"
    boundary["surface_count"] = 5
    boundary["surface_records"][0]["roadmap_phrase_present"] = False
    boundary["missing_evidence"]["plugin_trust_boundary_matrix"] = "recorded"
    boundary["required_evidence_fields"] = ["surface_records"]

    validation = validate_roadmap_plugin_extensibility_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_surface_count" in codes
    assert "invalid_surface_records" in codes
    assert "invalid_missing_evidence_plugin_trust_boundary_matrix" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_plugin_extensibility_summary_reports_shape():
    summary = render_roadmap_plugin_extensibility_boundary_summary(
        roadmap_plugin_extensibility_boundary_record()
    )

    assert "ROADMAP plugin extensibility boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_plugin_extensibility_matrix_without_external_plugin_readiness |"
        in summary
    )
    assert "| surface_count | 6 |" in summary
    assert "| active_todo_ref_count | 10 |" in summary
    assert "| missing_evidence_count | 9 |" in summary
