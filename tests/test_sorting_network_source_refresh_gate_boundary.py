from libreevolve.problems.benchmarks.sorting_network_source_refresh_gate_boundary import (
    SORTING_NETWORK_SOURCE_REFRESH_GATE_BOUNDARY_SCHEMA,
    render_sorting_network_source_refresh_gate_boundary_summary,
    sorting_network_source_refresh_gate_boundary_record,
    validate_sorting_network_source_refresh_gate_boundary,
)


def test_sorting_network_source_refresh_gate_boundary_accepts_record():
    boundary = sorting_network_source_refresh_gate_boundary_record()

    validation = validate_sorting_network_source_refresh_gate_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "deterministic_source_refresh_gate_recorded_with_archived_drift_outcome"
    )
    assert validation.script_artifact_checked is False
    assert validation.deterministic_gate_checked is False
    assert validation.source_count == 5
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == SORTING_NETWORK_SOURCE_REFRESH_GATE_BOUNDARY_SCHEMA
    assert boundary["source_snapshot_metadata_sidecar"] == (
        "papers/sorting_network_source_snapshot_boundary.json"
    )
    assert boundary["archived_outcome_artifact"]["path"] == (
        "papers/sorting_network_source_refresh_run_2026-06-18.json"
    )
    assert boundary["expected_report_schema"] == (
        "libreevolve.sorting_network_source_refresh_gate_report.v1"
    )
    assert "source-drift triage resolution" in boundary["claim_boundary"]
    assert "scheduled CI refresh-run history" in boundary["claim_boundary"]


def test_sorting_network_source_refresh_gate_boundary_rejects_drift_and_overclaim():
    boundary = sorting_network_source_refresh_gate_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "live_refresh_certified"
    boundary["script_artifact"]["sha256"] = "0" * 64
    boundary["archived_outcome_artifact"]["result"] = "fresh"
    boundary["expected_source_ids"] = ["codish_arxiv"]
    boundary["missing_evidence"]["scheduled_ci_refresh_run_history"] = "recorded"

    validation = validate_sorting_network_source_refresh_gate_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_script_artifact_sha256" in codes
    assert "invalid_archived_outcome_artifact_result" in codes
    assert "invalid_expected_source_ids" in codes
    assert "invalid_missing_evidence_scheduled_ci_refresh_run_history" in codes


def test_render_sorting_network_source_refresh_gate_boundary_summary_reports_shape():
    summary = render_sorting_network_source_refresh_gate_boundary_summary(
        sorting_network_source_refresh_gate_boundary_record()
    )

    assert "Sorting-network source refresh-gate boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | deterministic_source_refresh_gate_recorded_with_archived_drift_outcome |" in summary
    assert "| source_count | 5 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
