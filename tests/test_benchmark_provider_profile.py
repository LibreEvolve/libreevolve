import copy
import json
from pathlib import Path

from libreevolve.problems.benchmarks.benchmark_provider_profile import (
    BENCHMARK_PROVIDER_PROFILE_SCHEMA,
    render_benchmark_provider_profile_summary,
    validate_benchmark_provider_profile,
)


PROFILE_PATH = Path("libreevolve/problems/examples/sorting_network_9/benchmark_provider_profile.json")


def test_benchmark_provider_profile_accepts_sorting_network_fixture():
    validation = validate_benchmark_provider_profile(PROFILE_PATH)

    assert validation.ok is True
    assert validation.profile_id == "sorting_network_9_codex_spark_current"
    assert validation.problem_id == "sorting_network_9"
    assert validation.support_status == "experimental_protocol_input_not_benchmark_evidence"
    assert validation.backend_type == "codex"
    assert validation.model == "gpt-5.3-codex-spark"

    record = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    assert record["schema"] == BENCHMARK_PROVIDER_PROFILE_SCHEMA
    assert record["provider_lane"]["supported_in_ci"] is False
    assert record["result_linkage"]["validated_run_artifacts_committed"] is False


def test_benchmark_provider_profile_rejects_drift_and_overclaim():
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    profile["support_status"] = "certified"
    profile["provider_lane"]["model"] = "wrong-model"
    profile["provider_lane"]["supported_in_ci"] = True
    profile["budget"]["max_tokens"] = 123
    profile["transcript_policy"]["raw_transcripts_committed"] = True
    profile["artifact_expectations"]["expected_artifacts"] = [
        item
        for item in profile["artifact_expectations"]["expected_artifacts"]
        if "transcript" not in item
    ]
    profile["result_linkage"]["validated_run_artifacts_committed"] = True
    profile["result_linkage"]["certification_status"] = "certified"
    profile["claim_boundary"] = "This is benchmark evidence."

    validation = validate_benchmark_provider_profile(profile)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_support_status" in codes
    assert "codex_ci_overclaim" in codes
    assert "config_model_mismatch" in codes
    assert "config_max_tokens_mismatch" in codes
    assert "raw_transcript_commit_overclaim" in codes
    assert "missing_transcript_artifact_expectation" in codes
    assert "run_artifact_evidence_overclaim" in codes
    assert "certification_status_overclaim" in codes
    assert "claim_boundary_overclaim" in codes
    assert "contract_model_mismatch" in codes
    assert "contract_expected_artifacts_mismatch" in codes
    assert "prompt_model_mismatch" in codes


def test_benchmark_provider_profile_rejects_linkage_drift():
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    profile["config_path"] = "libreevolve/problems/examples/sorting_network_9/missing.yaml"
    profile["artifact_expectations"]["expected_run_dir"] = "runs/wrong"
    profile["result_linkage"]["prompt_id"] = "wrong"

    validation = validate_benchmark_provider_profile(profile)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_config_path" in codes
    assert "contract_expected_run_dir_mismatch" in codes
    assert "contract_prompt_id_mismatch" in codes
    assert "prompt_prompt_id_mismatch" in codes


def test_render_benchmark_provider_profile_summary_reports_shape():
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

    summary = render_benchmark_provider_profile_summary(copy.deepcopy(profile))

    assert "Benchmark provider profile" in summary
    assert "| schema_status | ok |" in summary
    assert "| profile_id | sorting_network_9_codex_spark_current |" in summary
    assert "| backend_type | codex |" in summary
    assert "| model | gpt-5.3-codex-spark |" in summary
