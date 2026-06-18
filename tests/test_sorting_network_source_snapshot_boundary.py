from libreevolve.problems.benchmarks.sorting_network_source_snapshot_boundary import (
    SORTING_NETWORK_SOURCE_SNAPSHOT_BOUNDARY_SCHEMA,
    render_sorting_network_source_snapshot_boundary_summary,
    sorting_network_source_snapshot_boundary_record,
    validate_sorting_network_source_snapshot_boundary,
)


def test_sorting_network_source_snapshot_boundary_accepts_record():
    boundary = sorting_network_source_snapshot_boundary_record()

    validation = validate_sorting_network_source_snapshot_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "source_snapshot_metadata_recorded_without_full_body_retention"
    assert validation.snapshot_count == 5
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == SORTING_NETWORK_SOURCE_SNAPSHOT_BOUNDARY_SCHEMA
    assert boundary["source_snapshots"]["zero_one_clrs"]["http_status"] == 200
    assert boundary["source_snapshots"]["dobbelaere_list"]["response_bytes"] == 70392
    assert boundary["source_snapshots"]["codish_publication"]["response_sha256"] == (
        "585198c1225b08f1f2f58cd6cc8f764dd22445b1b88c361619af3313c321b52a"
    )
    assert boundary["source_refresh_gate_sidecar"] == (
        "papers/sorting_network_source_refresh_gate_boundary.json"
    )
    assert boundary["latest_source_refresh_run_sidecar"] == (
        "papers/sorting_network_source_refresh_run_2026-06-18.json"
    )
    assert boundary["latest_source_refresh_status"] == "source_metadata_drift_detected"
    assert boundary["source_drift_triage_sidecar"] == (
        "papers/sorting_network_source_drift_triage_boundary.json"
    )
    assert boundary["source_drift_triage_status"] == (
        "full_page_hash_unstable_markers_present"
    )
    assert boundary["normalized_marker_snapshot_sidecar"] == (
        "papers/sorting_network_normalized_marker_snapshot_boundary.json"
    )
    assert boundary["normalized_marker_snapshot_status"] == "recorded"
    metadata_updates = boundary["source_snapshot_metadata_updates"]["codish_publication"]
    assert metadata_updates["freshness_basis"] == "normalized_marker_snapshot"
    assert metadata_updates["normalized_marker_snapshot_sidecar"] == (
        "papers/sorting_network_normalized_marker_snapshot_boundary.json"
    )
    assert metadata_updates["normalized_payload_sha256"] == (
        "5e58af11168018d97f35d0b5c7d6a31d11fbde8f646d2b371e722badafe6d27c"
    )
    assert metadata_updates["full_page_snapshot_status"] == (
        "historical_drift_evidence_not_freshness_basis"
    )
    assert "full raw source-body retention" in boundary["claim_boundary"]


def test_sorting_network_source_snapshot_boundary_rejects_drift_and_overclaim():
    boundary = sorting_network_source_snapshot_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "source_claim_ready"
    boundary["retrieved_on"] = "2026-01-01"
    boundary["source_refresh_gate_sidecar"] = "missing.json"
    boundary["latest_source_refresh_run_sidecar"] = "missing.json"
    boundary["latest_source_refresh_status"] = "fresh"
    boundary["source_drift_triage_sidecar"] = "missing.json"
    boundary["source_drift_triage_status"] = "untriaged"
    boundary["normalized_marker_snapshot_sidecar"] = "missing.json"
    boundary["normalized_marker_snapshot_status"] = "missing"
    boundary["source_snapshot_metadata_updates"]["codish_publication"]["freshness_basis"] = (
        "full_page_sha256"
    )
    boundary["source_snapshots"]["codish_arxiv"]["response_sha256"] = "0" * 64
    boundary["source_snapshots"].pop("zero_one_clrs")
    boundary["missing_evidence"]["scheduled_ci_refresh_run_history"] = "recorded"

    validation = validate_sorting_network_source_snapshot_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_retrieved_on" in codes
    assert "invalid_source_refresh_gate_sidecar" in codes
    assert "invalid_latest_source_refresh_run_sidecar" in codes
    assert "invalid_latest_source_refresh_status" in codes
    assert "invalid_source_drift_triage_sidecar" in codes
    assert "invalid_source_drift_triage_status" in codes
    assert "invalid_normalized_marker_snapshot_sidecar" in codes
    assert "invalid_normalized_marker_snapshot_status" in codes
    assert "invalid_source_snapshot_metadata_updates" in codes
    assert "invalid_source_snapshot_ids" in codes
    assert "missing_source_snapshot_zero_one_clrs" in codes
    assert "invalid_source_snapshot_codish_arxiv_response_sha256" in codes
    assert "invalid_missing_evidence_scheduled_ci_refresh_run_history" in codes


def test_render_sorting_network_source_snapshot_boundary_summary_reports_shape():
    summary = render_sorting_network_source_snapshot_boundary_summary(
        sorting_network_source_snapshot_boundary_record()
    )

    assert "Sorting-network source snapshot boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | source_snapshot_metadata_recorded_without_full_body_retention |" in summary
    assert "| snapshot_count | 5 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
