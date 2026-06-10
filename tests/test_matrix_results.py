import hashlib
import json
import shutil

import pytest

from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    EXPECTED_TARGET_COUNT,
    matrix_target_records,
)
from libreevolve.problems.benchmarks.companion_sources import (
    alphaevolve_companion_artifact_rights_record,
    alphaevolve_companion_selection_scope_record,
)
from libreevolve.problems.benchmarks.matrix_results import (
    MATRIX_ARTIFACT_INVENTORY_SCHEMA,
    MATRIX_BASELINE_COMPONENT_RUNTIME_SCHEMA,
    MATRIX_CASCADE_RUN_RUNTIME_SCHEMA,
    MATRIX_HEADLINE_HISTORICITY_SCHEMA,
    MATRIX_HEADLINE_HISTORICITY_RUNTIME_SCHEMA,
    MATRIX_NEAR_INTEGRALITY_SCHEMA,
    MATRIX_NEAR_INTEGRALITY_RUNTIME_SCHEMA,
    MATRIX_PUBLICATION_BUNDLE_SCHEMA,
    MATRIX_RESULT_SCHEMA,
    MATRIX_SCALAR_FIELD_SCHEMA,
    MATRIX_SCALAR_FIELD_RUNTIME_SCHEMA,
    MATRIX_SUITE_PUBLICATION_ARTIFACT_BOUNDARY_SCHEMA,
    MATRIX_SWEEP_SPACE_SCHEMA,
    MATRIX_SWEEP_SPACE_RUNTIME_SCHEMA,
    MATRIX_TENSOR_RANK_SCHEMA,
    MATRIX_TENSOR_RANK_RUNTIME_SCHEMA,
    STRASSEN_2X2_PUBLICATION_BUNDLE_ROOT,
    matrix_baseline_component_runtime_boundary_from_components,
    matrix_baseline_component_runtime_boundary_record,
    matrix_cascade_run_runtime_boundary_from_matrix_result,
    matrix_cascade_run_runtime_boundary_record,
    matrix_headline_historicity_runtime_boundary_from_evidence,
    matrix_headline_historicity_runtime_boundary_record,
    matrix_near_integrality_runtime_boundary_from_evidence,
    matrix_near_integrality_runtime_boundary_record,
    matrix_result_artifact_inventory,
    matrix_scalar_field_runtime_boundary_from_evidence,
    matrix_scalar_field_runtime_boundary_record,
    matrix_suite_publication_artifact_boundary_from_artifacts,
    matrix_suite_publication_artifact_boundary_record,
    matrix_sweep_space_runtime_boundary_from_evidence,
    matrix_sweep_space_runtime_boundary_record,
    matrix_tensor_rank_runtime_boundary_from_evidence,
    matrix_tensor_rank_runtime_boundary_record,
    render_matrix_baseline_component_runtime_boundary_summary,
    render_matrix_cascade_run_runtime_boundary_summary,
    render_matrix_headline_historicity_summary,
    render_matrix_headline_historicity_runtime_boundary_summary,
    render_matrix_near_integrality_summary,
    render_matrix_near_integrality_runtime_boundary_summary,
    render_matrix_result_summary,
    render_matrix_scalar_field_summary,
    render_matrix_scalar_field_runtime_boundary_summary,
    render_matrix_suite_publication_artifact_boundary_summary,
    render_matrix_sweep_space_summary,
    render_matrix_sweep_space_runtime_boundary_summary,
    render_matrix_tensor_rank_summary,
    render_matrix_tensor_rank_runtime_boundary_summary,
    strassen_2x2_publication_bundle_record,
    validate_matrix_baseline_component_runtime_boundary,
    validate_matrix_cascade_run_runtime_boundary,
    validate_matrix_headline_historicity_evidence,
    validate_matrix_headline_historicity_runtime_boundary,
    validate_matrix_near_integrality_evidence,
    validate_matrix_near_integrality_runtime_boundary,
    validate_matrix_publication_bundle,
    validate_matrix_result_report,
    validate_matrix_scalar_field_evidence,
    validate_matrix_scalar_field_runtime_boundary,
    validate_matrix_suite_publication_artifact_boundary,
    validate_matrix_sweep_space_evidence,
    validate_matrix_sweep_space_runtime_boundary,
    validate_matrix_tensor_rank_evidence,
    validate_matrix_tensor_rank_runtime_boundary,
    validate_strassen_2x2_publication_bundle,
    write_strassen_2x2_publication_bundle,
)


def _valid_report() -> dict:
    return {
        "schema": MATRIX_RESULT_SCHEMA,
        "target_suite": "alphaevolve_appendix_a",
        "target_id": "mm_4x4x4",
        "dimensions": [4, 4, 4],
        "seed_count": 4,
        "best_rank": 47,
        "hit_count": 2,
        "hit_fraction": 0.5,
        "coefficient_domain": "half_integer",
        "alphaevolve_comparable": True,
        "exactness_certificate": {
            "status": "verified",
            "method": "symbolic_tensor_identity",
            "certificate_sha256": "a" * 64,
        },
        "seed_results": [
            {"seed": 100, "rank": 47, "achieved_best_rank": True, "exact": True},
            {"seed": 101, "rank": 49, "achieved_best_rank": False, "exact": True},
            {"seed": 102, "rank": 47, "achieved_best_rank": True, "exact": True},
            {"seed": 103, "rank": 50, "achieved_best_rank": False, "exact": True},
        ],
        "artifacts": [
            {
                "kind": "algorithm",
                "path": "matrix/mm_4x4x4/algorithm.json",
                "sha256": "b" * 64,
                "bytes": 4096,
                "source_rights": alphaevolve_companion_artifact_rights_record(
                    "algorithm"
                ),
            },
            {
                "kind": "certificate",
                "path": "matrix/mm_4x4x4/certificate.json",
                "sha256": "a" * 64,
                "bytes": 2048,
                "source_rights": alphaevolve_companion_artifact_rights_record(
                    "certificate",
                    material_type="verification_code",
                    source_relationship="adapted_from_companion_repository",
                ),
            },
            {
                "kind": "notebook",
                "path": "matrix/mm_4x4x4/reproduce.ipynb",
                "sha256": "c" * 64,
                "bytes": 8192,
                "source_rights": alphaevolve_companion_artifact_rights_record(
                    "notebook"
                ),
            },
        ],
        "companion_selection_scope": alphaevolve_companion_selection_scope_record(
            "appendix_a_matrix_improved_decompositions"
        ),
    }


def _valid_baseline_component_record() -> dict:
    return {
        "run_id": "run_001",
        "target_id": "mm_4x4x4",
        "baseline_program_id": "baseline_001",
        "component_records": [
            {
                "component_name": "initializer",
                "component_id": "init_001",
                "component_ref": "matrix/mm_4x4x4/baseline.py:init",
                "source_path": "matrix/mm_4x4x4/baseline.py",
                "source_sha256": "a" * 64,
                "mutability": "mutable",
                "config": {"distribution": "normal"},
            },
            {
                "component_name": "reconstruction_loss",
                "component_id": "loss_001",
                "component_ref": "matrix/mm_4x4x4/baseline.py:loss",
                "source_path": "matrix/mm_4x4x4/baseline.py",
                "source_sha256": "b" * 64,
                "mutability": "mutable",
                "config": {"loss": "frobenius"},
            },
            {
                "component_name": "optimizer",
                "component_id": "adam_001",
                "component_ref": "matrix/mm_4x4x4/baseline.py:optimizer",
                "source_path": "matrix/mm_4x4x4/baseline.py",
                "source_sha256": "c" * 64,
                "mutability": "fixed",
                "config": {"optimizer": "Adam"},
            },
        ],
        "initializer_ref": "matrix/mm_4x4x4/baseline.py:init",
        "reconstruction_loss_ref": "matrix/mm_4x4x4/baseline.py:loss",
        "optimizer_ref": "matrix/mm_4x4x4/baseline.py:optimizer",
        "optimizer_name": "Adam",
        "optimizer_version": "torch.optim.Adam",
        "optimizer_config": {
            "learning_rate": 0.001,
            "beta1": 0.9,
            "beta2": 0.999,
        },
        "mutable_component_scopes": ["initializer", "reconstruction_loss"],
        "fixed_component_hashes": {"optimizer": "c" * 64},
        "generation0_metrics": {"rank": 50, "score": 0.0, "exact": True},
        "mutation_lineage": [
            {
                "generation": 1,
                "parent_program_id": "baseline_001",
                "child_program_id": "candidate_001",
                "changed_component_names": ["reconstruction_loss"],
            }
        ],
        "matrix_result_ref": "matrix/mm_4x4x4/result.json",
        "artifact_paths": ["matrix/mm_4x4x4/baseline_components.json"],
        "artifact_sha256": "d" * 64,
    }


def _valid_cascade_run_record() -> dict:
    return {
        "run_id": "run_001",
        "target_id": "mm_4x4x4",
        "seed": 100,
        "cascade_id": "matrix_rank_cascade",
        "cascade_version": "v1",
        "stage_traces": [
            {
                "stage_label": "rank_smoke",
                "threshold": 49,
                "rank": 47,
                "exact": True,
                "candidate_id": "candidate_001",
                "stop_reason": "passed",
            }
        ],
        "accepted_final_rank": 47,
        "stop_reason": "accepted_final_candidate",
        "final_candidate_id": "candidate_001",
        "matrix_result_ref": "matrix/mm_4x4x4/result.json",
        "matrix_result_report": _valid_report(),
        "artifact_paths": ["matrix/mm_4x4x4/cascade_trace.json"],
        "artifact_sha256": "d" * 64,
    }


def _valid_stage_traces_by_seed(report: dict) -> dict[int, list[dict]]:
    return {
        row["seed"]: [
            {
                "stage_label": "rank_smoke",
                "threshold": 50,
                "rank": row["rank"],
                "exact": True,
                "candidate_id": f"candidate_{row['seed']}",
                "stop_reason": "accepted_final_candidate",
            }
        ]
        for row in report["seed_results"]
    }


def test_matrix_result_report_validates_alphaevolve_publication_contract():
    report = _valid_report()

    validation = validate_matrix_result_report(report)

    assert validation.ok is True
    assert validation.alphaevolve_comparable is True
    assert validation.target_id == "mm_4x4x4"
    assert validation.seed_count == 4
    assert validation.best_rank == 47
    assert validation.hit_fraction == 0.5
    assert validation.issues == []


def test_matrix_result_report_loads_json_file(tmp_path):
    path = tmp_path / "matrix_report.json"
    path.write_text(json.dumps(_valid_report()), encoding="utf-8")

    validation = validate_matrix_result_report(path)

    assert validation.ok is True
    assert validation.target_id == "mm_4x4x4"


def test_matrix_baseline_component_runtime_boundary_accepts_current_absence():
    boundary = matrix_baseline_component_runtime_boundary_record()

    validation = validate_matrix_baseline_component_runtime_boundary(boundary)

    assert boundary["schema"] == MATRIX_BASELINE_COMPONENT_RUNTIME_SCHEMA
    assert validation.ok is True
    assert validation.runtime_emission_status == "not_emitted_by_local_runner"
    assert validation.emitted_record_count == 0
    assert validation.required_field_count == 17


def test_matrix_baseline_component_runtime_boundary_rejects_absence_with_records():
    boundary = matrix_baseline_component_runtime_boundary_record()
    boundary["emitted_records"] = [_valid_baseline_component_record()]

    validation = validate_matrix_baseline_component_runtime_boundary(boundary)

    assert validation.ok is False
    codes = {issue.code for issue in validation.issues}
    assert "unexpected_runtime_baseline_component_records" in codes


def test_matrix_baseline_component_runtime_boundary_requires_emitted_records():
    boundary = matrix_baseline_component_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"

    validation = validate_matrix_baseline_component_runtime_boundary(boundary)

    assert validation.ok is False
    codes = {issue.code for issue in validation.issues}
    assert "missing_runtime_baseline_component_records" in codes


def test_matrix_baseline_component_runtime_boundary_accepts_emitted_record():
    record = _valid_baseline_component_record()
    boundary = matrix_baseline_component_runtime_boundary_from_components(
        run_id=record["run_id"],
        target_id=record["target_id"],
        baseline_program_id=record["baseline_program_id"],
        component_records=record["component_records"],
        optimizer_name=record["optimizer_name"],
        optimizer_version=record["optimizer_version"],
        optimizer_config=record["optimizer_config"],
        generation0_metrics=record["generation0_metrics"],
        mutation_lineage=record["mutation_lineage"],
        matrix_result_ref=record["matrix_result_ref"],
        artifact_paths=record["artifact_paths"],
        artifact_sha256=record["artifact_sha256"],
    )

    validation = validate_matrix_baseline_component_runtime_boundary(boundary)

    assert validation.ok is True
    assert validation.emitted_record_count == 1
    assert validation.issues == []
    emitted_record = boundary["emitted_records"][0]
    assert emitted_record["initializer_ref"] == "matrix/mm_4x4x4/baseline.py:init"
    assert (
        emitted_record["reconstruction_loss_ref"]
        == "matrix/mm_4x4x4/baseline.py:loss"
    )
    assert emitted_record["optimizer_ref"] == "matrix/mm_4x4x4/baseline.py:optimizer"
    assert emitted_record["mutable_component_scopes"] == [
        "initializer",
        "reconstruction_loss",
    ]
    assert emitted_record["fixed_component_hashes"] == {"optimizer": "c" * 64}


def test_matrix_baseline_component_runtime_boundary_builder_rejects_missing_component():
    record = _valid_baseline_component_record()
    record["component_records"] = record["component_records"][:2]

    with pytest.raises(
        ValueError,
        match="component_records must include initializer, reconstruction_loss, and optimizer",
    ):
        matrix_baseline_component_runtime_boundary_from_components(
            run_id=record["run_id"],
            target_id=record["target_id"],
            baseline_program_id=record["baseline_program_id"],
            component_records=record["component_records"],
            optimizer_name=record["optimizer_name"],
            optimizer_version=record["optimizer_version"],
            optimizer_config=record["optimizer_config"],
            generation0_metrics=record["generation0_metrics"],
            mutation_lineage=record["mutation_lineage"],
            matrix_result_ref=record["matrix_result_ref"],
        )


def test_matrix_baseline_component_runtime_boundary_rejects_linkage_mismatch():
    record = _valid_baseline_component_record()
    boundary = matrix_baseline_component_runtime_boundary_from_components(
        run_id=record["run_id"],
        target_id=record["target_id"],
        baseline_program_id=record["baseline_program_id"],
        component_records=record["component_records"],
        optimizer_name=record["optimizer_name"],
        optimizer_version=record["optimizer_version"],
        optimizer_config=record["optimizer_config"],
        generation0_metrics=record["generation0_metrics"],
        mutation_lineage=record["mutation_lineage"],
        matrix_result_ref=record["matrix_result_ref"],
    )
    emitted_record = boundary["emitted_records"][0]
    emitted_record["initializer_ref"] = "matrix/mm_4x4x4/other.py:init"
    emitted_record["reconstruction_loss_ref"] = "matrix/mm_4x4x4/other.py:loss"
    emitted_record["optimizer_ref"] = "matrix/mm_4x4x4/other.py:optimizer"
    emitted_record["mutable_component_scopes"] = ["optimizer"]
    emitted_record["fixed_component_hashes"] = {"initializer": "a" * 64}

    validation = validate_matrix_baseline_component_runtime_boundary(boundary)

    assert validation.ok is False
    codes = {issue.code for issue in validation.issues}
    assert "runtime_record_0_initializer_ref_mismatch" in codes
    assert "runtime_record_0_reconstruction_loss_ref_mismatch" in codes
    assert "runtime_record_0_optimizer_ref_mismatch" in codes
    assert "runtime_record_0_mutable_component_scope_mismatch" in codes
    assert "runtime_record_0_fixed_component_hash_mismatch" in codes


def test_matrix_baseline_component_runtime_boundary_rejects_invalid_components():
    boundary = matrix_baseline_component_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    record = _valid_baseline_component_record()
    record["component_records"] = record["component_records"][:2]
    record["optimizer_name"] = "SGD"
    record["optimizer_config"]["learning_rate"] = "fast"
    record["artifact_paths"] = ["../escape.json"]
    boundary["emitted_records"] = [record]

    validation = validate_matrix_baseline_component_runtime_boundary(boundary)

    assert validation.ok is False
    codes = {issue.code for issue in validation.issues}
    assert "runtime_record_0_missing_required_components" in codes
    assert "runtime_record_0_invalid_optimizer_name" in codes
    assert "runtime_record_0_invalid_optimizer_config_learning_rate" in codes
    assert "runtime_record_0_invalid_baseline_component_artifact_path" in codes


def test_render_matrix_baseline_component_runtime_boundary_summary_reports_shape():
    summary = render_matrix_baseline_component_runtime_boundary_summary()

    assert "Matrix baseline-component runtime boundary" in summary
    assert "runtime_emission_status" in summary
    assert "required_field_count" in summary


def test_matrix_cascade_run_runtime_boundary_accepts_current_absence():
    boundary = matrix_cascade_run_runtime_boundary_record()

    validation = validate_matrix_cascade_run_runtime_boundary(boundary)

    assert boundary["schema"] == MATRIX_CASCADE_RUN_RUNTIME_SCHEMA
    assert validation.ok is True
    assert validation.runtime_emission_status == "not_emitted_by_local_runner"
    assert validation.emitted_record_count == 0
    assert validation.required_field_count == 13


def test_matrix_cascade_run_runtime_boundary_rejects_absence_with_records():
    boundary = matrix_cascade_run_runtime_boundary_record()
    boundary["emitted_records"] = [_valid_cascade_run_record()]

    validation = validate_matrix_cascade_run_runtime_boundary(boundary)

    assert validation.ok is False
    codes = {issue.code for issue in validation.issues}
    assert "unexpected_runtime_cascade_run_records" in codes


def test_matrix_cascade_run_runtime_boundary_requires_emitted_records():
    boundary = matrix_cascade_run_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"

    validation = validate_matrix_cascade_run_runtime_boundary(boundary)

    assert validation.ok is False
    codes = {issue.code for issue in validation.issues}
    assert "missing_runtime_cascade_run_records" in codes


def test_matrix_cascade_run_runtime_boundary_accepts_emitted_trace():
    report = _valid_report()
    boundary = matrix_cascade_run_runtime_boundary_from_matrix_result(
        run_id="run_001",
        cascade_id="matrix_rank_cascade",
        cascade_version="v1",
        matrix_result_report=report,
        matrix_result_ref="matrix/mm_4x4x4/result.json",
        stage_traces_by_seed=_valid_stage_traces_by_seed(report),
    )

    validation = validate_matrix_cascade_run_runtime_boundary(boundary)

    assert validation.ok is True
    assert validation.emitted_record_count == 4
    assert validation.issues == []


def test_matrix_cascade_run_runtime_boundary_builds_emitted_records_from_result():
    report = _valid_report()

    boundary = matrix_cascade_run_runtime_boundary_from_matrix_result(
        run_id="run_001",
        cascade_id="matrix_rank_cascade",
        cascade_version="v1",
        matrix_result_report=report,
        matrix_result_ref="matrix/mm_4x4x4/result.json",
        stage_traces_by_seed=_valid_stage_traces_by_seed(report),
    )

    validation = validate_matrix_cascade_run_runtime_boundary(boundary)

    assert boundary["runtime_emission_status"] == "emitted"
    assert validation.ok is True
    assert validation.emitted_record_count == report["seed_count"]
    assert {record["seed"] for record in boundary["emitted_records"]} == {
        row["seed"] for row in report["seed_results"]
    }
    assert all(
        record["accepted_final_rank"]
        == next(
            row["rank"]
            for row in report["seed_results"]
            if row["seed"] == record["seed"]
        )
        for record in boundary["emitted_records"]
    )


def test_matrix_cascade_run_runtime_boundary_builder_requires_seed_traces():
    report = _valid_report()

    with pytest.raises(ValueError, match="missing seed 100"):
        matrix_cascade_run_runtime_boundary_from_matrix_result(
            run_id="run_001",
            cascade_id="matrix_rank_cascade",
            cascade_version="v1",
            matrix_result_report=report,
            matrix_result_ref="matrix/mm_4x4x4/result.json",
            stage_traces_by_seed={},
        )


def test_matrix_cascade_run_runtime_boundary_rejects_incomplete_seed_coverage():
    boundary = matrix_cascade_run_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    boundary["emitted_records"] = [_valid_cascade_run_record()]

    validation = validate_matrix_cascade_run_runtime_boundary(boundary)

    assert validation.ok is False
    codes = {issue.code for issue in validation.issues}
    assert "runtime_group_0_matrix_result_seed_coverage_mismatch" in codes


def test_matrix_cascade_run_runtime_boundary_rejects_mixed_embedded_reports():
    report = _valid_report()
    boundary = matrix_cascade_run_runtime_boundary_from_matrix_result(
        run_id="run_001",
        cascade_id="matrix_rank_cascade",
        cascade_version="v1",
        matrix_result_report=report,
        matrix_result_ref="matrix/mm_4x4x4/result.json",
        stage_traces_by_seed=_valid_stage_traces_by_seed(report),
    )
    boundary["emitted_records"][1]["matrix_result_report"]["coefficient_domain"] = "integer"

    validation = validate_matrix_cascade_run_runtime_boundary(boundary)

    assert validation.ok is False
    codes = {issue.code for issue in validation.issues}
    assert "runtime_group_0_matrix_result_report_mismatch" in codes


def test_matrix_cascade_run_runtime_boundary_rejects_invalid_trace_and_report():
    boundary = matrix_cascade_run_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    record = _valid_cascade_run_record()
    record["stage_traces"][0]["threshold"] = "high"
    record["artifact_paths"] = ["../escape.json"]
    record["matrix_result_report"]["schema"] = "wrong"
    boundary["emitted_records"] = [record]

    validation = validate_matrix_cascade_run_runtime_boundary(boundary)

    assert validation.ok is False
    codes = {issue.code for issue in validation.issues}
    assert "runtime_record_0_stage_0_invalid_threshold" in codes
    assert "runtime_record_0_invalid_cascade_run_artifact_path" in codes
    assert "runtime_record_0_matrix_result_invalid_schema" in codes


def test_matrix_cascade_run_runtime_boundary_rejects_seed_rank_mismatch():
    boundary = matrix_cascade_run_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    record = _valid_cascade_run_record()
    record["accepted_final_rank"] = 48
    boundary["emitted_records"] = [record]

    validation = validate_matrix_cascade_run_runtime_boundary(boundary)

    assert validation.ok is False
    codes = {issue.code for issue in validation.issues}
    assert "runtime_record_0_matrix_result_seed_rank_mismatch" in codes


def test_matrix_cascade_run_runtime_boundary_rejects_final_stage_mismatch():
    boundary = matrix_cascade_run_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    record = _valid_cascade_run_record()
    record["stage_traces"][0]["rank"] = 48
    record["stage_traces"][0]["candidate_id"] = "other_candidate"
    boundary["emitted_records"] = [record]

    validation = validate_matrix_cascade_run_runtime_boundary(boundary)

    assert validation.ok is False
    codes = {issue.code for issue in validation.issues}
    assert "runtime_record_0_final_stage_rank_mismatch" in codes
    assert "runtime_record_0_final_stage_candidate_mismatch" in codes


def test_render_matrix_cascade_run_runtime_boundary_summary_reports_shape():
    summary = render_matrix_cascade_run_runtime_boundary_summary()

    assert "Matrix cascade-run runtime boundary" in summary
    assert "runtime_emission_status" in summary
    assert "required_field_count" in summary


def test_matrix_result_artifact_inventory_verifies_declared_files(tmp_path):
    report = _valid_report()
    for artifact in report["artifacts"]:
        path = tmp_path / artifact["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        content = f"{artifact['kind']} artifact".encode("utf-8")
        path.write_bytes(content)
        artifact["sha256"] = hashlib.sha256(content).hexdigest()
        artifact["bytes"] = len(content)

    inventory = matrix_result_artifact_inventory(report, tmp_path)

    assert inventory["schema"] == MATRIX_ARTIFACT_INVENTORY_SCHEMA
    assert inventory["target_id"] == "mm_4x4x4"
    assert inventory["artifact_root_policy"] == (
        "safe_relative_report_paths_under_artifact_root"
    )
    assert inventory["ok"] is True
    assert inventory["artifact_count"] == 3
    assert inventory["verified_count"] == 3
    assert inventory["missing_count"] == 0
    assert inventory["mismatch_count"] == 0
    assert inventory["invalid_count"] == 0
    assert len(inventory["records_sha256"]) == 64
    assert {artifact["status"] for artifact in inventory["artifacts"]} == {
        "verified"
    }
    assert all("actual_sha256" in artifact for artifact in inventory["artifacts"])
    assert all("source_rights" in artifact for artifact in inventory["artifacts"])


def test_matrix_result_artifact_inventory_reports_missing_mismatch_and_unsafe_paths(tmp_path):
    report = _valid_report()
    first = report["artifacts"][0]
    first_path = tmp_path / first["path"]
    first_path.parent.mkdir(parents=True, exist_ok=True)
    first_path.write_text("wrong", encoding="utf-8")
    first["sha256"] = "b" * 64
    first["bytes"] = 999
    report["artifacts"][1]["path"] = "missing/certificate.json"
    report["artifacts"][2]["path"] = "../escape.ipynb"

    inventory = matrix_result_artifact_inventory(report, tmp_path)
    records = {artifact["kind"]: artifact for artifact in inventory["artifacts"]}

    assert inventory["ok"] is False
    assert inventory["mismatch_count"] == 1
    assert inventory["missing_count"] == 1
    assert inventory["invalid_count"] == 1
    assert records["algorithm"]["status"] == "hash_mismatch"
    assert "artifact_hash_mismatch" in records["algorithm"]["issues"]
    assert "artifact_bytes_mismatch" in records["algorithm"]["issues"]
    assert records["certificate"]["status"] == "missing_file"
    assert records["notebook"]["status"] == "unsafe_path"


def test_matrix_result_report_allows_exploratory_non_publication_domains():
    report = _valid_report()
    report["alphaevolve_comparable"] = False
    report["coefficient_domain"] = "rational"
    report["artifacts"] = [artifact for artifact in report["artifacts"] if artifact["kind"] != "notebook"]

    validation = validate_matrix_result_report(report)

    assert validation.ok is True
    assert validation.alphaevolve_comparable is False


def test_matrix_result_report_rejects_non_publication_domain_for_alphaevolve_claim():
    report = _valid_report()
    report["coefficient_domain"] = "float"
    report["exactness_certificate"]["status"] = "not_checked"
    report["seed_results"][0]["exact"] = False
    report["artifacts"] = [artifact for artifact in report["artifacts"] if artifact["kind"] != "notebook"]

    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_comparable is True
    assert "non_publication_coefficient_domain" in codes
    assert "paper_claim_exactness_not_verified" in codes
    assert "paper_claim_seed_not_exact" in codes
    assert "missing_publication_artifact" in codes


def test_matrix_result_report_requires_explicit_alphaevolve_comparable_flag():
    report = _valid_report()
    del report["alphaevolve_comparable"]

    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_comparable is False
    assert "invalid_alphaevolve_comparable" in codes


def test_matrix_result_report_validates_known_appendix_a_target_dimensions():
    report = _valid_report()
    report["dimensions"] = [4, 4, 5]

    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "target_dimensions_mismatch" in codes

    report = _valid_report()
    report["target_id"] = "mm_missing"
    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "unknown_target_id" in codes


def test_matrix_result_report_rejects_inconsistent_hit_fraction_and_seed_hits():
    report = _valid_report()
    report["hit_fraction"] = 0.75
    report["seed_results"][1]["achieved_best_rank"] = True
    report["seed_results"][1]["rank"] = 49

    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_hit_fraction" in codes
    assert "inconsistent_seed_rank" in codes
    assert "invalid_seed_hit_count" in codes


def test_matrix_result_report_rejects_companion_selection_scope_drift():
    report = _valid_report()
    report["companion_selection_scope"]["companion_notebook_coverage"] = "intentionally_absent"
    report["companion_selection_scope"]["absence_reason"] = (
        "matched_but_not_outperformed_excluded_to_avoid_clutter"
    )
    report["companion_selection_scope"]["alphaevolve_runtime_code_available"] = True

    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "companion_selection_invalid_improved_result_coverage" in codes
    assert "companion_selection_unexpected_absence_reason" in codes
    assert "companion_selection_runtime_code_overclaim" in codes


def test_matrix_result_report_rejects_best_rank_inconsistent_with_seed_ranks():
    report = _valid_report()
    report["best_rank"] = 48
    report["hit_count"] = 1
    report["hit_fraction"] = 0.25
    report["seed_results"][0]["rank"] = 47
    report["seed_results"][0]["achieved_best_rank"] = False
    report["seed_results"][2]["rank"] = 48
    report["seed_results"][2]["achieved_best_rank"] = True

    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "inconsistent_best_rank" in codes


def test_matrix_result_report_rejects_best_rank_seed_without_hit_flag():
    report = _valid_report()
    report["hit_count"] = 1
    report["hit_fraction"] = 0.25
    report["seed_results"][2]["achieved_best_rank"] = False

    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "inconsistent_seed_hit_flag" in codes


def test_matrix_result_report_requires_safe_hashed_artifacts_and_verified_certificate():
    report = _valid_report()
    report["exactness_certificate"]["certificate_sha256"] = "not-a-hash"
    report["artifacts"] = [
        {
            "kind": "algorithm",
            "path": "C:/secret.json",
            "sha256": "not-a-hash",
            "bytes": 0,
        }
    ]

    validation = validate_matrix_result_report(report)
    codes = [issue.code for issue in validation.issues]

    assert validation.ok is False
    assert "invalid_certificate_hash" in codes
    assert "invalid_artifact_path" in codes
    assert "invalid_artifact_hash" in codes
    assert "invalid_artifact_bytes" in codes
    assert "artifact_source_rights_missing" in codes

    report["artifacts"][0]["path"] = "../secret.json"
    validation = validate_matrix_result_report(report)
    codes = [issue.code for issue in validation.issues]

    assert "invalid_artifact_path" in codes


def test_matrix_result_summary_renders_key_publication_fields():
    summary = render_matrix_result_summary(_valid_report())

    assert "Matrix result report: mm_4x4x4" in summary
    assert "| best_rank | 47 |" in summary
    assert "| seed_count | 4 |" in summary
    assert "| hit_fraction | 0.500 |" in summary
    assert "| coefficient_domain | half_integer |" in summary
    assert "| alphaevolve_comparable | True |" in summary
    assert "| exactness | verified |" in summary
    assert "| artifact_count | 3 |" in summary


def test_strassen_2x2_publication_bundle_writes_valid_artifacts(tmp_path):
    bundle = write_strassen_2x2_publication_bundle(tmp_path, seeds=(7, 11, 13))
    report = bundle["report"]

    validation = validate_matrix_result_report(report)
    bundle_validation = validate_matrix_publication_bundle(bundle)
    inventory = bundle["inventory"]

    assert bundle["schema"] == MATRIX_PUBLICATION_BUNDLE_SCHEMA
    assert bundle["target_id"] == "mm_2x2x2"
    assert validation.ok is True
    assert validation.alphaevolve_comparable is True
    assert bundle_validation.ok is True
    assert bundle_validation.report_ok is True
    assert bundle_validation.inventory_ok is True
    assert bundle_validation.alphaevolve_comparable is True
    assert bundle_validation.target_id == "mm_2x2x2"
    assert bundle_validation.issues == []
    assert validation.best_rank == 7
    assert validation.seed_count == 3
    assert validation.hit_fraction == 1.0
    assert report["dimensions"] == [2, 2, 2]
    assert report["coefficient_domain"] == "integer"
    assert report["exactness_certificate"]["status"] == "verified"
    assert inventory["ok"] is True
    assert inventory["artifact_count"] == 3
    assert inventory["verified_count"] == 3
    assert {artifact["kind"] for artifact in inventory["artifacts"]} == {
        "algorithm",
        "certificate",
        "notebook",
    }
    certificate_path = tmp_path / "matrix" / "mm_2x2x2" / "certificate.json"
    certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
    assert certificate["verified"] is True
    assert certificate["mismatch_count"] == 0
    assert certificate["tensor_entry_count"] == 64
    assert certificate["algorithm_sha256"] == report["artifacts"][0]["sha256"]
    report_path = tmp_path / bundle["report_path"]
    assert report_path.exists()
    inventory_path = tmp_path / bundle["inventory_path"]
    assert inventory_path.exists()
    assert json.loads(inventory_path.read_text(encoding="utf-8")) == inventory


def test_strassen_2x2_publication_bundle_validator_rejects_tampering(tmp_path):
    bundle = write_strassen_2x2_publication_bundle(tmp_path, seeds=(7, 11, 13))
    bundle["schema"] = "bad.schema"
    bundle["target_id"] = "mm_4x4x4"
    bundle["report_sha256"] = "0" * 64
    bundle["inventory"]["ok"] = False
    bundle["inventory"]["missing_count"] = 1

    validation = validate_matrix_publication_bundle(bundle)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.report_ok is True
    assert validation.inventory_ok is False
    assert validation.alphaevolve_comparable is True
    assert "invalid_bundle_schema" in codes
    assert "target_id_mismatch" in codes
    assert "inventory_target_id_mismatch" in codes
    assert "report_hash_mismatch" in codes
    assert "inventory_not_ok" in codes
    assert "inventory_missing_count_mismatch" in codes
    assert "inventory_missing_count_nonzero" in codes


def test_pinned_strassen_2x2_publication_bundle_validates_checked_in_artifacts():
    bundle = strassen_2x2_publication_bundle_record()

    validation = validate_strassen_2x2_publication_bundle()

    assert STRASSEN_2X2_PUBLICATION_BUNDLE_ROOT.exists()
    assert bundle["target_id"] == "mm_2x2x2"
    assert bundle["generation_seeds"] == [0, 1, 2, 3]
    assert validation.ok is True
    assert validation.report_ok is True
    assert validation.inventory_ok is True
    assert validation.alphaevolve_comparable is True
    assert validation.issues == []


def test_pinned_strassen_2x2_publication_bundle_detects_artifact_drift(tmp_path):
    copied_root = tmp_path / STRASSEN_2X2_PUBLICATION_BUNDLE_ROOT.name
    shutil.copytree(STRASSEN_2X2_PUBLICATION_BUNDLE_ROOT, copied_root)
    (copied_root / "matrix" / "mm_2x2x2" / "algorithm.json").write_text(
        "{}\n",
        encoding="utf-8",
    )

    validation = validate_strassen_2x2_publication_bundle(copied_root)

    assert validation.ok is False
    codes = {issue.code for issue in validation.issues}
    assert "strassen_regeneration_hash_mismatch" in codes


def test_matrix_publication_bundle_rejects_inventory_source_rights_drift(tmp_path):
    bundle = write_strassen_2x2_publication_bundle(tmp_path, seeds=(7, 11, 13))
    bundle["inventory"]["artifacts"][0]["source_rights"]["license"] = "MIT"
    records_payload = json.dumps(
        bundle["inventory"]["artifacts"],
        sort_keys=True,
        separators=(",", ":"),
    )
    bundle["inventory"]["records_sha256"] = hashlib.sha256(
        records_payload.encode("utf-8")
    ).hexdigest()

    validation = validate_matrix_publication_bundle(bundle)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "inventory_artifact_source_rights_invalid_material_license" in codes


def test_strassen_2x2_publication_bundle_rejects_bad_seed_list(tmp_path):
    for seeds in ((), (1, 1), (True,), ("1",)):
        with pytest.raises(ValueError, match="seeds"):
            write_strassen_2x2_publication_bundle(tmp_path, seeds=seeds)


def _suite_publication_artifact(target: dict) -> dict:
    target_id = target["id"]
    report = json.loads(json.dumps(_valid_report()))
    report["target_id"] = target_id
    report["dimensions"] = list(target["dimensions"])
    report["best_rank"] = target["alphaevolve_rank"]
    report["seed_results"] = [
        {"seed": 100, "rank": target["alphaevolve_rank"], "achieved_best_rank": True, "exact": True},
        {"seed": 101, "rank": target["alphaevolve_rank"] + 1, "achieved_best_rank": False, "exact": True},
        {"seed": 102, "rank": target["alphaevolve_rank"], "achieved_best_rank": True, "exact": True},
        {"seed": 103, "rank": target["alphaevolve_rank"] + 2, "achieved_best_rank": False, "exact": True},
    ]
    for artifact in report["artifacts"]:
        artifact["path"] = artifact["path"].replace("mm_4x4x4", target_id)
    inventory = {
        "schema": MATRIX_ARTIFACT_INVENTORY_SCHEMA,
        "report_schema": MATRIX_RESULT_SCHEMA,
        "target_suite": "alphaevolve_appendix_a",
        "target_id": target_id,
        "artifact_root_policy": "safe_relative_report_paths_under_artifact_root",
        "artifact_root_name": "matrix_suite_publication_artifacts",
        "artifact_count": 3,
        "verified_count": 3,
        "missing_count": 0,
        "mismatch_count": 0,
        "invalid_count": 0,
        "records_sha256": "e" * 64,
        "ok": True,
        "issues": [],
        "artifacts": [],
    }
    return {
        "target_id": target_id,
        "dimensions": list(target["dimensions"]),
        "target_tensor_ref": f"matrix/{target_id}/target_tensor.json",
        "target_tensor_sha256": "1" * 64,
        "algorithm_ref": f"matrix/{target_id}/algorithm.json",
        "algorithm_sha256": "b" * 64,
        "coefficient_domain": "half_integer",
        "coefficient_data_ref": f"matrix/{target_id}/coefficients.json",
        "coefficient_data_sha256": "3" * 64,
        "exactness_certificate_ref": f"matrix/{target_id}/certificate.json",
        "exactness_certificate_sha256": "a" * 64,
        "notebook_ref": f"matrix/{target_id}/reproduce.ipynb",
        "notebook_sha256": "c" * 64,
        "per_seed_report_ref": f"matrix/{target_id}/per_seed_report.json",
        "per_seed_report_sha256": "6" * 64,
        "matrix_result_report": report,
        "artifact_inventory": inventory,
        "publication_bundle_ref": f"matrix/{target_id}/bundle.json",
        "artifact_paths": [
            f"matrix/{target_id}/target_tensor.json",
            f"matrix/{target_id}/algorithm.json",
            f"matrix/{target_id}/certificate.json",
            f"matrix/{target_id}/reproduce.ipynb",
            f"matrix/{target_id}/per_seed_report.json",
        ],
        "artifact_sha256": "7" * 64,
    }


def _suite_publication_artifacts() -> list[dict]:
    return [_suite_publication_artifact(target) for target in matrix_target_records()]


def test_matrix_suite_publication_artifact_boundary_accepts_current_absence():
    boundary = matrix_suite_publication_artifact_boundary_record()

    validation = validate_matrix_suite_publication_artifact_boundary(boundary)

    assert validation.ok is True
    assert validation.artifact_status == "not_generated_locally"
    assert validation.generated_target_count == 0
    assert validation.required_field_count == 20
    assert boundary["schema"] == MATRIX_SUITE_PUBLICATION_ARTIFACT_BOUNDARY_SCHEMA
    assert boundary["registered_target_count"] == EXPECTED_TARGET_COUNT
    assert validation.issues == []


def test_matrix_suite_publication_artifact_boundary_rejects_absence_with_artifacts():
    boundary = matrix_suite_publication_artifact_boundary_record()
    boundary["generated_target_artifacts"] = [_suite_publication_artifact(matrix_target_records()[0])]
    boundary["claim_boundary"] = "Suite artifacts exist."

    validation = validate_matrix_suite_publication_artifact_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "unexpected_generated_target_artifacts" in codes
    assert "missing_absence_claim_boundary" in codes


def test_matrix_suite_publication_artifact_boundary_requires_all_registered_targets_when_generated():
    boundary = matrix_suite_publication_artifact_boundary_record()
    boundary["artifact_status"] = "generated"
    boundary["generated_target_artifacts"] = [_suite_publication_artifact(matrix_target_records()[0])]

    validation = validate_matrix_suite_publication_artifact_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_suite_publication_target" in codes


def test_matrix_suite_publication_artifact_boundary_accepts_generated_suite_fixture():
    boundary = matrix_suite_publication_artifact_boundary_from_artifacts(
        _suite_publication_artifacts()
    )

    validation = validate_matrix_suite_publication_artifact_boundary(boundary)

    assert validation.ok is True
    assert validation.artifact_status == "generated"
    assert validation.generated_target_count == EXPECTED_TARGET_COUNT
    assert validation.issues == []


def test_matrix_suite_publication_artifact_boundary_builder_rejects_incomplete_suite():
    with pytest.raises(
        ValueError,
        match="matrix suite publication artifact boundary is invalid",
    ):
        matrix_suite_publication_artifact_boundary_from_artifacts(
            [_suite_publication_artifact(matrix_target_records()[0])]
        )


def test_matrix_suite_publication_artifact_boundary_rejects_invalid_nested_evidence():
    boundary = matrix_suite_publication_artifact_boundary_record()
    boundary["artifact_status"] = "generated"
    artifacts = _suite_publication_artifacts()
    artifacts[0]["dimensions"] = [9, 9, 9]
    artifacts[0]["coefficient_domain"] = "float"
    artifacts[0]["target_tensor_ref"] = "../target_tensor.json"
    artifacts[0]["algorithm_sha256"] = "not-a-digest"
    artifacts[0]["matrix_result_report"]["target_id"] = "mm_4x4x4"
    artifacts[0]["artifact_inventory"]["ok"] = False
    boundary["generated_target_artifacts"] = artifacts

    validation = validate_matrix_suite_publication_artifact_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "suite_publication_dimensions_mismatch" in codes
    assert "invalid_suite_publication_coefficient_domain" in codes
    assert "invalid_target_tensor_ref" in codes
    assert "invalid_algorithm_sha256" in codes
    assert "matrix_result_target_mismatch" in codes
    assert "inventory_not_ok" in codes


def test_matrix_suite_publication_artifact_boundary_rejects_nested_report_link_drift():
    boundary = matrix_suite_publication_artifact_boundary_from_artifacts(
        _suite_publication_artifacts()
    )
    artifact = boundary["generated_target_artifacts"][0]
    artifact["matrix_result_report"]["dimensions"] = [9, 9, 9]
    report_algorithm = next(
        item
        for item in artifact["matrix_result_report"]["artifacts"]
        if item["kind"] == "algorithm"
    )
    report_algorithm["path"] = "matrix/changed/algorithm.json"

    validation = validate_matrix_suite_publication_artifact_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_nested_matrix_result_target_dimensions_mismatch" in codes
    assert "suite_publication_nested_dimensions_mismatch" in codes
    assert "suite_publication_nested_algorithm_ref_mismatch" in codes


def test_render_matrix_suite_publication_artifact_boundary_summary_reports_shape():
    summary = render_matrix_suite_publication_artifact_boundary_summary()

    assert "Matrix suite publication artifact boundary" in summary
    assert "| artifact_status | not_generated_locally |" in summary
    assert "| generated_target_count | 0 |" in summary


def _valid_near_integrality_evidence() -> dict:
    return {
        "schema": MATRIX_NEAR_INTEGRALITY_SCHEMA,
        "target_suite": "alphaevolve_appendix_a",
        "target_id": "mm_4x4x4",
        "local_search_evidence": True,
        "prompt_instruction": {
            "source": "matrix-search prompt fixture",
            "prompt_hash": "a" * 64,
            "text": "Generate near-integral matrix tensor decomposition coefficients.",
        },
        "rounding_policy": {
            "target_domain": "half_integer",
            "method": "nearest",
            "max_abs_error": 0.02,
            "certificate_scope": "rounded_coefficients",
        },
        "candidate_records": [
            {
                "candidate_id": "candidate_001",
                "seed": 7,
                "raw_coefficients": [0.01, 0.49, -1.02, 1.51],
                "rounded_coefficients": [0.0, 0.5, -1.0, 1.5],
                "max_abs_rounding_error": 0.02,
                "exactness_certificate_ref": "certificates/candidate_001.json",
            }
        ],
    }


def test_matrix_near_integrality_evidence_accepts_prompt_rounding_and_certificate_links():
    evidence = _valid_near_integrality_evidence()

    validation = validate_matrix_near_integrality_evidence(evidence)

    assert validation.ok is True
    assert validation.target_id == "mm_4x4x4"
    assert validation.candidate_count == 1
    assert validation.coefficient_count == 4
    assert validation.issues == []


def test_matrix_near_integrality_evidence_rejects_missing_prompt_semantics():
    evidence = _valid_near_integrality_evidence()
    evidence["prompt_instruction"]["text"] = "Optimize the program."
    evidence["prompt_instruction"]["prompt_hash"] = ""

    validation = validate_matrix_near_integrality_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_near_integral_instruction" in codes
    assert "missing_matrix_decomposition_instruction" in codes
    assert "missing_prompt_prompt_hash" in codes


def test_matrix_near_integrality_evidence_rejects_rounding_drift():
    evidence = _valid_near_integrality_evidence()
    evidence["rounding_policy"]["target_domain"] = "float"
    evidence["rounding_policy"]["method"] = "floor"
    evidence["rounding_policy"]["certificate_scope"] = "raw_coefficients"

    validation = validate_matrix_near_integrality_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_rounding_target_domain" in codes
    assert "invalid_rounding_method" in codes
    assert "invalid_certificate_scope" in codes


def test_matrix_near_integrality_evidence_rejects_bad_candidate_diagnostics():
    evidence = _valid_near_integrality_evidence()
    candidate = evidence["candidate_records"][0]
    candidate["rounded_coefficients"][1] = 0.25
    candidate["max_abs_rounding_error"] = 0.01
    candidate["exactness_certificate_ref"] = ""

    validation = validate_matrix_near_integrality_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "rounded_coefficient_not_half_integer" in codes
    assert "max_abs_rounding_error_mismatch" in codes
    assert "missing_exactness_certificate_ref" in codes


def test_render_matrix_near_integrality_summary_reports_shape():
    summary = render_matrix_near_integrality_summary(_valid_near_integrality_evidence())

    assert "Matrix near-integrality evidence" in summary
    assert "| schema_status | ok |" in summary
    assert "| target_id | mm_4x4x4 |" in summary
    assert "| candidate_count | 1 |" in summary
    assert "| coefficient_count | 4 |" in summary


def test_matrix_near_integrality_runtime_boundary_accepts_current_absence():
    boundary = matrix_near_integrality_runtime_boundary_record()

    validation = validate_matrix_near_integrality_runtime_boundary(boundary)

    assert boundary["schema"] == MATRIX_NEAR_INTEGRALITY_RUNTIME_SCHEMA
    assert validation.ok is True
    assert validation.runtime_emission_status == "not_emitted_by_local_runner"
    assert validation.emitted_record_count == 0
    assert validation.required_field_count == 13
    assert "prompt_hash" in boundary["required_emission_fields"]
    assert "matrix_result_ref" in boundary["required_emission_fields"]
    assert "exactness_certificate_ref" in boundary["required_emission_fields"]


def test_matrix_near_integrality_runtime_boundary_rejects_absence_with_records():
    boundary = matrix_near_integrality_runtime_boundary_record()
    boundary["emitted_records"] = [
        {
            "run_id": "run_001",
            "candidate_id": "candidate_001",
            "matrix_result_ref": "matrix/mm_4x4x4/report.json",
            "near_integrality_evidence": _valid_near_integrality_evidence(),
        }
    ]

    validation = validate_matrix_near_integrality_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "unexpected_runtime_near_integrality_records" in codes


def test_matrix_near_integrality_runtime_boundary_requires_emitted_records():
    boundary = matrix_near_integrality_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"

    validation = validate_matrix_near_integrality_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_runtime_near_integrality_records" in codes


def test_matrix_near_integrality_runtime_boundary_accepts_emitted_evidence():
    boundary = matrix_near_integrality_runtime_boundary_from_evidence(
        run_id="run_001",
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        near_integrality_evidence=_valid_near_integrality_evidence(),
    )

    validation = validate_matrix_near_integrality_runtime_boundary(boundary)

    assert validation.ok is True
    assert validation.runtime_emission_status == "emitted"
    assert validation.emitted_record_count == 1
    record = boundary["emitted_records"][0]
    assert record["target_id"] == "mm_4x4x4"
    assert record["seed"] == 7
    assert record["prompt_hash"] == "a" * 64
    assert record["raw_coefficients"] == [0.01, 0.49, -1.02, 1.51]
    assert record["rounded_coefficients"] == [0.0, 0.5, -1.0, 1.5]


def test_matrix_near_integrality_runtime_boundary_rejects_invalid_nested_evidence():
    boundary = matrix_near_integrality_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    nested = _valid_near_integrality_evidence()
    nested["prompt_instruction"]["text"] = "Optimize the program."
    boundary["emitted_records"] = [
        {
            "run_id": "run_001",
            "candidate_id": "candidate_001",
            "matrix_result_ref": "matrix/mm_4x4x4/report.json",
            "near_integrality_evidence": nested,
        }
    ]

    validation = validate_matrix_near_integrality_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "runtime_record_0_near_integrality_missing_near_integral_instruction" in codes


def test_matrix_near_integrality_runtime_boundary_builder_rejects_invalid_evidence():
    evidence = _valid_near_integrality_evidence()
    evidence["prompt_instruction"]["text"] = "Optimize the program."

    with pytest.raises(ValueError, match="near_integrality_evidence is invalid"):
        matrix_near_integrality_runtime_boundary_from_evidence(
            run_id="run_001",
            matrix_result_ref="matrix/mm_4x4x4/report.json",
            near_integrality_evidence=evidence,
        )


def test_matrix_near_integrality_runtime_boundary_rejects_linkage_mismatch():
    boundary = matrix_near_integrality_runtime_boundary_from_evidence(
        run_id="run_001",
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        near_integrality_evidence=_valid_near_integrality_evidence(),
    )
    record = boundary["emitted_records"][0]
    record["target_id"] = "mm_2x2x2"
    record["seed"] = 8
    record["prompt_hash"] = "b" * 64
    record["raw_coefficients"][0] = 0.2
    record["rounded_coefficients"][1] = 1.0
    record["max_abs_rounding_error"] = 0.5
    record["exactness_certificate_ref"] = "certificates/other.json"

    validation = validate_matrix_near_integrality_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "runtime_record_0_near_integrality_target_mismatch" in codes
    assert "runtime_record_0_near_integrality_seed_mismatch" in codes
    assert "runtime_record_0_near_integrality_prompt_hash_mismatch" in codes
    assert "runtime_record_0_near_integrality_raw_coefficients_mismatch" in codes
    assert "runtime_record_0_near_integrality_rounded_coefficients_mismatch" in codes
    assert "runtime_record_0_near_integrality_rounding_error_mismatch" in codes
    assert "runtime_record_0_near_integrality_certificate_ref_mismatch" in codes


def test_matrix_near_integrality_runtime_boundary_rejects_missing_required_record_fields():
    boundary = matrix_near_integrality_runtime_boundary_from_evidence(
        run_id="run_001",
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        near_integrality_evidence=_valid_near_integrality_evidence(),
    )
    record = boundary["emitted_records"][0]
    del record["artifact_paths"]
    record["prompt_hash"] = "not-a-sha"
    record["raw_coefficients"] = []

    validation = validate_matrix_near_integrality_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_runtime_record_prompt_hash" in codes
    assert "invalid_runtime_record_raw_coefficients" in codes
    assert "runtime_record_0_invalid_near_integrality_artifact_paths" in codes


def test_render_matrix_near_integrality_runtime_boundary_summary_reports_shape():
    summary = render_matrix_near_integrality_runtime_boundary_summary()

    assert "Matrix near-integrality runtime boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| runtime_emission_status | not_emitted_by_local_runner |" in summary
    assert "| emitted_record_count | 0 |" in summary
    assert "| required_field_count | 13 |" in summary


def _valid_sweep_space_evidence() -> dict:
    return {
        "schema": MATRIX_SWEEP_SPACE_SCHEMA,
        "target_suite": "alphaevolve_appendix_a",
        "target_id": "mm_4x4x4",
        "source_figure": "Figures 9a-9c",
        "local_search_evidence": True,
        "sweep_function_name": "sweep",
        "search_program_ref": "programs/mm_4x4x4_sweep.py",
        "hyper_library": {
            "name": "hyper",
            "source": "user_provided_hyper_library",
        },
        "hyperparameters": [
            {
                "name": "learning_rate",
                "distribution": "uniform",
                "low": 0.001,
                "high": 0.1,
                "dtype": "float",
            },
            {
                "name": "noise",
                "distribution": "uniform",
                "low": 0.0,
                "high": 1.0,
                "dtype": "float",
            },
        ],
        "sampled_configurations": [
            {
                "configuration_id": "cfg_001",
                "hyperparameters": {
                    "learning_rate": 0.01,
                    "noise": 0.2,
                },
                "loss": 1.5,
                "rank": 49,
                "selected": False,
            },
            {
                "configuration_id": "cfg_002",
                "hyperparameters": {
                    "learning_rate": 0.02,
                    "noise": 0.1,
                },
                "loss": 0.9,
                "rank": 48,
                "selected": True,
                "exactness_certificate_ref": "certificates/cfg_002.json",
                "final_decomposition_ref": "decompositions/cfg_002.json",
            },
        ],
        "winning_configuration_id": "cfg_002",
    }


def test_matrix_sweep_space_evidence_accepts_figure9_hyper_records():
    evidence = _valid_sweep_space_evidence()

    validation = validate_matrix_sweep_space_evidence(evidence)

    assert validation.ok is True
    assert validation.target_id == "mm_4x4x4"
    assert validation.hyperparameter_count == 2
    assert validation.sampled_configuration_count == 2
    assert validation.issues == []


def test_matrix_sweep_space_evidence_rejects_missing_figure9_identity():
    evidence = _valid_sweep_space_evidence()
    evidence["source_figure"] = "Figure 4"
    evidence["sweep_function_name"] = "main"
    evidence["hyper_library"]["name"] = "config"
    evidence["hyper_library"]["source"] = ""

    validation = validate_matrix_sweep_space_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_source_figure" in codes
    assert "invalid_sweep_function" in codes
    assert "invalid_hyper_library_name" in codes
    assert "missing_hyper_library_source" in codes


def test_matrix_sweep_space_evidence_rejects_bad_ranges_and_sampled_values():
    evidence = _valid_sweep_space_evidence()
    evidence["hyperparameters"][0]["low"] = 0.1
    evidence["hyperparameters"][0]["high"] = 0.1
    del evidence["sampled_configurations"][0]["hyperparameters"]["noise"]
    evidence["sampled_configurations"][1]["hyperparameters"]["noise"] = 1.2

    validation = validate_matrix_sweep_space_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_hyperparameter_range" in codes
    assert "missing_configuration_hyperparameter" in codes
    assert "configuration_hyperparameter_out_of_range" in codes


def test_matrix_sweep_space_evidence_requires_selected_winner_certificate_links():
    evidence = _valid_sweep_space_evidence()
    evidence["winning_configuration_id"] = "cfg_001"
    evidence["sampled_configurations"][1]["exactness_certificate_ref"] = ""
    del evidence["sampled_configurations"][1]["final_decomposition_ref"]

    validation = validate_matrix_sweep_space_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "winning_configuration_not_selected" in codes
    assert "missing_exactness_certificate_ref" in codes
    assert "missing_final_decomposition_ref" in codes


def test_render_matrix_sweep_space_summary_reports_shape():
    summary = render_matrix_sweep_space_summary(_valid_sweep_space_evidence())

    assert "Matrix sweep-space evidence" in summary
    assert "| schema_status | ok |" in summary
    assert "| target_id | mm_4x4x4 |" in summary
    assert "| hyperparameter_count | 2 |" in summary
    assert "| sampled_configuration_count | 2 |" in summary


def test_matrix_sweep_space_runtime_boundary_accepts_current_absence():
    boundary = matrix_sweep_space_runtime_boundary_record()

    validation = validate_matrix_sweep_space_runtime_boundary(boundary)

    assert boundary["schema"] == MATRIX_SWEEP_SPACE_RUNTIME_SCHEMA
    assert validation.ok is True
    assert validation.runtime_emission_status == "not_emitted_by_local_runner"
    assert validation.emitted_record_count == 0
    assert validation.required_field_count == 15
    assert "hyperparameters" in boundary["required_emission_fields"]
    assert "winning_configuration_id" in boundary["required_emission_fields"]
    assert "final_decomposition_ref" in boundary["required_emission_fields"]


def test_matrix_sweep_space_runtime_boundary_rejects_absence_with_records():
    boundary = matrix_sweep_space_runtime_boundary_record()
    boundary["emitted_records"] = [
        {
            "run_id": "run_001",
            "candidate_id": "candidate_001",
            "matrix_result_ref": "matrix/mm_4x4x4/report.json",
            "sweep_space_evidence": _valid_sweep_space_evidence(),
        }
    ]

    validation = validate_matrix_sweep_space_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "unexpected_runtime_sweep_space_records" in codes


def test_matrix_sweep_space_runtime_boundary_requires_emitted_records():
    boundary = matrix_sweep_space_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"

    validation = validate_matrix_sweep_space_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_runtime_sweep_space_records" in codes


def test_matrix_sweep_space_runtime_boundary_accepts_emitted_evidence():
    boundary = matrix_sweep_space_runtime_boundary_from_evidence(
        run_id="run_001",
        candidate_id="candidate_001",
        seed=11,
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        sweep_space_evidence=_valid_sweep_space_evidence(),
    )

    validation = validate_matrix_sweep_space_runtime_boundary(boundary)

    assert validation.ok is True
    assert validation.runtime_emission_status == "emitted"
    assert validation.emitted_record_count == 1
    record = boundary["emitted_records"][0]
    assert record["target_id"] == "mm_4x4x4"
    assert record["seed"] == 11
    assert record["search_program_ref"] == "programs/mm_4x4x4_sweep.py"
    assert record["sweep_function_name"] == "sweep"
    assert record["winning_configuration_id"] == "cfg_002"
    assert record["exactness_certificate_ref"] == "certificates/cfg_002.json"
    assert record["final_decomposition_ref"] == "decompositions/cfg_002.json"


def test_matrix_sweep_space_runtime_boundary_builder_rejects_invalid_evidence():
    evidence = _valid_sweep_space_evidence()
    evidence["sweep_function_name"] = "search"

    with pytest.raises(ValueError, match="sweep_space_evidence is invalid"):
        matrix_sweep_space_runtime_boundary_from_evidence(
            run_id="run_001",
            candidate_id="candidate_001",
            seed=11,
            matrix_result_ref="matrix/mm_4x4x4/report.json",
            sweep_space_evidence=evidence,
        )


def test_matrix_sweep_space_runtime_boundary_rejects_linkage_mismatch():
    boundary = matrix_sweep_space_runtime_boundary_from_evidence(
        run_id="run_001",
        candidate_id="candidate_001",
        seed=11,
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        sweep_space_evidence=_valid_sweep_space_evidence(),
    )
    record = boundary["emitted_records"][0]
    record["target_id"] = "mm_5x5x5"
    record["search_program_ref"] = "programs/other.py"
    record["sweep_function_name"] = "search"
    record["hyper_library"] = {"name": "other", "source": "user"}
    record["hyperparameters"][0]["high"] = 0.2
    record["sampled_configurations"][1]["loss"] = 2.0
    record["winning_configuration_id"] = "cfg_001"
    record["exactness_certificate_ref"] = "certificates/other.json"
    record["final_decomposition_ref"] = "decompositions/other.json"

    validation = validate_matrix_sweep_space_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "runtime_record_0_sweep_space_target_mismatch" in codes
    assert "runtime_record_0_sweep_space_search_program_mismatch" in codes
    assert "runtime_record_0_sweep_space_function_mismatch" in codes
    assert "runtime_record_0_sweep_space_hyper_library_mismatch" in codes
    assert "runtime_record_0_sweep_space_hyperparameters_mismatch" in codes
    assert "runtime_record_0_sweep_space_configurations_mismatch" in codes
    assert "runtime_record_0_sweep_space_winner_mismatch" in codes
    assert "runtime_record_0_sweep_space_missing_winner" in codes


def test_matrix_sweep_space_runtime_boundary_rejects_missing_required_record_fields():
    boundary = matrix_sweep_space_runtime_boundary_from_evidence(
        run_id="run_001",
        candidate_id="candidate_001",
        seed=11,
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        sweep_space_evidence=_valid_sweep_space_evidence(),
    )
    record = boundary["emitted_records"][0]
    del record["artifact_paths"]
    record["seed"] = "11"
    record["hyperparameters"] = []
    record["artifact_sha256"] = "not-a-sha"

    validation = validate_matrix_sweep_space_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_runtime_record_seed" in codes
    assert "invalid_runtime_record_hyperparameters" in codes
    assert "runtime_record_0_invalid_sweep_space_artifact_paths" in codes
    assert "runtime_record_0_invalid_sweep_space_artifact_hash" in codes


def test_matrix_sweep_space_runtime_boundary_rejects_invalid_nested_evidence():
    boundary = matrix_sweep_space_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    nested = _valid_sweep_space_evidence()
    nested["source_figure"] = "Figure 4"
    boundary["emitted_records"] = [
        {
            "run_id": "run_001",
            "candidate_id": "candidate_001",
            "matrix_result_ref": "matrix/mm_4x4x4/report.json",
            "sweep_space_evidence": nested,
        }
    ]

    validation = validate_matrix_sweep_space_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "runtime_record_0_sweep_space_invalid_source_figure" in codes


def test_render_matrix_sweep_space_runtime_boundary_summary_reports_shape():
    summary = render_matrix_sweep_space_runtime_boundary_summary()

    assert "Matrix sweep-space runtime boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| runtime_emission_status | not_emitted_by_local_runner |" in summary
    assert "| emitted_record_count | 0 |" in summary
    assert "| required_field_count | 15 |" in summary


def _valid_scalar_field_evidence() -> dict:
    return {
        "schema": MATRIX_SCALAR_FIELD_SCHEMA,
        "target_suite": "alphaevolve_appendix_a",
        "target_id": "mm_4x4x4",
        "source_refs": [
            {
                "source": "AlphaEvolve Section 3.1",
                "page": 10,
                "claim": "rank-48 complex-valued matrices over characteristic zero",
            },
            {
                "source": "AlphaEvolve Appendix A Table 3 note",
                "page": 34,
                "claim": "complex-valued algorithms can be used for exact complex or real-valued matrix multiplication",
            },
        ],
        "field_claims": [
            {
                "claim_id": "complex_characteristic_zero",
                "scalar_field": "complex",
                "characteristic": "zero",
                "applicability": ["complex_matrices", "real_matrices"],
                "certificate_scope": "complex_and_real",
                "paper_complex_row": True,
                "coefficient_representation": {
                    "representation": "complex_half_integer",
                    "exact": True,
                    "real_part_domain": "half_integer",
                    "imaginary_part_domain": "half_integer",
                },
                "algorithm_ref": "algorithms/mm_4x4x4_complex.json",
                "certificate_ref": "certificates/mm_4x4x4_complex.json",
            },
        ],
    }


def test_matrix_scalar_field_evidence_accepts_complex_characteristic_zero_claim():
    evidence = _valid_scalar_field_evidence()

    validation = validate_matrix_scalar_field_evidence(evidence)

    assert validation.ok is True
    assert validation.target_id == "mm_4x4x4"
    assert validation.field_claim_count == 1
    assert validation.complex_claim_count == 1
    assert validation.issues == []


def test_matrix_scalar_field_evidence_accepts_finite_field_caveat():
    evidence = _valid_scalar_field_evidence()
    evidence["target_id"] = "mm_4x4x4"
    evidence["field_claims"] = [
        {
            "claim_id": "fawzi_f2_caveat",
            "scalar_field": "finite_field",
            "characteristic": "positive",
            "prime_characteristic": 2,
            "field_order": 2,
            "applicability": ["finite_field_matrices"],
            "certificate_scope": "finite_field_only",
            "coefficient_representation": {
                "representation": "finite_field",
                "exact": True,
            },
            "algorithm_ref": "prior/fawzi_f2.json",
            "certificate_ref": "prior/fawzi_f2_certificate.json",
        }
    ]

    validation = validate_matrix_scalar_field_evidence(evidence)

    assert validation.ok is True
    assert validation.field_claim_count == 1
    assert validation.complex_claim_count == 0


def test_matrix_scalar_field_evidence_rejects_complex_scope_drift():
    evidence = _valid_scalar_field_evidence()
    claim = evidence["field_claims"][0]
    claim["characteristic"] = "positive"
    claim["applicability"] = ["complex_matrices"]
    claim["certificate_scope"] = "complex_only"
    claim["paper_complex_row"] = False
    claim["coefficient_representation"]["representation"] = "half_integer"
    claim["coefficient_representation"]["imaginary_part_domain"] = "float"

    validation = validate_matrix_scalar_field_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_complex_characteristic" in codes
    assert "missing_complex_real_applicability" in codes
    assert "invalid_complex_certificate_scope" in codes
    assert "missing_paper_complex_row" in codes
    assert "invalid_complex_coefficient_representation" in codes
    assert "invalid_complex_component_domain" in codes


def test_matrix_scalar_field_evidence_rejects_finite_field_scope_drift():
    evidence = _valid_scalar_field_evidence()
    evidence["field_claims"][0] = {
        "claim_id": "bad_finite_field",
        "scalar_field": "finite_field",
        "characteristic": "zero",
        "prime_characteristic": 1,
        "field_order": 1,
        "applicability": ["real_matrices"],
        "certificate_scope": "real_only",
        "coefficient_representation": {
            "representation": "integer",
            "exact": False,
        },
        "algorithm_ref": "",
        "certificate_ref": "",
    }

    validation = validate_matrix_scalar_field_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_finite_field_characteristic" in codes
    assert "invalid_prime_characteristic" in codes
    assert "invalid_field_order" in codes
    assert "missing_finite_field_applicability" in codes
    assert "invalid_finite_field_certificate_scope" in codes
    assert "invalid_finite_field_representation" in codes
    assert "coefficient_representation_not_exact" in codes
    assert "missing_algorithm_ref" in codes
    assert "missing_certificate_ref" in codes


def test_render_matrix_scalar_field_summary_reports_shape():
    summary = render_matrix_scalar_field_summary(_valid_scalar_field_evidence())

    assert "Matrix scalar-field evidence" in summary
    assert "| schema_status | ok |" in summary
    assert "| target_id | mm_4x4x4 |" in summary
    assert "| field_claim_count | 1 |" in summary
    assert "| complex_claim_count | 1 |" in summary


def test_matrix_scalar_field_runtime_boundary_accepts_current_absence():
    boundary = matrix_scalar_field_runtime_boundary_record()

    validation = validate_matrix_scalar_field_runtime_boundary(boundary)

    assert boundary["schema"] == MATRIX_SCALAR_FIELD_RUNTIME_SCHEMA
    assert validation.ok is True
    assert validation.runtime_emission_status == "not_emitted_by_local_runner"
    assert validation.emitted_record_count == 0
    assert validation.required_field_count == 13
    assert "scalar_field" in boundary["required_emission_fields"]
    assert "certificate_ref" in boundary["required_emission_fields"]
    assert "matrix_result_ref" in boundary["required_emission_fields"]


def test_matrix_scalar_field_runtime_boundary_rejects_absence_with_records():
    boundary = matrix_scalar_field_runtime_boundary_record()
    boundary["emitted_records"] = [
        {
            "run_id": "run_001",
            "candidate_id": "candidate_001",
            "matrix_result_ref": "matrix/mm_4x4x4/report.json",
            "scalar_field_evidence": _valid_scalar_field_evidence(),
        }
    ]

    validation = validate_matrix_scalar_field_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "unexpected_runtime_scalar_field_records" in codes


def test_matrix_scalar_field_runtime_boundary_requires_emitted_records():
    boundary = matrix_scalar_field_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"

    validation = validate_matrix_scalar_field_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_runtime_scalar_field_records" in codes


def test_matrix_scalar_field_runtime_boundary_accepts_emitted_evidence():
    boundary = matrix_scalar_field_runtime_boundary_from_evidence(
        run_id="run_001",
        candidate_id="candidate_001",
        seed=13,
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        scalar_field_evidence=_valid_scalar_field_evidence(),
    )

    validation = validate_matrix_scalar_field_runtime_boundary(boundary)

    assert validation.ok is True
    assert validation.runtime_emission_status == "emitted"
    assert validation.emitted_record_count == 1
    record = boundary["emitted_records"][0]
    assert record["target_id"] == "mm_4x4x4"
    assert record["seed"] == 13
    assert record["claim_id"] == "complex_characteristic_zero"
    assert record["scalar_field"] == "complex"
    assert record["characteristic"] == "zero"
    assert record["applicability"] == ["complex_matrices", "real_matrices"]
    assert record["algorithm_ref"] == "algorithms/mm_4x4x4_complex.json"
    assert record["certificate_ref"] == "certificates/mm_4x4x4_complex.json"


def test_matrix_scalar_field_runtime_boundary_builder_rejects_invalid_evidence():
    evidence = _valid_scalar_field_evidence()
    evidence["field_claims"][0]["certificate_ref"] = ""

    with pytest.raises(ValueError, match="scalar_field_evidence is invalid"):
        matrix_scalar_field_runtime_boundary_from_evidence(
            run_id="run_001",
            candidate_id="candidate_001",
            seed=13,
            matrix_result_ref="matrix/mm_4x4x4/report.json",
            scalar_field_evidence=evidence,
        )


def test_matrix_scalar_field_runtime_boundary_rejects_linkage_mismatch():
    boundary = matrix_scalar_field_runtime_boundary_from_evidence(
        run_id="run_001",
        candidate_id="candidate_001",
        seed=13,
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        scalar_field_evidence=_valid_scalar_field_evidence(),
    )
    record = boundary["emitted_records"][0]
    record["target_id"] = "mm_5x5x5"
    record["scalar_field"] = "real"
    record["characteristic"] = "positive"
    record["applicability"] = ["finite_field_matrices"]
    record["coefficient_representation"]["representation"] = "integer"
    record["algorithm_ref"] = "algorithms/other.json"
    record["certificate_ref"] = "certificates/other.json"

    validation = validate_matrix_scalar_field_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "runtime_record_0_scalar_field_target_mismatch" in codes
    assert "runtime_record_0_scalar_field_field_mismatch" in codes
    assert "runtime_record_0_scalar_field_characteristic_mismatch" in codes
    assert "runtime_record_0_scalar_field_applicability_mismatch" in codes
    assert "runtime_record_0_scalar_field_representation_mismatch" in codes
    assert "runtime_record_0_scalar_field_algorithm_mismatch" in codes
    assert "runtime_record_0_scalar_field_certificate_mismatch" in codes


def test_matrix_scalar_field_runtime_boundary_rejects_missing_required_record_fields():
    boundary = matrix_scalar_field_runtime_boundary_from_evidence(
        run_id="run_001",
        candidate_id="candidate_001",
        seed=13,
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        scalar_field_evidence=_valid_scalar_field_evidence(),
    )
    record = boundary["emitted_records"][0]
    del record["artifact_paths"]
    record["seed"] = "13"
    record["applicability"] = []
    record["coefficient_representation"] = "complex"
    record["artifact_sha256"] = "not-a-sha"

    validation = validate_matrix_scalar_field_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_runtime_record_seed" in codes
    assert "invalid_runtime_record_applicability" in codes
    assert "invalid_runtime_record_coefficient_representation" in codes
    assert "runtime_record_0_invalid_scalar_field_artifact_paths" in codes
    assert "runtime_record_0_invalid_scalar_field_artifact_hash" in codes


def test_matrix_scalar_field_runtime_boundary_rejects_invalid_nested_evidence():
    boundary = matrix_scalar_field_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    nested = _valid_scalar_field_evidence()
    nested["field_claims"][0]["certificate_ref"] = ""
    boundary["emitted_records"] = [
        {
            "run_id": "run_001",
            "candidate_id": "candidate_001",
            "matrix_result_ref": "matrix/mm_4x4x4/report.json",
            "scalar_field_evidence": nested,
        }
    ]

    validation = validate_matrix_scalar_field_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "runtime_record_0_scalar_field_missing_certificate_ref" in codes


def test_render_matrix_scalar_field_runtime_boundary_summary_reports_shape():
    summary = render_matrix_scalar_field_runtime_boundary_summary()

    assert "Matrix scalar-field runtime boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| runtime_emission_status | not_emitted_by_local_runner |" in summary
    assert "| emitted_record_count | 0 |" in summary
    assert "| required_field_count | 13 |" in summary


def _valid_tensor_rank_evidence() -> dict:
    return {
        "schema": MATRIX_TENSOR_RANK_SCHEMA,
        "target_suite": "alphaevolve_appendix_a",
        "target_id": "mm_4x4x4",
        "source_refs": [
            {
                "source": "AlphaEvolve Section 3.1",
                "page": 10,
                "claim": "matrix results are low-rank tensor decompositions",
            },
            {
                "source": "AlphaEvolve Section 3.1 note 3",
                "page": 10,
                "claim": "some fewer-than-49 algorithms are not matrix tensor decompositions and cannot be applied recursively",
                "note": "footnote body may require rendered/PDF note extraction",
            },
        ],
        "rank_claims": [
            {
                "claim_id": "alphaevolve_mm_4x4x4_rank48",
                "algorithm_kind": "matrix_multiplication_tensor_decomposition",
                "rank": 48,
                "recursive_applicable": True,
                "certificate_scope": "matrix_multiplication_tensor_identity",
                "tensor_identity_verified": True,
                "target_tensor_ref": "tensors/mm_4x4x4.json",
                "exactness_certificate_ref": "certificates/mm_4x4x4_tensor_identity.json",
            }
        ],
    }


def test_matrix_tensor_rank_evidence_accepts_recursive_tensor_decomposition_claim():
    evidence = _valid_tensor_rank_evidence()

    validation = validate_matrix_tensor_rank_evidence(evidence)

    assert validation.ok is True
    assert validation.target_id == "mm_4x4x4"
    assert validation.claim_count == 1
    assert validation.tensor_decomposition_count == 1
    assert validation.recursive_applicable_count == 1
    assert validation.issues == []


def test_matrix_tensor_rank_evidence_accepts_non_tensor_caveat_claim():
    evidence = _valid_tensor_rank_evidence()
    evidence["rank_claims"] = [
        {
            "claim_id": "non_tensor_less_than_49_caveat",
            "algorithm_kind": "non_tensor_multiplication_algorithm",
            "rank": 47,
            "recursive_applicable": False,
            "certificate_scope": "functional_multiplication_only",
            "non_tensor_caveat": {
                "not_matrix_tensor_decomposition": True,
                "not_recursively_applicable": True,
                "source_note_ref": "AlphaEvolve Section 3.1 footnote 3",
            },
        }
    ]

    validation = validate_matrix_tensor_rank_evidence(evidence)

    assert validation.ok is True
    assert validation.claim_count == 1
    assert validation.tensor_decomposition_count == 0
    assert validation.recursive_applicable_count == 0


def test_matrix_tensor_rank_evidence_rejects_tensor_claim_scope_drift():
    evidence = _valid_tensor_rank_evidence()
    claim = evidence["rank_claims"][0]
    claim["recursive_applicable"] = False
    claim["certificate_scope"] = "functional_multiplication_only"
    claim["tensor_identity_verified"] = False
    claim["target_tensor_ref"] = ""
    claim["exactness_certificate_ref"] = ""
    claim["non_tensor_caveat"] = {"not_matrix_tensor_decomposition": True}

    validation = validate_matrix_tensor_rank_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_tensor_decomposition_certificate_scope" in codes
    assert "missing_recursive_applicability" in codes
    assert "tensor_identity_not_verified" in codes
    assert "missing_target_tensor_ref" in codes
    assert "missing_exactness_certificate_ref" in codes
    assert "unexpected_non_tensor_caveat" in codes


def test_matrix_tensor_rank_evidence_rejects_non_tensor_caveat_drift():
    evidence = _valid_tensor_rank_evidence()
    evidence["rank_claims"][0] = {
        "claim_id": "bad_non_tensor",
        "algorithm_kind": "non_tensor_multiplication_algorithm",
        "rank": 47,
        "recursive_applicable": True,
        "certificate_scope": "matrix_multiplication_tensor_identity",
        "non_tensor_caveat": {
            "not_matrix_tensor_decomposition": False,
            "not_recursively_applicable": False,
            "source_note_ref": "",
        },
    }

    validation = validate_matrix_tensor_rank_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_non_tensor_certificate_scope" in codes
    assert "invalid_non_tensor_recursive_applicability" in codes
    assert "missing_non_tensor_decomposition_caveat" in codes
    assert "missing_non_recursive_caveat" in codes
    assert "missing_source_note_ref" in codes


def test_render_matrix_tensor_rank_summary_reports_shape():
    summary = render_matrix_tensor_rank_summary(_valid_tensor_rank_evidence())

    assert "Matrix tensor-rank evidence" in summary
    assert "| schema_status | ok |" in summary
    assert "| target_id | mm_4x4x4 |" in summary
    assert "| claim_count | 1 |" in summary
    assert "| tensor_decomposition_count | 1 |" in summary
    assert "| recursive_applicable_count | 1 |" in summary


def test_matrix_tensor_rank_runtime_boundary_accepts_current_absence():
    boundary = matrix_tensor_rank_runtime_boundary_record()

    validation = validate_matrix_tensor_rank_runtime_boundary(boundary)

    assert boundary["schema"] == MATRIX_TENSOR_RANK_RUNTIME_SCHEMA
    assert validation.ok is True
    assert validation.runtime_emission_status == "not_emitted_by_local_runner"
    assert validation.emitted_record_count == 0
    assert validation.required_field_count == 14
    assert "algorithm_kind" in boundary["required_emission_fields"]
    assert "target_tensor_ref" in boundary["required_emission_fields"]
    assert "exactness_certificate_ref" in boundary["required_emission_fields"]


def test_matrix_tensor_rank_runtime_boundary_rejects_absence_with_records():
    boundary = matrix_tensor_rank_runtime_boundary_record()
    boundary["emitted_records"] = [
        {
            "run_id": "run_001",
            "candidate_id": "candidate_001",
            "matrix_result_ref": "matrix/mm_4x4x4/report.json",
            "tensor_rank_evidence": _valid_tensor_rank_evidence(),
        }
    ]

    validation = validate_matrix_tensor_rank_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "unexpected_runtime_tensor_rank_records" in codes


def test_matrix_tensor_rank_runtime_boundary_requires_emitted_records():
    boundary = matrix_tensor_rank_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"

    validation = validate_matrix_tensor_rank_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_runtime_tensor_rank_records" in codes


def test_matrix_tensor_rank_runtime_boundary_accepts_emitted_evidence():
    boundary = matrix_tensor_rank_runtime_boundary_from_evidence(
        run_id="run_001",
        candidate_id="candidate_001",
        seed=17,
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        tensor_rank_evidence=_valid_tensor_rank_evidence(),
    )

    validation = validate_matrix_tensor_rank_runtime_boundary(boundary)

    assert validation.ok is True
    assert validation.runtime_emission_status == "emitted"
    assert validation.emitted_record_count == 1
    record = boundary["emitted_records"][0]
    assert record["target_id"] == "mm_4x4x4"
    assert record["seed"] == 17
    assert record["claim_id"] == "alphaevolve_mm_4x4x4_rank48"
    assert record["algorithm_kind"] == "matrix_multiplication_tensor_decomposition"
    assert record["rank"] == 48
    assert record["recursive_applicable"] is True
    assert record["certificate_scope"] == "matrix_multiplication_tensor_identity"
    assert record["tensor_identity_verified"] is True
    assert record["target_tensor_ref"] == "tensors/mm_4x4x4.json"
    assert record["exactness_certificate_ref"] == "certificates/mm_4x4x4_tensor_identity.json"


def test_matrix_tensor_rank_runtime_boundary_builder_rejects_invalid_evidence():
    evidence = _valid_tensor_rank_evidence()
    evidence["rank_claims"][0]["target_tensor_ref"] = ""

    with pytest.raises(ValueError, match="tensor_rank_evidence is invalid"):
        matrix_tensor_rank_runtime_boundary_from_evidence(
            run_id="run_001",
            candidate_id="candidate_001",
            seed=17,
            matrix_result_ref="matrix/mm_4x4x4/report.json",
            tensor_rank_evidence=evidence,
        )


def test_matrix_tensor_rank_runtime_boundary_rejects_linkage_mismatch():
    boundary = matrix_tensor_rank_runtime_boundary_from_evidence(
        run_id="run_001",
        candidate_id="candidate_001",
        seed=17,
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        tensor_rank_evidence=_valid_tensor_rank_evidence(),
    )
    record = boundary["emitted_records"][0]
    record["target_id"] = "mm_5x5x5"
    record["algorithm_kind"] = "non_tensor_multiplication_algorithm"
    record["rank"] = 49
    record["recursive_applicable"] = False
    record["certificate_scope"] = "functional_multiplication_only"
    record["tensor_identity_verified"] = False
    record["target_tensor_ref"] = "tensors/other.json"
    record["exactness_certificate_ref"] = "certificates/other.json"

    validation = validate_matrix_tensor_rank_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "runtime_record_0_tensor_rank_target_mismatch" in codes
    assert "runtime_record_0_tensor_rank_algorithm_kind_mismatch" in codes
    assert "runtime_record_0_tensor_rank_rank_mismatch" in codes
    assert "runtime_record_0_tensor_rank_recursive_mismatch" in codes
    assert "runtime_record_0_tensor_rank_certificate_scope_mismatch" in codes
    assert "runtime_record_0_tensor_rank_identity_mismatch" in codes
    assert "runtime_record_0_tensor_rank_target_tensor_mismatch" in codes
    assert "runtime_record_0_tensor_rank_certificate_mismatch" in codes


def test_matrix_tensor_rank_runtime_boundary_rejects_missing_required_record_fields():
    boundary = matrix_tensor_rank_runtime_boundary_from_evidence(
        run_id="run_001",
        candidate_id="candidate_001",
        seed=17,
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        tensor_rank_evidence=_valid_tensor_rank_evidence(),
    )
    record = boundary["emitted_records"][0]
    del record["artifact_paths"]
    record["seed"] = "17"
    record["recursive_applicable"] = "yes"
    record["tensor_identity_verified"] = "yes"
    record["artifact_sha256"] = "not-a-sha"

    validation = validate_matrix_tensor_rank_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_runtime_record_seed" in codes
    assert "invalid_runtime_record_recursive_applicable" in codes
    assert "invalid_runtime_record_tensor_identity_verified" in codes
    assert "runtime_record_0_invalid_tensor_rank_artifact_paths" in codes
    assert "runtime_record_0_invalid_tensor_rank_artifact_hash" in codes


def test_matrix_tensor_rank_runtime_boundary_rejects_invalid_nested_evidence():
    boundary = matrix_tensor_rank_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    nested = _valid_tensor_rank_evidence()
    nested["rank_claims"][0]["recursive_applicable"] = False
    boundary["emitted_records"] = [
        {
            "run_id": "run_001",
            "candidate_id": "candidate_001",
            "matrix_result_ref": "matrix/mm_4x4x4/report.json",
            "tensor_rank_evidence": nested,
        }
    ]

    validation = validate_matrix_tensor_rank_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "runtime_record_0_tensor_rank_missing_recursive_applicability" in codes


def test_render_matrix_tensor_rank_runtime_boundary_summary_reports_shape():
    summary = render_matrix_tensor_rank_runtime_boundary_summary()

    assert "Matrix tensor-rank runtime boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| runtime_emission_status | not_emitted_by_local_runner |" in summary
    assert "| emitted_record_count | 0 |" in summary
    assert "| required_field_count | 14 |" in summary


def _valid_headline_historicity_evidence() -> dict:
    return {
        "schema": MATRIX_HEADLINE_HISTORICITY_SCHEMA,
        "target_suite": "alphaevolve_appendix_a",
        "target_id": "mm_4x4x4",
        "dimensions": [4, 4, 4],
        "source_refs": [
            {
                "source": "AlphaEvolve abstract",
                "page": 1,
                "span": "abstract matrix multiplication sentence",
                "claim": "4x4 complex-valued matrices using 48 scalar multiplications",
            },
            {
                "source": "AlphaEvolve Section 3.1",
                "page": 10,
                "span": "matrix multiplication historicity paragraph",
                "claim": "first method in 56 years to find rank below 49 over a characteristic-zero field",
            },
        ],
        "headline_claim": {
            "target_id": "mm_4x4x4",
            "rank": 48,
            "multiplication_count": 48,
            "scalar_field": "complex",
            "characteristic": "zero",
            "first_characteristic_zero_rank_below_49": True,
            "rank_below_strassen_recursive": True,
            "finite_field_only_prior_distinguished": True,
            "claim_text": "AlphaEvolve is the first method in 56 years to find rank below 49 over a characteristic-zero field.",
            "source_ref": "AlphaEvolve Section 3.1 page 10",
        },
        "prior_comparisons": [
            {
                "prior_id": "strassen_recursive",
                "rank": 49,
                "field_scope": "any_field",
                "characteristic_scope": "any_characteristic",
                "recursive_applicable": True,
                "reference_id": "95",
            },
            {
                "prior_id": "fawzi_f2",
                "rank": 47,
                "field_scope": "finite_field_2",
                "characteristic_scope": "positive",
                "alphaevolve_comparable_characteristic_zero": False,
                "reference_id": "26",
            },
        ],
        "evidence_links": {
            "matrix_result_ref": "matrix/mm_4x4x4/report.json",
            "scalar_field_evidence_ref": "matrix/mm_4x4x4/scalar_field.json",
            "tensor_rank_evidence_ref": "matrix/mm_4x4x4/tensor_rank.json",
            "figure4_exhibit_ref": "exhibits/figure4_mm_4x4x4.json",
            "figure9_exhibit_ref": "exhibits/figure9_mm_4x4x4.json",
            "companion_colab_ref": "external/alphaevolve_results/mathematical_results.ipynb",
        },
        "companion_selection_scope": alphaevolve_companion_selection_scope_record(
            "appendix_a_matrix_improved_decompositions"
        ),
    }


def test_matrix_headline_historicity_evidence_accepts_rank48_context():
    evidence = _valid_headline_historicity_evidence()

    validation = validate_matrix_headline_historicity_evidence(evidence)

    assert validation.ok is True
    assert validation.target_id == "mm_4x4x4"
    assert validation.prior_comparison_count == 2
    assert validation.source_ref_count == 2
    assert validation.issues == []


def test_matrix_headline_historicity_evidence_rejects_headline_scope_drift():
    evidence = _valid_headline_historicity_evidence()
    evidence["target_id"] = "mm_4x4x8"
    evidence["dimensions"] = [4, 4, 8]
    claim = evidence["headline_claim"]
    claim["rank"] = 49
    claim["multiplication_count"] = 49
    claim["scalar_field"] = "finite_field"
    claim["characteristic"] = "positive"
    claim["first_characteristic_zero_rank_below_49"] = False
    claim["rank_below_strassen_recursive"] = False
    claim["finite_field_only_prior_distinguished"] = False
    claim["claim_text"] = "rank 49 over a finite field"

    validation = validate_matrix_headline_historicity_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_headline_target" in codes
    assert "invalid_headline_dimensions" in codes
    assert "invalid_headline_rank" in codes
    assert "invalid_multiplication_count" in codes
    assert "invalid_headline_scalar_field" in codes
    assert "invalid_headline_characteristic" in codes
    assert "missing_first_characteristic_zero_rank_below_49" in codes
    assert "missing_rank_below_strassen_recursive" in codes
    assert "missing_finite_field_only_prior_distinguished" in codes
    assert "missing_56_year_wording" in codes
    assert "missing_characteristic_zero_first_wording" in codes


def test_matrix_headline_historicity_evidence_rejects_bad_prior_context():
    evidence = _valid_headline_historicity_evidence()
    evidence["prior_comparisons"][0]["rank"] = 48
    evidence["prior_comparisons"][0]["field_scope"] = "complex"
    evidence["prior_comparisons"][0]["recursive_applicable"] = False
    evidence["prior_comparisons"][1]["field_scope"] = "complex"
    evidence["prior_comparisons"][1]["alphaevolve_comparable_characteristic_zero"] = True
    evidence["prior_comparisons"][1]["reference_id"] = "95"

    validation = validate_matrix_headline_historicity_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_strassen_rank" in codes
    assert "invalid_strassen_field_scope" in codes
    assert "invalid_strassen_recursive_applicability" in codes
    assert "invalid_fawzi_field_scope" in codes
    assert "invalid_fawzi_zero_characteristic_comparability" in codes
    assert "invalid_fawzi_reference" in codes

    evidence = _valid_headline_historicity_evidence()
    evidence["prior_comparisons"] = [evidence["prior_comparisons"][0]]
    validation = validate_matrix_headline_historicity_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_fawzi_prior" in codes


def test_matrix_headline_historicity_evidence_requires_sources_and_links():
    evidence = _valid_headline_historicity_evidence()
    evidence["source_refs"] = [{"source": "", "page": 0, "claim": ""}]
    evidence["headline_claim"]["source_ref"] = ""
    evidence["evidence_links"]["matrix_result_ref"] = ""
    del evidence["evidence_links"]["companion_colab_ref"]
    del evidence["companion_selection_scope"]

    validation = validate_matrix_headline_historicity_evidence(evidence)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_source_ref_source" in codes
    assert "invalid_source_ref_page" in codes
    assert "missing_source_ref_claim" in codes
    assert "missing_headline_source_ref" in codes
    assert "missing_matrix_result_ref" in codes
    assert "missing_companion_colab_ref" in codes
    assert "missing_companion_selection_scope" in codes


def test_render_matrix_headline_historicity_summary_reports_shape():
    summary = render_matrix_headline_historicity_summary(_valid_headline_historicity_evidence())

    assert "Matrix headline historicity evidence" in summary
    assert "| schema_status | ok |" in summary
    assert "| target_id | mm_4x4x4 |" in summary
    assert "| prior_comparison_count | 2 |" in summary
    assert "| source_ref_count | 2 |" in summary


def test_matrix_headline_historicity_runtime_boundary_accepts_current_absence():
    boundary = matrix_headline_historicity_runtime_boundary_record()

    validation = validate_matrix_headline_historicity_runtime_boundary(boundary)

    assert boundary["schema"] == MATRIX_HEADLINE_HISTORICITY_RUNTIME_SCHEMA
    assert validation.ok is True
    assert validation.runtime_emission_status == "not_emitted_by_local_runner"
    assert validation.emitted_record_count == 0
    assert validation.required_field_count == 14
    assert "prior_comparisons" in boundary["required_emission_fields"]
    assert "evidence_links" in boundary["required_emission_fields"]
    assert "matrix_result_ref" in boundary["required_emission_fields"]


def test_matrix_headline_historicity_runtime_boundary_rejects_absence_with_records():
    boundary = matrix_headline_historicity_runtime_boundary_record()
    boundary["emitted_records"] = [
        {
            "run_id": "run_001",
            "candidate_id": "candidate_001",
            "matrix_result_ref": "matrix/mm_4x4x4/report.json",
            "headline_historicity_evidence": _valid_headline_historicity_evidence(),
        }
    ]

    validation = validate_matrix_headline_historicity_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "unexpected_runtime_headline_historicity_records" in codes


def test_matrix_headline_historicity_runtime_boundary_requires_emitted_records():
    boundary = matrix_headline_historicity_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"

    validation = validate_matrix_headline_historicity_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_runtime_headline_historicity_records" in codes


def test_matrix_headline_historicity_runtime_boundary_accepts_emitted_evidence():
    boundary = matrix_headline_historicity_runtime_boundary_from_evidence(
        run_id="run_001",
        candidate_id="candidate_001",
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        headline_historicity_evidence=_valid_headline_historicity_evidence(),
    )

    validation = validate_matrix_headline_historicity_runtime_boundary(boundary)

    assert validation.ok is True
    assert validation.runtime_emission_status == "emitted"
    assert validation.emitted_record_count == 1
    record = boundary["emitted_records"][0]
    assert record["target_id"] == "mm_4x4x4"
    assert record["dimensions"] == [4, 4, 4]
    assert record["rank"] == 48
    assert record["multiplication_count"] == 48
    assert record["scalar_field"] == "complex"
    assert record["characteristic"] == "zero"
    assert len(record["source_refs"]) == 2
    assert len(record["prior_comparisons"]) == 2
    assert record["evidence_links"]["matrix_result_ref"] == "matrix/mm_4x4x4/report.json"


def test_matrix_headline_historicity_runtime_boundary_builder_rejects_invalid_evidence():
    evidence = _valid_headline_historicity_evidence()
    evidence["headline_claim"]["rank"] = 49

    with pytest.raises(ValueError, match="headline_historicity_evidence is invalid"):
        matrix_headline_historicity_runtime_boundary_from_evidence(
            run_id="run_001",
            candidate_id="candidate_001",
            matrix_result_ref="matrix/mm_4x4x4/report.json",
            headline_historicity_evidence=evidence,
        )


def test_matrix_headline_historicity_runtime_boundary_rejects_linkage_mismatch():
    boundary = matrix_headline_historicity_runtime_boundary_from_evidence(
        run_id="run_001",
        candidate_id="candidate_001",
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        headline_historicity_evidence=_valid_headline_historicity_evidence(),
    )
    record = boundary["emitted_records"][0]
    record["target_id"] = "mm_4x4x8"
    record["dimensions"] = [4, 4, 8]
    record["rank"] = 49
    record["multiplication_count"] = 49
    record["scalar_field"] = "real"
    record["characteristic"] = "positive"
    record["source_refs"][0]["claim"] = "different claim"
    record["prior_comparisons"][0]["rank"] = 48
    record["evidence_links"]["matrix_result_ref"] = "matrix/other/report.json"
    record["matrix_result_ref"] = "matrix/other/report.json"

    validation = validate_matrix_headline_historicity_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "runtime_record_0_headline_historicity_target_mismatch" in codes
    assert "runtime_record_0_headline_historicity_dimensions_mismatch" in codes
    assert "runtime_record_0_headline_historicity_rank_mismatch" in codes
    assert "runtime_record_0_headline_historicity_multiplication_count_mismatch" in codes
    assert "runtime_record_0_headline_historicity_scalar_field_mismatch" in codes
    assert "runtime_record_0_headline_historicity_characteristic_mismatch" in codes
    assert "runtime_record_0_headline_historicity_source_refs_mismatch" in codes
    assert "runtime_record_0_headline_historicity_prior_comparisons_mismatch" in codes
    assert "runtime_record_0_headline_historicity_evidence_links_mismatch" in codes
    assert "runtime_record_0_headline_historicity_matrix_result_mismatch" in codes


def test_matrix_headline_historicity_runtime_boundary_rejects_missing_required_record_fields():
    boundary = matrix_headline_historicity_runtime_boundary_from_evidence(
        run_id="run_001",
        candidate_id="candidate_001",
        matrix_result_ref="matrix/mm_4x4x4/report.json",
        headline_historicity_evidence=_valid_headline_historicity_evidence(),
    )
    record = boundary["emitted_records"][0]
    del record["artifact_paths"]
    record["dimensions"] = [4, 4]
    record["rank"] = "48"
    record["source_refs"] = []
    record["prior_comparisons"] = []
    record["evidence_links"] = []
    record["artifact_sha256"] = "not-a-sha"

    validation = validate_matrix_headline_historicity_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_runtime_record_dimensions" in codes
    assert "invalid_runtime_record_rank" in codes
    assert "invalid_runtime_record_source_refs" in codes
    assert "invalid_runtime_record_prior_comparisons" in codes
    assert "invalid_runtime_record_evidence_links" in codes
    assert "runtime_record_0_invalid_headline_historicity_artifact_paths" in codes
    assert "runtime_record_0_invalid_headline_historicity_artifact_hash" in codes


def test_matrix_headline_historicity_runtime_boundary_rejects_invalid_nested_evidence():
    boundary = matrix_headline_historicity_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    nested = _valid_headline_historicity_evidence()
    nested["headline_claim"]["rank"] = 49
    boundary["emitted_records"] = [
        {
            "run_id": "run_001",
            "candidate_id": "candidate_001",
            "matrix_result_ref": "matrix/mm_4x4x4/report.json",
            "headline_historicity_evidence": nested,
        }
    ]

    validation = validate_matrix_headline_historicity_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "runtime_record_0_headline_historicity_invalid_headline_rank" in codes


def test_render_matrix_headline_historicity_runtime_boundary_summary_reports_shape():
    summary = render_matrix_headline_historicity_runtime_boundary_summary()

    assert "Matrix headline historicity runtime boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| runtime_emission_status | not_emitted_by_local_runner |" in summary
    assert "| emitted_record_count | 0 |" in summary
    assert "| required_field_count | 14 |" in summary
