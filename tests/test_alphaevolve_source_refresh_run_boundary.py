from libreevolve.problems.benchmarks.alphaevolve_source_refresh_run_boundary import (
    ALPHAEVOLVE_SOURCE_REFRESH_RUN_BOUNDARY_SCHEMA,
    alphaevolve_source_refresh_run_boundary_record,
    render_alphaevolve_source_refresh_run_boundary_summary,
    validate_alphaevolve_source_refresh_run_boundary,
)


def test_alphaevolve_source_refresh_run_boundary_accepts_record():
    boundary = alphaevolve_source_refresh_run_boundary_record()

    validation = validate_alphaevolve_source_refresh_run_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "manual_live_source_refresh_run_archived_without_scheduled_history"
    )
    assert validation.source_count == 6
    assert validation.missing_evidence_count == 1
    assert boundary["schema"] == ALPHAEVOLVE_SOURCE_REFRESH_RUN_BOUNDARY_SCHEMA
    assert boundary["run_report"]["mode"] == "live_network"


def test_alphaevolve_source_refresh_run_boundary_rejects_overclaim_and_drift():
    boundary = alphaevolve_source_refresh_run_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "source_refresh_run_publication_ready"
    boundary["run_report"]["checks"][0]["observed"]["sha256"] = "0" * 64
    boundary["missing_evidence"]["scheduled_ci_refresh_run_history"] = "recorded"

    validation = validate_alphaevolve_source_refresh_run_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_run_report_sha256" in codes
    assert "invalid_versioned_abstract_observed_sha256" in codes
    assert (
        "invalid_missing_evidence_scheduled_ci_refresh_run_history"
        in codes
    )


def test_alphaevolve_source_refresh_run_boundary_validates_repo_file():
    validation = validate_alphaevolve_source_refresh_run_boundary(
        "papers/alphaevolve_source_refresh_run_2026-06-14.json"
    )

    assert validation.ok is True
    assert validation.script_artifact_checked is True
    assert validation.run_report_checked is True


def test_render_alphaevolve_source_refresh_run_boundary_summary_reports_shape():
    summary = render_alphaevolve_source_refresh_run_boundary_summary(
        alphaevolve_source_refresh_run_boundary_record()
    )

    assert "AlphaEvolve source refresh-run boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | manual_live_source_refresh_run_archived_without_scheduled_history |"
        in summary
    )
    assert "| source_count | 6 |" in summary
    assert "| missing_evidence_count | 1 |" in summary
