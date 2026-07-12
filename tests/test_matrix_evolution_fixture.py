import copy
import json
from pathlib import Path

from libreevolve.core.config import Config
from libreevolve.problems.benchmarks.matrix_evolution_fixture import (
    MATRIX_EVOLUTION_FIXTURE_REPORT_PATH,
    MATRIX_EVOLUTION_FIXTURE_ROOT,
    MATRIX_EVOLUTION_FIXTURE_SCHEMA,
    matrix_evolution_fixture_stages,
    run_matrix_evolution_fixture,
    validate_matrix_evolution_fixture_bundle,
    validate_matrix_evolution_fixture_report,
    write_matrix_evolution_fixture_bundle,
)
from libreevolve.problems.benchmarks.matrix_results import (
    validate_matrix_cascade_run_runtime_boundary,
    validate_matrix_result_report,
)


def test_matrix_evolution_stages_keep_rank8_parent_eligible():
    stages = matrix_evolution_fixture_stages()

    config = Config(eval_stages=stages)

    assert config.eval_stages == stages
    assert stages[0]["min_score"] == 0.12
    assert stages[1]["hypothesis_test"]["min"] == 0.12
    assert [stage["role"] for stage in stages] == [
        "small_scale_filter",
        "main_test",
    ]


def test_matrix_evolution_fixture_runs_normal_pipeline_with_lineage():
    report = run_matrix_evolution_fixture(search_seeds=(0,))
    seed_run = report["seed_artifacts"][0]["payload"]
    final = seed_run["final_candidate"]

    assert report["schema"] == MATRIX_EVOLUTION_FIXTURE_SCHEMA
    assert report["fixture_mode"] == "scripted_control"
    assert report["search_evidence_status"] == "executed_normal_evolve_pipeline"
    assert seed_run["runtime_status"] == "completed"
    assert seed_run["stop_reason"] == "max_evaluations"
    assert seed_run["consumed"] == {
        "seed_evaluations": 1,
        "candidate_evaluations": 1,
        "llm_calls": 1,
        "generations_started": 1,
        "generations_completed": 1,
    }
    assert seed_run["history_row_count"] == 2
    assert [row["candidate_type"] for row in seed_run["history"]] == [
        "seed",
        "generated",
    ]
    assert final["generation"] == 1
    assert final["rank"] == 7
    assert final["parent_id"] == final["lineage"][-1]
    assert final["known_strassen_match"] is True
    assert final["exact"] is True
    assert len(seed_run["stage_traces"]) == 2
    assert all(record["candidate_id"] == final["candidate_id"] for record in seed_run["stage_traces"])


def test_matrix_evolution_fixture_emits_valid_matrix_and_cascade_reports():
    report = run_matrix_evolution_fixture()
    matrix_report = report["matrix_result_artifact"]["payload"]
    runtime_boundary = report["runtime_boundary"]

    fixture_validation = validate_matrix_evolution_fixture_report(report)
    matrix_validation = validate_matrix_result_report(matrix_report)
    runtime_validation = validate_matrix_cascade_run_runtime_boundary(runtime_boundary)

    assert fixture_validation["ok"] is True
    assert fixture_validation["seed_count"] == 4
    assert matrix_validation.ok is True
    assert matrix_report["alphaevolve_comparable"] is False
    assert matrix_report["best_rank"] == 7
    assert matrix_report["hit_fraction"] == 1.0
    assert runtime_validation.ok is True
    assert runtime_validation.emitted_record_count == 4
    assert all(record["accepted_final_rank"] == 7 for record in runtime_boundary["emitted_records"])


def test_matrix_evolution_fixture_validator_rejects_lineage_and_linkage_drift():
    report = run_matrix_evolution_fixture(search_seeds=(0,))
    tampered = copy.deepcopy(report)
    payload = tampered["seed_artifacts"][0]["payload"]
    payload["final_candidate"]["parent_id"] = None
    tampered["runtime_boundary"]["emitted_records"][0]["accepted_final_rank"] = 8

    validation = validate_matrix_evolution_fixture_report(tampered)
    codes = {issue["code"] for issue in validation["issues"]}

    assert validation["ok"] is False
    assert "payload_artifact_hash_mismatch" in codes
    assert "runtime_boundary_runtime_record_0_matrix_result_seed_rank_mismatch" in codes
    assert "runtime_seed_result_mismatch" in codes


def test_matrix_evolution_fixture_bundle_round_trip(tmp_path):
    bundle = write_matrix_evolution_fixture_bundle(tmp_path, search_seeds=(0,))

    validation = validate_matrix_evolution_fixture_bundle(tmp_path)

    assert validation["ok"] is True
    assert validation["seed_count"] == 1
    assert bundle["report_path"] == MATRIX_EVOLUTION_FIXTURE_REPORT_PATH.as_posix()
    report = json.loads(
        (tmp_path / MATRIX_EVOLUTION_FIXTURE_REPORT_PATH).read_text(encoding="utf-8")
    )
    seed_path = tmp_path / report["seed_artifacts"][0]["path"]
    seed_path.write_text("{}\n", encoding="utf-8")
    tampered = validate_matrix_evolution_fixture_bundle(tmp_path)
    assert tampered["ok"] is False
    assert "bundle_artifact_hash_mismatch" in {
        issue["code"] for issue in tampered["issues"]
    }


def test_checked_matrix_evolution_fixture_regenerates_exactly():
    validation = validate_matrix_evolution_fixture_bundle(
        MATRIX_EVOLUTION_FIXTURE_ROOT,
        verify_regeneration=True,
    )

    assert validation["ok"] is True
    assert validation["seed_count"] == 4
    report = json.loads(
        (MATRIX_EVOLUTION_FIXTURE_ROOT / MATRIX_EVOLUTION_FIXTURE_REPORT_PATH).read_text(
            encoding="utf-8"
        )
    )
    paper_boundary = json.loads(
        Path("papers/matrix_cascade_run_runtime_boundary.json").read_text(
            encoding="utf-8"
        )
    )
    assert paper_boundary == report["runtime_boundary"]
