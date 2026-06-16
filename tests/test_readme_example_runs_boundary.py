from click.testing import CliRunner

from libreevolve.cli import cli
from libreevolve.problems.benchmarks.readme_example_runs_boundary import (
    README_EXAMPLE_RUNS_BOUNDARY_SCHEMA,
    readme_example_runs_boundary_record,
    render_readme_example_runs_boundary_summary,
    validate_readme_example_runs_boundary,
)


def test_readme_example_runs_boundary_accepts_current_fixtures():
    boundary = readme_example_runs_boundary_record()

    validation = validate_readme_example_runs_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "example_runs_readme_structural_fixture_map_without_reproducibility_proof"
    )
    assert boundary["schema"] == README_EXAMPLE_RUNS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["example_runs_readme_path"] == "examples/runs/README.md"
    assert boundary["fixture_ids"] == ["hello_world_ensemble", "sorting_ttt_rl"]
    assert validation.readme_marker_count == 13
    assert validation.missing_readme_marker_count == 0
    assert validation.fixture_count == 2
    assert validation.fixture_drift_count == 0
    assert validation.evidence_anchor_count == 9
    assert validation.missing_evidence_anchor_count == 0
    assert boundary["missing_readme_marker_records"] == []
    assert boundary["fixture_drift_records"] == []
    assert boundary["missing_evidence_anchor_records"] == []
    assert boundary["example_runs_readme_map_status"] == (
        "example_runs_readme_structural_fixture_map_present"
    )
    fixture_map = {record["fixture_id"]: record for record in boundary["fixture_records"]}
    assert fixture_map["hello_world_ensemble"]["actual_record_count"] == 11
    assert fixture_map["hello_world_ensemble"]["actual_best_fitness"] == 1.0
    assert fixture_map["hello_world_ensemble"]["actual_best_generation"] == 0
    assert fixture_map["hello_world_ensemble"]["present_artifacts"] == [
        "best.py",
        "history.jsonl",
    ]
    assert fixture_map["sorting_ttt_rl"]["actual_record_count"] == 56
    assert fixture_map["sorting_ttt_rl"]["actual_best_fitness"] == 1.0
    assert fixture_map["sorting_ttt_rl"]["actual_best_generation"] == 0
    assert fixture_map["sorting_ttt_rl"]["present_artifacts"] == [
        "best.py",
        "history.jsonl",
    ]
    assert boundary["missing_evidence"] == {
        "show_command_execution_transcript": "not_recorded_locally",
        "per_fixture_behavior_semantic_verifier": "not_recorded_locally",
        "current_run_artifact_parity_check": "not_recorded_locally",
        "alphaevolve_reproducibility_boundary": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "fixture history row counts" in boundary["claim_boundary"]
    assert "AlphaEvolve-level reproducibility evidence" in boundary["claim_boundary"]


def test_readme_example_runs_boundary_rejects_overclaim_and_drift():
    boundary = readme_example_runs_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "example_runs_reproducibility_proof_ready"
    boundary["readme_marker_count"] = 0
    boundary["missing_readme_marker_count"] = 1
    boundary["missing_readme_marker_records"] = [boundary["readme_marker_records"][0]]
    boundary["readme_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["fixture_count"] = 0
    boundary["fixture_drift_count"] = 1
    boundary["fixture_drift_records"] = [boundary["fixture_records"][0]]
    boundary["fixture_records"][0]["fixture_status"] = "fixture_claims_drifted"
    boundary["evidence_anchor_count"] = 0
    boundary["missing_evidence_anchor_count"] = 1
    boundary["missing_evidence_anchor_records"] = [
        boundary["evidence_anchor_records"][0]
    ]
    boundary["evidence_anchor_records"][0]["marker_status"] = "marker_missing"
    boundary["example_runs_readme_map_status"] = (
        "example_runs_readme_structural_fixture_map_incomplete"
    )
    boundary["missing_evidence"]["show_command_execution_transcript"] = "recorded"
    boundary["required_evidence_fields"] = ["example_runs_readme_markers"]

    validation = validate_readme_example_runs_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_readme_marker_count" in codes
    assert "invalid_missing_readme_marker_count" in codes
    assert "invalid_missing_readme_marker_records" in codes
    assert "invalid_readme_marker_records" in codes
    assert "missing_example_runs_readme_marker" in codes
    assert "invalid_fixture_count" in codes
    assert "invalid_fixture_drift_count" in codes
    assert "invalid_fixture_drift_records" in codes
    assert "invalid_fixture_records" in codes
    assert "example_runs_fixture_drift" in codes
    assert "invalid_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_records" in codes
    assert "invalid_evidence_anchor_records" in codes
    assert "missing_example_runs_evidence_anchor" in codes
    assert "invalid_example_runs_readme_map_status" in codes
    assert "invalid_missing_evidence_show_command_execution_transcript" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_example_runs_boundary_summary_reports_shape():
    summary = render_readme_example_runs_boundary_summary(
        readme_example_runs_boundary_record()
    )

    assert "README example-runs boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | example_runs_readme_structural_fixture_map_without_reproducibility_proof |"
        in summary
    )
    assert "| readme_marker_count | 13 |" in summary
    assert "| missing_readme_marker_count | 0 |" in summary
    assert "| fixture_count | 2 |" in summary
    assert "| fixture_drift_count | 0 |" in summary
    assert "| evidence_anchor_count | 9 |" in summary
    assert "| missing_evidence_anchor_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary


def test_documented_example_run_show_commands_work_for_legacy_fixtures():
    runner = CliRunner()

    hello = runner.invoke(cli, ["show", "examples/runs/hello_world_ensemble"])
    sorting = runner.invoke(cli, ["show", "examples/runs/sorting_ttt_rl"])

    assert hello.exit_code == 0
    assert "Run status:     legacy history-only (manifest.json missing)" in hello.output
    assert "legacy highest-fitness" in hello.output
    assert 'return f"Hello, {name}!"' in hello.output
    assert sorting.exit_code == 0
    assert "Run status:     legacy history-only (manifest.json missing)" in sorting.output
    assert "legacy highest-fitness" in sorting.output
    assert "def sort_list(lst):" in sorting.output
