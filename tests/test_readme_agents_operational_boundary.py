from libreevolve.problems.benchmarks.readme_agents_operational_boundary import (
    README_AGENTS_OPERATIONAL_BOUNDARY_SCHEMA,
    readme_agents_operational_boundary_record,
    render_readme_agents_operational_boundary_summary,
    validate_readme_agents_operational_boundary,
)


def test_readme_agents_operational_boundary_accepts_current_drift_record():
    boundary = readme_agents_operational_boundary_record()

    validation = validate_readme_agents_operational_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "agents_operational_static_drift_record_without_complete_instruction_map"
    )
    assert boundary["schema"] == README_AGENTS_OPERATIONAL_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert validation.actual_example_count == 10
    assert validation.listed_example_count == 7
    assert validation.missing_example_count == 3
    assert boundary["missing_examples"] == [
        "embedded_evaluate_math",
        "sorting_network_8",
        "sorting_network_9",
    ]
    assert boundary["stale_examples"] == []
    assert validation.run_artifact_record_count == 15
    assert validation.missing_run_artifact_count == 5
    assert [
        record["artifact_name"]
        for record in boundary["missing_run_artifact_records"]
    ] == [
        "controller_budget_events.jsonl",
        "evaluator_results.jsonl",
        "prompt_current_binding_table.jsonl",
        "prompt_prior_score_table.jsonl",
        "task_specification.json",
    ]
    assert validation.evidence_anchor_count == 11
    assert validation.missing_evidence_anchor_count == 0
    assert boundary["missing_evidence_anchor_records"] == []
    assert (
        boundary["agents_operational_drift_status"]
        == "agents_operational_drift_recorded"
    )
    assert boundary["missing_evidence"] == {
        "complete_instruction_to_source_map": "not_recorded_locally",
        "dependency_list_semantic_check": "not_recorded_locally",
        "provider_guidance_semantic_check": "not_recorded_locally",
        "alphaevolve_scope_semantic_check": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "AGENTS.md operational-instruction drift" in boundary["claim_boundary"]
    assert "example problem directories and run-artifact names" in boundary["claim_boundary"]


def test_readme_agents_operational_boundary_rejects_overclaim_and_drift():
    boundary = readme_agents_operational_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "agents_operational_instruction_map_complete"
    boundary["actual_example_count"] = 0
    boundary["missing_example_count"] = 0
    boundary["missing_examples"] = []
    boundary["missing_run_artifact_count"] = 0
    boundary["missing_run_artifact_records"] = []
    boundary["evidence_anchor_count"] = 0
    boundary["missing_evidence_anchor_count"] = 1
    boundary["missing_evidence_anchor_records"] = [
        boundary["evidence_anchor_records"][0]
    ]
    boundary["evidence_anchor_records"][0]["marker_status"] = "marker_missing"
    boundary["agents_operational_drift_status"] = (
        "agents_operational_drift_record_incomplete"
    )
    boundary["missing_evidence"]["complete_instruction_to_source_map"] = "recorded"
    boundary["required_evidence_fields"] = ["agents_architecture_example_inventory"]

    validation = validate_readme_agents_operational_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_actual_example_count" in codes
    assert "invalid_missing_example_count" in codes
    assert "invalid_missing_examples" in codes
    assert "invalid_missing_run_artifact_count" in codes
    assert "invalid_missing_run_artifact_records" in codes
    assert "invalid_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_records" in codes
    assert "invalid_evidence_anchor_records" in codes
    assert "missing_agents_operational_evidence_anchor" in codes
    assert "invalid_agents_operational_drift_status" in codes
    assert "invalid_missing_evidence_complete_instruction_to_source_map" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_agents_operational_boundary_summary_reports_shape():
    summary = render_readme_agents_operational_boundary_summary(
        readme_agents_operational_boundary_record()
    )

    assert "README AGENTS operational boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | agents_operational_static_drift_record_without_complete_instruction_map |"
        in summary
    )
    assert "| actual_example_count | 10 |" in summary
    assert "| listed_example_count | 7 |" in summary
    assert "| missing_example_count | 3 |" in summary
    assert "| run_artifact_record_count | 15 |" in summary
    assert "| missing_run_artifact_count | 5 |" in summary
    assert "| evidence_anchor_count | 11 |" in summary
    assert "| missing_evidence_anchor_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
