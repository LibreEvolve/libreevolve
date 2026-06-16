from libreevolve.problems.benchmarks.roadmap_non_goal_plugin_docstring_boundary import (
    ROADMAP_NON_GOAL_PLUGIN_DOCSTRING_BOUNDARY_SCHEMA,
    render_roadmap_non_goal_plugin_docstring_boundary_summary,
    roadmap_non_goal_plugin_docstring_boundary_record,
    validate_roadmap_non_goal_plugin_docstring_boundary,
)


def test_roadmap_non_goal_plugin_docstring_accepts_current_sources():
    boundary = roadmap_non_goal_plugin_docstring_boundary_record()

    validation = validate_roadmap_non_goal_plugin_docstring_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "plugin_docstring_scan_without_runtime_or_promotion_gate"
    )
    assert boundary["schema"] == ROADMAP_NON_GOAL_PLUGIN_DOCSTRING_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["source_non_goal_count"] == 3
    assert boundary["plugin_source_root"] == "libreevolve/plugins"
    assert boundary["plugin_source_file_count"] == 7
    assert boundary["source_read_error_count"] == 0
    assert boundary["builtin_plugin_count"] == 4
    assert boundary["paper_inspired_builtin_plugin_count"] == 4
    assert boundary["docstring_record_count"] == 14
    assert boundary["forbidden_phrase_count"] == 7
    assert boundary["faithful_overclaim_count"] == 0
    assert boundary["missing_disclaimer_count"] == 0
    assert [record["label"] for record in boundary["builtin_plugin_records"]] == [
        "causal",
        "deep_research",
        "modular",
        "ttt_rl",
    ]
    assert all(
        record["class_docstring_present"]
        and record["paper_inspired_term_present"]
        and record["non_faithful_disclaimer_present"]
        for record in boundary["paper_inspired_plugin_scope_records"]
    )
    assert boundary["missing_evidence"] == {
        "runtime_metadata_scan": "not_recorded_locally",
        "ci_non_goal_promotion_gate": "not_recorded_locally",
        "intentional_promotion_workflow": "not_recorded_locally",
        "claim_surface_remediation": "not_recorded_locally",
        "runtime_plugin_scope_join": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "AST docstrings" in boundary["claim_boundary"]


def test_roadmap_non_goal_plugin_docstring_rejects_overclaim_and_drift():
    boundary = roadmap_non_goal_plugin_docstring_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_non_goal_promotion_gate_ready"
    boundary["faithful_overclaim_count"] = 1
    boundary["faithful_overclaim_hit_records"] = [
        {
            "path": "libreevolve/plugins/modular.py",
            "line_start": 1,
            "phrase": "faithful implementation",
            "column_start": 1,
        }
    ]
    boundary["missing_disclaimer_count"] = 1
    boundary["missing_disclaimer_records"] = [
        boundary["paper_inspired_plugin_scope_records"][0]
    ]
    boundary["missing_evidence"]["runtime_metadata_scan"] = "recorded"
    boundary["required_evidence_fields"] = ["stable_non_goal_ids"]

    validation = validate_roadmap_non_goal_plugin_docstring_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_faithful_overclaim_count" in codes
    assert "invalid_faithful_overclaim_hit_records" in codes
    assert "faithful_overclaim_detected" in codes
    assert "missing_plugin_disclaimer" in codes
    assert "invalid_missing_evidence_runtime_metadata_scan" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_non_goal_plugin_docstring_summary_reports_shape():
    summary = render_roadmap_non_goal_plugin_docstring_boundary_summary(
        roadmap_non_goal_plugin_docstring_boundary_record()
    )

    assert "ROADMAP non-goal plugin docstring boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | plugin_docstring_scan_without_runtime_or_promotion_gate |"
        in summary
    )
    assert "| plugin_source_file_count | 7 |" in summary
    assert "| builtin_plugin_count | 4 |" in summary
    assert "| docstring_record_count | 14 |" in summary
    assert "| faithful_overclaim_count | 0 |" in summary
    assert "| missing_disclaimer_count | 0 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
