from libreevolve.problems.benchmarks.problem_format_loader_contract_boundary import (
    PROBLEM_FORMAT_LOADER_CONTRACT_BOUNDARY_SCHEMA,
    problem_format_loader_contract_boundary_record,
    render_problem_format_loader_contract_boundary_summary,
    validate_problem_format_loader_contract_boundary,
)


def test_problem_format_loader_contract_boundary_accepts_current_map():
    boundary = problem_format_loader_contract_boundary_record()

    validation = validate_problem_format_loader_contract_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "problem_format_structural_map_without_semantic_loader_contract_proof"
    )
    assert boundary["schema"] == PROBLEM_FORMAT_LOADER_CONTRACT_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["problem_format_path"] == "docs/problem-format.md"
    assert validation.guide_marker_count == 23
    assert validation.missing_guide_marker_count == 0
    assert validation.evidence_anchor_count == 48
    assert validation.missing_evidence_anchor_count == 0
    assert boundary["missing_guide_marker_records"] == []
    assert boundary["missing_evidence_anchor_records"] == []
    assert boundary["problem_format_contract_map_status"] == (
        "problem_format_structural_loader_contract_map_present"
    )
    assert boundary["missing_evidence"] == {
        "semantic_problem_format_claim_verifier": "not_recorded_locally",
        "per_manifest_key_executable_trace": "not_recorded_locally",
        "problem_format_docs_ci_drift_gate": "not_recorded_locally",
        "new_problem_surface_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "docs/problem-format.md section and claim markers" in boundary["claim_boundary"]
    assert "loader/config/evaluator source anchors" in boundary["claim_boundary"]


def test_problem_format_loader_contract_boundary_rejects_overclaim_and_drift():
    boundary = problem_format_loader_contract_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "semantic_problem_format_loader_contract_verified"
    boundary["guide_marker_count"] = 0
    boundary["missing_guide_marker_count"] = 1
    boundary["missing_guide_marker_records"] = [boundary["guide_marker_records"][0]]
    boundary["guide_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["evidence_anchor_count"] = 0
    boundary["missing_evidence_anchor_count"] = 1
    boundary["missing_evidence_anchor_records"] = [
        boundary["evidence_anchor_records"][0]
    ]
    boundary["evidence_anchor_records"][0]["marker_status"] = "marker_missing"
    boundary["problem_format_contract_map_status"] = (
        "problem_format_structural_loader_contract_map_incomplete"
    )
    boundary["missing_evidence"]["semantic_problem_format_claim_verifier"] = "recorded"
    boundary["required_evidence_fields"] = ["problem_format_section_inventory"]

    validation = validate_problem_format_loader_contract_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_guide_marker_count" in codes
    assert "invalid_missing_guide_marker_count" in codes
    assert "invalid_missing_guide_marker_records" in codes
    assert "invalid_guide_marker_records" in codes
    assert "missing_problem_format_guide_marker" in codes
    assert "invalid_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_records" in codes
    assert "invalid_evidence_anchor_records" in codes
    assert "missing_problem_format_evidence_anchor" in codes
    assert "invalid_problem_format_contract_map_status" in codes
    assert (
        "invalid_missing_evidence_semantic_problem_format_claim_verifier"
        in codes
    )
    assert "missing_required_evidence_field" in codes


def test_render_problem_format_loader_contract_boundary_summary_reports_shape():
    summary = render_problem_format_loader_contract_boundary_summary(
        problem_format_loader_contract_boundary_record()
    )

    assert "Problem-format loader contract boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | problem_format_structural_map_without_semantic_loader_contract_proof |"
        in summary
    )
    assert "| guide_marker_count | 23 |" in summary
    assert "| missing_guide_marker_count | 0 |" in summary
    assert "| evidence_anchor_count | 48 |" in summary
    assert "| missing_evidence_anchor_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
