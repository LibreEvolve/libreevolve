from libreevolve.problems.benchmarks.readme_license_boundary import (
    README_LICENSE_BOUNDARY_SCHEMA,
    readme_license_boundary_record,
    render_readme_license_boundary_summary,
    validate_readme_license_boundary,
)


def test_readme_license_boundary_accepts_current_static_map():
    boundary = readme_license_boundary_record()

    validation = validate_readme_license_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_license_static_consistency_with_rights_surface_map_without_rights_drift_gate"
    )
    assert boundary["schema"] == README_LICENSE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["readme_path"] == "README.md"
    assert boundary["license_path"] == "LICENSE"
    assert boundary["pyproject_path"] == "pyproject.toml"
    assert boundary["source_rights_path"] == "papers/source_rights.json"
    assert validation.readme_marker_count == 2
    assert validation.missing_readme_marker_count == 0
    assert boundary["missing_readme_marker_records"] == []
    assert boundary["project_license_id"] == "MIT"
    assert boundary["pyproject_license_id"] == "MIT"
    assert boundary["source_rights_summary"] == {
        "summary_status": "source_rights_summary_recorded",
        "source_rights_policy": "paper_derived_artifacts_must_carry_source_rights_and_reproduction_policy",
        "source_rights_count": 1,
        "artifact_classes": ["excerpt", "table", "figure", "quote", "appendix_claim"],
        "claim_surfaces": [
            "README.md",
            "ROADMAP.md",
            "papers/README.md",
            "docs/todo/code.md",
            "docs/todo/papers.md",
            "docs/todo/readme.md",
            "docs/todo/roadmap.md",
        ],
        "reproduction_policy": "third_party_paper_source_rights_require_separate_review_before_reproduction",
        "must_separate_from_libreevolve_mit_license": True,
        "publication_ready_without_rights_review": False,
    }
    assert validation.rights_surface_map_count == 7
    assert (
        boundary["rights_surface_map_status"]
        == "all_source_rights_claim_surfaces_mapped"
    )
    assert boundary["rights_surface_map_records"][0]["claim_surface"] == "README.md"
    assert boundary["rights_surface_map_records"][0]["map_status"] == "mapped"
    assert validation.evidence_anchor_count == 12
    assert validation.missing_evidence_anchor_count == 0
    assert boundary["missing_evidence_anchor_records"] == []
    assert boundary["readme_license_map_status"] == "readme_license_static_map_present"
    assert boundary["missing_evidence"] == {
        "packaged_license_file_verification": "not_recorded_locally",
        "license_metadata_drift_gate": "not_recorded_locally",
        "paper_rights_policy_drift_gate": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "README License heading and MIT sentence" in boundary["claim_boundary"]
    assert "third-party paper/source rights separate" in boundary["claim_boundary"]
    assert (
        "bounded third-party source-rights claim-surface map"
        in boundary["claim_boundary"]
    )
    assert (
        "does not claim packaged license-file verification"
        in boundary["claim_boundary"]
    )


def test_readme_license_boundary_rejects_overclaim_and_drift():
    boundary = readme_license_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "readme_license_rights_drift_gate_ready"
    boundary["readme_marker_count"] = 0
    boundary["missing_readme_marker_count"] = 1
    boundary["missing_readme_marker_records"] = [boundary["readme_marker_records"][0]]
    boundary["readme_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["pyproject_license_id"] = "Apache-2.0"
    boundary["rights_surface_map_count"] = 0
    boundary["rights_surface_map_status"] = "source_rights_claim_surface_map_incomplete"
    boundary["rights_surface_map_records"][0]["map_status"] = "missing_policy_field"
    boundary["evidence_anchor_count"] = 0
    boundary["missing_evidence_anchor_count"] = 1
    boundary["missing_evidence_anchor_records"] = [
        boundary["evidence_anchor_records"][0]
    ]
    boundary["evidence_anchor_records"][0]["marker_status"] = "marker_missing"
    boundary["readme_license_map_status"] = "readme_license_static_map_incomplete"
    boundary["missing_evidence"]["license_metadata_drift_gate"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_license_sentence"]

    validation = validate_readme_license_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_readme_marker_count" in codes
    assert "invalid_missing_readme_marker_count" in codes
    assert "invalid_missing_readme_marker_records" in codes
    assert "invalid_readme_marker_records" in codes
    assert "missing_readme_license_marker" in codes
    assert "invalid_pyproject_license_id" in codes
    assert "invalid_rights_surface_map_count" in codes
    assert "invalid_rights_surface_map_records" in codes
    assert "invalid_rights_surface_map_status" in codes
    assert "invalid_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_records" in codes
    assert "invalid_evidence_anchor_records" in codes
    assert "missing_readme_license_evidence_anchor" in codes
    assert "invalid_readme_license_map_status" in codes
    assert "invalid_missing_evidence_license_metadata_drift_gate" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_license_boundary_summary_reports_shape():
    summary = render_readme_license_boundary_summary(readme_license_boundary_record())

    assert "README license boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_license_static_consistency_with_rights_surface_map_without_rights_drift_gate |"
        in summary
    )
    assert "| readme_marker_count | 2 |" in summary
    assert "| missing_readme_marker_count | 0 |" in summary
    assert "| evidence_anchor_count | 12 |" in summary
    assert "| missing_evidence_anchor_count | 0 |" in summary
    assert "| rights_surface_map_count | 7 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
