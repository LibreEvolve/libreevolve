import copy
import json

from libreevolve.core.config import Config
from libreevolve.problems.benchmarks.matrix_cascade_fixture import (
    MATRIX_CASCADE_FIXTURE_ROOT,
    MATRIX_CASCADE_FIXTURE_REPORT_PATH,
    MATRIX_CASCADE_FIXTURE_SCHEMA,
    MATRIX_CASCADE_FIXTURE_SEEDS,
    matrix_cascade_fixture_stages,
    run_matrix_cascade_fixture,
    validate_matrix_cascade_fixture_bundle,
    validate_matrix_cascade_fixture_report,
    write_matrix_cascade_fixture_bundle,
)
from libreevolve.problems.benchmarks.matrix_results import (
    validate_matrix_cascade_run_runtime_boundary,
)


def test_matrix_cascade_fixture_stages_are_valid_and_pinned():
    stages = matrix_cascade_fixture_stages()

    config = Config(eval_stages=stages)

    assert config.eval_stages == stages
    assert [stage["role"] for stage in stages] == [
        "small_scale_filter",
        "main_test",
    ]
    assert stages[0]["test_set"]["id"] == "smoke_cases"
    assert stages[1]["test_set"]["id"] == "main_cases"
    assert stages[1]["hypothesis_test"]["min"] == 0.13
    assert stages[1]["seeds"] == list(MATRIX_CASCADE_FIXTURE_SEEDS)


def test_matrix_cascade_fixture_executes_positive_and_negative_controls():
    report = run_matrix_cascade_fixture()
    positive = report["candidate_results"]["positive_control"]
    negative = report["candidate_results"]["negative_control"]

    assert report["schema"] == MATRIX_CASCADE_FIXTURE_SCHEMA
    assert positive["final_passed"] is True
    assert positive["final_rank"] == 7
    assert positive["stages"][0]["passed"] is True
    assert positive["stages"][1]["hypothesis_test_result"]["passed"] is True
    assert negative["final_passed"] is False
    assert negative["final_rank"] == 8
    assert negative["stages"][0]["passed"] is True
    assert negative["stages"][1]["hypothesis_test_result"]["passed"] is False
    assert negative["final_stop_reason"] == "hypothesis_test_not_met"


def test_matrix_cascade_fixture_emits_valid_per_seed_runtime_records():
    report = run_matrix_cascade_fixture()

    fixture_validation = validate_matrix_cascade_fixture_report(report)
    runtime_validation = validate_matrix_cascade_run_runtime_boundary(
        report["runtime_boundary"]
    )

    assert fixture_validation.ok is True
    assert fixture_validation.seed_count == 4
    assert fixture_validation.trace_artifact_count == 4
    assert fixture_validation.positive_candidate_passed is True
    assert fixture_validation.negative_candidate_rejected is True
    assert runtime_validation.ok is True
    assert runtime_validation.emitted_record_count == 4
    records = report["runtime_boundary"]["emitted_records"]
    assert {record["seed"] for record in records} == set(MATRIX_CASCADE_FIXTURE_SEEDS)
    assert all(record["accepted_final_rank"] == 7 for record in records)
    assert all(len(record["stage_traces"]) == 2 for record in records)


def test_matrix_cascade_fixture_validator_rejects_decision_and_trace_drift():
    report = run_matrix_cascade_fixture()
    tampered = copy.deepcopy(report)
    tampered["candidate_results"]["negative_control"]["final_passed"] = True
    tampered["trace_artifacts"][0]["payload"]["stage_traces"][0]["rank"] = 8
    tampered["runtime_boundary"]["emitted_records"][1]["artifact_sha256"] = "0" * 64

    validation = validate_matrix_cascade_fixture_report(tampered)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "negative_control_not_rejected" in codes
    assert "trace_artifact_hash_mismatch" in codes
    assert "runtime_trace_hash_mismatch" in codes


def test_matrix_cascade_fixture_bundle_round_trip_and_hash_check(tmp_path):
    bundle = write_matrix_cascade_fixture_bundle(tmp_path)

    validation = validate_matrix_cascade_fixture_bundle(tmp_path)

    assert validation.ok is True
    assert bundle["report_path"] == MATRIX_CASCADE_FIXTURE_REPORT_PATH.as_posix()
    report_path = tmp_path / MATRIX_CASCADE_FIXTURE_REPORT_PATH
    report = json.loads(report_path.read_text(encoding="utf-8"))
    trace_path = tmp_path / report["trace_artifacts"][0]["path"]
    trace_path.write_text("{}\n", encoding="utf-8")

    tampered_validation = validate_matrix_cascade_fixture_bundle(tmp_path)
    assert tampered_validation.ok is False
    assert "trace_artifact_hash_mismatch" in {
        issue.code for issue in tampered_validation.issues
    }


def test_matrix_cascade_fixture_bundle_checks_source_hashes(tmp_path):
    write_matrix_cascade_fixture_bundle(tmp_path)
    report_path = tmp_path / MATRIX_CASCADE_FIXTURE_REPORT_PATH
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["test_set_artifacts"][0]["sha256"] = "0" * 64
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    validation = validate_matrix_cascade_fixture_bundle(tmp_path)

    assert validation.ok is False
    assert "test_set_source_hash_mismatch" in {
        issue.code for issue in validation.issues
    }


def test_checked_matrix_cascade_fixture_bundle_is_valid():
    validation = validate_matrix_cascade_fixture_bundle(MATRIX_CASCADE_FIXTURE_ROOT)

    assert validation.ok is True
