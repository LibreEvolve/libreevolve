from libreevolve.problems.benchmarks.backend_guide_contract_drift_boundary import (
    BACKEND_GUIDE_CONTRACT_DRIFT_BOUNDARY_SCHEMA,
    backend_guide_contract_drift_boundary_record,
    render_backend_guide_contract_drift_boundary_summary,
    validate_backend_guide_contract_drift_boundary,
)


def test_backend_guide_contract_drift_boundary_accepts_current_map():
    boundary = backend_guide_contract_drift_boundary_record()

    validation = validate_backend_guide_contract_drift_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "backend_guide_structural_evidence_map_without_semantic_contract_proof"
    )
    assert boundary["schema"] == BACKEND_GUIDE_CONTRACT_DRIFT_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert validation.guide_marker_count == 22
    assert validation.missing_guide_marker_count == 0
    assert validation.evidence_anchor_count == 28
    assert validation.missing_evidence_anchor_count == 0
    assert boundary["backend_guide_contract_map_status"] == (
        "backend_guide_structural_evidence_map_present"
    )
    assert boundary["missing_guide_marker_records"] == []
    assert boundary["missing_evidence_anchor_records"] == []
    assert boundary["missing_evidence"] == {
        "semantic_backend_claim_verifier": "not_recorded_locally",
        "per_constructor_field_evidence_map": "not_recorded_locally",
        "per_telemetry_field_evidence_map": "not_recorded_locally",
        "backend_docs_ci_drift_gate": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "docs/backends.md section and claim markers" in boundary["claim_boundary"]


def test_backend_guide_contract_drift_boundary_rejects_overclaim_and_drift():
    boundary = backend_guide_contract_drift_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "backend_guide_semantic_contract_verified"
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
    boundary["backend_guide_contract_map_status"] = (
        "backend_guide_structural_evidence_map_incomplete"
    )
    boundary["missing_evidence"]["semantic_backend_claim_verifier"] = "recorded"
    boundary["required_evidence_fields"] = ["backend_guide_section_inventory"]

    validation = validate_backend_guide_contract_drift_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_guide_marker_count" in codes
    assert "invalid_missing_guide_marker_count" in codes
    assert "invalid_missing_guide_marker_records" in codes
    assert "invalid_guide_marker_records" in codes
    assert "invalid_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_records" in codes
    assert "invalid_evidence_anchor_records" in codes
    assert "missing_backend_guide_marker" in codes
    assert "missing_backend_evidence_anchor" in codes
    assert "invalid_backend_guide_contract_map_status" in codes
    assert "invalid_missing_evidence_semantic_backend_claim_verifier" in codes
    assert "missing_required_evidence_field" in codes


def test_render_backend_guide_contract_drift_boundary_summary_reports_shape():
    summary = render_backend_guide_contract_drift_boundary_summary(
        backend_guide_contract_drift_boundary_record()
    )

    assert "Backend guide contract drift boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | backend_guide_structural_evidence_map_without_semantic_contract_proof |"
        in summary
    )
    assert "| guide_marker_count | 22 |" in summary
    assert "| missing_guide_marker_count | 0 |" in summary
    assert "| evidence_anchor_count | 28 |" in summary
    assert "| missing_evidence_anchor_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
