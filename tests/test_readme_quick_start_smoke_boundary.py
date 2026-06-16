import json
from pathlib import Path

from click.testing import CliRunner

from libreevolve.cli import cli
from libreevolve.problems.benchmarks.readme_quick_start_smoke_boundary import (
    README_QUICK_START_SMOKE_BOUNDARY_SCHEMA,
    readme_quick_start_smoke_boundary_record,
    render_readme_quick_start_smoke_boundary_summary,
    validate_readme_quick_start_smoke_boundary,
)


def test_readme_quick_start_smoke_boundary_accepts_current_markers():
    boundary = readme_quick_start_smoke_boundary_record()

    validation = validate_readme_quick_start_smoke_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_quick_start_smoke_test_recorded_without_ci_matrix"
    )
    assert boundary["schema"] == README_QUICK_START_SMOKE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["run_command"] == (
        "py -3.12 -m libreevolve run libreevolve/problems/examples/sorting "
        "--run-name readme_smoke_sorting --max-llm-calls 0 --overwrite"
    )
    assert boundary["show_command"] == (
        "py -3.12 -m libreevolve show runs/readme_smoke_sorting"
    )
    assert validation.readme_marker_count == 6
    assert validation.missing_readme_marker_count == 0
    assert validation.missing_test_marker_count == 0
    assert boundary["expected_stop_reason"] == "max_llm_calls"
    assert boundary["expected_best_fitness"] == "1.000000"
    assert boundary["missing_evidence"] == {
        "ci_job_integration": "not_recorded_locally",
        "cross_platform_shell_transcript": "not_recorded_locally",
        "fresh_checkout_transcript": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "README Quick Start no-provider command markers" in boundary["claim_boundary"]


def test_readme_quick_start_smoke_boundary_rejects_overclaim_and_drift():
    boundary = readme_quick_start_smoke_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "readme_quick_start_ci_matrix_verified"
    boundary["missing_readme_marker_count"] = 1
    boundary["missing_readme_marker_records"] = [boundary["readme_marker_records"][0]]
    boundary["readme_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["missing_test_marker_count"] = 1
    boundary["missing_test_marker_records"] = [boundary["test_marker_records"][0]]
    boundary["test_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_quick_start_command_markers"]

    validation = validate_readme_quick_start_smoke_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_readme_marker_count" in codes
    assert "invalid_missing_readme_marker_records" in codes
    assert "invalid_readme_marker_records" in codes
    assert "missing_readme_quick_start_marker" in codes
    assert "invalid_missing_test_marker_count" in codes
    assert "invalid_missing_test_marker_records" in codes
    assert "invalid_test_marker_records" in codes
    assert "missing_smoke_test_marker" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_quick_start_smoke_boundary_summary_reports_shape():
    summary = render_readme_quick_start_smoke_boundary_summary(
        readme_quick_start_smoke_boundary_record()
    )

    assert "README quick-start smoke boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_quick_start_smoke_test_recorded_without_ci_matrix |"
        in summary
    )
    assert "| readme_marker_count | 6 |" in summary
    assert "| missing_readme_marker_count | 0 |" in summary
    assert "| missing_test_marker_count | 0 |" in summary
    assert "| missing_evidence_count | 4 |" in summary


def test_readme_quick_start_smoke_executes_documented_no_provider_path():
    runner = CliRunner()
    run_result = runner.invoke(
        cli,
        [
            "run",
            "libreevolve/problems/examples/sorting",
            "--run-name",
            "readme_smoke_sorting",
            "--max-llm-calls",
            "0",
            "--overwrite",
        ],
    )

    assert run_result.exit_code == 0, run_result.output
    assert "Running 1000 generations on 'readme_smoke_sorting'" in run_result.output
    assert "Best fitness: 1.000000" in run_result.output
    assert "Best program saved to:" in run_result.output
    assert "Best workspace saved to:" in run_result.output

    manifest_path = Path("runs/readme_smoke_sorting/manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["config"]["max_llm_calls"] == 0
    assert manifest["runtime"]["stop_reason"] == "max_llm_calls"
    assert manifest["runtime"]["llm_scheduler"]["status"] == "not_initialized"

    show_result = runner.invoke(cli, ["show", "runs/readme_smoke_sorting"])

    assert show_result.exit_code == 0, show_result.output
    assert "Run status:     completed (stop_reason: max_llm_calls)" in show_result.output
    assert "Selection:      archive-retained valid" in show_result.output
    assert "Best fitness:   1.000000" in show_result.output
    assert 'Metrics:        {"accuracy": 1.0, "is_valid": true}' in show_result.output
