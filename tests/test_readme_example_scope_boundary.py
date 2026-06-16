from libreevolve.problems.benchmarks.readme_example_scope_boundary import (
    README_EXAMPLE_SCOPE_BOUNDARY_SCHEMA,
    readme_example_scope_boundary_record,
    render_readme_example_scope_boundary_summary,
    validate_readme_example_scope_boundary,
)


def test_readme_example_scope_boundary_accepts_current_map():
    boundary = readme_example_scope_boundary_record()

    validation = validate_readme_example_scope_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_example_scope_structural_map_without_benchmark_certification"
    )
    assert boundary["schema"] == README_EXAMPLE_SCOPE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["readme_path"] == "README.md"
    assert boundary["example_scope_sidecar_path"] == "papers/example_benchmark_scope.json"
    assert validation.readme_marker_count == 13
    assert validation.missing_readme_marker_count == 0
    assert validation.evidence_anchor_count == 21
    assert validation.missing_evidence_anchor_count == 0
    assert validation.scope_record_count == 8
    assert validation.comparable_problem_count == 0
    assert boundary["smoke_problem_ids"] == [
        "hello_world",
        "sorting",
        "workspace_math",
        "embedded_evaluate_math",
        "matrix_multiplication",
        "circle_packing",
    ]
    assert boundary["benchmark_problem_ids"] == [
        "sorting_network_8",
        "sorting_network_9",
    ]
    assert boundary["comparable_problem_ids"] == []
    assert boundary["missing_readme_marker_records"] == []
    assert boundary["missing_evidence_anchor_records"] == []
    assert boundary["missing_example_paths"] == []
    assert boundary["example_path_status"] == "all_example_scope_paths_present"
    assert boundary["readme_example_scope_map_status"] == (
        "readme_example_scope_structural_map_present"
    )
    assert boundary["missing_evidence"] == {
        "semantic_scope_claim_verifier": "not_recorded_locally",
        "runtime_scope_metadata_comparison": "not_recorded_locally",
        "paper_comparable_certification_gate": "not_recorded_locally",
        "new_example_surface_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "README Example Scope markers" in boundary["claim_boundary"]
    assert "paper-comparable certification gates" in boundary["claim_boundary"]


def test_readme_example_scope_boundary_rejects_overclaim_and_drift():
    boundary = readme_example_scope_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "readme_example_scope_certified"
    boundary["readme_marker_count"] = 0
    boundary["missing_readme_marker_count"] = 1
    boundary["missing_readme_marker_records"] = [boundary["readme_marker_records"][0]]
    boundary["readme_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["evidence_anchor_count"] = 0
    boundary["missing_evidence_anchor_count"] = 1
    boundary["missing_evidence_anchor_records"] = [
        boundary["evidence_anchor_records"][0]
    ]
    boundary["evidence_anchor_records"][0]["marker_status"] = "marker_missing"
    boundary["scope_registry_validation_status"] = "scope_registry_invalid"
    boundary["comparable_problem_ids"] = ["hello_world"]
    boundary["comparable_problem_count"] = 1
    boundary["missing_example_paths"] = ["libreevolve/problems/examples/hello_world"]
    boundary["example_path_status"] = "missing_example_scope_paths"
    boundary["readme_example_scope_map_status"] = (
        "readme_example_scope_structural_map_incomplete"
    )
    boundary["missing_evidence"]["paper_comparable_certification_gate"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_example_scope_markers"]

    validation = validate_readme_example_scope_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_readme_marker_count" in codes
    assert "invalid_missing_readme_marker_count" in codes
    assert "invalid_missing_readme_marker_records" in codes
    assert "invalid_readme_marker_records" in codes
    assert "missing_readme_example_scope_marker" in codes
    assert "invalid_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_records" in codes
    assert "invalid_evidence_anchor_records" in codes
    assert "missing_readme_example_scope_evidence_anchor" in codes
    assert "invalid_scope_registry_validation_status" in codes
    assert "paper_comparable_overclaim" in codes
    assert "missing_example_scope_path" in codes
    assert "invalid_readme_example_scope_map_status" in codes
    assert "invalid_missing_evidence_paper_comparable_certification_gate" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_example_scope_boundary_summary_reports_shape():
    summary = render_readme_example_scope_boundary_summary(
        readme_example_scope_boundary_record()
    )

    assert "README Example Scope boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_example_scope_structural_map_without_benchmark_certification |"
        in summary
    )
    assert "| readme_marker_count | 13 |" in summary
    assert "| missing_readme_marker_count | 0 |" in summary
    assert "| evidence_anchor_count | 21 |" in summary
    assert "| missing_evidence_anchor_count | 0 |" in summary
    assert "| scope_record_count | 8 |" in summary
    assert "| comparable_problem_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
