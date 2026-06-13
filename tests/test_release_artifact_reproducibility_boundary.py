from libreevolve.problems.benchmarks.release_artifact_reproducibility_boundary import (
    RELEASE_ARTIFACT_REPRODUCIBILITY_BOUNDARY_SCHEMA,
    release_artifact_reproducibility_boundary_record,
    render_release_artifact_reproducibility_boundary_summary,
    validate_release_artifact_reproducibility_boundary,
)


def test_release_artifact_reproducibility_boundary_accepts_editable_boundary():
    boundary = release_artifact_reproducibility_boundary_record()

    validation = validate_release_artifact_reproducibility_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "ci_release_artifact_smoke_available"
    assert validation.required_evidence_field_count == 13
    assert validation.missing_evidence_count == 1
    assert boundary["schema"] == RELEASE_ARTIFACT_REPRODUCIBILITY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["partial_evidence"]["wheel_build_check"] == "ci_smoke"
    assert boundary["partial_evidence"]["sdist_build_check"] == "ci_smoke"
    assert boundary["partial_evidence"]["install_from_wheel_cli_smoke"] == "ci_smoke"
    assert (
        boundary["partial_evidence"]["package_data_inclusion_check"]
        == "complete_libreevolve_package_tree_wheel_and_sdist_inventory"
    )
    assert (
        boundary["partial_evidence"]["release_artifact_provenance"]
        == "ci_dist_artifact_and_source_hash_manifest"
    )
    assert "under the libreevolve package tree" in boundary["claim_boundary"]


def test_release_artifact_reproducibility_boundary_rejects_release_overclaim():
    boundary = release_artifact_reproducibility_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "verified_release_distribution"
    boundary["partial_evidence"]["release_artifact_provenance"] = "signed_release_ready"
    boundary["required_evidence_fields"] = ["pyproject_metadata_recorded"]

    validation = validate_release_artifact_reproducibility_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_partial_evidence_release_artifact_provenance" in codes
    assert "missing_required_evidence_field" in codes


def test_render_release_artifact_reproducibility_boundary_summary_reports_shape():
    summary = render_release_artifact_reproducibility_boundary_summary(
        release_artifact_reproducibility_boundary_record()
    )

    assert "Release artifact reproducibility boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | ci_release_artifact_smoke_available |" in summary
    assert "| required_evidence_field_count | 13 |" in summary
    assert "| missing_evidence_count | 1 |" in summary
