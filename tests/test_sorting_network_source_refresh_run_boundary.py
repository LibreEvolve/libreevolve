from libreevolve.problems.benchmarks.sorting_network_source_refresh_run_boundary import (
    SORTING_NETWORK_SOURCE_REFRESH_RUN_BOUNDARY_SCHEMA,
    render_sorting_network_source_refresh_run_boundary_summary,
    sorting_network_source_refresh_run_boundary_record,
    validate_sorting_network_source_refresh_run_boundary,
)


def test_sorting_network_source_refresh_run_boundary_accepts_drift_record():
    boundary = sorting_network_source_refresh_run_boundary_record()

    validation = validate_sorting_network_source_refresh_run_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "live_source_refresh_run_archived_with_source_drift"
    assert validation.run_report_checked is True
    assert validation.source_count == 5
    assert validation.drift_count == 1
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == SORTING_NETWORK_SOURCE_REFRESH_RUN_BOUNDARY_SCHEMA
    assert boundary["run_report"]["ok"] is False
    assert boundary["drift_summary"]["drift_source_ids"] == ["codish_publication"]
    assert boundary["source_drift_triage_sidecar"] == (
        "papers/sorting_network_source_drift_triage_boundary.json"
    )
    assert boundary["source_drift_triage_status"] == (
        "full_page_hash_unstable_markers_present"
    )
    drifted = boundary["run_report"]["checks"][-1]
    assert drifted["source_id"] == "codish_publication"
    assert drifted["issues"] == ["bytes_drift", "sha256_drift"]


def test_sorting_network_source_refresh_run_boundary_rejects_overclaim_and_drift():
    boundary = sorting_network_source_refresh_run_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "source_fresh"
    boundary["run_report"]["ok"] = True
    boundary["drift_summary"]["triage_required"] = False
    boundary["source_drift_triage_sidecar"] = "missing.json"
    boundary["source_drift_triage_status"] = "untriaged"
    boundary["missing_evidence"]["stable_normalized_source_snapshot"] = "recorded"

    validation = validate_sorting_network_source_refresh_run_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_run_report" in codes
    assert "invalid_run_report_ok" in codes
    assert "invalid_drift_summary" in codes
    assert "invalid_source_drift_triage_sidecar" in codes
    assert "invalid_source_drift_triage_status" in codes
    assert "invalid_missing_evidence_stable_normalized_source_snapshot" in codes


def test_render_sorting_network_source_refresh_run_boundary_summary_reports_shape():
    summary = render_sorting_network_source_refresh_run_boundary_summary(
        sorting_network_source_refresh_run_boundary_record()
    )

    assert "Sorting-network source refresh-run boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | live_source_refresh_run_archived_with_source_drift |" in summary
    assert "| source_count | 5 |" in summary
    assert "| drift_count | 1 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
