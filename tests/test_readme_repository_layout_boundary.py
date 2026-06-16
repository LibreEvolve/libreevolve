from libreevolve.problems.benchmarks.readme_repository_layout_boundary import (
    README_REPOSITORY_LAYOUT_BOUNDARY_SCHEMA,
    readme_repository_layout_boundary_record,
    render_readme_repository_layout_boundary_summary,
    validate_readme_repository_layout_boundary,
)


def test_readme_repository_layout_boundary_accepts_current_layout():
    boundary = readme_repository_layout_boundary_record()

    validation = validate_readme_repository_layout_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_repository_layout_recorded_without_semantic_role_verifier"
    )
    assert boundary["schema"] == README_REPOSITORY_LAYOUT_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["readme_path"] == "README.md"
    assert boundary["layout_block_status"] == "layout_block_present"
    assert validation.layout_entry_count == 13
    assert validation.missing_layout_entry_count == 0
    assert boundary["missing_layout_entry_records"] == []
    assert validation.missing_evidence_path_count == 0
    assert boundary["missing_evidence_paths"] == []
    assert boundary["custom_backend_layout_status"] == "custom_backend_marker_present"
    assert boundary["archival_old_layout_status"] == "archival_old_layout_present"
    assert boundary["run_output_scope_status"] == "run_output_scope_present"
    llm_record = next(
        record for record in boundary["layout_entry_records"] if record["entry_id"] == "llm"
    )
    assert "custom backends" in llm_record["entry_line"]
    assert llm_record["missing_summary_markers"] == []
    assert llm_record["missing_evidence_paths"] == []
    assert boundary["missing_evidence"] == {
        "module_role_semantic_verifier": "not_recorded_locally",
        "new_top_level_detector": "not_recorded_locally",
        "new_major_docs_detector": "not_recorded_locally",
        "alphaevolve_parity_placeholder_classifier": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "README Repository Layout code block" in boundary["claim_boundary"]


def test_readme_repository_layout_boundary_rejects_overclaim_and_drift():
    boundary = readme_repository_layout_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "readme_repository_layout_semantically_verified"
    boundary["layout_block_status"] = "layout_block_missing"
    boundary["missing_layout_entry_count"] = 1
    boundary["missing_layout_entry_records"] = [boundary["layout_entry_records"][0]]
    boundary["layout_entry_records"][0]["entry_status"] = "entry_path_or_markers_missing"
    boundary["missing_evidence_path_count"] = 1
    boundary["missing_evidence_paths"] = ["libreevolve/core/loop.py"]
    boundary["custom_backend_layout_status"] = "custom_backend_marker_missing"
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["repository_layout_block_inventory"]

    validation = validate_readme_repository_layout_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_layout_block_status" in codes
    assert "missing_layout_block" in codes
    assert "invalid_missing_layout_entry_count" in codes
    assert "invalid_missing_layout_entry_records" in codes
    assert "invalid_layout_entry_records" in codes
    assert "missing_layout_entry" in codes
    assert "invalid_missing_evidence_path_count" in codes
    assert "invalid_missing_evidence_paths" in codes
    assert "missing_layout_evidence_path" in codes
    assert "missing_custom_backend_layout_marker" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_repository_layout_boundary_summary_reports_shape():
    summary = render_readme_repository_layout_boundary_summary(
        readme_repository_layout_boundary_record()
    )

    assert "README Repository Layout boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_repository_layout_recorded_without_semantic_role_verifier |"
        in summary
    )
    assert "| layout_entry_count | 13 |" in summary
    assert "| missing_layout_entry_count | 0 |" in summary
    assert "| missing_evidence_path_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
