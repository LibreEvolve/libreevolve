from libreevolve.problems.benchmarks.readme_problem_layout_boundary import (
    README_PROBLEM_LAYOUT_BOUNDARY_SCHEMA,
    readme_problem_layout_boundary_record,
    render_readme_problem_layout_boundary_summary,
    validate_readme_problem_layout_boundary,
)


def test_readme_problem_layout_boundary_accepts_current_map():
    boundary = readme_problem_layout_boundary_record()

    validation = validate_readme_problem_layout_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_problem_layout_structural_map_without_semantic_loader_proof"
    )
    assert boundary["schema"] == README_PROBLEM_LAYOUT_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["readme_path"] == "README.md"
    assert boundary["problem_format_path"] == "docs/problem-format.md"
    assert boundary["problem_layout_block_status"] == "problem_layout_block_present"
    assert validation.layout_item_count == 6
    assert validation.missing_layout_item_count == 0
    assert validation.contract_marker_count == 30
    assert validation.missing_contract_marker_count == 0
    assert validation.missing_example_path_count == 0
    assert boundary["missing_layout_item_records"] == []
    assert boundary["missing_contract_marker_records"] == []
    assert boundary["missing_example_paths"] == []
    assert boundary["readme_problem_layout_map_status"] == (
        "readme_problem_layout_structural_map_present"
    )
    assert {
        record["item_id"]: record["status"]
        for record in boundary["layout_item_records"]
    } == {
        "initial_programs": "required_with_file_or_directory_seed_support",
        "validate_py": "required_for_external_validator_with_embedded_only_exception",
        "metrics_yaml": "required_metric_schema_file",
        "task_description": "required_prompt_task_file",
        "config_yaml": "optional_problem_runtime_configuration",
        "seed_policy_yaml": "optional_seed_workspace_policy_and_primary_selection",
    }
    assert boundary["missing_evidence"] == {
        "semantic_loader_contract_verifier": "not_recorded_locally",
        "minimal_problem_smoke_fixture": "not_recorded_locally",
        "problem_format_long_contract_drift_gate": "not_recorded_locally",
        "new_problem_surface_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "README Problem Layout block" in boundary["claim_boundary"]


def test_readme_problem_layout_boundary_rejects_overclaim_and_drift():
    boundary = readme_problem_layout_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "readme_problem_layout_semantically_verified"
    boundary["problem_layout_block_status"] = "problem_layout_block_missing"
    boundary["missing_layout_item_count"] = 1
    boundary["missing_layout_item_records"] = [boundary["layout_item_records"][0]]
    boundary["layout_item_records"][0]["item_status"] = "item_markers_or_examples_missing"
    boundary["contract_marker_count"] = 0
    boundary["missing_contract_marker_count"] = 1
    boundary["missing_contract_marker_records"] = [boundary["contract_marker_records"][0]]
    boundary["contract_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["missing_example_path_count"] = 1
    boundary["missing_example_paths"] = ["libreevolve/problems/examples/hello_world"]
    boundary["readme_problem_layout_map_status"] = (
        "readme_problem_layout_structural_map_incomplete"
    )
    boundary["missing_evidence"]["semantic_loader_contract_verifier"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_problem_layout_block_inventory"]

    validation = validate_readme_problem_layout_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_problem_layout_block_status" in codes
    assert "missing_problem_layout_block" in codes
    assert "invalid_missing_layout_item_count" in codes
    assert "invalid_missing_layout_item_records" in codes
    assert "invalid_layout_item_records" in codes
    assert "missing_problem_layout_item" in codes
    assert "invalid_contract_marker_count" in codes
    assert "invalid_missing_contract_marker_count" in codes
    assert "invalid_missing_contract_marker_records" in codes
    assert "invalid_contract_marker_records" in codes
    assert "missing_problem_layout_contract_marker" in codes
    assert "invalid_missing_example_path_count" in codes
    assert "invalid_missing_example_paths" in codes
    assert "missing_problem_layout_example_path" in codes
    assert "invalid_readme_problem_layout_map_status" in codes
    assert "invalid_missing_evidence_semantic_loader_contract_verifier" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_problem_layout_boundary_summary_reports_shape():
    summary = render_readme_problem_layout_boundary_summary(
        readme_problem_layout_boundary_record()
    )

    assert "README Problem Layout boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_problem_layout_structural_map_without_semantic_loader_proof |"
        in summary
    )
    assert "| layout_item_count | 6 |" in summary
    assert "| missing_layout_item_count | 0 |" in summary
    assert "| contract_marker_count | 30 |" in summary
    assert "| missing_contract_marker_count | 0 |" in summary
    assert "| missing_example_path_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
