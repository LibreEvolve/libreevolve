from pathlib import Path

from libreevolve.problems.benchmarks.alphaevolve_source_refresh_gate_boundary import (
    ALPHAEVOLVE_SOURCE_REFRESH_GATE_BOUNDARY_SCHEMA,
    alphaevolve_source_refresh_gate_boundary_record,
    render_alphaevolve_source_refresh_gate_boundary_summary,
    validate_alphaevolve_source_refresh_gate_boundary,
)


def test_alphaevolve_source_refresh_gate_boundary_accepts_record():
    boundary = alphaevolve_source_refresh_gate_boundary_record()

    validation = validate_alphaevolve_source_refresh_gate_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "scheduled_live_source_refresh_gate_recorded_without_archived_outcome"
    )
    assert validation.source_count == 6
    assert validation.missing_evidence_count == 2
    assert boundary["schema"] == ALPHAEVOLVE_SOURCE_REFRESH_GATE_BOUNDARY_SCHEMA
    assert (
        boundary["script_artifact"]["path"]
        == "libreevolve/tools/alphaevolve_source_refresh_gate.py"
    )


def test_alphaevolve_source_refresh_gate_boundary_rejects_overclaim():
    boundary = alphaevolve_source_refresh_gate_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "source_refresh_gate_publication_ready"
    boundary["script_artifact"]["sha256"] = "0" * 64
    boundary["workflow_artifact"]["schedule_cron"] = "0 0 * * *"
    boundary["expected_source_ids"] = ["datacite_api"]
    boundary["missing_evidence"]["archived_successful_live_refresh_run"] = "recorded"

    validation = validate_alphaevolve_source_refresh_gate_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_script_artifact_sha256" in codes
    assert "invalid_workflow_artifact_schedule_cron" in codes
    assert "invalid_expected_source_ids" in codes
    assert (
        "invalid_missing_evidence_archived_successful_live_refresh_run"
        in codes
    )


def test_alphaevolve_source_refresh_gate_boundary_validates_repo_files():
    validation = validate_alphaevolve_source_refresh_gate_boundary(
        "papers/alphaevolve_source_refresh_gate_boundary.json"
    )

    assert validation.ok is True
    assert validation.script_artifact_checked is True
    assert validation.workflow_artifact_checked is True
    assert validation.deterministic_gate_checked is True


def test_alphaevolve_source_refresh_gate_boundary_detects_file_drift(tmp_path):
    source_root = Path(__file__).resolve().parents[1]
    script_target = tmp_path / "libreevolve" / "tools" / "alphaevolve_source_refresh_gate.py"
    workflow_target = tmp_path / ".github" / "workflows" / "tests.yml"
    script_target.parent.mkdir(parents=True)
    workflow_target.parent.mkdir(parents=True)
    script_target.write_text("print('drift')\n", encoding="utf-8")
    workflow_target.write_text(
        (source_root / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / "papers" / "alphaevolve_source_refresh_gate_boundary.json"
    sidecar.parent.mkdir()
    sidecar.write_text(
        (source_root / "papers" / "alphaevolve_source_refresh_gate_boundary.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    validation = validate_alphaevolve_source_refresh_gate_boundary(sidecar)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_script_artifact_file_bytes" in codes
    assert "invalid_script_artifact_file_sha256" in codes


def test_render_alphaevolve_source_refresh_gate_boundary_summary_reports_shape():
    summary = render_alphaevolve_source_refresh_gate_boundary_summary(
        alphaevolve_source_refresh_gate_boundary_record()
    )

    assert "AlphaEvolve source refresh-gate boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | scheduled_live_source_refresh_gate_recorded_without_archived_outcome |"
        in summary
    )
    assert "| source_count | 6 |" in summary
    assert "| missing_evidence_count | 2 |" in summary
