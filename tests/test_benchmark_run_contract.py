import copy
import json
from pathlib import Path

from libreevolve.problems.benchmarks.benchmark_run_contract import (
    render_benchmark_run_contract_summary,
    validate_benchmark_run_contract,
)


CONTRACT_PATH = Path("libreevolve/problems/examples/sorting_network_9/run_contract.json")


def test_benchmark_run_contract_accepts_sorting_network_fixture():
    validation = validate_benchmark_run_contract(CONTRACT_PATH)

    assert validation.ok is True
    assert validation.schema == "libreevolve.sorting_network_9_clean_checkout_run_contract.v1"
    assert validation.problem_id == "sorting_network_9"
    assert validation.run_name == "sorting_network_9_codex_spark_clean_checkout"
    assert validation.expected_artifact_count >= 10
    assert validation.manifest_assertion_count >= 10


def test_benchmark_run_contract_rejects_drift_and_overclaim():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["status"] = "certified_rediscovery"
    contract["auth_setup"]["model"] = "wrong-model"
    contract["validator_budget"]["target_comparators"] = 24
    contract["expected_artifacts"] = [
        artifact
        for artifact in contract["expected_artifacts"]
        if "transcript" not in artifact
    ]
    contract["claim_boundary"] = "This certifies AlphaEvolve rediscovery."

    validation = validate_benchmark_run_contract(contract)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "status_overclaim" in codes
    assert "config_model_mismatch" in codes
    assert "validator_budget_target_comparators_mismatch" in codes
    assert "missing_codex_transcript_artifact" in codes
    assert "claim_boundary_overclaim" in codes
    assert "goal_prompt_mismatched_model" in codes


def test_benchmark_run_contract_rejects_path_and_manifest_assertion_drift():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["config_path"] = "libreevolve/problems/examples/sorting_network_9/missing.yaml"
    contract["expected_run_dir"] = "runs/wrong"
    contract["manifest_assertions"] = [
        assertion
        for assertion in contract["manifest_assertions"]
        if "runtime.benchmark_goal_prompt" not in assertion
    ]

    validation = validate_benchmark_run_contract(contract)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_config_path" in codes
    assert "expected_run_dir_mismatch" in codes
    assert "missing_goal_prompt_manifest_assertion" in codes


def test_render_benchmark_run_contract_summary_reports_shape():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    summary = render_benchmark_run_contract_summary(copy.deepcopy(contract))

    assert "Benchmark run contract" in summary
    assert "| schema_status | ok |" in summary
    assert "| problem_id | sorting_network_9 |" in summary
    assert "| run_name | sorting_network_9_codex_spark_clean_checkout |" in summary
