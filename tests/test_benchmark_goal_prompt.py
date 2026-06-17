import json
from pathlib import Path

from libreevolve.problems.benchmarks.benchmark_goal_prompt import (
    BENCHMARK_GOAL_PROMPT_SCHEMA,
    render_benchmark_goal_prompt_summary,
    validate_benchmark_goal_prompt,
)


PROMPT_PATH = Path("libreevolve/problems/examples/sorting_network_9/benchmark_goal_prompt.json")
CONTRACT_PATH = Path("libreevolve/problems/examples/sorting_network_9/run_contract.json")


def test_benchmark_goal_prompt_accepts_sorting_network_artifact():
    validation = validate_benchmark_goal_prompt(PROMPT_PATH)

    assert validation.ok is True
    assert validation.prompt_id == "sorting_network_9_codex_spark_clean_checkout_goal_v1"
    assert validation.prompt_character_count == 1501
    assert validation.character_limit == 4000
    assert (
        validation.run_contract_path
        == "libreevolve/problems/examples/sorting_network_9/run_contract.json"
    )

    prompt_record = json.loads(PROMPT_PATH.read_text(encoding="utf-8"))
    assert prompt_record["schema"] == BENCHMARK_GOAL_PROMPT_SCHEMA


def test_benchmark_goal_prompt_rejects_drift_and_overclaim():
    prompt_record = json.loads(PROMPT_PATH.read_text(encoding="utf-8"))
    prompt_record["prompt_character_count"] = 1
    prompt_record["character_limit"] = 10
    prompt_record["claim_boundary"] = "This proves rediscovery."
    prompt_record["prompt"] += "\nsk-proj_thislookssecret1234567890"

    validation = validate_benchmark_goal_prompt(prompt_record, run_contract=CONTRACT_PATH)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_prompt_character_count" in codes
    assert "prompt_exceeds_character_limit" in codes
    assert "claim_boundary_overclaim" in codes
    assert "secret_like_prompt_text" in codes


def test_benchmark_goal_prompt_rejects_run_contract_mismatch():
    prompt_record = json.loads(PROMPT_PATH.read_text(encoding="utf-8"))
    prompt_record["model"] = "wrong-model"
    prompt_record["backend_type"] = "openai"
    prompt_record["auth_name"] = "wrong-auth"
    prompt_record["run_name"] = "wrong-run"

    validation = validate_benchmark_goal_prompt(prompt_record, run_contract=CONTRACT_PATH)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "mismatched_model" in codes
    assert "mismatched_backend_type" in codes
    assert "mismatched_auth_name" in codes
    assert "mismatched_run_name" in codes


def test_render_benchmark_goal_prompt_summary_reports_shape():
    prompt_record = json.loads(PROMPT_PATH.read_text(encoding="utf-8"))

    summary = render_benchmark_goal_prompt_summary(prompt_record)

    assert "Benchmark goal prompt" in summary
    assert "| schema_status | ok |" in summary
    assert "| prompt_id | sorting_network_9_codex_spark_clean_checkout_goal_v1 |" in summary
    assert "| prompt_character_count | 1501 |" in summary
    assert "| character_limit | 4000 |" in summary
