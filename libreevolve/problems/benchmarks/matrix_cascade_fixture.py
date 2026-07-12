from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.core.config import Config
from libreevolve.core.evaluator import CascadeEvaluator, EvaluationResult
from libreevolve.problems.benchmarks.matrix_results import (
    MATRIX_CASCADE_RUN_RUNTIME_SCHEMA,
    matrix_cascade_run_runtime_boundary_from_matrix_result,
    strassen_2x2_publication_bundle_record,
    validate_matrix_cascade_run_runtime_boundary,
)
from libreevolve.problems.loader import load_problem


MATRIX_CASCADE_FIXTURE_SCHEMA = "libreevolve.matrix_cascade_fixture_report.v1"
MATRIX_CASCADE_SEED_TRACE_SCHEMA = "libreevolve.matrix_cascade_seed_trace.v1"
MATRIX_CASCADE_FIXTURE_BUNDLE_SCHEMA = "libreevolve.matrix_cascade_fixture_bundle.v1"
MATRIX_CASCADE_FIXTURE_SEEDS = (0, 1, 2, 3)
MATRIX_CASCADE_FIXTURE_TARGET_ID = "mm_2x2x2"
MATRIX_CASCADE_FIXTURE_RUN_ID = "matrix_cascade_fixture_mm_2x2x2_v1"
MATRIX_CASCADE_FIXTURE_ID = "matrix_rank7_calibration"
MATRIX_CASCADE_FIXTURE_VERSION = "v1"
MATRIX_CASCADE_FIXTURE_ROOT = (
    Path(__file__).resolve().parent / "artifacts" / "matrix_cascade_fixture"
)
REPO_ROOT = Path(__file__).resolve().parents[3]
MATRIX_EXAMPLE_ROOT = (
    Path(__file__).resolve().parents[1] / "examples" / "matrix_multiplication"
)
MATRIX_CASCADE_FIXTURE_REPORT_PATH = Path(
    "matrix/mm_2x2x2/cascade_fixture_report.json"
)


@dataclass(frozen=True)
class MatrixCascadeFixtureIssue:
    code: str
    message: str


@dataclass(frozen=True)
class MatrixCascadeFixtureValidation:
    ok: bool
    seed_count: int
    trace_artifact_count: int
    positive_candidate_passed: bool
    negative_candidate_rejected: bool
    issues: list[MatrixCascadeFixtureIssue]


def matrix_cascade_fixture_stages() -> list[dict[str, Any]]:
    """Return the pinned two-stage matrix calibration cascade."""
    seeds = list(MATRIX_CASCADE_FIXTURE_SEEDS)
    return [
        {
            "name": "rank_smoke",
            "role": "small_scale_filter",
            "difficulty_or_scale": {
                "label": "smoke_4_cases",
                "level": 0,
                "rationale": "Cheap exact-arithmetic rejection before the main case set.",
                "estimated_cost": 4,
            },
            "test_set": {
                "id": "smoke_cases",
                "source": "declared_data",
                "split": "smoke",
                "expected_file_count": 1,
            },
            "data_include": ["fixtures/smoke_cases.json"],
            "samples": len(seeds),
            "seeds": seeds,
            "min_score": 0.12,
        },
        {
            "name": "rank_main",
            "role": "main_test",
            "difficulty_or_scale": {
                "label": "main_12_cases",
                "level": 1,
                "rationale": "Broader exact-arithmetic validation and rank promotion gate.",
                "estimated_cost": 12,
            },
            "test_set": {
                "id": "main_cases",
                "source": "declared_data",
                "split": "main",
                "expected_file_count": 1,
            },
            "data_include": ["fixtures/main_cases.json"],
            "samples": len(seeds),
            "seeds": seeds,
            "hypothesis_test": {
                "type": "one_sided_lower_confidence_bound",
                "metric": "inverse_multiplications",
                "min": 0.13,
                "confidence": 0.95,
                "min_samples": len(seeds),
            },
        },
    ]


def run_matrix_cascade_fixture() -> dict[str, Any]:
    """Execute the deterministic rank-7/rank-8 cascade calibration fixture."""
    stages = matrix_cascade_fixture_stages()
    Config(eval_stages=stages)
    problem = load_problem(MATRIX_EXAMPLE_ROOT)
    positive_path = MATRIX_EXAMPLE_ROOT / "benchmark_candidates" / "strassen_rank7.py"
    negative_path = MATRIX_EXAMPLE_ROOT / "initial_programs" / "seed.py"
    positive_code = positive_path.read_text(encoding="utf-8")
    negative_code = negative_path.read_text(encoding="utf-8")
    positive_result = CascadeEvaluator(problem, stages=stages).evaluate(
        positive_code, diff_error=None
    )
    negative_result = CascadeEvaluator(problem, stages=stages).evaluate(
        negative_code, diff_error=None
    )
    positive = _candidate_result_record(
        "strassen_rank7", positive_path, positive_code, positive_result
    )
    negative = _candidate_result_record(
        "naive_rank8", negative_path, negative_code, negative_result
    )
    stage_traces_by_seed = _stage_traces_by_seed(positive)
    trace_artifacts = _trace_artifact_records(stage_traces_by_seed)
    trace_paths = {
        item["seed"]: [item["path"]]
        for item in trace_artifacts
    }
    trace_hashes = {
        item["seed"]: item["sha256"]
        for item in trace_artifacts
    }
    matrix_bundle = strassen_2x2_publication_bundle_record()
    matrix_result_report = matrix_bundle["report"]
    runtime_boundary = matrix_cascade_run_runtime_boundary_from_matrix_result(
        run_id=MATRIX_CASCADE_FIXTURE_RUN_ID,
        cascade_id=MATRIX_CASCADE_FIXTURE_ID,
        cascade_version=MATRIX_CASCADE_FIXTURE_VERSION,
        matrix_result_report=matrix_result_report,
        matrix_result_ref=(
            "libreevolve/problems/benchmarks/artifacts/"
            "strassen_2x2_publication_bundle/matrix/mm_2x2x2/report.json"
        ),
        stage_traces_by_seed=stage_traces_by_seed,
        artifact_paths_by_seed=trace_paths,
        artifact_sha256_by_seed=trace_hashes,
    )
    report = {
        "schema": MATRIX_CASCADE_FIXTURE_SCHEMA,
        "source_paper_id": "2506.13131",
        "source_section_id": "3.1",
        "fixture_scope": "deterministic_local_cascade_calibration",
        "run_id": MATRIX_CASCADE_FIXTURE_RUN_ID,
        "target_id": MATRIX_CASCADE_FIXTURE_TARGET_ID,
        "cascade_id": MATRIX_CASCADE_FIXTURE_ID,
        "cascade_version": MATRIX_CASCADE_FIXTURE_VERSION,
        "seeds": list(MATRIX_CASCADE_FIXTURE_SEEDS),
        "stage_config": copy.deepcopy(stages),
        "test_set_artifacts": [
            _source_artifact_record(
                MATRIX_EXAMPLE_ROOT / "fixtures" / "smoke_cases.json",
                "libreevolve/problems/examples/matrix_multiplication/fixtures/smoke_cases.json",
            ),
            _source_artifact_record(
                MATRIX_EXAMPLE_ROOT / "fixtures" / "main_cases.json",
                "libreevolve/problems/examples/matrix_multiplication/fixtures/main_cases.json",
            ),
        ],
        "candidate_results": {
            "positive_control": positive,
            "negative_control": negative,
        },
        "calibration": {
            "metric": "inverse_multiplications",
            "promotion_threshold": 0.13,
            "positive_rank": 7,
            "positive_metric": 1.0 / 7.0,
            "positive_expected_decision": "accepted_final_candidate",
            "negative_rank": 8,
            "negative_metric": 1.0 / 8.0,
            "negative_expected_decision": "hypothesis_test_not_met",
            "positive_margin": (1.0 / 7.0) - 0.13,
            "negative_margin": (1.0 / 8.0) - 0.13,
        },
        "trace_artifacts": trace_artifacts,
        "runtime_boundary_schema": MATRIX_CASCADE_RUN_RUNTIME_SCHEMA,
        "runtime_boundary": runtime_boundary,
        "matrix_result_report_sha256": matrix_bundle["report_sha256"],
        "claim_ready": False,
        "claim_boundary": (
            "This executed fixture proves deterministic local rank-7 promotion, "
            "rank-8 rejection, repeated-seed stage tracing, and matrix-result "
            "linkage. It does not claim AlphaEvolve-scale stochastic search, "
            "rediscovery of Strassen, empirical false-decision rates, or a new "
            "matrix-multiplication result."
        ),
    }
    validation = validate_matrix_cascade_fixture_report(report)
    if not validation.ok:
        messages = "; ".join(issue.message for issue in validation.issues)
        raise ValueError(f"generated matrix cascade fixture is invalid: {messages}")
    return report


def write_matrix_cascade_fixture_bundle(
    artifact_root: str | Path = MATRIX_CASCADE_FIXTURE_ROOT,
) -> dict[str, Any]:
    """Execute and write the checked matrix cascade calibration artifacts."""
    root = Path(artifact_root)
    report = run_matrix_cascade_fixture()
    for artifact in report["trace_artifacts"]:
        path = root / artifact["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_json_bytes(artifact["payload"]))
    report_path = root / MATRIX_CASCADE_FIXTURE_REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_bytes(_json_bytes(report))
    return matrix_cascade_fixture_bundle_record(root)


def matrix_cascade_fixture_bundle_record(
    artifact_root: str | Path = MATRIX_CASCADE_FIXTURE_ROOT,
) -> dict[str, Any]:
    root = Path(artifact_root)
    report_path = root / MATRIX_CASCADE_FIXTURE_REPORT_PATH
    report = json.loads(report_path.read_text(encoding="utf-8"))
    return {
        "schema": MATRIX_CASCADE_FIXTURE_BUNDLE_SCHEMA,
        "artifact_root": str(root),
        "report_path": MATRIX_CASCADE_FIXTURE_REPORT_PATH.as_posix(),
        "report_sha256": _file_sha256(report_path),
        "report_bytes": report_path.stat().st_size,
        "report": report,
        "generation_command": (
            "py -3.12 -c \"from libreevolve.problems.benchmarks."
            "matrix_cascade_fixture import write_matrix_cascade_fixture_bundle; "
            "write_matrix_cascade_fixture_bundle()\""
        ),
    }


def write_matrix_cascade_fixture_paper_boundary(
    path: str | Path,
    artifact_root: str | Path = MATRIX_CASCADE_FIXTURE_ROOT,
) -> Path:
    """Write the emitted runtime boundary from a validated fixture bundle."""
    root = Path(artifact_root)
    validation = validate_matrix_cascade_fixture_bundle(root)
    if not validation.ok:
        messages = "; ".join(issue.message for issue in validation.issues)
        raise ValueError(f"matrix cascade fixture bundle is invalid: {messages}")
    report = matrix_cascade_fixture_bundle_record(root)["report"]
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(_json_bytes(report["runtime_boundary"]))
    return output


def validate_matrix_cascade_fixture_report(
    report: object | str | Path,
) -> MatrixCascadeFixtureValidation:
    data, read_issues = _load_report(report)
    if read_issues:
        return MatrixCascadeFixtureValidation(False, 0, 0, False, False, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixCascadeFixtureIssue] = []
    if data.get("schema") != MATRIX_CASCADE_FIXTURE_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported matrix cascade fixture schema"))
    if data.get("source_paper_id") != "2506.13131" or data.get("source_section_id") != "3.1":
        issues.append(_issue("invalid_source", "fixture must cite AlphaEvolve Section 3.1"))
    if data.get("fixture_scope") != "deterministic_local_cascade_calibration":
        issues.append(_issue("invalid_fixture_scope", "fixture scope must remain deterministic local calibration"))
    if data.get("target_id") != MATRIX_CASCADE_FIXTURE_TARGET_ID:
        issues.append(_issue("invalid_target_id", "fixture must target mm_2x2x2"))
    seeds = data.get("seeds")
    if seeds != list(MATRIX_CASCADE_FIXTURE_SEEDS):
        issues.append(_issue("invalid_seeds", "fixture seeds must be [0, 1, 2, 3]"))
        seed_count = len(seeds) if isinstance(seeds, list) else 0
    else:
        seed_count = len(seeds)
    _validate_stage_config(data.get("stage_config"), issues)
    _validate_source_artifacts(data.get("test_set_artifacts"), issues)
    candidates = data.get("candidate_results")
    positive_passed, negative_rejected = _validate_candidate_results(candidates, issues)
    trace_count = _validate_trace_artifacts(data.get("trace_artifacts"), issues)
    boundary = data.get("runtime_boundary")
    boundary_validation = validate_matrix_cascade_run_runtime_boundary(boundary)
    issues.extend(
        _issue(f"runtime_boundary_{item.code}", item.message)
        for item in boundary_validation.issues
    )
    if boundary_validation.emitted_record_count != len(MATRIX_CASCADE_FIXTURE_SEEDS):
        issues.append(_issue("invalid_runtime_record_count", "runtime boundary must emit one record per fixture seed"))
    _validate_runtime_trace_linkage(boundary, data.get("trace_artifacts"), issues)
    if data.get("runtime_boundary_schema") != MATRIX_CASCADE_RUN_RUNTIME_SCHEMA:
        issues.append(_issue("invalid_runtime_boundary_schema", "runtime boundary schema linkage is invalid"))
    calibration = data.get("calibration")
    if not isinstance(calibration, dict) or calibration.get("promotion_threshold") != 0.13:
        issues.append(_issue("invalid_calibration", "fixture must retain the pinned 0.13 promotion threshold"))
    expected_matrix_sha = strassen_2x2_publication_bundle_record().get("report_sha256")
    if data.get("matrix_result_report_sha256") != expected_matrix_sha:
        issues.append(_issue("matrix_result_report_hash_mismatch", "fixture must link the checked Strassen result report hash"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "deterministic fixture must not claim AlphaEvolve readiness"))
    claim = data.get("claim_boundary")
    if not isinstance(claim, str) or "does not claim AlphaEvolve-scale stochastic search" not in claim:
        issues.append(_issue("missing_claim_boundary", "fixture must disclaim AlphaEvolve-scale stochastic search"))
    return MatrixCascadeFixtureValidation(
        ok=not issues,
        seed_count=seed_count,
        trace_artifact_count=trace_count,
        positive_candidate_passed=positive_passed,
        negative_candidate_rejected=negative_rejected,
        issues=issues,
    )


def validate_matrix_cascade_fixture_bundle(
    artifact_root: str | Path = MATRIX_CASCADE_FIXTURE_ROOT,
) -> MatrixCascadeFixtureValidation:
    root = Path(artifact_root)
    report_path = root / MATRIX_CASCADE_FIXTURE_REPORT_PATH
    validation = validate_matrix_cascade_fixture_report(report_path)
    issues = list(validation.issues)
    if validation.ok:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        for artifact in report["trace_artifacts"]:
            path = root / artifact["path"]
            if not path.is_file():
                issues.append(_issue("missing_trace_artifact", f"missing trace artifact: {artifact['path']}"))
                continue
            if _file_sha256(path) != artifact["sha256"]:
                issues.append(_issue("trace_artifact_hash_mismatch", f"trace artifact hash mismatch: {artifact['path']}"))
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                issues.append(_issue("invalid_trace_artifact", f"trace artifact could not be read: {exc}"))
                continue
            if payload != artifact["payload"]:
                issues.append(_issue("trace_artifact_payload_mismatch", f"trace artifact payload mismatch: {artifact['path']}"))
        for artifact in report["test_set_artifacts"]:
            source = REPO_ROOT / artifact["path"]
            if not source.is_file():
                issues.append(_issue("missing_test_set_source", f"missing test-set source: {artifact['path']}"))
                continue
            if _file_sha256(source) != artifact["sha256"] or source.stat().st_size != artifact["bytes"]:
                issues.append(_issue("test_set_source_hash_mismatch", f"test-set source hash/size mismatch: {artifact['path']}"))
        candidates = report["candidate_results"]
        for candidate in candidates.values():
            source = REPO_ROOT / candidate["source_path"]
            if not source.is_file():
                issues.append(_issue("missing_candidate_source", f"missing candidate source: {candidate['source_path']}"))
                continue
            text = source.read_text(encoding="utf-8")
            if hashlib.sha256(text.encode("utf-8")).hexdigest() != candidate["source_sha256"]:
                issues.append(_issue("candidate_source_hash_mismatch", f"candidate source hash mismatch: {candidate['source_path']}"))
    return MatrixCascadeFixtureValidation(
        ok=not issues,
        seed_count=validation.seed_count,
        trace_artifact_count=validation.trace_artifact_count,
        positive_candidate_passed=validation.positive_candidate_passed,
        negative_candidate_rejected=validation.negative_candidate_rejected,
        issues=issues,
    )


def _candidate_result_record(
    candidate_id: str,
    source_path: Path,
    source_code: str,
    result: EvaluationResult,
) -> dict[str, Any]:
    configured = result.metadata.get("configured_stage_results")
    if not isinstance(configured, list):
        raise ValueError("matrix cascade fixture did not retain configured stage results")
    stages = []
    samples_by_stage: dict[str, list[dict[str, Any]]] = {}
    for stage in configured:
        metadata = stage.get("metadata")
        samples = metadata.get("samples") if isinstance(metadata, dict) else None
        if not isinstance(samples, list) or len(samples) != len(MATRIX_CASCADE_FIXTURE_SEEDS):
            raise ValueError("matrix cascade fixture stage did not retain all seed samples")
        samples_by_stage[str(stage["name"])] = [
            _deterministic_sample_record(sample) for sample in samples
        ]
        stages.append(
            {
                "name": stage["name"],
                "stage_index": stage["stage_index"],
                "passed": stage["passed"],
                "threshold": stage["threshold"],
                "threshold_passed": stage["threshold_passed"],
                "hypothesis_test_result": copy.deepcopy(stage["hypothesis_test_result"]),
                "fitness": stage["fitness"],
                "metrics": copy.deepcopy(stage["metrics"]),
                "stop_reason": stage.get("stop_reason"),
            }
        )
    return {
        "candidate_id": candidate_id,
        "source_path": source_path.relative_to(MATRIX_EXAMPLE_ROOT.parents[3]).as_posix(),
        "source_sha256": hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        "final_passed": result.is_valid,
        "final_stop_reason": result.error or "accepted_final_candidate",
        "final_rank": int(result.metrics["multiplication_count"]),
        "final_metric": result.metrics["inverse_multiplications"],
        "stages": stages,
        "samples_by_stage": samples_by_stage,
    }


def _stage_traces_by_seed(candidate: dict[str, Any]) -> dict[int, list[dict[str, Any]]]:
    traces: dict[int, list[dict[str, Any]]] = {}
    for sample_index, seed in enumerate(MATRIX_CASCADE_FIXTURE_SEEDS):
        rows = []
        for stage_index, stage in enumerate(candidate["stages"]):
            sample = candidate["samples_by_stage"][stage["name"]][sample_index]
            outputs = sample["program_outputs"]
            config = sample["stage_config"]
            hypothesis = stage["hypothesis_test_result"]
            rows.append(
                {
                    "stage_label": stage["name"],
                    "stage_role": config["role"],
                    "stage_index": stage_index,
                    "seed": seed,
                    "sample_index": sample_index,
                    "candidate_id": f"{candidate['candidate_id']}_seed_{seed}",
                    "candidate_source_sha256": candidate["source_sha256"],
                    "threshold": (
                        stage["threshold"]
                        if stage["threshold"] is not None
                        else hypothesis["min"]
                    ),
                    "rank": int(sample["metrics"]["multiplication_count"]),
                    "exact": bool(sample["is_valid"]),
                    "metrics": copy.deepcopy(sample["metrics"]),
                    "test_set": {
                        "id": config["test_set"]["id"],
                        "split": config["test_set"]["split"],
                        "source": config["test_set"]["source"],
                        "case_count": outputs["case_count"],
                    },
                    "hypothesis_test_result": copy.deepcopy(hypothesis),
                    "stop_reason": (
                        "accepted_final_candidate"
                        if stage_index == len(candidate["stages"]) - 1
                        else "promoted_to_next_stage"
                    ),
                }
            )
        traces[seed] = rows
    return traces


def _deterministic_sample_record(sample: object) -> dict[str, Any]:
    if not isinstance(sample, dict):
        raise ValueError("matrix cascade fixture sample must be an object")
    metadata = sample.get("metadata")
    stage = metadata.get("stage") if isinstance(metadata, dict) else None
    outputs = metadata.get("program_outputs") if isinstance(metadata, dict) else None
    if not isinstance(stage, dict) or not isinstance(stage.get("config"), dict):
        raise ValueError("matrix cascade fixture sample lacks stage config")
    if not isinstance(outputs, dict) or not isinstance(outputs.get("value"), dict):
        raise ValueError("matrix cascade fixture sample lacks validator output provenance")
    return {
        "sample_index": stage.get("sample_index"),
        "seed": stage.get("seed"),
        "is_valid": sample.get("is_valid"),
        "fitness": sample.get("fitness"),
        "metrics": copy.deepcopy(sample.get("metrics")),
        "stage_config": copy.deepcopy(stage["config"]),
        "evaluator_data": copy.deepcopy(stage.get("evaluator_data")),
        "program_outputs": copy.deepcopy(outputs["value"]),
        "program_outputs_sha256": outputs.get("sha256"),
    }


def _trace_artifact_records(
    traces_by_seed: dict[int, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    records = []
    for seed in MATRIX_CASCADE_FIXTURE_SEEDS:
        payload = {
            "schema": MATRIX_CASCADE_SEED_TRACE_SCHEMA,
            "run_id": MATRIX_CASCADE_FIXTURE_RUN_ID,
            "target_id": MATRIX_CASCADE_FIXTURE_TARGET_ID,
            "seed": seed,
            "stage_traces": traces_by_seed[seed],
        }
        raw = _json_bytes(payload)
        records.append(
            {
                "seed": seed,
                "path": f"matrix/mm_2x2x2/cascade_seed_{seed}.json",
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "payload": payload,
            }
        )
    return records


def _source_artifact_record(path: Path, display_path: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "id": payload["id"],
        "path": display_path,
        "sha256": _file_sha256(path),
        "bytes": path.stat().st_size,
        "case_count": len(payload["cases"]),
    }


def _validate_stage_config(value: object, issues: list[MatrixCascadeFixtureIssue]) -> None:
    try:
        Config(eval_stages=value if isinstance(value, list) else value)
    except (TypeError, ValueError) as exc:
        issues.append(_issue("invalid_stage_config", f"stage config is invalid: {exc}"))
        return
    if value != matrix_cascade_fixture_stages():
        issues.append(_issue("stage_config_drift", "stage config differs from the pinned fixture cascade"))


def _validate_source_artifacts(value: object, issues: list[MatrixCascadeFixtureIssue]) -> None:
    if not isinstance(value, list) or len(value) != 2:
        issues.append(_issue("invalid_test_set_artifacts", "fixture must record two test-set artifacts"))
        return
    if {item.get("id") for item in value if isinstance(item, dict)} != {"smoke_cases", "main_cases"}:
        issues.append(_issue("invalid_test_set_ids", "fixture test-set ids are incomplete"))
    for item in value:
        if not isinstance(item, dict) or not _is_sha256(item.get("sha256")):
            issues.append(_issue("invalid_test_set_hash", "test-set artifacts must include SHA-256 hashes"))


def _validate_candidate_results(
    value: object,
    issues: list[MatrixCascadeFixtureIssue],
) -> tuple[bool, bool]:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_candidate_results", "candidate_results must be an object"))
        return False, False
    positive = value.get("positive_control")
    negative = value.get("negative_control")
    positive_passed = (
        isinstance(positive, dict)
        and positive.get("candidate_id") == "strassen_rank7"
        and positive.get("final_passed") is True
        and positive.get("final_rank") == 7
        and positive.get("final_stop_reason") == "accepted_final_candidate"
    )
    negative_rejected = (
        isinstance(negative, dict)
        and negative.get("candidate_id") == "naive_rank8"
        and negative.get("final_passed") is False
        and negative.get("final_rank") == 8
        and negative.get("final_stop_reason") == "hypothesis_test_not_met"
    )
    if not positive_passed:
        issues.append(_issue("positive_control_not_promoted", "rank-7 positive control must pass the cascade"))
    if not negative_rejected:
        issues.append(_issue("negative_control_not_rejected", "rank-8 negative control must fail the main gate"))
    return positive_passed, negative_rejected


def _validate_trace_artifacts(value: object, issues: list[MatrixCascadeFixtureIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_trace_artifacts", "trace_artifacts must be a list"))
        return 0
    if len(value) != len(MATRIX_CASCADE_FIXTURE_SEEDS):
        issues.append(_issue("invalid_trace_artifact_count", "fixture must retain one trace artifact per seed"))
    seeds = set()
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_trace_artifact", "trace artifact records must be objects"))
            continue
        seeds.add(item.get("seed"))
        payload = item.get("payload")
        raw = _json_bytes(payload)
        if item.get("sha256") != hashlib.sha256(raw).hexdigest():
            issues.append(_issue("trace_artifact_hash_mismatch", "trace artifact hash does not match its payload"))
        if not isinstance(payload, dict) or payload.get("schema") != MATRIX_CASCADE_SEED_TRACE_SCHEMA:
            issues.append(_issue("invalid_trace_schema", "trace artifact payload schema is invalid"))
    if seeds != set(MATRIX_CASCADE_FIXTURE_SEEDS):
        issues.append(_issue("trace_seed_coverage_mismatch", "trace artifacts must cover all fixture seeds"))
    return len(value)


def _validate_runtime_trace_linkage(
    boundary: object,
    trace_artifacts: object,
    issues: list[MatrixCascadeFixtureIssue],
) -> None:
    if not isinstance(boundary, dict) or not isinstance(trace_artifacts, list):
        return
    records = boundary.get("emitted_records")
    if not isinstance(records, list):
        return
    artifacts_by_seed = {
        item.get("seed"): item
        for item in trace_artifacts
        if isinstance(item, dict)
    }
    records_by_seed = {
        item.get("seed"): item
        for item in records
        if isinstance(item, dict)
    }
    for seed in MATRIX_CASCADE_FIXTURE_SEEDS:
        artifact = artifacts_by_seed.get(seed)
        record = records_by_seed.get(seed)
        if not isinstance(artifact, dict) or not isinstance(record, dict):
            continue
        payload = artifact.get("payload")
        stage_traces = payload.get("stage_traces") if isinstance(payload, dict) else None
        if record.get("stage_traces") != stage_traces:
            issues.append(_issue("runtime_trace_payload_mismatch", f"runtime stage traces do not match seed {seed} artifact payload"))
        if record.get("artifact_paths") != [artifact.get("path")]:
            issues.append(_issue("runtime_trace_path_mismatch", f"runtime artifact path does not match seed {seed} trace"))
        if record.get("artifact_sha256") != artifact.get("sha256"):
            issues.append(_issue("runtime_trace_hash_mismatch", f"runtime artifact hash does not match seed {seed} trace"))


def _load_report(
    value: object | str | Path,
) -> tuple[dict[str, Any] | None, list[MatrixCascadeFixtureIssue]]:
    if isinstance(value, dict):
        return copy.deepcopy(value), []
    if isinstance(value, str) and value.lstrip().startswith("{"):
        try:
            loaded = json.loads(value)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"fixture report JSON is invalid: {exc}")]
    else:
        try:
            loaded = json.loads(Path(value).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_report", f"fixture report could not be loaded: {exc}")]
    if not isinstance(loaded, dict):
        return None, [_issue("invalid_shape", "fixture report must be a JSON object")]
    return loaded, []


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _issue(code: str, message: str) -> MatrixCascadeFixtureIssue:
    return MatrixCascadeFixtureIssue(code, message)
