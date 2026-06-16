from libreevolve.problems.benchmarks.readme_paper_cache_rehydrate_boundary import (
    README_PAPER_CACHE_REHYDRATE_BOUNDARY_SCHEMA,
    readme_paper_cache_rehydrate_boundary_record,
    render_readme_paper_cache_rehydrate_boundary_summary,
    validate_readme_paper_cache_rehydrate_boundary,
)


def test_readme_paper_cache_rehydrate_boundary_accepts_current_markers():
    boundary = readme_paper_cache_rehydrate_boundary_record()

    validation = validate_readme_paper_cache_rehydrate_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_rehydrate_cli_and_test_markers_without_clean_checkout_transcript"
    )
    assert boundary["schema"] == README_PAPER_CACHE_REHYDRATE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["readme_rehydrate_command"] == (
        "py -3.12 -m libreevolve.tools.paper_manifest --rehydrate"
    )
    assert validation.manifest_row_count == 53
    assert validation.missing_marker_count == 0
    assert boundary["missing_marker_records"] == []
    assert boundary["rehydrate_marker_status"] == "readme_rehydrate_cli_and_tests_present"
    assert boundary["missing_evidence"] == {
        "clean_checkout_absent_cache_transcript": "not_recorded_locally",
        "network_outcome_matrix": "not_recorded_locally",
        "hash_verification_transcript": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "redacted network-failure test" in boundary["claim_boundary"]


def test_readme_paper_cache_rehydrate_boundary_rejects_overclaim_and_marker_drift():
    boundary = readme_paper_cache_rehydrate_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "clean_checkout_rehydrate_transcript_ready"
    boundary["manifest_row_count"] = 0
    boundary["missing_marker_count"] = 1
    boundary["missing_marker_records"] = [boundary["marker_records"][0]]
    boundary["marker_records"][0]["marker_status"] = "marker_missing"
    boundary["rehydrate_marker_status"] = "readme_rehydrate_cli_and_tests_incomplete"
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_rehydrate_command"]

    validation = validate_readme_paper_cache_rehydrate_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_manifest_row_count" in codes
    assert "invalid_missing_marker_count" in codes
    assert "invalid_missing_marker_records" in codes
    assert "invalid_marker_records" in codes
    assert "missing_manifest_rows" in codes
    assert "missing_rehydrate_marker" in codes
    assert "invalid_rehydrate_marker_status" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_paper_cache_rehydrate_boundary_summary_reports_shape():
    summary = render_readme_paper_cache_rehydrate_boundary_summary(
        readme_paper_cache_rehydrate_boundary_record()
    )

    assert "README paper-cache rehydrate boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_rehydrate_cli_and_test_markers_without_clean_checkout_transcript |"
        in summary
    )
    assert "| manifest_row_count | 53 |" in summary
    assert "| missing_marker_count | 0 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
