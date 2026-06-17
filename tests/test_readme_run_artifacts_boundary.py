from libreevolve.problems.benchmarks.readme_run_artifacts_boundary import (
    README_RUN_ARTIFACTS_BOUNDARY_SCHEMA,
    readme_run_artifacts_boundary_record,
    render_readme_run_artifacts_boundary_summary,
    validate_readme_run_artifacts_boundary,
)


def test_readme_run_artifacts_boundary_accepts_current_list_map():
    boundary = readme_run_artifacts_boundary_record()

    validation = validate_readme_run_artifacts_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_run_artifacts_structural_list_without_lifecycle_parity"
    )
    assert boundary["schema"] == README_RUN_ARTIFACTS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["readme_path"] == "README.md"
    assert boundary["run_artifacts_doc_path"] == "docs/run-artifacts.md"
    assert boundary["cleanup_source_path"] == "libreevolve/core/database.py"
    assert validation.readme_marker_count == 7
    assert validation.missing_readme_marker_count == 0
    assert validation.common_artifact_count == 14
    assert validation.missing_common_artifact_count == 0
    assert validation.cleanup_artifact_count == 23
    assert validation.scoped_omission_count == 9
    assert validation.evidence_anchor_count == 18
    assert validation.missing_evidence_anchor_count == 0
    assert boundary["missing_readme_marker_records"] == []
    assert boundary["missing_common_artifact_records"] == []
    assert boundary["missing_evidence_anchor_records"] == []
    assert boundary["scope_omission_drift_records"] == []
    assert boundary["readme_common_without_cleanup_names"] == []
    assert boundary["cleanup_without_readme_common_names"] == [
        "archive_events_invalid.jsonl",
        "controller_budget_events_invalid.jsonl",
        "failure_history_invalid.jsonl",
        "history_invalid.jsonl",
        "llm_calls_invalid.jsonl",
        "manifest_invalid.jsonl",
        "paper_artifacts",
        "prompt_history_invalid.jsonl",
        "task_specification.json",
    ]
    assert {
        record["name"]: record["scope_status"]
        for record in boundary["scope_omission_records"]
    } == {
        "task_specification.json": "documented_outside_readme_common_list",
        "history_invalid.jsonl": "documented_outside_readme_common_list",
        "failure_history_invalid.jsonl": "documented_outside_readme_common_list",
        "archive_events_invalid.jsonl": "documented_outside_readme_common_list",
        "controller_budget_events_invalid.jsonl": "documented_outside_readme_common_list",
        "llm_calls_invalid.jsonl": "documented_outside_readme_common_list",
        "manifest_invalid.jsonl": "documented_outside_readme_common_list",
        "prompt_history_invalid.jsonl": "documented_outside_readme_common_list",
        "paper_artifacts": "documented_outside_readme_common_list",
    }
    paper_artifacts = next(
        record
        for record in boundary["scope_omission_records"]
        if record["name"] == "paper_artifacts"
    )
    assert paper_artifacts["present_in_cleanup_set"] is True
    assert boundary["readme_run_artifacts_map_status"] == (
        "readme_run_artifacts_structural_list_map_present"
    )
    assert boundary["missing_evidence"] == {
        "fresh_smoke_run_artifact_presence_matrix": "not_recorded_locally",
        "artifact_writer_reader_schema_map": "not_recorded_locally",
        "restore_and_show_lifecycle_proof": "not_recorded_locally",
        "optional_artifact_classification_gate": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "14 README common output records" in boundary["claim_boundary"]
    assert "restore/show lifecycle proof" in boundary["claim_boundary"]


def test_readme_run_artifacts_boundary_rejects_overclaim_and_drift():
    boundary = readme_run_artifacts_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "readme_run_artifacts_lifecycle_parity_ready"
    boundary["readme_marker_count"] = 0
    boundary["missing_readme_marker_count"] = 1
    boundary["missing_readme_marker_records"] = [boundary["readme_marker_records"][0]]
    boundary["readme_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["common_artifact_count"] = 0
    boundary["missing_common_artifact_count"] = 1
    boundary["missing_common_artifact_records"] = [boundary["common_artifact_records"][0]]
    boundary["common_artifact_records"][0]["readme_status"] = "missing_from_readme"
    boundary["cleanup_artifact_count"] = 0
    boundary["cleanup_artifact_names"] = []
    boundary["scoped_omission_count"] = 0
    boundary["scope_omission_drift_count"] = 1
    boundary["scope_omission_drift_records"] = [boundary["scope_omission_records"][0]]
    boundary["scope_omission_records"][0]["scope_status"] = "scope_omission_anchor_missing"
    boundary["evidence_anchor_count"] = 0
    boundary["missing_evidence_anchor_count"] = 1
    boundary["missing_evidence_anchor_records"] = [
        boundary["evidence_anchor_records"][0]
    ]
    boundary["evidence_anchor_records"][0]["marker_status"] = "marker_missing"
    boundary["readme_run_artifacts_map_status"] = (
        "readme_run_artifacts_structural_list_map_incomplete"
    )
    boundary["missing_evidence"]["restore_and_show_lifecycle_proof"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_run_artifact_markers"]

    validation = validate_readme_run_artifacts_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_readme_marker_count" in codes
    assert "invalid_missing_readme_marker_count" in codes
    assert "invalid_missing_readme_marker_records" in codes
    assert "invalid_readme_marker_records" in codes
    assert "missing_readme_run_artifacts_marker" in codes
    assert "invalid_common_artifact_count" in codes
    assert "invalid_missing_common_artifact_count" in codes
    assert "invalid_missing_common_artifact_records" in codes
    assert "invalid_common_artifact_records" in codes
    assert "missing_readme_common_artifact" in codes
    assert "invalid_cleanup_artifact_count" in codes
    assert "invalid_cleanup_artifact_names" in codes
    assert "invalid_scoped_omission_count" in codes
    assert "invalid_scope_omission_drift_count" in codes
    assert "invalid_scope_omission_records" in codes
    assert "invalid_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_records" in codes
    assert "invalid_evidence_anchor_records" in codes
    assert "missing_readme_run_artifacts_evidence_anchor" in codes
    assert "invalid_readme_run_artifacts_map_status" in codes
    assert "invalid_missing_evidence_restore_and_show_lifecycle_proof" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_run_artifacts_boundary_summary_reports_shape():
    summary = render_readme_run_artifacts_boundary_summary(
        readme_run_artifacts_boundary_record()
    )

    assert "README run-artifacts boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_run_artifacts_structural_list_without_lifecycle_parity |"
        in summary
    )
    assert "| readme_marker_count | 7 |" in summary
    assert "| missing_readme_marker_count | 0 |" in summary
    assert "| common_artifact_count | 14 |" in summary
    assert "| missing_common_artifact_count | 0 |" in summary
    assert "| cleanup_artifact_count | 23 |" in summary
    assert "| scoped_omission_count | 9 |" in summary
    assert "| evidence_anchor_count | 18 |" in summary
    assert "| missing_evidence_anchor_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
