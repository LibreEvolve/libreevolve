from libreevolve.problems.benchmarks.roadmap_non_goal_runtime_metadata_boundary import (
    ROADMAP_NON_GOAL_RUNTIME_METADATA_BOUNDARY_SCHEMA,
    render_roadmap_non_goal_runtime_metadata_boundary_summary,
    roadmap_non_goal_runtime_metadata_boundary_record,
    validate_roadmap_non_goal_runtime_metadata_boundary,
)


def test_roadmap_non_goal_runtime_metadata_accepts_current_sources():
    boundary = roadmap_non_goal_runtime_metadata_boundary_record()

    validation = validate_roadmap_non_goal_runtime_metadata_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "runtime_metadata_scan_without_ci_or_promotion_gate"
    )
    assert boundary["schema"] == ROADMAP_NON_GOAL_RUNTIME_METADATA_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["source_non_goal_count"] == 3
    assert boundary["runtime_surface_count"] == 4
    assert boundary["runtime_metadata_path_count"] == 13
    assert boundary["source_missing_count"] == 0
    assert boundary["safe_phrase_missing_count"] == 0
    assert boundary["builtin_plugin_registry_count"] == 4
    assert boundary["forbidden_phrase_count"] == 10
    assert boundary["contradiction_count"] == 0
    assert [record["surface_id"] for record in boundary["runtime_surface_records"]] == [
        "startup_manifest_config_plugins",
        "runtime_plugin_state",
        "runtime_plugin_artifacts",
        "builtin_plugin_registry",
    ]
    assert all(
        record["source_status"] == "present"
        and not record["missing_safe_phrase_records"]
        and not record["forbidden_support_claim_hit_records"]
        for record in boundary["runtime_surface_records"]
    )
    assert boundary["missing_evidence"] == {
        "ci_non_goal_promotion_gate": "not_recorded_locally",
        "intentional_promotion_workflow": "not_recorded_locally",
        "claim_surface_remediation": "not_recorded_locally",
        "runtime_plugin_scope_join": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "source-defined runtime metadata surfaces" in boundary["claim_boundary"]


def test_roadmap_non_goal_runtime_metadata_rejects_overclaim_and_drift():
    boundary = roadmap_non_goal_runtime_metadata_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_non_goal_promotion_gate_ready"
    boundary["contradiction_count"] = 1
    boundary["contradiction_records"] = [
        {
            "path": "libreevolve/core/database.py",
            "line_start": 1,
            "phrase": "supports arbitrary-language runners",
            "column_start": 1,
        }
    ]
    boundary["missing_evidence"]["ci_non_goal_promotion_gate"] = "recorded"
    boundary["required_evidence_fields"] = ["stable_non_goal_ids"]

    validation = validate_roadmap_non_goal_runtime_metadata_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_contradiction_count" in codes
    assert "invalid_contradiction_records" in codes
    assert "contradiction_detected" in codes
    assert "invalid_missing_evidence_ci_non_goal_promotion_gate" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_non_goal_runtime_metadata_summary_reports_shape():
    summary = render_roadmap_non_goal_runtime_metadata_boundary_summary(
        roadmap_non_goal_runtime_metadata_boundary_record()
    )

    assert "ROADMAP non-goal runtime metadata boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | runtime_metadata_scan_without_ci_or_promotion_gate |"
        in summary
    )
    assert "| runtime_surface_count | 4 |" in summary
    assert "| source_missing_count | 0 |" in summary
    assert "| safe_phrase_missing_count | 0 |" in summary
    assert "| contradiction_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
