from libreevolve.problems.benchmarks.alphaevolve_metadata_extraction_script_boundary import (
    ALPHAEVOLVE_METADATA_EXTRACTION_SCRIPT_BOUNDARY_SCHEMA,
    alphaevolve_metadata_extraction_script_boundary_record,
    render_alphaevolve_metadata_extraction_script_boundary_summary,
    validate_alphaevolve_metadata_extraction_script_boundary,
)


def test_alphaevolve_metadata_extraction_script_boundary_accepts_record():
    boundary = alphaevolve_metadata_extraction_script_boundary_record()

    validation = validate_alphaevolve_metadata_extraction_script_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "offline_metadata_extraction_script_recorded_without_refresh_gate"
    )
    assert validation.artifact_count == 5
    assert validation.missing_evidence_count == 1
    assert boundary["schema"] == ALPHAEVOLVE_METADATA_EXTRACTION_SCRIPT_BOUNDARY_SCHEMA
    assert (
        boundary["script_artifact"]["path"]
        == "libreevolve/tools/alphaevolve_source_metadata.py"
    )


def test_alphaevolve_metadata_extraction_script_boundary_rejects_overclaim():
    boundary = alphaevolve_metadata_extraction_script_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "metadata_refresh_gate_ready"
    boundary["script_artifact"]["sha256"] = "0" * 64
    boundary["missing_evidence"]["automated_live_refresh_ci_gate"] = "recorded"

    validation = validate_alphaevolve_metadata_extraction_script_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_script_artifact_sha256" in codes
    assert "invalid_missing_evidence_automated_live_refresh_ci_gate" in codes


def test_alphaevolve_metadata_extraction_script_boundary_validates_repo_file():
    validation = validate_alphaevolve_metadata_extraction_script_boundary(
        "papers/alphaevolve_metadata_extraction_script_boundary.json"
    )

    assert validation.ok is True
    assert validation.script_artifact_checked is True
    assert validation.extraction_report_checked is True


def test_render_alphaevolve_metadata_extraction_script_boundary_summary_reports_shape():
    summary = render_alphaevolve_metadata_extraction_script_boundary_summary(
        alphaevolve_metadata_extraction_script_boundary_record()
    )

    assert "AlphaEvolve metadata extraction-script boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | offline_metadata_extraction_script_recorded_without_refresh_gate |"
        in summary
    )
    assert "| artifact_count | 5 |" in summary
    assert "| missing_evidence_count | 1 |" in summary
