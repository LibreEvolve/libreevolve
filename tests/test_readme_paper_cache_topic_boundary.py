from libreevolve.problems.benchmarks.readme_paper_cache_topic_boundary import (
    README_PAPER_CACHE_TOPIC_BOUNDARY_SCHEMA,
    readme_paper_cache_topic_boundary_record,
    render_readme_paper_cache_topic_boundary_summary,
    validate_readme_paper_cache_topic_boundary,
)


def test_readme_paper_cache_topic_boundary_accepts_current_markers():
    boundary = readme_paper_cache_topic_boundary_record()

    validation = validate_readme_paper_cache_topic_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_paper_cache_topic_markers_without_row_level_taxonomy"
    )
    assert boundary["schema"] == README_PAPER_CACHE_TOPIC_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert validation.manifest_row_count == 53
    assert validation.status_row_count == 53
    assert boundary["manifest_status"] == "manifest_and_status_rows_aligned"
    assert validation.topic_family_count == 4
    assert validation.missing_marker_count == 0
    assert boundary["missing_marker_records"] == []
    assert boundary["missing_topic_family_records"] == []
    topic_counts = {
        record["topic_family"]: record["row_signal_count"]
        for record in boundary["topic_family_records"]
    }
    assert topic_counts["llm_guided_evolution"] >= 1
    assert topic_counts["program_synthesis"] >= 1
    assert topic_counts["quality_diversity"] >= 1
    assert topic_counts["related_benchmarks"] >= 1
    assert boundary["topic_marker_status"] == "readme_paper_cache_topic_markers_present"
    assert boundary["missing_evidence"] == {
        "row_level_topic_taxonomy": "not_recorded_locally",
        "topic_taxonomy_reviewer_signoff": "not_recorded_locally",
        "topic_phrase_semantic_verifier": "not_recorded_locally",
        "new_paper_out_of_scope_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "bounded heuristic topic-family signals" in boundary["claim_boundary"]


def test_readme_paper_cache_topic_boundary_rejects_overclaim_and_drift():
    boundary = readme_paper_cache_topic_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "row_level_topic_taxonomy_ready"
    boundary["manifest_row_count"] = 52
    boundary["manifest_status"] = "manifest_and_status_rows_misaligned"
    boundary["missing_marker_count"] = 1
    boundary["missing_marker_records"] = [boundary["marker_records"][0]]
    boundary["marker_records"][0]["marker_status"] = "marker_missing"
    boundary["missing_topic_family_count"] = 1
    boundary["missing_topic_family_records"] = [boundary["topic_family_records"][0]]
    boundary["topic_family_records"][0]["row_signal_count"] = 0
    boundary["topic_marker_status"] = "readme_paper_cache_topic_markers_incomplete"
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_topic_sentence"]

    validation = validate_readme_paper_cache_topic_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_manifest_row_count" in codes
    assert "invalid_manifest_status" in codes
    assert "invalid_missing_marker_count" in codes
    assert "invalid_missing_marker_records" in codes
    assert "invalid_marker_records" in codes
    assert "invalid_missing_topic_family_count" in codes
    assert "invalid_missing_topic_family_records" in codes
    assert "invalid_topic_family_records" in codes
    assert "manifest_status_row_count_mismatch" in codes
    assert "missing_topic_marker" in codes
    assert "missing_topic_family_signal" in codes
    assert "invalid_topic_marker_status" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_paper_cache_topic_boundary_summary_reports_shape():
    summary = render_readme_paper_cache_topic_boundary_summary(
        readme_paper_cache_topic_boundary_record()
    )

    assert "README paper-cache topic boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_paper_cache_topic_markers_without_row_level_taxonomy |"
        in summary
    )
    assert "| manifest_row_count | 53 |" in summary
    assert "| status_row_count | 53 |" in summary
    assert "| topic_family_count | 4 |" in summary
    assert "| missing_marker_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
