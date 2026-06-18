from libreevolve.problems.benchmarks.sorting_network_source_drift_triage_boundary import (
    SORTING_NETWORK_SOURCE_DRIFT_TRIAGE_BOUNDARY_SCHEMA,
    render_sorting_network_source_drift_triage_boundary_summary,
    sorting_network_source_drift_triage_boundary_record,
    validate_sorting_network_source_drift_triage_boundary,
)


def test_sorting_network_source_drift_triage_boundary_accepts_record():
    boundary = sorting_network_source_drift_triage_boundary_record()

    validation = validate_sorting_network_source_drift_triage_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "codish_publication_hash_drift_triaged_as_dynamic_source"
    assert validation.marker_count == 5
    assert validation.repeated_fetch_count == 3
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == SORTING_NETWORK_SOURCE_DRIFT_TRIAGE_BOUNDARY_SCHEMA
    assert boundary["drift_source_id"] == "codish_publication"
    assert boundary["normalized_marker_snapshot_sidecar"] == (
        "papers/sorting_network_normalized_marker_snapshot_boundary.json"
    )
    assert boundary["normalized_marker_snapshot_status"] == "recorded"
    assert boundary["repeated_fetch_probe"]["conclusion"] == (
        "full_page_sha256_unstable_for_same_length_response"
    )
    assert "normalized marker snapshot" in boundary["triage_resolution"]


def test_sorting_network_source_drift_triage_boundary_rejects_overclaim_and_drift():
    boundary = sorting_network_source_drift_triage_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "source_fresh"
    boundary["normalized_marker_snapshot_sidecar"] = "missing.json"
    boundary["normalized_marker_snapshot_status"] = "missing"
    boundary["triage_observation"]["stable_markers_present"] = []
    boundary["repeated_fetch_probe"]["response_sha256"] = ["0" * 64]
    boundary["missing_evidence"]["scheduled_ci_refresh_run_history"] = "recorded"

    validation = validate_sorting_network_source_drift_triage_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_normalized_marker_snapshot_sidecar" in codes
    assert "invalid_normalized_marker_snapshot_status" in codes
    assert "invalid_triage_observation_stable_markers_present" in codes
    assert "invalid_repeated_fetch_probe_response_sha256" in codes
    assert "invalid_missing_evidence_scheduled_ci_refresh_run_history" in codes


def test_render_sorting_network_source_drift_triage_boundary_summary_reports_shape():
    summary = render_sorting_network_source_drift_triage_boundary_summary(
        sorting_network_source_drift_triage_boundary_record()
    )

    assert "Sorting-network source drift triage boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | codish_publication_hash_drift_triaged_as_dynamic_source |" in summary
    assert "| marker_count | 5 |" in summary
    assert "| repeated_fetch_count | 3 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
