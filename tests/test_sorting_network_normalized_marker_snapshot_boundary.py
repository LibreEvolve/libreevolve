from libreevolve.problems.benchmarks.sorting_network_normalized_marker_snapshot_boundary import (
    SORTING_NETWORK_NORMALIZED_MARKER_SNAPSHOT_BOUNDARY_SCHEMA,
    render_sorting_network_normalized_marker_snapshot_boundary_summary,
    sorting_network_normalized_marker_snapshot_boundary_record,
    validate_sorting_network_normalized_marker_snapshot_boundary,
)


def test_sorting_network_normalized_marker_snapshot_boundary_accepts_record():
    boundary = sorting_network_normalized_marker_snapshot_boundary_record()

    validation = validate_sorting_network_normalized_marker_snapshot_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "codish_publication_normalized_marker_snapshot_recorded"
    assert validation.marker_count == 5
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == SORTING_NETWORK_NORMALIZED_MARKER_SNAPSHOT_BOUNDARY_SCHEMA
    assert boundary["normalized_payload_bytes"] == 350
    assert boundary["normalized_payload_sha256"] == (
        "5e58af11168018d97f35d0b5c7d6a31d11fbde8f646d2b371e722badafe6d27c"
    )
    assert boundary["normalized_payload"]["markers"]["target_comparators"] == "25"


def test_sorting_network_normalized_marker_snapshot_boundary_rejects_overclaim_and_drift():
    boundary = sorting_network_normalized_marker_snapshot_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "source_fresh"
    boundary["normalized_payload"]["markers"]["target_comparators"] = "24"
    boundary["missing_evidence"]["updated_source_snapshot_metadata"] = "recorded"

    validation = validate_sorting_network_normalized_marker_snapshot_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_normalized_payload" in codes
    assert "normalized_payload_digest_mismatch" in codes
    assert "invalid_missing_evidence_updated_source_snapshot_metadata" in codes


def test_render_sorting_network_normalized_marker_snapshot_boundary_summary_reports_shape():
    summary = render_sorting_network_normalized_marker_snapshot_boundary_summary(
        sorting_network_normalized_marker_snapshot_boundary_record()
    )

    assert "Sorting-network normalized marker snapshot boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | codish_publication_normalized_marker_snapshot_recorded |" in summary
    assert "| marker_count | 5 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
