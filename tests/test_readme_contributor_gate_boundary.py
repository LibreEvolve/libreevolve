from libreevolve.problems.benchmarks.readme_contributor_gate_boundary import (
    README_CONTRIBUTOR_GATE_BOUNDARY_SCHEMA,
    readme_contributor_gate_boundary_record,
    render_readme_contributor_gate_boundary_summary,
    validate_readme_contributor_gate_boundary,
)


def test_readme_contributor_gate_boundary_accepts_current_static_map():
    boundary = readme_contributor_gate_boundary_record()

    validation = validate_readme_contributor_gate_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_contributor_gate_static_map_without_policy_drift_proof"
    )
    assert boundary["schema"] == README_CONTRIBUTOR_GATE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["readme_path"] == "README.md"
    assert boundary["development_path"] == "docs/development.md"
    assert boundary["precommit_path"] == ".pre-commit-config.yaml"
    assert boundary["secret_scan_path"] == ".secrets.baseline"
    assert boundary["workflow_path"] == ".github/workflows/tests.yml"
    assert validation.readme_marker_count == 10
    assert validation.missing_readme_marker_count == 0
    assert boundary["missing_readme_marker_records"] == []
    assert validation.evidence_anchor_count == 25
    assert validation.missing_evidence_anchor_count == 0
    assert boundary["missing_evidence_anchor_records"] == []
    assert (
        boundary["contributor_gate_map_status"]
        == "readme_contributor_gate_static_map_present"
    )
    assert boundary["missing_evidence"] == {
        "complete_sentence_to_artifact_map": "not_recorded_locally",
        "precommit_drift_gate": "not_recorded_locally",
        "source_boundary_file_change_detector": "not_recorded_locally",
        "semantic_secret_policy_verifier": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "README Contributing markers" in boundary["claim_boundary"]
    assert "pre-commit detect-secrets hook" in boundary["claim_boundary"]
    assert (
        "does not claim a complete sentence-to-artifact map"
        in boundary["claim_boundary"]
    )


def test_readme_contributor_gate_boundary_rejects_overclaim_and_drift():
    boundary = readme_contributor_gate_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "readme_contributor_policy_drift_proof_ready"
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
    boundary["contributor_gate_map_status"] = (
        "readme_contributor_gate_static_map_incomplete"
    )
    boundary["missing_evidence"]["precommit_drift_gate"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_contributing_markers"]

    validation = validate_readme_contributor_gate_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_readme_marker_count" in codes
    assert "invalid_missing_readme_marker_count" in codes
    assert "invalid_missing_readme_marker_records" in codes
    assert "invalid_readme_marker_records" in codes
    assert "missing_readme_contributor_marker" in codes
    assert "invalid_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_records" in codes
    assert "invalid_evidence_anchor_records" in codes
    assert "missing_contributor_gate_evidence_anchor" in codes
    assert "invalid_contributor_gate_map_status" in codes
    assert "invalid_missing_evidence_precommit_drift_gate" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_contributor_gate_boundary_summary_reports_shape():
    summary = render_readme_contributor_gate_boundary_summary(
        readme_contributor_gate_boundary_record()
    )

    assert "README contributor-gate boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_contributor_gate_static_map_without_policy_drift_proof |"
        in summary
    )
    assert "| readme_marker_count | 10 |" in summary
    assert "| missing_readme_marker_count | 0 |" in summary
    assert "| evidence_anchor_count | 25 |" in summary
    assert "| missing_evidence_anchor_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
