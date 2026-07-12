from __future__ import annotations

import ast
import copy
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from libreevolve.core.config import Config
from libreevolve.core.loop import evolve
from libreevolve.population.program import Program
from libreevolve.problems.benchmarks.companion_sources import (
    alphaevolve_companion_artifact_rights_record,
)
from libreevolve.problems.benchmarks.matrix_cascade_fixture import (
    MATRIX_CASCADE_FIXTURE_SEEDS,
    MATRIX_EXAMPLE_ROOT,
    matrix_cascade_fixture_stages,
)
from libreevolve.problems.benchmarks.matrix_results import (
    MATRIX_CASCADE_RUN_RUNTIME_SCHEMA,
    MATRIX_RESULT_SCHEMA,
    matrix_cascade_run_runtime_boundary_from_matrix_result,
    strassen_2x2_publication_bundle_record,
    validate_matrix_cascade_run_runtime_boundary,
    validate_matrix_result_report,
)
from libreevolve.problems.loader import load_problem


MATRIX_EVOLUTION_FIXTURE_SCHEMA = "libreevolve.matrix_evolution_fixture_report.v1"
MATRIX_EVOLUTION_SEED_RUN_SCHEMA = "libreevolve.matrix_evolution_seed_run.v1"
MATRIX_EVOLUTION_SEARCH_SUMMARY_SCHEMA = "libreevolve.matrix_evolution_search_summary.v1"
MATRIX_EVOLUTION_FIXTURE_BUNDLE_SCHEMA = "libreevolve.matrix_evolution_fixture_bundle.v1"
MATRIX_EVOLUTION_FIXTURE_ROOT = (
    Path(__file__).resolve().parent / "artifacts" / "matrix_evolution_fixture"
)
MATRIX_EVOLUTION_FIXTURE_REPORT_PATH = Path(
    "matrix/mm_2x2x2/evolution_fixture_report.json"
)
MATRIX_EVOLUTION_MATRIX_RESULT_PATH = Path(
    "matrix/mm_2x2x2/evolution_matrix_result.json"
)
MATRIX_EVOLUTION_SEARCH_SUMMARY_PATH = Path(
    "matrix/mm_2x2x2/evolution_search_summary.json"
)
MATRIX_EVOLUTION_CASCADE_BOUNDARY_PATH = Path(
    "matrix/mm_2x2x2/evolution_cascade_boundary.json"
)
MATRIX_EVOLUTION_TARGET_ID = "mm_2x2x2"
MATRIX_EVOLUTION_CASCADE_ID = "matrix_rank_evolution_search"
MATRIX_EVOLUTION_CASCADE_VERSION = "v1"
MATRIX_EVOLUTION_SCRIPTED_MODEL = "matrix-scripted-rank7-v1"


class ScriptedStrassenMutationBackend:
    """Checked control backend that emits one canonical rank-7 mutation."""

    api_mode = "custom"

    def __init__(self, model: str, max_tokens: int | None = None):
        self.model = model
        self.max_tokens = max_tokens

    @property
    def name(self) -> str:
        return f"matrix-scripted/{self.model}"

    def generate(self, prompt: str, **kwargs: object) -> str:
        del prompt, kwargs
        return _scripted_strassen_diff()


def matrix_evolution_scripted_backend_specs() -> list[dict[str, Any]]:
    return [
        {
            "type": "custom",
            "model": MATRIX_EVOLUTION_SCRIPTED_MODEL,
            "class_path": (
                "libreevolve.problems.benchmarks.matrix_evolution_fixture:"
                "ScriptedStrassenMutationBackend"
            ),
            "max_tokens": 4096,
        }
    ]


def matrix_evolution_fixture_stages() -> list[dict[str, Any]]:
    """Return the search cascade; rank 8 stays eligible as the parent."""
    stages = matrix_cascade_fixture_stages()
    stages[1]["hypothesis_test"]["min"] = 0.12
    stages[1]["difficulty_or_scale"]["rationale"] = (
        "Broader exact-arithmetic search evaluation that retains the valid rank-8 baseline."
    )
    return stages


def run_matrix_evolution_fixture(
    *,
    backend_specs: list[dict[str, Any]] | None = None,
    search_seeds: tuple[int, ...] = MATRIX_CASCADE_FIXTURE_SEEDS,
    work_root: str | Path | None = None,
) -> dict[str, Any]:
    """Execute independent one-generation matrix searches through evolve()."""
    specs = copy.deepcopy(
        matrix_evolution_scripted_backend_specs()
        if backend_specs is None
        else backend_specs
    )
    fixture_mode = (
        "scripted_control"
        if specs == matrix_evolution_scripted_backend_specs()
        else "configured_backend_search"
    )
    if not search_seeds or len(set(search_seeds)) != len(search_seeds):
        raise ValueError("search_seeds must be non-empty and unique")
    if any(isinstance(seed, bool) or not isinstance(seed, int) for seed in search_seeds):
        raise ValueError("search_seeds must contain integers")
    if work_root is None:
        with tempfile.TemporaryDirectory(prefix="libreevolve-matrix-search-") as tmp:
            return _run_matrix_evolution_fixture(
                specs,
                tuple(search_seeds),
                Path(tmp),
                fixture_mode,
            )
    return _run_matrix_evolution_fixture(
        specs,
        tuple(search_seeds),
        Path(work_root),
        fixture_mode,
    )


def _run_matrix_evolution_fixture(
    backend_specs: list[dict[str, Any]],
    search_seeds: tuple[int, ...],
    work_root: Path,
    fixture_mode: str,
) -> dict[str, Any]:
    problem = load_problem(MATRIX_EXAMPLE_ROOT)
    stage_config = matrix_evolution_fixture_stages()
    seed_payloads: list[dict[str, Any]] = []
    for search_seed in search_seeds:
        problem_name = f"matrix_evolution_seed_{search_seed}"
        config = Config(
            max_generations=1,
            max_evaluations=2,
            proposals_per_generation=1,
            num_inspirations=0,
            parent_selection_strategy="exploit",
            initial_program_validity_policy="alphaevolve_strict",
            eval_stages=copy.deepcopy(stage_config),
            backends=copy.deepcopy(backend_specs),
            max_llm_calls=1,
            llm_max_retries=0,
            llm_fallback=False,
            n_islands=5,
            log_dir=str(work_root),
            problem_name=problem_name,
            run_id=f"matrix-evolution-fixture-seed-{search_seed}",
            seed=search_seed,
        )
        best = evolve(problem, config)
        if best is None:
            raise ValueError(f"matrix evolution seed {search_seed} produced no final program")
        run_dir = work_root / problem_name
        seed_payloads.append(
            _seed_run_payload(
                search_seed=search_seed,
                run_dir=run_dir,
                config=config,
                best=best,
                fixture_mode=fixture_mode,
            )
        )
    seed_artifacts = [_seed_artifact(payload) for payload in seed_payloads]
    search_summary = _search_summary_payload(seed_artifacts, fixture_mode)
    search_summary_artifact = _payload_artifact(
        MATRIX_EVOLUTION_SEARCH_SUMMARY_PATH,
        search_summary,
    )
    matrix_result_report = _matrix_result_report(
        seed_payloads,
        search_summary_artifact,
    )
    matrix_result_artifact = _payload_artifact(
        MATRIX_EVOLUTION_MATRIX_RESULT_PATH,
        matrix_result_report,
    )
    stage_traces = {
        payload["search_seed"]: payload["stage_traces"]
        for payload in seed_payloads
    }
    paths_by_seed = {
        artifact["seed"]: [artifact["path"]]
        for artifact in seed_artifacts
    }
    hashes_by_seed = {
        artifact["seed"]: artifact["sha256"]
        for artifact in seed_artifacts
    }
    runtime_boundary = matrix_cascade_run_runtime_boundary_from_matrix_result(
        run_id="matrix_evolution_fixture_v1",
        cascade_id=MATRIX_EVOLUTION_CASCADE_ID,
        cascade_version=MATRIX_EVOLUTION_CASCADE_VERSION,
        matrix_result_report=matrix_result_report,
        matrix_result_ref=MATRIX_EVOLUTION_MATRIX_RESULT_PATH.as_posix(),
        stage_traces_by_seed=stage_traces,
        artifact_paths_by_seed=paths_by_seed,
        artifact_sha256_by_seed=hashes_by_seed,
    )
    runtime_boundary_artifact = _payload_artifact(
        MATRIX_EVOLUTION_CASCADE_BOUNDARY_PATH,
        runtime_boundary,
    )
    report = {
        "schema": MATRIX_EVOLUTION_FIXTURE_SCHEMA,
        "source_paper_id": "2506.13131",
        "source_section_id": "3.1",
        "fixture_scope": "normal_evolve_pipeline_per_seed_search_fixture",
        "fixture_mode": fixture_mode,
        "target_id": MATRIX_EVOLUTION_TARGET_ID,
        "search_seeds": list(search_seeds),
        "backend_specs": copy.deepcopy(backend_specs),
        "search_config": {
            "max_generations": 1,
            "proposals_per_generation": 1,
            "max_evaluations": 2,
            "max_llm_calls": 1,
            "n_islands": 5,
            "parent_selection_strategy": "exploit",
            "initial_program_validity_policy": "alphaevolve_strict",
            "mutation_mode": "diff",
            "stage_config": copy.deepcopy(stage_config),
        },
        "seed_artifacts": seed_artifacts,
        "search_summary_artifact": search_summary_artifact,
        "matrix_result_schema": MATRIX_RESULT_SCHEMA,
        "matrix_result_artifact": matrix_result_artifact,
        "runtime_boundary_schema": MATRIX_CASCADE_RUN_RUNTIME_SCHEMA,
        "runtime_boundary_artifact": runtime_boundary_artifact,
        "runtime_boundary": runtime_boundary,
        "search_evidence_status": "executed_normal_evolve_pipeline",
        "claim_ready": False,
        "claim_boundary": (
            "This fixture executes independent run-local searches through the normal "
            "LibreEvolve evolve, prompt, mutation, cascade, archive, budget, and lineage "
            "pipeline. The checked artifact uses a scripted rank-7 mutation control; it "
            "does not claim stochastic LLM discovery, Strassen rediscovery, AlphaEvolve "
            "matrix-decomposition formulation parity, comparable search budgets, target-"
            "suite scale, or a new matrix result."
        ),
    }
    validation = validate_matrix_evolution_fixture_report(report)
    if not validation["ok"]:
        raise ValueError(
            "generated matrix evolution fixture is invalid: "
            + "; ".join(issue["message"] for issue in validation["issues"])
        )
    return report


def write_matrix_evolution_fixture_bundle(
    artifact_root: str | Path = MATRIX_EVOLUTION_FIXTURE_ROOT,
    *,
    backend_specs: list[dict[str, Any]] | None = None,
    search_seeds: tuple[int, ...] = MATRIX_CASCADE_FIXTURE_SEEDS,
) -> dict[str, Any]:
    root = Path(artifact_root)
    report = run_matrix_evolution_fixture(
        backend_specs=backend_specs,
        search_seeds=search_seeds,
    )
    artifacts = [
        *report["seed_artifacts"],
        report["search_summary_artifact"],
        report["matrix_result_artifact"],
        report["runtime_boundary_artifact"],
    ]
    for artifact in artifacts:
        path = root / artifact["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_json_bytes(artifact["payload"]))
    report_path = root / MATRIX_EVOLUTION_FIXTURE_REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_bytes(_json_bytes(report))
    return matrix_evolution_fixture_bundle_record(root)


def matrix_evolution_fixture_bundle_record(
    artifact_root: str | Path = MATRIX_EVOLUTION_FIXTURE_ROOT,
) -> dict[str, Any]:
    root = Path(artifact_root)
    report_path = root / MATRIX_EVOLUTION_FIXTURE_REPORT_PATH
    report = json.loads(report_path.read_text(encoding="utf-8"))
    return {
        "schema": MATRIX_EVOLUTION_FIXTURE_BUNDLE_SCHEMA,
        "artifact_root": str(root),
        "report_path": MATRIX_EVOLUTION_FIXTURE_REPORT_PATH.as_posix(),
        "report_sha256": _file_sha256(report_path),
        "report_bytes": report_path.stat().st_size,
        "report": report,
        "generation_command": (
            "py -3.12 -c \"from libreevolve.problems.benchmarks."
            "matrix_evolution_fixture import write_matrix_evolution_fixture_bundle; "
            "write_matrix_evolution_fixture_bundle()\""
        ),
    }


def write_matrix_evolution_fixture_paper_boundary(
    path: str | Path,
    artifact_root: str | Path = MATRIX_EVOLUTION_FIXTURE_ROOT,
) -> Path:
    root = Path(artifact_root)
    validation = validate_matrix_evolution_fixture_bundle(root)
    if not validation["ok"]:
        raise ValueError(
            "matrix evolution fixture bundle is invalid: "
            + "; ".join(issue["message"] for issue in validation["issues"])
        )
    report = matrix_evolution_fixture_bundle_record(root)["report"]
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(_json_bytes(report["runtime_boundary"]))
    return output


def validate_matrix_evolution_fixture_report(
    report: object | str | Path,
) -> dict[str, Any]:
    data, issues = _load_report(report)
    if data is None:
        return {"ok": False, "seed_count": 0, "issues": issues}
    if data.get("schema") != MATRIX_EVOLUTION_FIXTURE_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported matrix evolution fixture schema"))
    if data.get("source_paper_id") != "2506.13131" or data.get("source_section_id") != "3.1":
        issues.append(_issue("invalid_source", "fixture must cite AlphaEvolve Section 3.1"))
    if data.get("fixture_scope") != "normal_evolve_pipeline_per_seed_search_fixture":
        issues.append(_issue("invalid_fixture_scope", "fixture scope must identify normal evolve pipeline searches"))
    mode = data.get("fixture_mode")
    if mode not in {"scripted_control", "configured_backend_search"}:
        issues.append(_issue("invalid_fixture_mode", "fixture_mode is invalid"))
    seeds = data.get("search_seeds")
    if not isinstance(seeds, list) or not seeds or len(set(seeds)) != len(seeds):
        issues.append(_issue("invalid_search_seeds", "search_seeds must be non-empty and unique"))
        seeds = []
    seed_artifacts = data.get("seed_artifacts")
    if not isinstance(seed_artifacts, list) or len(seed_artifacts) != len(seeds):
        issues.append(_issue("invalid_seed_artifacts", "one seed artifact is required per search seed"))
        seed_artifacts = []
    observed_seeds: set[int] = set()
    for artifact in seed_artifacts:
        if not _validate_payload_artifact(artifact, issues, expected_schema=MATRIX_EVOLUTION_SEED_RUN_SCHEMA):
            continue
        seed = artifact.get("seed")
        payload = artifact["payload"]
        observed_seeds.add(seed)
        _validate_seed_payload(payload, mode, issues)
    if observed_seeds != set(seeds):
        issues.append(_issue("seed_artifact_coverage_mismatch", "seed artifacts do not cover search_seeds"))
    _validate_payload_artifact(
        data.get("search_summary_artifact"),
        issues,
        expected_schema=MATRIX_EVOLUTION_SEARCH_SUMMARY_SCHEMA,
    )
    matrix_artifact = data.get("matrix_result_artifact")
    if _validate_payload_artifact(matrix_artifact, issues, expected_schema=MATRIX_RESULT_SCHEMA):
        matrix_validation = validate_matrix_result_report(matrix_artifact["payload"])
        issues.extend(
            _issue(f"matrix_result_{item.code}", item.message)
            for item in matrix_validation.issues
        )
        if matrix_artifact["payload"].get("alphaevolve_comparable") is not False:
            issues.append(_issue("matrix_result_overclaim", "fixture matrix result must remain non-comparable"))
    boundary_artifact = data.get("runtime_boundary_artifact")
    _validate_payload_artifact(
        boundary_artifact,
        issues,
        expected_schema=MATRIX_CASCADE_RUN_RUNTIME_SCHEMA,
    )
    runtime_boundary = data.get("runtime_boundary")
    runtime_validation = validate_matrix_cascade_run_runtime_boundary(runtime_boundary)
    issues.extend(
        _issue(f"runtime_boundary_{item.code}", item.message)
        for item in runtime_validation.issues
    )
    if isinstance(boundary_artifact, dict) and boundary_artifact.get("payload") != runtime_boundary:
        issues.append(_issue("runtime_boundary_artifact_mismatch", "runtime boundary artifact payload drifted"))
    if runtime_validation.emitted_record_count != len(seeds):
        issues.append(_issue("runtime_record_count_mismatch", "runtime boundary must emit one record per search seed"))
    _validate_runtime_seed_linkage(runtime_boundary, seed_artifacts, issues)
    if mode == "scripted_control" and data.get("backend_specs") != matrix_evolution_scripted_backend_specs():
        issues.append(_issue("scripted_backend_drift", "scripted fixture backend spec drifted"))
    if data.get("search_evidence_status") != "executed_normal_evolve_pipeline":
        issues.append(_issue("invalid_search_evidence_status", "search evidence status is invalid"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "fixture must not claim AlphaEvolve readiness"))
    claim = data.get("claim_boundary")
    if not isinstance(claim, str) or "does not claim stochastic LLM discovery" not in claim:
        issues.append(_issue("missing_claim_boundary", "fixture must disclaim stochastic LLM discovery"))
    return {"ok": not issues, "seed_count": len(seeds), "issues": issues}


def validate_matrix_evolution_fixture_bundle(
    artifact_root: str | Path = MATRIX_EVOLUTION_FIXTURE_ROOT,
    *,
    verify_regeneration: bool = False,
) -> dict[str, Any]:
    root = Path(artifact_root)
    report_path = root / MATRIX_EVOLUTION_FIXTURE_REPORT_PATH
    validation = validate_matrix_evolution_fixture_report(report_path)
    issues = list(validation["issues"])
    if validation["ok"]:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        artifacts = [
            *report["seed_artifacts"],
            report["search_summary_artifact"],
            report["matrix_result_artifact"],
            report["runtime_boundary_artifact"],
        ]
        for artifact in artifacts:
            path = root / artifact["path"]
            if not path.is_file():
                issues.append(_issue("missing_bundle_artifact", f"missing bundle artifact: {artifact['path']}"))
                continue
            if _file_sha256(path) != artifact["sha256"] or path.stat().st_size != artifact["bytes"]:
                issues.append(_issue("bundle_artifact_hash_mismatch", f"bundle artifact hash/size mismatch: {artifact['path']}"))
            else:
                payload = json.loads(path.read_text(encoding="utf-8"))
                if payload != artifact["payload"]:
                    issues.append(_issue("bundle_artifact_payload_mismatch", f"bundle artifact payload mismatch: {artifact['path']}"))
        if verify_regeneration:
            regenerated = run_matrix_evolution_fixture()
            if _json_bytes(regenerated) != _json_bytes(report):
                issues.append(_issue("regeneration_mismatch", "checked fixture differs from fresh evolve runs"))
    return {"ok": not issues, "seed_count": validation["seed_count"], "issues": issues}


def _seed_run_payload(
    *,
    search_seed: int,
    run_dir: Path,
    config: Config,
    best: Program,
    fixture_mode: str,
) -> dict[str, Any]:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    history = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    compact_history = [_compact_history_row(row) for row in history]
    known_strassen_match = _matmul_function_matches_checked_strassen(best.code)
    exact = bool(known_strassen_match)
    stage_traces = _program_stage_traces(
        best,
        search_seed=search_seed,
        exact=exact,
    )
    runtime = manifest["runtime"]
    consumed = runtime.get("consumed", {})
    retained_consumed = {
        key: consumed.get(key)
        for key in (
            "seed_evaluations",
            "candidate_evaluations",
            "llm_calls",
            "generations_started",
            "generations_completed",
        )
        if key in consumed
    }
    return {
        "schema": MATRIX_EVOLUTION_SEED_RUN_SCHEMA,
        "search_seed": search_seed,
        "run_id": config.run_id,
        "problem_name": config.problem_name,
        "fixture_mode": fixture_mode,
        "runtime_status": runtime.get("status"),
        "stop_reason": runtime.get("stop_reason"),
        "consumed": retained_consumed,
        "history_row_count": len(history),
        "history": compact_history,
        "final_candidate": {
            "candidate_id": best.id,
            "parent_id": best.parent_id,
            "lineage": list(best.lineage),
            "generation": best.generation,
            "rank": int(best.metrics["multiplication_count"]),
            "inverse_multiplications": float(best.metrics["inverse_multiplications"]),
            "is_valid": bool(best.evaluation.get("is_valid")),
            "known_strassen_match": known_strassen_match,
            "exact": exact,
            "workspace_sha256": _workspace_text_sha256(best.files),
        },
        "stage_traces": stage_traces,
        "run_artifact_presence": _run_artifact_presence(run_dir),
    }


def _compact_history_row(row: dict[str, Any]) -> dict[str, Any]:
    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    admission = metadata.get("archive_admission") if isinstance(metadata.get("archive_admission"), dict) else {}
    metrics = row.get("metrics") if isinstance(row.get("metrics"), dict) else {}
    return {
        "candidate_id": row.get("id"),
        "candidate_type": metadata.get("candidate_type"),
        "parent_id": row.get("parent_id"),
        "lineage": copy.deepcopy(row.get("lineage", [])),
        "generation": row.get("generation"),
        "rank": int(metrics["multiplication_count"]),
        "inverse_multiplications": float(metrics["inverse_multiplications"]),
        "is_valid": bool((row.get("evaluation") or {}).get("is_valid")),
        "archive_admitted": admission.get("admitted"),
        "archive_reason": admission.get("reason"),
        "diff_sha256": (
            hashlib.sha256(metadata["diff"].encode("utf-8")).hexdigest()
            if isinstance(metadata.get("diff"), str)
            else None
        ),
    }


def _program_stage_traces(
    program: Program,
    *,
    search_seed: int,
    exact: bool,
) -> list[dict[str, Any]]:
    metadata = program.evaluation.get("metadata")
    configured = metadata.get("configured_stage_results") if isinstance(metadata, dict) else None
    if not isinstance(configured, list) or not configured:
        raise ValueError("final matrix program lacks configured stage results")
    rows = []
    for index, stage in enumerate(configured):
        hypothesis = stage.get("hypothesis_test_result")
        threshold = stage.get("threshold")
        if threshold is None and isinstance(hypothesis, dict):
            threshold = hypothesis.get("min")
        stage_metadata = stage.get("metadata")
        sample_count = stage_metadata.get("sample_count") if isinstance(stage_metadata, dict) else 1
        rows.append(
            {
                "stage_label": stage["name"],
                "stage_index": stage["stage_index"],
                "search_seed": search_seed,
                "candidate_id": program.id,
                "parent_id": program.parent_id,
                "lineage": list(program.lineage),
                "generation": program.generation,
                "threshold": float(threshold),
                "rank": int(program.metrics["multiplication_count"]),
                "exact": exact,
                "sample_count": sample_count,
                "metrics": copy.deepcopy(stage["metrics"]),
                "hypothesis_test_result": copy.deepcopy(hypothesis),
                "stop_reason": (
                    "accepted_final_candidate"
                    if index == len(configured) - 1
                    else "promoted_to_next_stage"
                ),
            }
        )
    return rows


def _seed_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    seed = payload["search_seed"]
    artifact = _payload_artifact(
        Path(f"matrix/mm_2x2x2/evolution_seed_{seed}.json"),
        payload,
    )
    artifact["seed"] = seed
    return artifact


def _search_summary_payload(
    seed_artifacts: list[dict[str, Any]],
    fixture_mode: str,
) -> dict[str, Any]:
    return {
        "schema": MATRIX_EVOLUTION_SEARCH_SUMMARY_SCHEMA,
        "target_id": MATRIX_EVOLUTION_TARGET_ID,
        "fixture_mode": fixture_mode,
        "seed_count": len(seed_artifacts),
        "seed_outcomes": [
            {
                "seed": artifact["seed"],
                "run_id": artifact["payload"]["run_id"],
                **copy.deepcopy(artifact["payload"]["final_candidate"]),
                "seed_artifact_path": artifact["path"],
                "seed_artifact_sha256": artifact["sha256"],
            }
            for artifact in seed_artifacts
        ],
        "claim_boundary": (
            "Search outcomes come from normal evolve() runs. Scripted-control mode "
            "does not establish stochastic LLM discovery."
        ),
    }


def _matrix_result_report(
    seed_payloads: list[dict[str, Any]],
    search_summary_artifact: dict[str, Any],
) -> dict[str, Any]:
    ranks = [payload["final_candidate"]["rank"] for payload in seed_payloads]
    best_rank = min(ranks)
    seed_results = [
        {
            "seed": payload["search_seed"],
            "rank": payload["final_candidate"]["rank"],
            "achieved_best_rank": payload["final_candidate"]["rank"] == best_rank,
            "exact": payload["final_candidate"]["exact"],
        }
        for payload in seed_payloads
    ]
    hit_count = sum(row["achieved_best_rank"] for row in seed_results)
    all_exact = all(row["exact"] for row in seed_results)
    strassen_bundle = strassen_2x2_publication_bundle_record()
    return {
        "schema": MATRIX_RESULT_SCHEMA,
        "target_suite": "alphaevolve_appendix_a",
        "target_id": MATRIX_EVOLUTION_TARGET_ID,
        "dimensions": [2, 2, 2],
        "seed_count": len(seed_results),
        "best_rank": best_rank,
        "hit_count": hit_count,
        "hit_fraction": hit_count / len(seed_results),
        "seed_results": seed_results,
        "coefficient_domain": "integer",
        "exactness_certificate": (
            {
                "status": "verified",
                "method": "checked_strassen_symbolic_tensor_identity_match",
                "certificate_sha256": strassen_bundle["report"]["exactness_certificate"]["certificate_sha256"],
            }
            if all_exact and best_rank == 7
            else {
                "status": "not_checked",
                "method": "finite_case_validator_only",
            }
        ),
        "artifacts": [
            {
                "kind": "summary",
                "path": search_summary_artifact["path"],
                "sha256": search_summary_artifact["sha256"],
                "bytes": search_summary_artifact["bytes"],
                "source_rights": alphaevolve_companion_artifact_rights_record("summary"),
            }
        ],
        "alphaevolve_comparable": False,
    }


def _payload_artifact(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    raw = _json_bytes(payload)
    return {
        "path": path.as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "payload": payload,
    }


def _validate_seed_payload(
    payload: dict[str, Any],
    mode: object,
    issues: list[dict[str, str]],
) -> None:
    if payload.get("runtime_status") != "completed" or payload.get("stop_reason") != "max_evaluations":
        issues.append(_issue("seed_run_not_completed", "seed run must complete one generation at the two-evaluation budget"))
    final = payload.get("final_candidate")
    if not isinstance(final, dict) or not isinstance(final.get("rank"), int):
        issues.append(_issue("invalid_final_candidate", "seed run final candidate is invalid"))
        return
    history = payload.get("history")
    if not isinstance(history, list) or not history:
        issues.append(_issue("missing_search_history", "seed run must retain compact history"))
    traces = payload.get("stage_traces")
    if not isinstance(traces, list) or len(traces) != 2:
        issues.append(_issue("invalid_stage_traces", "seed run must retain both cascade stages"))
    if mode == "scripted_control":
        if final.get("rank") != 7 or final.get("generation") != 1:
            issues.append(_issue("scripted_control_not_improved", "scripted run must produce rank 7 at generation 1"))
        if not final.get("parent_id") or final.get("lineage") == []:
            issues.append(_issue("missing_scripted_lineage", "scripted run must retain parent and lineage"))
        if final.get("known_strassen_match") is not True or final.get("exact") is not True:
            issues.append(_issue("scripted_strassen_match_failed", "scripted result must match checked Strassen"))


def _validate_payload_artifact(
    artifact: object,
    issues: list[dict[str, str]],
    *,
    expected_schema: str,
) -> bool:
    if not isinstance(artifact, dict):
        issues.append(_issue("invalid_payload_artifact", "payload artifact must be an object"))
        return False
    payload = artifact.get("payload")
    if not isinstance(payload, dict) or payload.get("schema") != expected_schema:
        issues.append(_issue("invalid_payload_schema", f"payload artifact must use {expected_schema}"))
        return False
    raw = _json_bytes(payload)
    if artifact.get("sha256") != hashlib.sha256(raw).hexdigest() or artifact.get("bytes") != len(raw):
        issues.append(_issue("payload_artifact_hash_mismatch", "payload artifact hash/size mismatch"))
        return False
    path = artifact.get("path")
    if not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts:
        issues.append(_issue("invalid_payload_artifact_path", "payload artifact path is unsafe"))
        return False
    return True


def _validate_runtime_seed_linkage(
    boundary: object,
    seed_artifacts: list[dict[str, Any]],
    issues: list[dict[str, str]],
) -> None:
    if not isinstance(boundary, dict) or not isinstance(boundary.get("emitted_records"), list):
        return
    artifacts = {item.get("seed"): item for item in seed_artifacts}
    for record in boundary["emitted_records"]:
        if not isinstance(record, dict):
            continue
        artifact = artifacts.get(record.get("seed"))
        if not isinstance(artifact, dict):
            continue
        payload = artifact["payload"]
        final = payload["final_candidate"]
        if record.get("artifact_paths") != [artifact["path"]] or record.get("artifact_sha256") != artifact["sha256"]:
            issues.append(_issue("runtime_seed_artifact_mismatch", "runtime record does not link its seed artifact"))
        if record.get("final_candidate_id") != final["candidate_id"] or record.get("accepted_final_rank") != final["rank"]:
            issues.append(_issue("runtime_seed_result_mismatch", "runtime record final candidate/rank drifted"))
        if record.get("stage_traces") != payload["stage_traces"]:
            issues.append(_issue("runtime_seed_trace_mismatch", "runtime record stage traces drifted"))


def _run_artifact_presence(run_dir: Path) -> list[dict[str, Any]]:
    records = []
    for name in (
        "manifest.json",
        "history.jsonl",
        "evaluator_results.jsonl",
        "llm_calls.jsonl",
        "prompt_history.jsonl",
        "archive_events.jsonl",
    ):
        path = run_dir / name
        records.append(
            {
                "path": name,
                "present": path.is_file(),
                "row_count": (
                    sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
                    if path.is_file() and path.suffix == ".jsonl"
                    else None
                ),
            }
        )
    return records


def _matmul_function_matches_checked_strassen(code: str) -> bool:
    expected = (MATRIX_EXAMPLE_ROOT / "benchmark_candidates" / "strassen_rank7.py").read_text(
        encoding="utf-8"
    )
    return _matmul_ast(code) == _matmul_ast(expected)


def _matmul_ast(code: str) -> str | None:
    tree = ast.parse(code)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "matmul2":
            return ast.dump(node, include_attributes=False)
    return None


def _scripted_strassen_diff() -> str:
    seed = (MATRIX_EXAMPLE_ROOT / "initial_programs" / "seed.py").read_text(encoding="utf-8")
    replacement = (
        MATRIX_EXAMPLE_ROOT / "benchmark_candidates" / "strassen_rank7.py"
    ).read_text(encoding="utf-8").strip()
    start_marker = "# EVOLVE-BLOCK-START matmul\n"
    end_marker = "\n# EVOLVE-BLOCK-END"
    start = seed.index(start_marker) + len(start_marker)
    end = seed.index(end_marker, start)
    search = seed[start:end]
    return (
        "<<<<<<< SEARCH\n"
        f"{search}\n"
        "=======\n"
        f"{replacement}\n"
        ">>>>>>> REPLACE"
    )


def _workspace_text_sha256(files: dict[str, str]) -> str:
    payload = json.dumps(files, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_report(
    value: object | str | Path,
) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
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


def _issue(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}
