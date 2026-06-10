from __future__ import annotations

import json
import hashlib
import math
import re
import tempfile
import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    EXPECTED_TARGET_COUNT as APPENDIX_A_EXPECTED_TARGET_COUNT,
    TARGET_SUITE as APPENDIX_A_TARGET_SUITE,
    matrix_target_by_id,
    matrix_target_records,
)
from libreevolve.problems.benchmarks.companion_sources import (
    alphaevolve_companion_artifact_rights_record,
    validate_alphaevolve_companion_selection_scope,
    validate_alphaevolve_companion_artifact_rights,
)


MATRIX_RESULT_SCHEMA = "libreevolve.matrix_result_report.v1"
MATRIX_ARTIFACT_INVENTORY_SCHEMA = "libreevolve.matrix_result_artifact_inventory.v1"
MATRIX_PUBLICATION_BUNDLE_SCHEMA = "libreevolve.matrix_publication_bundle.v1"
MATRIX_SUITE_PUBLICATION_ARTIFACT_BOUNDARY_SCHEMA = "libreevolve.matrix_suite_publication_artifact_boundary.v1"
MATRIX_BASELINE_COMPONENT_RUNTIME_SCHEMA = "libreevolve.matrix_baseline_component_runtime_boundary.v1"
MATRIX_CASCADE_RUN_RUNTIME_SCHEMA = "libreevolve.matrix_cascade_run_runtime_boundary.v1"
MATRIX_NEAR_INTEGRALITY_SCHEMA = "libreevolve.matrix_near_integrality_evidence.v1"
MATRIX_NEAR_INTEGRALITY_RUNTIME_SCHEMA = "libreevolve.matrix_near_integrality_runtime_boundary.v1"
MATRIX_SWEEP_SPACE_SCHEMA = "libreevolve.matrix_sweep_space_evidence.v1"
MATRIX_SWEEP_SPACE_RUNTIME_SCHEMA = "libreevolve.matrix_sweep_space_runtime_boundary.v1"
MATRIX_SCALAR_FIELD_SCHEMA = "libreevolve.matrix_scalar_field_evidence.v1"
MATRIX_SCALAR_FIELD_RUNTIME_SCHEMA = "libreevolve.matrix_scalar_field_runtime_boundary.v1"
MATRIX_TENSOR_RANK_SCHEMA = "libreevolve.matrix_tensor_rank_evidence.v1"
MATRIX_TENSOR_RANK_RUNTIME_SCHEMA = "libreevolve.matrix_tensor_rank_runtime_boundary.v1"
MATRIX_HEADLINE_HISTORICITY_SCHEMA = "libreevolve.matrix_headline_historicity_evidence.v1"
MATRIX_HEADLINE_HISTORICITY_RUNTIME_SCHEMA = "libreevolve.matrix_headline_historicity_runtime_boundary.v1"
STRASSEN_2X2_PUBLICATION_BUNDLE_ROOT = (
    Path(__file__).resolve().parent
    / "artifacts"
    / "strassen_2x2_publication_bundle"
)
STRASSEN_2X2_PUBLICATION_BUNDLE_SEEDS = (0, 1, 2, 3)
STRASSEN_2X2_PUBLICATION_BUNDLE_FILES = (
    "matrix/mm_2x2x2/algorithm.json",
    "matrix/mm_2x2x2/certificate.json",
    "matrix/mm_2x2x2/reproduce.ipynb",
    "matrix/mm_2x2x2/report.json",
    "matrix/mm_2x2x2/inventory.json",
)
COEFFICIENT_DOMAINS = frozenset({"integer", "half_integer", "rational", "float"})
PUBLICATION_COEFFICIENT_DOMAINS = frozenset({"integer", "half_integer"})
EXACTNESS_STATUSES = frozenset({"verified", "failed", "not_checked"})
ARTIFACT_KINDS = frozenset({"algorithm", "certificate", "summary", "notebook"})
MATRIX_SUITE_PUBLICATION_ARTIFACT_STATUSES = frozenset({"not_generated_locally", "generated"})
MATRIX_SUITE_PUBLICATION_ARTIFACT_REQUIRED_FIELDS = (
    "target_id",
    "dimensions",
    "target_tensor_ref",
    "target_tensor_sha256",
    "algorithm_ref",
    "algorithm_sha256",
    "coefficient_domain",
    "coefficient_data_ref",
    "coefficient_data_sha256",
    "exactness_certificate_ref",
    "exactness_certificate_sha256",
    "notebook_ref",
    "notebook_sha256",
    "per_seed_report_ref",
    "per_seed_report_sha256",
    "matrix_result_report",
    "artifact_inventory",
    "publication_bundle_ref",
    "artifact_paths",
    "artifact_sha256",
)
MATRIX_BASELINE_COMPONENT_RUNTIME_STATUSES = frozenset({"not_emitted_by_local_runner", "emitted"})
MATRIX_BASELINE_COMPONENT_REQUIRED_NAMES = frozenset({"initializer", "reconstruction_loss", "optimizer"})
MATRIX_BASELINE_COMPONENT_MUTABILITY = frozenset({"fixed", "mutable"})
MATRIX_BASELINE_COMPONENT_RUNTIME_REQUIRED_FIELDS = (
    "run_id",
    "target_id",
    "baseline_program_id",
    "component_records",
    "initializer_ref",
    "reconstruction_loss_ref",
    "optimizer_ref",
    "optimizer_name",
    "optimizer_version",
    "optimizer_config",
    "mutable_component_scopes",
    "fixed_component_hashes",
    "generation0_metrics",
    "mutation_lineage",
    "matrix_result_ref",
    "artifact_paths",
    "artifact_sha256",
)
MATRIX_CASCADE_RUN_RUNTIME_STATUSES = frozenset({"not_emitted_by_local_runner", "emitted"})
MATRIX_CASCADE_RUN_RUNTIME_REQUIRED_FIELDS = (
    "run_id",
    "target_id",
    "seed",
    "cascade_id",
    "cascade_version",
    "stage_traces",
    "accepted_final_rank",
    "stop_reason",
    "final_candidate_id",
    "matrix_result_ref",
    "matrix_result_report",
    "artifact_paths",
    "artifact_sha256",
)
NEAR_INTEGRAL_ROUNDING_DOMAINS = frozenset({"integer", "half_integer"})
SWEEP_SOURCE_FIGURES = frozenset({"Figures 9a-9c"})
SWEEP_DISTRIBUTIONS = frozenset({"uniform", "log_uniform", "choice"})
SWEEP_DTYPES = frozenset({"float", "int"})
SCALAR_FIELD_TYPES = frozenset({"real", "complex", "finite_field", "any_field"})
SCALAR_FIELD_CHARACTERISTICS = frozenset({"zero", "positive", "any"})
SCALAR_FIELD_APPLICABILITY = frozenset({"real_matrices", "complex_matrices", "finite_field_matrices", "all_fields"})
SCALAR_FIELD_CERTIFICATE_SCOPES = frozenset({"real_only", "complex_only", "complex_and_real", "finite_field_only", "all_fields"})
SCALAR_FIELD_COEFFICIENT_REPRESENTATIONS = frozenset(
    {
        "integer",
        "half_integer",
        "complex_integer",
        "complex_half_integer",
        "finite_field",
    }
)
PAPER_COMPLEX_TARGET_IDS = frozenset({"mm_3x4x7", "mm_4x4x4", "mm_4x4x8"})
MATRIX_ALGORITHM_KINDS = frozenset(
    {
        "matrix_multiplication_tensor_decomposition",
        "non_tensor_multiplication_algorithm",
    }
)
MATRIX_NEAR_INTEGRALITY_RUNTIME_STATUSES = frozenset(
    {"not_emitted_by_local_runner", "emitted"}
)
MATRIX_NEAR_INTEGRALITY_RUNTIME_REQUIRED_FIELDS = (
    "run_id",
    "candidate_id",
    "target_id",
    "seed",
    "prompt_hash",
    "prompt_instruction",
    "raw_coefficients",
    "rounded_coefficients",
    "max_abs_rounding_error",
    "exactness_certificate_ref",
    "matrix_result_ref",
    "artifact_paths",
    "artifact_sha256",
)
MATRIX_SWEEP_SPACE_RUNTIME_STATUSES = frozenset(
    {"not_emitted_by_local_runner", "emitted"}
)
MATRIX_SWEEP_SPACE_RUNTIME_REQUIRED_FIELDS = (
    "run_id",
    "candidate_id",
    "target_id",
    "seed",
    "search_program_ref",
    "sweep_function_name",
    "hyper_library",
    "hyperparameters",
    "sampled_configurations",
    "winning_configuration_id",
    "exactness_certificate_ref",
    "final_decomposition_ref",
    "matrix_result_ref",
    "artifact_paths",
    "artifact_sha256",
)
MATRIX_SCALAR_FIELD_RUNTIME_STATUSES = frozenset(
    {"not_emitted_by_local_runner", "emitted"}
)
MATRIX_SCALAR_FIELD_RUNTIME_REQUIRED_FIELDS = (
    "run_id",
    "candidate_id",
    "target_id",
    "seed",
    "scalar_field",
    "characteristic",
    "applicability",
    "coefficient_representation",
    "algorithm_ref",
    "certificate_ref",
    "matrix_result_ref",
    "artifact_paths",
    "artifact_sha256",
)
MATRIX_TENSOR_RANK_RUNTIME_STATUSES = frozenset(
    {"not_emitted_by_local_runner", "emitted"}
)
MATRIX_TENSOR_RANK_RUNTIME_REQUIRED_FIELDS = (
    "run_id",
    "candidate_id",
    "target_id",
    "seed",
    "algorithm_kind",
    "rank",
    "recursive_applicable",
    "certificate_scope",
    "tensor_identity_verified",
    "target_tensor_ref",
    "exactness_certificate_ref",
    "matrix_result_ref",
    "artifact_paths",
    "artifact_sha256",
)
MATRIX_HEADLINE_HISTORICITY_RUNTIME_STATUSES = frozenset(
    {"not_emitted_by_local_runner", "emitted"}
)
MATRIX_HEADLINE_HISTORICITY_RUNTIME_REQUIRED_FIELDS = (
    "run_id",
    "candidate_id",
    "target_id",
    "dimensions",
    "rank",
    "multiplication_count",
    "scalar_field",
    "characteristic",
    "source_refs",
    "prior_comparisons",
    "evidence_links",
    "matrix_result_ref",
    "artifact_paths",
    "artifact_sha256",
)
MATRIX_HEADLINE_TARGET_ID = "mm_4x4x4"
MATRIX_HEADLINE_COMPANION_CLAIM_ID = "appendix_a_matrix_improved_decompositions"
MATRIX_HEADLINE_DIMENSIONS = [4, 4, 4]
MATRIX_HEADLINE_RANK = 48
MATRIX_HEADLINE_BASELINE_RANKS = {
    "strassen_recursive": 49,
    "fawzi_f2": 47,
}
MATRIX_HEADLINE_EVIDENCE_LINK_FIELDS = frozenset(
    {
        "matrix_result_ref",
        "scalar_field_evidence_ref",
        "tensor_rank_evidence_ref",
        "figure4_exhibit_ref",
        "figure9_exhibit_ref",
        "companion_colab_ref",
    }
)
TENSOR_CERTIFICATE_SCOPES = frozenset(
    {
        "matrix_multiplication_tensor_identity",
        "functional_multiplication_only",
        "not_certified",
    }
)
_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_STRASSEN_TARGET_ID = "mm_2x2x2"
_STRASSEN_DIMENSIONS = [2, 2, 2]
_A_BASIS = ("a11", "a12", "a21", "a22")
_B_BASIS = ("b11", "b12", "b21", "b22")
_C_BASIS = ("c11", "c12", "c21", "c22")
_STRASSEN_TERMS = (
    {
        "id": "p1",
        "left": {"a11": 1, "a22": 1},
        "right": {"b11": 1, "b22": 1},
        "output": {"c11": 1, "c22": 1},
    },
    {
        "id": "p2",
        "left": {"a21": 1, "a22": 1},
        "right": {"b11": 1},
        "output": {"c21": 1, "c22": -1},
    },
    {
        "id": "p3",
        "left": {"a11": 1},
        "right": {"b12": 1, "b22": -1},
        "output": {"c12": 1, "c22": 1},
    },
    {
        "id": "p4",
        "left": {"a22": 1},
        "right": {"b21": 1, "b11": -1},
        "output": {"c11": 1, "c21": 1},
    },
    {
        "id": "p5",
        "left": {"a11": 1, "a12": 1},
        "right": {"b22": 1},
        "output": {"c11": -1, "c12": 1},
    },
    {
        "id": "p6",
        "left": {"a21": 1, "a11": -1},
        "right": {"b11": 1, "b12": 1},
        "output": {"c22": 1},
    },
    {
        "id": "p7",
        "left": {"a12": 1, "a22": -1},
        "right": {"b21": 1, "b22": 1},
        "output": {"c11": 1},
    },
)


@dataclass(frozen=True)
class MatrixResultIssue:
    code: str
    message: str


@dataclass(frozen=True)
class MatrixResultValidation:
    ok: bool
    alphaevolve_comparable: bool
    target_id: str | None
    seed_count: int
    best_rank: int | None
    hit_fraction: float | None
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixPublicationBundleValidation:
    ok: bool
    target_id: str | None
    report_ok: bool
    inventory_ok: bool
    alphaevolve_comparable: bool
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixSuitePublicationArtifactBoundaryValidation:
    ok: bool
    artifact_status: str | None
    generated_target_count: int
    required_field_count: int
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixBaselineComponentRuntimeValidation:
    ok: bool
    runtime_emission_status: str | None
    emitted_record_count: int
    required_field_count: int
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixCascadeRunRuntimeValidation:
    ok: bool
    runtime_emission_status: str | None
    emitted_record_count: int
    required_field_count: int
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixNearIntegralityValidation:
    ok: bool
    target_id: str | None
    candidate_count: int
    coefficient_count: int
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixNearIntegralityRuntimeValidation:
    ok: bool
    runtime_emission_status: str | None
    emitted_record_count: int
    required_field_count: int
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixSweepSpaceValidation:
    ok: bool
    target_id: str | None
    hyperparameter_count: int
    sampled_configuration_count: int
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixSweepSpaceRuntimeValidation:
    ok: bool
    runtime_emission_status: str | None
    emitted_record_count: int
    required_field_count: int
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixScalarFieldValidation:
    ok: bool
    target_id: str | None
    field_claim_count: int
    complex_claim_count: int
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixScalarFieldRuntimeValidation:
    ok: bool
    runtime_emission_status: str | None
    emitted_record_count: int
    required_field_count: int
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixTensorRankValidation:
    ok: bool
    target_id: str | None
    claim_count: int
    tensor_decomposition_count: int
    recursive_applicable_count: int
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixTensorRankRuntimeValidation:
    ok: bool
    runtime_emission_status: str | None
    emitted_record_count: int
    required_field_count: int
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixHeadlineHistoricityValidation:
    ok: bool
    target_id: str | None
    prior_comparison_count: int
    source_ref_count: int
    issues: list[MatrixResultIssue]


@dataclass(frozen=True)
class MatrixHeadlineHistoricityRuntimeValidation:
    ok: bool
    runtime_emission_status: str | None
    emitted_record_count: int
    required_field_count: int
    issues: list[MatrixResultIssue]


def validate_matrix_result_report(report: object | str | Path) -> MatrixResultValidation:
    """Validate AlphaEvolve-style matrix result publication metadata."""
    data, read_issues = _load_report(report)
    if read_issues:
        return MatrixResultValidation(False, False, None, 0, None, None, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_RESULT_SCHEMA:
        issues.append(MatrixResultIssue("invalid_schema", "unsupported matrix result schema"))
    target_id = _text_field(data, "target_id", issues)
    target_suite = _text_field(data, "target_suite", issues)
    dimensions = data.get("dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        issues.append(MatrixResultIssue("invalid_dimensions", "dimensions must be a non-empty list"))
    else:
        for value in dimensions:
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                issues.append(MatrixResultIssue("invalid_dimensions", "dimensions must be positive integers"))
                break
    if (
        target_id is not None
        and target_suite == APPENDIX_A_TARGET_SUITE
        and isinstance(dimensions, list)
        and all(isinstance(value, int) and not isinstance(value, bool) for value in dimensions)
    ):
        _validate_known_target_dimensions(target_id, dimensions, issues)
    seed_count = _positive_int(data.get("seed_count"), "seed_count", issues)
    best_rank = _positive_int(data.get("best_rank"), "best_rank", issues)
    hit_count = _nonnegative_int(data.get("hit_count"), "hit_count", issues)
    hit_fraction = _finite_fraction(data.get("hit_fraction"), "hit_fraction", issues)
    if seed_count is not None and hit_count is not None and hit_count > seed_count:
        issues.append(MatrixResultIssue("invalid_hit_count", "hit_count must be <= seed_count"))
    if seed_count and hit_count is not None and hit_fraction is not None:
        expected = hit_count / seed_count
        if not math.isclose(hit_fraction, expected, rel_tol=0.0, abs_tol=1e-12):
            issues.append(MatrixResultIssue("invalid_hit_fraction", "hit_fraction must equal hit_count / seed_count"))
    alphaevolve_comparable = data.get("alphaevolve_comparable")
    if not isinstance(alphaevolve_comparable, bool):
        issues.append(MatrixResultIssue("invalid_alphaevolve_comparable", "alphaevolve_comparable must be boolean"))
        alphaevolve_comparable = False
    coefficient_domain = data.get("coefficient_domain")
    if coefficient_domain not in COEFFICIENT_DOMAINS:
        issues.append(MatrixResultIssue("invalid_coefficient_domain", "unsupported coefficient domain"))
    exactness_status = _validate_exactness(data.get("exactness_certificate"), issues)
    all_seeds_exact = _validate_seed_results(data.get("seed_results"), seed_count, best_rank, hit_count, issues)
    artifact_kinds = _validate_artifacts(data.get("artifacts"), issues)
    if target_id == MATRIX_HEADLINE_TARGET_ID:
        _validate_companion_selection_scope(
            data.get("companion_selection_scope"),
            issues,
        )
    if alphaevolve_comparable:
        if coefficient_domain not in PUBLICATION_COEFFICIENT_DOMAINS:
            issues.append(
                MatrixResultIssue(
                    "non_publication_coefficient_domain",
                    "AlphaEvolve-comparable matrix claims require integer or half_integer coefficients",
                )
            )
        if exactness_status != "verified":
            issues.append(MatrixResultIssue("paper_claim_exactness_not_verified", "AlphaEvolve-comparable matrix claims require verified exactness"))
        if all_seeds_exact is False:
            issues.append(MatrixResultIssue("paper_claim_seed_not_exact", "AlphaEvolve-comparable matrix claims require exact per-seed results"))
        missing_artifacts = sorted({"algorithm", "certificate", "notebook"} - artifact_kinds)
        if missing_artifacts:
            issues.append(
                MatrixResultIssue(
                    "missing_publication_artifact",
                    "AlphaEvolve-comparable matrix claims require algorithm, certificate, and notebook artifacts",
                )
            )
    return MatrixResultValidation(
        ok=not issues,
        alphaevolve_comparable=alphaevolve_comparable,
        target_id=target_id,
        seed_count=seed_count or 0,
        best_rank=best_rank,
        hit_fraction=hit_fraction,
        issues=issues,
    )


def matrix_suite_publication_artifact_boundary_record() -> dict[str, Any]:
    return {
        "schema": MATRIX_SUITE_PUBLICATION_ARTIFACT_BOUNDARY_SCHEMA,
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "result_schema": MATRIX_RESULT_SCHEMA,
        "artifact_inventory_schema": MATRIX_ARTIFACT_INVENTORY_SCHEMA,
        "publication_bundle_schema": MATRIX_PUBLICATION_BUNDLE_SCHEMA,
        "artifact_status": "not_generated_locally",
        "local_generation_scope": "appendix_a_matrix_suite_publication_artifacts",
        "registered_target_count": APPENDIX_A_EXPECTED_TARGET_COUNT,
        "checked_baseline_bundle_ref": "strassen_2x2_publication_bundle",
        "required_artifact_fields": list(MATRIX_SUITE_PUBLICATION_ARTIFACT_REQUIRED_FIELDS),
        "generated_target_artifacts": [],
        "claim_boundary": (
            "This is an Appendix A matrix suite publication-artifact boundary. "
            "It does not claim local artifacts include target tensors, discovered "
            "decompositions, coefficient data, exactness certificates, notebooks, "
            "and per-seed reports for every registered Appendix A target."
        ),
    }


def validate_matrix_suite_publication_artifact_boundary(
    boundary: object | str | Path | None = None,
) -> MatrixSuitePublicationArtifactBoundaryValidation:
    data, read_issues = _load_report(
        matrix_suite_publication_artifact_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MatrixSuitePublicationArtifactBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_SUITE_PUBLICATION_ARTIFACT_BOUNDARY_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_schema",
                "unsupported matrix suite publication-artifact boundary schema",
            )
        )
    if data.get("target_suite") != APPENDIX_A_TARGET_SUITE:
        issues.append(
            MatrixResultIssue(
                "invalid_target_suite",
                "suite publication boundary must target AlphaEvolve Appendix A",
            )
        )
    if data.get("result_schema") != MATRIX_RESULT_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_result_schema",
                "suite publication boundary must reference the matrix result report schema",
            )
        )
    if data.get("artifact_inventory_schema") != MATRIX_ARTIFACT_INVENTORY_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_artifact_inventory_schema",
                "suite publication boundary must reference the matrix artifact inventory schema",
            )
        )
    if data.get("publication_bundle_schema") != MATRIX_PUBLICATION_BUNDLE_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_publication_bundle_schema",
                "suite publication boundary must reference the matrix publication bundle schema",
            )
        )
    status = data.get("artifact_status")
    if status not in MATRIX_SUITE_PUBLICATION_ARTIFACT_STATUSES:
        issues.append(
            MatrixResultIssue(
                "invalid_artifact_status",
                "artifact_status must be not_generated_locally or generated",
            )
        )
        status = None
    if not isinstance(data.get("local_generation_scope"), str) or not data["local_generation_scope"].strip():
        issues.append(
            MatrixResultIssue(
                "missing_local_generation_scope",
                "local_generation_scope must identify the local artifact-generation surface",
            )
        )
    if data.get("registered_target_count") != APPENDIX_A_EXPECTED_TARGET_COUNT:
        issues.append(
            MatrixResultIssue(
                "invalid_registered_target_count",
                "registered_target_count must match the Appendix A registry target count",
            )
        )
    required_field_count = _validate_matrix_suite_publication_required_fields(
        data.get("required_artifact_fields"),
        issues,
    )
    artifacts = data.get("generated_target_artifacts")
    if not isinstance(artifacts, list):
        issues.append(
            MatrixResultIssue(
                "invalid_generated_target_artifacts",
                "generated_target_artifacts must be a list",
            )
        )
        artifacts = []
    generated_count = len(artifacts)
    if status == "not_generated_locally":
        if artifacts:
            issues.append(
                MatrixResultIssue(
                    "unexpected_generated_target_artifacts",
                    "not_generated_locally status must not include generated target artifacts",
                )
            )
        claim_boundary = data.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary.lower():
            issues.append(
                MatrixResultIssue(
                    "missing_absence_claim_boundary",
                    "absence boundary must explicitly say it does not claim suite artifact generation",
                )
            )
    elif status == "generated":
        if not artifacts:
            issues.append(
                MatrixResultIssue(
                    "missing_suite_publication_artifacts",
                    "generated status requires one artifact record per Appendix A target",
                )
            )
        _validate_matrix_suite_publication_artifacts(artifacts, issues)
    return MatrixSuitePublicationArtifactBoundaryValidation(
        ok=not issues,
        artifact_status=status if isinstance(status, str) else None,
        generated_target_count=generated_count,
        required_field_count=required_field_count,
        issues=issues,
    )


def matrix_baseline_component_runtime_boundary_record() -> dict[str, Any]:
    return {
        "schema": MATRIX_BASELINE_COMPONENT_RUNTIME_SCHEMA,
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "result_schema": MATRIX_RESULT_SCHEMA,
        "runtime_emission_status": "not_emitted_by_local_runner",
        "local_runner_scope": "matrix_benchmark_runner",
        "required_emission_fields": list(MATRIX_BASELINE_COMPONENT_RUNTIME_REQUIRED_FIELDS),
        "emitted_records": [],
        "claim_boundary": (
            "This is a matrix baseline-component absence/readiness boundary. "
            "It does not claim local matrix runners emit AlphaEvolve Section "
            "3.1 initializer, reconstruction-loss, and Adam-optimizer provenance."
        ),
    }


def validate_matrix_baseline_component_runtime_boundary(
    boundary: object | str | Path | None = None,
) -> MatrixBaselineComponentRuntimeValidation:
    """Validate whether matrix runners emit Section 3.1 baseline-component records."""
    data, read_issues = _load_report(
        matrix_baseline_component_runtime_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MatrixBaselineComponentRuntimeValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_BASELINE_COMPONENT_RUNTIME_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_schema",
                "unsupported matrix baseline-component runtime boundary schema",
            )
        )
    if data.get("target_suite") != APPENDIX_A_TARGET_SUITE:
        issues.append(
            MatrixResultIssue(
                "invalid_target_suite",
                "runtime boundary must target AlphaEvolve Appendix A",
            )
        )
    if data.get("result_schema") != MATRIX_RESULT_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_result_schema",
                "runtime boundary must reference the matrix result report schema",
            )
        )
    status = data.get("runtime_emission_status")
    if status not in MATRIX_BASELINE_COMPONENT_RUNTIME_STATUSES:
        issues.append(
            MatrixResultIssue(
                "invalid_runtime_emission_status",
                "runtime_emission_status must be not_emitted_by_local_runner or emitted",
            )
        )
        status = None
    if not isinstance(data.get("local_runner_scope"), str) or not data["local_runner_scope"].strip():
        issues.append(
            MatrixResultIssue(
                "missing_local_runner_scope",
                "local_runner_scope must identify the local runner surface",
            )
        )
    required_field_count = _validate_matrix_baseline_component_required_fields(
        data.get("required_emission_fields"),
        issues,
    )
    emitted_records = data.get("emitted_records")
    if not isinstance(emitted_records, list):
        issues.append(
            MatrixResultIssue(
                "invalid_emitted_records",
                "emitted_records must be a list",
            )
        )
        emitted_records = []
    emitted_record_count = len(emitted_records)
    if status == "not_emitted_by_local_runner":
        if emitted_records:
            issues.append(
                MatrixResultIssue(
                    "unexpected_runtime_baseline_component_records",
                    "not_emitted_by_local_runner status must not include emitted records",
                )
            )
        claim_boundary = data.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary.lower():
            issues.append(
                MatrixResultIssue(
                    "missing_absence_claim_boundary",
                    "absence boundary must explicitly say it does not claim runtime emission",
                )
            )
    elif status == "emitted":
        if not emitted_records:
            issues.append(
                MatrixResultIssue(
                    "missing_runtime_baseline_component_records",
                    "emitted status requires at least one emitted record",
                )
            )
        _validate_matrix_baseline_component_records(emitted_records, issues)
    return MatrixBaselineComponentRuntimeValidation(
        ok=not issues,
        runtime_emission_status=status if isinstance(status, str) else None,
        emitted_record_count=emitted_record_count,
        required_field_count=required_field_count,
        issues=issues,
    )


def matrix_cascade_run_runtime_boundary_record() -> dict[str, Any]:
    return {
        "schema": MATRIX_CASCADE_RUN_RUNTIME_SCHEMA,
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "result_schema": MATRIX_RESULT_SCHEMA,
        "runtime_emission_status": "not_emitted_by_local_runner",
        "local_runner_scope": "matrix_benchmark_runner",
        "required_emission_fields": list(MATRIX_CASCADE_RUN_RUNTIME_REQUIRED_FIELDS),
        "emitted_records": [],
        "claim_boundary": (
            "This is a matrix cascade-run absence/readiness boundary. It does "
            "not claim local matrix runners emit AlphaEvolve Section 3.1 executed "
            "cascade traces behind per-seed rank reports."
        ),
    }


def matrix_cascade_run_runtime_boundary_from_matrix_result(
    *,
    run_id: str,
    cascade_id: str,
    cascade_version: str,
    matrix_result_report: dict[str, Any],
    matrix_result_ref: str,
    stage_traces_by_seed: dict[int | str, list[dict[str, Any]]],
    artifact_paths_by_seed: dict[int | str, list[str]] | None = None,
    artifact_sha256_by_seed: dict[int | str, str] | None = None,
) -> dict[str, Any]:
    """Build emitted matrix cascade-run records from per-seed result rows."""
    validation = validate_matrix_result_report(matrix_result_report)
    if not validation.ok:
        messages = "; ".join(issue.message for issue in validation.issues)
        raise ValueError(f"matrix_result_report is invalid: {messages}")
    seed_results = matrix_result_report.get("seed_results")
    if not isinstance(seed_results, list) or not seed_results:
        raise ValueError("matrix_result_report.seed_results must be non-empty")
    target_id = matrix_result_report.get("target_id")
    if not isinstance(target_id, str) or not target_id.strip():
        raise ValueError("matrix_result_report.target_id must be non-empty")
    records: list[dict[str, Any]] = []
    for seed_result in seed_results:
        if not isinstance(seed_result, dict):
            raise ValueError("matrix_result_report.seed_results entries must be objects")
        seed = seed_result.get("seed")
        rank = seed_result.get("rank")
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError("matrix_result_report seed rows must include integer seed")
        if isinstance(rank, bool) or not isinstance(rank, int) or rank <= 0:
            raise ValueError("matrix_result_report seed rows must include positive rank")
        stage_traces = _lookup_seed_mapping(
            stage_traces_by_seed,
            seed,
            field_name="stage_traces_by_seed",
        )
        if not isinstance(stage_traces, list) or not stage_traces:
            raise ValueError(f"stage_traces_by_seed[{seed}] must be a non-empty list")
        final_stage = stage_traces[-1]
        if not isinstance(final_stage, dict):
            raise ValueError(f"stage_traces_by_seed[{seed}] final entry must be an object")
        final_candidate_id = final_stage.get("candidate_id")
        if not isinstance(final_candidate_id, str) or not final_candidate_id.strip():
            raise ValueError(
                f"stage_traces_by_seed[{seed}] final entry must include candidate_id"
            )
        stop_reason = final_stage.get("stop_reason")
        if not isinstance(stop_reason, str) or not stop_reason.strip():
            raise ValueError(
                f"stage_traces_by_seed[{seed}] final entry must include stop_reason"
            )
        artifact_paths = (
            _lookup_seed_mapping(
                artifact_paths_by_seed,
                seed,
                field_name="artifact_paths_by_seed",
            )
            if artifact_paths_by_seed is not None
            else [f"matrix/{target_id}/cascade_seed_{seed}.json"]
        )
        artifact_sha256 = (
            _lookup_seed_mapping(
                artifact_sha256_by_seed,
                seed,
                field_name="artifact_sha256_by_seed",
            )
            if artifact_sha256_by_seed is not None
            else _stable_json_sha256(
                {
                    "run_id": run_id,
                    "target_id": target_id,
                    "seed": seed,
                    "cascade_id": cascade_id,
                    "cascade_version": cascade_version,
                    "stage_traces": stage_traces,
                    "rank": rank,
                }
            )
        )
        records.append(
            {
                "run_id": run_id,
                "target_id": target_id,
                "seed": seed,
                "cascade_id": cascade_id,
                "cascade_version": cascade_version,
                "stage_traces": copy.deepcopy(stage_traces),
                "accepted_final_rank": rank,
                "stop_reason": stop_reason,
                "final_candidate_id": final_candidate_id,
                "matrix_result_ref": matrix_result_ref,
                "matrix_result_report": copy.deepcopy(matrix_result_report),
                "artifact_paths": copy.deepcopy(artifact_paths),
                "artifact_sha256": artifact_sha256,
            }
        )
    boundary = matrix_cascade_run_runtime_boundary_record()
    boundary.update(
        {
            "runtime_emission_status": "emitted",
            "emitted_records": records,
            "claim_boundary": (
                "Emitted records are per-seed matrix cascade traces linked to "
                "matrix_result_report seed rows; this still does not claim full "
                "AlphaEvolve Section 3.1 scale or state-of-the-art discovery."
            ),
        }
    )
    return boundary


def validate_matrix_cascade_run_runtime_boundary(
    boundary: object | str | Path | None = None,
) -> MatrixCascadeRunRuntimeValidation:
    """Validate whether matrix runners emit executed cascade traces for result rows."""
    data, read_issues = _load_report(
        matrix_cascade_run_runtime_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MatrixCascadeRunRuntimeValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_CASCADE_RUN_RUNTIME_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_schema",
                "unsupported matrix cascade-run runtime boundary schema",
            )
        )
    if data.get("target_suite") != APPENDIX_A_TARGET_SUITE:
        issues.append(
            MatrixResultIssue(
                "invalid_target_suite",
                "runtime boundary must target AlphaEvolve Appendix A",
            )
        )
    if data.get("result_schema") != MATRIX_RESULT_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_result_schema",
                "runtime boundary must reference the matrix result report schema",
            )
        )
    status = data.get("runtime_emission_status")
    if status not in MATRIX_CASCADE_RUN_RUNTIME_STATUSES:
        issues.append(
            MatrixResultIssue(
                "invalid_runtime_emission_status",
                "runtime_emission_status must be not_emitted_by_local_runner or emitted",
            )
        )
        status = None
    if not isinstance(data.get("local_runner_scope"), str) or not data["local_runner_scope"].strip():
        issues.append(
            MatrixResultIssue(
                "missing_local_runner_scope",
                "local_runner_scope must identify the local runner surface",
            )
        )
    required_field_count = _validate_matrix_cascade_run_runtime_required_fields(
        data.get("required_emission_fields"),
        issues,
    )
    emitted_records = data.get("emitted_records")
    if not isinstance(emitted_records, list):
        issues.append(
            MatrixResultIssue(
                "invalid_emitted_records",
                "emitted_records must be a list",
            )
        )
        emitted_records = []
    emitted_record_count = len(emitted_records)
    if status == "not_emitted_by_local_runner":
        if emitted_records:
            issues.append(
                MatrixResultIssue(
                    "unexpected_runtime_cascade_run_records",
                    "not_emitted_by_local_runner status must not include emitted records",
                )
            )
        claim_boundary = data.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary.lower():
            issues.append(
                MatrixResultIssue(
                    "missing_absence_claim_boundary",
                    "absence boundary must explicitly say it does not claim runtime emission",
                )
            )
    elif status == "emitted":
        if not emitted_records:
            issues.append(
                MatrixResultIssue(
                    "missing_runtime_cascade_run_records",
                    "emitted status requires at least one emitted record",
                )
            )
        _validate_matrix_cascade_run_runtime_records(emitted_records, issues)
    return MatrixCascadeRunRuntimeValidation(
        ok=not issues,
        runtime_emission_status=status if isinstance(status, str) else None,
        emitted_record_count=emitted_record_count,
        required_field_count=required_field_count,
        issues=issues,
    )


def validate_matrix_publication_bundle(
    bundle: object | str | Path,
) -> MatrixPublicationBundleValidation:
    """Validate a matrix publication bundle wrapper and its embedded evidence."""
    data, read_issues = _load_report(bundle)
    if read_issues:
        return MatrixPublicationBundleValidation(
            False,
            None,
            False,
            False,
            False,
            read_issues,
        )
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_PUBLICATION_BUNDLE_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_bundle_schema",
                "unsupported matrix publication bundle schema",
            )
        )
    target_suite = _text_field(data, "target_suite", issues)
    target_id = _text_field(data, "target_id", issues)
    report = data.get("report")
    report_validation = validate_matrix_result_report(report)
    issues.extend(
        MatrixResultIssue(f"report_{issue.code}", issue.message)
        for issue in report_validation.issues
    )
    if isinstance(report, dict):
        if target_suite is not None and report.get("target_suite") != target_suite:
            issues.append(
                MatrixResultIssue(
                    "target_suite_mismatch",
                    "bundle target_suite must match embedded report",
                )
            )
        if target_id is not None and report.get("target_id") != target_id:
            issues.append(
                MatrixResultIssue(
                    "target_id_mismatch",
                    "bundle target_id must match embedded report",
                )
            )
    artifact_root = data.get("artifact_root")
    report_path = data.get("report_path")
    if not isinstance(artifact_root, str) or not artifact_root.strip():
        issues.append(
            MatrixResultIssue(
                "invalid_artifact_root",
                "artifact_root must be a non-empty string",
            )
        )
        root = None
    else:
        root = Path(artifact_root)
    if root is not None:
        _validate_bundle_report_file(data, root, issues)
        _validate_bundle_inventory_file(data, root, issues)
    elif not isinstance(report_path, str) or not report_path:
        issues.append(
            MatrixResultIssue(
                "invalid_report_path",
                "report_path must be a safe relative path",
            )
        )

    inventory = data.get("inventory")
    inventory_ok = _validate_matrix_publication_inventory(inventory, data, issues)
    if isinstance(inventory, dict):
        if target_id is not None and inventory.get("target_id") != target_id:
            inventory_ok = False
            issues.append(
                MatrixResultIssue(
                    "inventory_target_id_mismatch",
                    "inventory target_id must match bundle target_id",
                )
            )
    else:
        inventory_ok = False
        issues.append(
            MatrixResultIssue(
                "invalid_inventory",
                "bundle inventory must be an object",
            )
    )
    if isinstance(report, dict) and isinstance(inventory, dict):
        artifact_count = (
            len(report["artifacts"])
            if isinstance(report.get("artifacts"), list)
            else None
        )
        if artifact_count is not None and inventory.get("artifact_count") != artifact_count:
            inventory_ok = False
            issues.append(
                MatrixResultIssue(
                    "inventory_artifact_count_mismatch",
                    "inventory artifact_count must match report artifacts",
                )
            )
    return MatrixPublicationBundleValidation(
        ok=not issues,
        target_id=target_id,
        report_ok=report_validation.ok,
        inventory_ok=inventory_ok,
        alphaevolve_comparable=report_validation.alphaevolve_comparable,
        issues=issues,
    )


def validate_matrix_near_integrality_evidence(
    evidence: object | str | Path,
) -> MatrixNearIntegralityValidation:
    """Validate search-time near-integrality prompt and rounding evidence."""
    data, read_issues = _load_report(evidence)
    if read_issues:
        return MatrixNearIntegralityValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_NEAR_INTEGRALITY_SCHEMA:
        issues.append(MatrixResultIssue("invalid_schema", "unsupported matrix near-integrality evidence schema"))
    target_id = _text_field(data, "target_id", issues)
    target_suite = _text_field(data, "target_suite", issues)
    if target_id is not None and target_suite == APPENDIX_A_TARGET_SUITE:
        if matrix_target_by_id(target_id) is None:
            issues.append(MatrixResultIssue("unknown_appendix_a_target", "target_id is not in the AlphaEvolve Appendix A matrix registry"))
    if not isinstance(data.get("local_search_evidence"), bool):
        issues.append(MatrixResultIssue("invalid_local_search_evidence", "local_search_evidence must be boolean"))
    _validate_near_integrality_prompt(data.get("prompt_instruction"), issues)
    rounding_domain = _validate_rounding_policy(data.get("rounding_policy"), issues)
    candidate_count, coefficient_count = _validate_near_integrality_candidates(
        data.get("candidate_records"),
        rounding_domain,
        issues,
    )
    return MatrixNearIntegralityValidation(
        ok=not issues,
        target_id=target_id,
        candidate_count=candidate_count,
        coefficient_count=coefficient_count,
        issues=issues,
    )


def matrix_near_integrality_runtime_boundary_record() -> dict[str, Any]:
    return {
        "schema": MATRIX_NEAR_INTEGRALITY_RUNTIME_SCHEMA,
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "evidence_schema": MATRIX_NEAR_INTEGRALITY_SCHEMA,
        "runtime_emission_status": "not_emitted_by_local_runner",
        "local_runner_scope": "matrix_benchmark_runner",
        "required_emission_fields": list(MATRIX_NEAR_INTEGRALITY_RUNTIME_REQUIRED_FIELDS),
        "emitted_records": [],
        "claim_boundary": (
            "This is a runtime-emission absence/readiness boundary. It does not "
            "claim local matrix runners emit AlphaEvolve Section 3.1 near-integrality evidence."
        ),
    }


def matrix_near_integrality_runtime_boundary_from_evidence(
    *,
    run_id: str,
    matrix_result_ref: str,
    near_integrality_evidence: dict[str, Any],
    artifact_paths_by_candidate: dict[str, list[str]] | None = None,
    artifact_sha256_by_candidate: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build emitted near-integrality runtime records from validated evidence."""
    validation = validate_matrix_near_integrality_evidence(near_integrality_evidence)
    if not validation.ok:
        messages = "; ".join(issue.message for issue in validation.issues)
        raise ValueError(f"near_integrality_evidence is invalid: {messages}")
    target_id = near_integrality_evidence.get("target_id")
    prompt = near_integrality_evidence.get("prompt_instruction")
    candidates = near_integrality_evidence.get("candidate_records")
    if not isinstance(target_id, str) or not target_id.strip():
        raise ValueError("near_integrality_evidence.target_id must be non-empty")
    if not isinstance(prompt, dict):
        raise ValueError("near_integrality_evidence.prompt_instruction must be an object")
    prompt_hash = prompt.get("prompt_hash")
    prompt_text = prompt.get("text")
    if not isinstance(prompt_hash, str) or _SHA256_RE.fullmatch(prompt_hash) is None:
        raise ValueError("prompt_instruction.prompt_hash must be a SHA-256 digest")
    if not isinstance(prompt_text, str) or not prompt_text.strip():
        raise ValueError("prompt_instruction.text must be non-empty")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("near_integrality_evidence.candidate_records must be non-empty")
    records: list[dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("candidate_records entries must be objects")
        candidate_id = candidate.get("candidate_id")
        seed = candidate.get("seed")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            raise ValueError("candidate_records entries must include candidate_id")
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError("candidate_records entries must include integer seed")
        artifact_paths = (
            artifact_paths_by_candidate[candidate_id]
            if artifact_paths_by_candidate is not None
            and candidate_id in artifact_paths_by_candidate
            else [f"matrix/{target_id}/near_integrality_{candidate_id}.json"]
        )
        artifact_sha256 = (
            artifact_sha256_by_candidate[candidate_id]
            if artifact_sha256_by_candidate is not None
            and candidate_id in artifact_sha256_by_candidate
            else _stable_json_sha256(
                {
                    "run_id": run_id,
                    "target_id": target_id,
                    "candidate_id": candidate_id,
                    "seed": seed,
                    "raw_coefficients": candidate.get("raw_coefficients"),
                    "rounded_coefficients": candidate.get("rounded_coefficients"),
                    "max_abs_rounding_error": candidate.get("max_abs_rounding_error"),
                    "exactness_certificate_ref": candidate.get(
                        "exactness_certificate_ref"
                    ),
                }
            )
        )
        records.append(
            {
                "run_id": run_id,
                "candidate_id": candidate_id,
                "target_id": target_id,
                "seed": seed,
                "prompt_hash": prompt_hash,
                "prompt_instruction": prompt_text,
                "raw_coefficients": copy.deepcopy(candidate.get("raw_coefficients")),
                "rounded_coefficients": copy.deepcopy(
                    candidate.get("rounded_coefficients")
                ),
                "max_abs_rounding_error": candidate.get("max_abs_rounding_error"),
                "exactness_certificate_ref": candidate.get(
                    "exactness_certificate_ref"
                ),
                "matrix_result_ref": matrix_result_ref,
                "artifact_paths": copy.deepcopy(artifact_paths),
                "artifact_sha256": artifact_sha256,
                "near_integrality_evidence": copy.deepcopy(
                    near_integrality_evidence
                ),
            }
        )
    boundary = matrix_near_integrality_runtime_boundary_record()
    boundary.update(
        {
            "runtime_emission_status": "emitted",
            "emitted_records": records,
            "claim_boundary": (
                "Emitted records link matrix search candidates to near-integral "
                "rounding diagnostics and certificates; this still does not claim "
                "local runners automatically emit AlphaEvolve Section 3.1 evidence."
            ),
        }
    )
    return boundary


def validate_matrix_near_integrality_runtime_boundary(
    boundary: object | str | Path | None = None,
) -> MatrixNearIntegralityRuntimeValidation:
    """Validate whether local matrix runners emit near-integrality evidence records."""
    data, read_issues = _load_report(
        matrix_near_integrality_runtime_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MatrixNearIntegralityRuntimeValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_NEAR_INTEGRALITY_RUNTIME_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_schema",
                "unsupported matrix near-integrality runtime boundary schema",
            )
        )
    if data.get("target_suite") != APPENDIX_A_TARGET_SUITE:
        issues.append(
            MatrixResultIssue(
                "invalid_target_suite",
                "runtime boundary must target AlphaEvolve Appendix A",
            )
        )
    if data.get("evidence_schema") != MATRIX_NEAR_INTEGRALITY_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_evidence_schema",
                "runtime boundary must reference the matrix near-integrality evidence schema",
            )
        )
    status = data.get("runtime_emission_status")
    if status not in MATRIX_NEAR_INTEGRALITY_RUNTIME_STATUSES:
        issues.append(
            MatrixResultIssue(
                "invalid_runtime_emission_status",
                "runtime_emission_status must be not_emitted_by_local_runner or emitted",
            )
        )
        status = None
    if not isinstance(data.get("local_runner_scope"), str) or not data["local_runner_scope"].strip():
        issues.append(
            MatrixResultIssue(
                "missing_local_runner_scope",
                "local_runner_scope must identify the local runner surface",
            )
        )
    required_field_count = _validate_near_integrality_runtime_required_fields(
        data.get("required_emission_fields"),
        issues,
    )
    emitted_records = data.get("emitted_records")
    if not isinstance(emitted_records, list):
        issues.append(
            MatrixResultIssue(
                "invalid_emitted_records",
                "emitted_records must be a list",
            )
        )
        emitted_records = []
    emitted_record_count = len(emitted_records)
    if status == "not_emitted_by_local_runner":
        if emitted_records:
            issues.append(
                MatrixResultIssue(
                    "unexpected_runtime_near_integrality_records",
                    "not_emitted_by_local_runner status must not include emitted records",
                )
            )
        claim_boundary = data.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary.lower():
            issues.append(
                MatrixResultIssue(
                    "missing_absence_claim_boundary",
                    "absence boundary must explicitly say it does not claim runtime emission",
                )
            )
    elif status == "emitted":
        if not emitted_records:
            issues.append(
                MatrixResultIssue(
                    "missing_runtime_near_integrality_records",
                    "emitted status requires at least one emitted record",
                )
            )
        _validate_near_integrality_runtime_records(emitted_records, issues)
    return MatrixNearIntegralityRuntimeValidation(
        ok=not issues,
        runtime_emission_status=status if isinstance(status, str) else None,
        emitted_record_count=emitted_record_count,
        required_field_count=required_field_count,
        issues=issues,
    )


def validate_matrix_sweep_space_evidence(
    evidence: object | str | Path,
) -> MatrixSweepSpaceValidation:
    """Validate AlphaEvolve Figure 9-style matrix sweep-space evidence."""
    data, read_issues = _load_report(evidence)
    if read_issues:
        return MatrixSweepSpaceValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_SWEEP_SPACE_SCHEMA:
        issues.append(MatrixResultIssue("invalid_schema", "unsupported matrix sweep-space evidence schema"))
    target_id = _text_field(data, "target_id", issues)
    target_suite = _text_field(data, "target_suite", issues)
    if target_id is not None and target_suite == APPENDIX_A_TARGET_SUITE:
        if matrix_target_by_id(target_id) is None:
            issues.append(MatrixResultIssue("unknown_appendix_a_target", "target_id is not in the AlphaEvolve Appendix A matrix registry"))
    if data.get("source_figure") not in SWEEP_SOURCE_FIGURES:
        issues.append(MatrixResultIssue("invalid_source_figure", "source_figure must identify AlphaEvolve Figures 9a-9c"))
    if data.get("sweep_function_name") != "sweep":
        issues.append(MatrixResultIssue("invalid_sweep_function", "sweep_function_name must be sweep"))
    if not isinstance(data.get("local_search_evidence"), bool):
        issues.append(MatrixResultIssue("invalid_local_search_evidence", "local_search_evidence must be boolean"))
    for field in ("search_program_ref",):
        if not isinstance(data.get(field), str) or not data[field].strip():
            issues.append(MatrixResultIssue(f"missing_{field}", f"{field} is required"))
    _validate_sweep_hyper_library(data.get("hyper_library"), issues)
    hyperparameter_names, hyperparameter_specs = _validate_sweep_hyperparameters(
        data.get("hyperparameters"),
        issues,
    )
    sampled_count = _validate_sweep_configurations(
        data.get("sampled_configurations"),
        hyperparameter_names,
        hyperparameter_specs,
        data.get("winning_configuration_id"),
        issues,
    )
    return MatrixSweepSpaceValidation(
        ok=not issues,
        target_id=target_id,
        hyperparameter_count=len(hyperparameter_names),
        sampled_configuration_count=sampled_count,
        issues=issues,
    )


def matrix_sweep_space_runtime_boundary_record() -> dict[str, Any]:
    return {
        "schema": MATRIX_SWEEP_SPACE_RUNTIME_SCHEMA,
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "evidence_schema": MATRIX_SWEEP_SPACE_SCHEMA,
        "runtime_emission_status": "not_emitted_by_local_runner",
        "local_runner_scope": "matrix_benchmark_runner",
        "required_emission_fields": list(MATRIX_SWEEP_SPACE_RUNTIME_REQUIRED_FIELDS),
        "emitted_records": [],
        "claim_boundary": (
            "This is a runtime-emission absence/readiness boundary. It does not "
            "claim local matrix runners emit AlphaEvolve Figure 9 sweep-space evidence."
        ),
    }


def matrix_sweep_space_runtime_boundary_from_evidence(
    *,
    run_id: str,
    candidate_id: str,
    seed: int,
    matrix_result_ref: str,
    sweep_space_evidence: dict[str, Any],
    artifact_paths: list[str] | None = None,
    artifact_sha256: str | None = None,
) -> dict[str, Any]:
    """Build an emitted sweep-space runtime record from validated evidence."""
    validation = validate_matrix_sweep_space_evidence(sweep_space_evidence)
    if not validation.ok:
        messages = "; ".join(issue.message for issue in validation.issues)
        raise ValueError(f"sweep_space_evidence is invalid: {messages}")
    target_id = sweep_space_evidence.get("target_id")
    if not isinstance(target_id, str) or not target_id.strip():
        raise ValueError("sweep_space_evidence.target_id must be non-empty")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id must be non-empty")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be non-empty")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    if not isinstance(matrix_result_ref, str) or not matrix_result_ref.strip():
        raise ValueError("matrix_result_ref must be non-empty")
    winning_configuration = _selected_sweep_configuration(
        sweep_space_evidence,
        sweep_space_evidence.get("winning_configuration_id"),
    )
    paths = (
        artifact_paths
        if artifact_paths is not None
        else [f"matrix/{target_id}/sweep_space_{candidate_id}.json"]
    )
    digest = (
        artifact_sha256
        if artifact_sha256 is not None
        else _stable_json_sha256(
            {
                "run_id": run_id,
                "candidate_id": candidate_id,
                "target_id": target_id,
                "seed": seed,
                "search_program_ref": sweep_space_evidence.get(
                    "search_program_ref"
                ),
                "winning_configuration_id": sweep_space_evidence.get(
                    "winning_configuration_id"
                ),
                "exactness_certificate_ref": winning_configuration.get(
                    "exactness_certificate_ref"
                ),
                "final_decomposition_ref": winning_configuration.get(
                    "final_decomposition_ref"
                ),
                "matrix_result_ref": matrix_result_ref,
            }
        )
    )
    boundary = matrix_sweep_space_runtime_boundary_record()
    boundary.update(
        {
            "runtime_emission_status": "emitted",
            "emitted_records": [
                {
                    "run_id": run_id,
                    "candidate_id": candidate_id,
                    "target_id": target_id,
                    "seed": seed,
                    "search_program_ref": sweep_space_evidence.get(
                        "search_program_ref"
                    ),
                    "sweep_function_name": sweep_space_evidence.get(
                        "sweep_function_name"
                    ),
                    "hyper_library": copy.deepcopy(
                        sweep_space_evidence.get("hyper_library")
                    ),
                    "hyperparameters": copy.deepcopy(
                        sweep_space_evidence.get("hyperparameters")
                    ),
                    "sampled_configurations": copy.deepcopy(
                        sweep_space_evidence.get("sampled_configurations")
                    ),
                    "winning_configuration_id": sweep_space_evidence.get(
                        "winning_configuration_id"
                    ),
                    "exactness_certificate_ref": winning_configuration.get(
                        "exactness_certificate_ref"
                    ),
                    "final_decomposition_ref": winning_configuration.get(
                        "final_decomposition_ref"
                    ),
                    "matrix_result_ref": matrix_result_ref,
                    "artifact_paths": copy.deepcopy(paths),
                    "artifact_sha256": digest,
                    "sweep_space_evidence": copy.deepcopy(sweep_space_evidence),
                }
            ],
            "claim_boundary": (
                "Emitted records link matrix search programs to Figure 9 "
                "sweep-space hyperparameter evidence; this still does not claim "
                "local runners automatically emit those records."
            ),
        }
    )
    return boundary


def validate_matrix_sweep_space_runtime_boundary(
    boundary: object | str | Path | None = None,
) -> MatrixSweepSpaceRuntimeValidation:
    """Validate whether local matrix runners emit sweep-space evidence records."""
    data, read_issues = _load_report(
        matrix_sweep_space_runtime_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MatrixSweepSpaceRuntimeValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_SWEEP_SPACE_RUNTIME_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_schema",
                "unsupported matrix sweep-space runtime boundary schema",
            )
        )
    if data.get("target_suite") != APPENDIX_A_TARGET_SUITE:
        issues.append(
            MatrixResultIssue(
                "invalid_target_suite",
                "runtime boundary must target AlphaEvolve Appendix A",
            )
        )
    if data.get("evidence_schema") != MATRIX_SWEEP_SPACE_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_evidence_schema",
                "runtime boundary must reference the matrix sweep-space evidence schema",
            )
        )
    status = data.get("runtime_emission_status")
    if status not in MATRIX_SWEEP_SPACE_RUNTIME_STATUSES:
        issues.append(
            MatrixResultIssue(
                "invalid_runtime_emission_status",
                "runtime_emission_status must be not_emitted_by_local_runner or emitted",
            )
        )
        status = None
    if not isinstance(data.get("local_runner_scope"), str) or not data["local_runner_scope"].strip():
        issues.append(
            MatrixResultIssue(
                "missing_local_runner_scope",
                "local_runner_scope must identify the local runner surface",
            )
        )
    required_field_count = _validate_sweep_space_runtime_required_fields(
        data.get("required_emission_fields"),
        issues,
    )
    emitted_records = data.get("emitted_records")
    if not isinstance(emitted_records, list):
        issues.append(
            MatrixResultIssue(
                "invalid_emitted_records",
                "emitted_records must be a list",
            )
        )
        emitted_records = []
    emitted_record_count = len(emitted_records)
    if status == "not_emitted_by_local_runner":
        if emitted_records:
            issues.append(
                MatrixResultIssue(
                    "unexpected_runtime_sweep_space_records",
                    "not_emitted_by_local_runner status must not include emitted records",
                )
            )
        claim_boundary = data.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary.lower():
            issues.append(
                MatrixResultIssue(
                    "missing_absence_claim_boundary",
                    "absence boundary must explicitly say it does not claim runtime emission",
                )
            )
    elif status == "emitted":
        if not emitted_records:
            issues.append(
                MatrixResultIssue(
                    "missing_runtime_sweep_space_records",
                    "emitted status requires at least one emitted record",
                )
            )
        _validate_sweep_space_runtime_records(emitted_records, issues)
    return MatrixSweepSpaceRuntimeValidation(
        ok=not issues,
        runtime_emission_status=status if isinstance(status, str) else None,
        emitted_record_count=emitted_record_count,
        required_field_count=required_field_count,
        issues=issues,
    )


def validate_matrix_scalar_field_evidence(
    evidence: object | str | Path,
) -> MatrixScalarFieldValidation:
    """Validate scalar-field and characteristic claims for matrix decompositions."""
    data, read_issues = _load_report(evidence)
    if read_issues:
        return MatrixScalarFieldValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_SCALAR_FIELD_SCHEMA:
        issues.append(MatrixResultIssue("invalid_schema", "unsupported matrix scalar-field evidence schema"))
    target_id = _text_field(data, "target_id", issues)
    target_suite = _text_field(data, "target_suite", issues)
    if target_id is not None and target_suite == APPENDIX_A_TARGET_SUITE:
        if matrix_target_by_id(target_id) is None:
            issues.append(MatrixResultIssue("unknown_appendix_a_target", "target_id is not in the AlphaEvolve Appendix A matrix registry"))
    source_refs = data.get("source_refs")
    if not isinstance(source_refs, list) or not source_refs:
        issues.append(MatrixResultIssue("invalid_source_refs", "source_refs must be a non-empty list"))
    else:
        for source_ref in source_refs:
            _validate_scalar_field_source_ref(source_ref, issues)
    field_claim_count, complex_claim_count = _validate_scalar_field_claims(
        data.get("field_claims"),
        target_id,
        issues,
    )
    return MatrixScalarFieldValidation(
        ok=not issues,
        target_id=target_id,
        field_claim_count=field_claim_count,
        complex_claim_count=complex_claim_count,
        issues=issues,
    )


def matrix_scalar_field_runtime_boundary_record() -> dict[str, Any]:
    return {
        "schema": MATRIX_SCALAR_FIELD_RUNTIME_SCHEMA,
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "evidence_schema": MATRIX_SCALAR_FIELD_SCHEMA,
        "runtime_emission_status": "not_emitted_by_local_runner",
        "local_runner_scope": "matrix_benchmark_runner",
        "required_emission_fields": list(MATRIX_SCALAR_FIELD_RUNTIME_REQUIRED_FIELDS),
        "emitted_records": [],
        "claim_boundary": (
            "This is a runtime-emission absence/readiness boundary. It does not "
            "claim local matrix runners emit AlphaEvolve Section 3.1 scalar-field evidence."
        ),
    }


def validate_matrix_scalar_field_runtime_boundary(
    boundary: object | str | Path | None = None,
) -> MatrixScalarFieldRuntimeValidation:
    """Validate whether local matrix runners emit scalar-field evidence records."""
    data, read_issues = _load_report(
        matrix_scalar_field_runtime_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MatrixScalarFieldRuntimeValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_SCALAR_FIELD_RUNTIME_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_schema",
                "unsupported matrix scalar-field runtime boundary schema",
            )
        )
    if data.get("target_suite") != APPENDIX_A_TARGET_SUITE:
        issues.append(
            MatrixResultIssue(
                "invalid_target_suite",
                "runtime boundary must target AlphaEvolve Appendix A",
            )
        )
    if data.get("evidence_schema") != MATRIX_SCALAR_FIELD_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_evidence_schema",
                "runtime boundary must reference the matrix scalar-field evidence schema",
            )
        )
    status = data.get("runtime_emission_status")
    if status not in MATRIX_SCALAR_FIELD_RUNTIME_STATUSES:
        issues.append(
            MatrixResultIssue(
                "invalid_runtime_emission_status",
                "runtime_emission_status must be not_emitted_by_local_runner or emitted",
            )
        )
        status = None
    if not isinstance(data.get("local_runner_scope"), str) or not data["local_runner_scope"].strip():
        issues.append(
            MatrixResultIssue(
                "missing_local_runner_scope",
                "local_runner_scope must identify the local runner surface",
            )
        )
    required_field_count = _validate_scalar_field_runtime_required_fields(
        data.get("required_emission_fields"),
        issues,
    )
    emitted_records = data.get("emitted_records")
    if not isinstance(emitted_records, list):
        issues.append(
            MatrixResultIssue(
                "invalid_emitted_records",
                "emitted_records must be a list",
            )
        )
        emitted_records = []
    emitted_record_count = len(emitted_records)
    if status == "not_emitted_by_local_runner":
        if emitted_records:
            issues.append(
                MatrixResultIssue(
                    "unexpected_runtime_scalar_field_records",
                    "not_emitted_by_local_runner status must not include emitted records",
                )
            )
        claim_boundary = data.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary.lower():
            issues.append(
                MatrixResultIssue(
                    "missing_absence_claim_boundary",
                    "absence boundary must explicitly say it does not claim runtime emission",
                )
            )
    elif status == "emitted":
        if not emitted_records:
            issues.append(
                MatrixResultIssue(
                    "missing_runtime_scalar_field_records",
                    "emitted status requires at least one emitted record",
                )
            )
        _validate_scalar_field_runtime_records(emitted_records, issues)
    return MatrixScalarFieldRuntimeValidation(
        ok=not issues,
        runtime_emission_status=status if isinstance(status, str) else None,
        emitted_record_count=emitted_record_count,
        required_field_count=required_field_count,
        issues=issues,
    )


def validate_matrix_tensor_rank_evidence(
    evidence: object | str | Path,
) -> MatrixTensorRankValidation:
    """Validate tensor-rank and recursive-applicability claims."""
    data, read_issues = _load_report(evidence)
    if read_issues:
        return MatrixTensorRankValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_TENSOR_RANK_SCHEMA:
        issues.append(MatrixResultIssue("invalid_schema", "unsupported matrix tensor-rank evidence schema"))
    target_id = _text_field(data, "target_id", issues)
    target_suite = _text_field(data, "target_suite", issues)
    if target_id is not None and target_suite == APPENDIX_A_TARGET_SUITE:
        if matrix_target_by_id(target_id) is None:
            issues.append(MatrixResultIssue("unknown_appendix_a_target", "target_id is not in the AlphaEvolve Appendix A matrix registry"))
    source_refs = data.get("source_refs")
    if not isinstance(source_refs, list) or not source_refs:
        issues.append(MatrixResultIssue("invalid_source_refs", "source_refs must be a non-empty list"))
    else:
        for source_ref in source_refs:
            _validate_tensor_rank_source_ref(source_ref, issues)
    claim_count, tensor_count, recursive_count = _validate_tensor_rank_claims(
        data.get("rank_claims"),
        issues,
    )
    return MatrixTensorRankValidation(
        ok=not issues,
        target_id=target_id,
        claim_count=claim_count,
        tensor_decomposition_count=tensor_count,
        recursive_applicable_count=recursive_count,
        issues=issues,
    )


def matrix_tensor_rank_runtime_boundary_record() -> dict[str, Any]:
    return {
        "schema": MATRIX_TENSOR_RANK_RUNTIME_SCHEMA,
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "evidence_schema": MATRIX_TENSOR_RANK_SCHEMA,
        "runtime_emission_status": "not_emitted_by_local_runner",
        "local_runner_scope": "matrix_benchmark_runner",
        "required_emission_fields": list(MATRIX_TENSOR_RANK_RUNTIME_REQUIRED_FIELDS),
        "emitted_records": [],
        "claim_boundary": (
            "This is a runtime-emission absence/readiness boundary. It does not "
            "claim local matrix runners emit AlphaEvolve Section 3.1 tensor-rank evidence."
        ),
    }


def validate_matrix_tensor_rank_runtime_boundary(
    boundary: object | str | Path | None = None,
) -> MatrixTensorRankRuntimeValidation:
    """Validate whether local matrix runners emit tensor-rank evidence records."""
    data, read_issues = _load_report(
        matrix_tensor_rank_runtime_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MatrixTensorRankRuntimeValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_TENSOR_RANK_RUNTIME_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_schema",
                "unsupported matrix tensor-rank runtime boundary schema",
            )
        )
    if data.get("target_suite") != APPENDIX_A_TARGET_SUITE:
        issues.append(
            MatrixResultIssue(
                "invalid_target_suite",
                "runtime boundary must target AlphaEvolve Appendix A",
            )
        )
    if data.get("evidence_schema") != MATRIX_TENSOR_RANK_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_evidence_schema",
                "runtime boundary must reference the matrix tensor-rank evidence schema",
            )
        )
    status = data.get("runtime_emission_status")
    if status not in MATRIX_TENSOR_RANK_RUNTIME_STATUSES:
        issues.append(
            MatrixResultIssue(
                "invalid_runtime_emission_status",
                "runtime_emission_status must be not_emitted_by_local_runner or emitted",
            )
        )
        status = None
    if not isinstance(data.get("local_runner_scope"), str) or not data["local_runner_scope"].strip():
        issues.append(
            MatrixResultIssue(
                "missing_local_runner_scope",
                "local_runner_scope must identify the local runner surface",
            )
        )
    required_field_count = _validate_tensor_rank_runtime_required_fields(
        data.get("required_emission_fields"),
        issues,
    )
    emitted_records = data.get("emitted_records")
    if not isinstance(emitted_records, list):
        issues.append(
            MatrixResultIssue(
                "invalid_emitted_records",
                "emitted_records must be a list",
            )
        )
        emitted_records = []
    emitted_record_count = len(emitted_records)
    if status == "not_emitted_by_local_runner":
        if emitted_records:
            issues.append(
                MatrixResultIssue(
                    "unexpected_runtime_tensor_rank_records",
                    "not_emitted_by_local_runner status must not include emitted records",
                )
            )
        claim_boundary = data.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary.lower():
            issues.append(
                MatrixResultIssue(
                    "missing_absence_claim_boundary",
                    "absence boundary must explicitly say it does not claim runtime emission",
                )
            )
    elif status == "emitted":
        if not emitted_records:
            issues.append(
                MatrixResultIssue(
                    "missing_runtime_tensor_rank_records",
                    "emitted status requires at least one emitted record",
                )
            )
        _validate_tensor_rank_runtime_records(emitted_records, issues)
    return MatrixTensorRankRuntimeValidation(
        ok=not issues,
        runtime_emission_status=status if isinstance(status, str) else None,
        emitted_record_count=emitted_record_count,
        required_field_count=required_field_count,
        issues=issues,
    )


def validate_matrix_headline_historicity_evidence(
    evidence: object | str | Path,
) -> MatrixHeadlineHistoricityValidation:
    """Validate provenance for the 4x4 complex rank-48 historicity headline."""
    data, read_issues = _load_report(evidence)
    if read_issues:
        return MatrixHeadlineHistoricityValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_HEADLINE_HISTORICITY_SCHEMA:
        issues.append(MatrixResultIssue("invalid_schema", "unsupported matrix headline historicity schema"))
    target_id = _text_field(data, "target_id", issues)
    target_suite = _text_field(data, "target_suite", issues)
    dimensions = data.get("dimensions")
    _validate_headline_target(target_suite, target_id, dimensions, issues)
    source_ref_count = _validate_headline_source_refs(data.get("source_refs"), issues)
    _validate_headline_claim(data.get("headline_claim"), target_id, issues)
    prior_count = _validate_headline_prior_comparisons(data.get("prior_comparisons"), issues)
    _validate_headline_evidence_links(data.get("evidence_links"), issues)
    _validate_companion_selection_scope(data.get("companion_selection_scope"), issues)
    return MatrixHeadlineHistoricityValidation(
        ok=not issues,
        target_id=target_id,
        prior_comparison_count=prior_count,
        source_ref_count=source_ref_count,
        issues=issues,
    )


def matrix_headline_historicity_runtime_boundary_record() -> dict[str, Any]:
    return {
        "schema": MATRIX_HEADLINE_HISTORICITY_RUNTIME_SCHEMA,
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "evidence_schema": MATRIX_HEADLINE_HISTORICITY_SCHEMA,
        "runtime_emission_status": "not_emitted_by_local_runner",
        "local_runner_scope": "matrix_benchmark_runner",
        "required_emission_fields": list(MATRIX_HEADLINE_HISTORICITY_RUNTIME_REQUIRED_FIELDS),
        "emitted_records": [],
        "claim_boundary": (
            "This is a runtime-emission absence/readiness boundary. It does not "
            "claim local matrix runners emit AlphaEvolve Section 3.1 headline historicity evidence."
        ),
    }


def validate_matrix_headline_historicity_runtime_boundary(
    boundary: object | str | Path | None = None,
) -> MatrixHeadlineHistoricityRuntimeValidation:
    """Validate whether local matrix runners emit headline historicity evidence records."""
    data, read_issues = _load_report(
        matrix_headline_historicity_runtime_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MatrixHeadlineHistoricityRuntimeValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResultIssue] = []
    if data.get("schema") != MATRIX_HEADLINE_HISTORICITY_RUNTIME_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_schema",
                "unsupported matrix headline historicity runtime boundary schema",
            )
        )
    if data.get("target_suite") != APPENDIX_A_TARGET_SUITE:
        issues.append(
            MatrixResultIssue(
                "invalid_target_suite",
                "runtime boundary must target AlphaEvolve Appendix A",
            )
        )
    if data.get("evidence_schema") != MATRIX_HEADLINE_HISTORICITY_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_evidence_schema",
                "runtime boundary must reference the matrix headline historicity evidence schema",
            )
        )
    status = data.get("runtime_emission_status")
    if status not in MATRIX_HEADLINE_HISTORICITY_RUNTIME_STATUSES:
        issues.append(
            MatrixResultIssue(
                "invalid_runtime_emission_status",
                "runtime_emission_status must be not_emitted_by_local_runner or emitted",
            )
        )
        status = None
    if not isinstance(data.get("local_runner_scope"), str) or not data["local_runner_scope"].strip():
        issues.append(
            MatrixResultIssue(
                "missing_local_runner_scope",
                "local_runner_scope must identify the local runner surface",
            )
        )
    required_field_count = _validate_headline_historicity_runtime_required_fields(
        data.get("required_emission_fields"),
        issues,
    )
    emitted_records = data.get("emitted_records")
    if not isinstance(emitted_records, list):
        issues.append(
            MatrixResultIssue(
                "invalid_emitted_records",
                "emitted_records must be a list",
            )
        )
        emitted_records = []
    emitted_record_count = len(emitted_records)
    if status == "not_emitted_by_local_runner":
        if emitted_records:
            issues.append(
                MatrixResultIssue(
                    "unexpected_runtime_headline_historicity_records",
                    "not_emitted_by_local_runner status must not include emitted records",
                )
            )
        claim_boundary = data.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary.lower():
            issues.append(
                MatrixResultIssue(
                    "missing_absence_claim_boundary",
                    "absence boundary must explicitly say it does not claim runtime emission",
                )
            )
    elif status == "emitted":
        if not emitted_records:
            issues.append(
                MatrixResultIssue(
                    "missing_runtime_headline_historicity_records",
                    "emitted status requires at least one emitted record",
                )
            )
        _validate_headline_historicity_runtime_records(emitted_records, issues)
    return MatrixHeadlineHistoricityRuntimeValidation(
        ok=not issues,
        runtime_emission_status=status if isinstance(status, str) else None,
        emitted_record_count=emitted_record_count,
        required_field_count=required_field_count,
        issues=issues,
    )


def render_matrix_near_integrality_summary(evidence: dict[str, Any]) -> str:
    validation = validate_matrix_near_integrality_evidence(evidence)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Matrix near-integrality evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| target_id | {validation.target_id or '<unknown>'} |",
        f"| candidate_count | {validation.candidate_count} |",
        f"| coefficient_count | {validation.coefficient_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_near_integrality_runtime_boundary_summary(
    boundary: dict[str, Any] | None = None,
) -> str:
    validation = validate_matrix_near_integrality_runtime_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Matrix near-integrality runtime boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| runtime_emission_status | {validation.runtime_emission_status or '<unknown>'} |",
        f"| emitted_record_count | {validation.emitted_record_count} |",
        f"| required_field_count | {validation.required_field_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_scalar_field_summary(evidence: dict[str, Any]) -> str:
    validation = validate_matrix_scalar_field_evidence(evidence)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Matrix scalar-field evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| target_id | {validation.target_id or '<unknown>'} |",
        f"| field_claim_count | {validation.field_claim_count} |",
        f"| complex_claim_count | {validation.complex_claim_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_scalar_field_runtime_boundary_summary(
    boundary: dict[str, Any] | None = None,
) -> str:
    validation = validate_matrix_scalar_field_runtime_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Matrix scalar-field runtime boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| runtime_emission_status | {validation.runtime_emission_status or '<unknown>'} |",
        f"| emitted_record_count | {validation.emitted_record_count} |",
        f"| required_field_count | {validation.required_field_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_tensor_rank_summary(evidence: dict[str, Any]) -> str:
    validation = validate_matrix_tensor_rank_evidence(evidence)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Matrix tensor-rank evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| target_id | {validation.target_id or '<unknown>'} |",
        f"| claim_count | {validation.claim_count} |",
        f"| tensor_decomposition_count | {validation.tensor_decomposition_count} |",
        f"| recursive_applicable_count | {validation.recursive_applicable_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_tensor_rank_runtime_boundary_summary(
    boundary: dict[str, Any] | None = None,
) -> str:
    validation = validate_matrix_tensor_rank_runtime_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Matrix tensor-rank runtime boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| runtime_emission_status | {validation.runtime_emission_status or '<unknown>'} |",
        f"| emitted_record_count | {validation.emitted_record_count} |",
        f"| required_field_count | {validation.required_field_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_headline_historicity_summary(evidence: dict[str, Any]) -> str:
    validation = validate_matrix_headline_historicity_evidence(evidence)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Matrix headline historicity evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| target_id | {validation.target_id or '<unknown>'} |",
        f"| prior_comparison_count | {validation.prior_comparison_count} |",
        f"| source_ref_count | {validation.source_ref_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_headline_historicity_runtime_boundary_summary(
    boundary: dict[str, Any] | None = None,
) -> str:
    validation = validate_matrix_headline_historicity_runtime_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Matrix headline historicity runtime boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| runtime_emission_status | {validation.runtime_emission_status or '<unknown>'} |",
        f"| emitted_record_count | {validation.emitted_record_count} |",
        f"| required_field_count | {validation.required_field_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_suite_publication_artifact_boundary_summary(
    boundary: dict[str, Any] | None = None,
) -> str:
    validation = validate_matrix_suite_publication_artifact_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Matrix suite publication artifact boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| artifact_status | {validation.artifact_status or '<unknown>'} |",
        f"| generated_target_count | {validation.generated_target_count} |",
        f"| required_field_count | {validation.required_field_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_sweep_space_summary(evidence: dict[str, Any]) -> str:
    validation = validate_matrix_sweep_space_evidence(evidence)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Matrix sweep-space evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| target_id | {validation.target_id or '<unknown>'} |",
        f"| hyperparameter_count | {validation.hyperparameter_count} |",
        f"| sampled_configuration_count | {validation.sampled_configuration_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_sweep_space_runtime_boundary_summary(
    boundary: dict[str, Any] | None = None,
) -> str:
    validation = validate_matrix_sweep_space_runtime_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Matrix sweep-space runtime boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| runtime_emission_status | {validation.runtime_emission_status or '<unknown>'} |",
        f"| emitted_record_count | {validation.emitted_record_count} |",
        f"| required_field_count | {validation.required_field_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_cascade_run_runtime_boundary_summary(
    boundary: dict[str, Any] | None = None,
) -> str:
    validation = validate_matrix_cascade_run_runtime_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Matrix cascade-run runtime boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| runtime_emission_status | {validation.runtime_emission_status or '<unknown>'} |",
        f"| emitted_record_count | {validation.emitted_record_count} |",
        f"| required_field_count | {validation.required_field_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_baseline_component_runtime_boundary_summary(
    boundary: dict[str, Any] | None = None,
) -> str:
    validation = validate_matrix_baseline_component_runtime_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Matrix baseline-component runtime boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| runtime_emission_status | {validation.runtime_emission_status or '<unknown>'} |",
        f"| emitted_record_count | {validation.emitted_record_count} |",
        f"| required_field_count | {validation.required_field_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_result_summary(report: dict[str, Any]) -> str:
    validation = validate_matrix_result_report(report)
    status = "ok" if validation.ok else "invalid"
    target_id = report.get("target_id", "<unknown>")
    hit_fraction = report.get("hit_fraction")
    hit_text = "unknown" if hit_fraction is None else f"{float(hit_fraction):.3f}"
    lines = [
        f"Matrix result report: {target_id}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| target_suite | {report.get('target_suite', '<unknown>')} |",
        f"| dimensions | {report.get('dimensions', '<unknown>')} |",
        f"| best_rank | {report.get('best_rank', '<unknown>')} |",
        f"| seed_count | {report.get('seed_count', '<unknown>')} |",
        f"| hit_fraction | {hit_text} |",
        f"| coefficient_domain | {report.get('coefficient_domain', '<unknown>')} |",
        f"| alphaevolve_comparable | {report.get('alphaevolve_comparable', '<unknown>')} |",
        f"| exactness | {_exactness_status(report.get('exactness_certificate'))} |",
        f"| artifact_count | {len(report.get('artifacts', [])) if isinstance(report.get('artifacts'), list) else 0} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def write_strassen_2x2_publication_bundle(
    artifact_root: str | Path,
    *,
    seeds: list[int] | tuple[int, ...] = (0, 1, 2, 3),
) -> dict[str, Any]:
    """Write a checked Strassen artifact bundle for the registered 2x2x2 target."""
    normalized_seeds = _validate_bundle_seeds(seeds)
    root = Path(artifact_root)
    base = root / "matrix" / _STRASSEN_TARGET_ID
    base.mkdir(parents=True, exist_ok=True)

    algorithm = _strassen_algorithm_artifact()
    algorithm_path = base / "algorithm.json"
    algorithm_sha, algorithm_bytes = _write_canonical_json(algorithm_path, algorithm)

    certificate = _strassen_certificate_artifact(algorithm_sha)
    certificate_path = base / "certificate.json"
    certificate_sha, certificate_bytes = _write_canonical_json(
        certificate_path,
        certificate,
    )

    notebook = _strassen_notebook_artifact(algorithm_sha, certificate_sha)
    notebook_path = base / "reproduce.ipynb"
    notebook_sha, notebook_bytes = _write_canonical_json(notebook_path, notebook)

    report = {
        "schema": MATRIX_RESULT_SCHEMA,
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "target_id": _STRASSEN_TARGET_ID,
        "dimensions": list(_STRASSEN_DIMENSIONS),
        "seed_count": len(normalized_seeds),
        "best_rank": len(_STRASSEN_TERMS),
        "hit_count": len(normalized_seeds),
        "hit_fraction": 1.0,
        "coefficient_domain": "integer",
        "alphaevolve_comparable": True,
        "exactness_certificate": {
            "status": "verified",
            "method": "symbolic_tensor_identity",
            "certificate_sha256": certificate_sha,
        },
        "seed_results": [
            {
                "seed": seed,
                "rank": len(_STRASSEN_TERMS),
                "achieved_best_rank": True,
                "exact": True,
            }
            for seed in normalized_seeds
        ],
        "artifacts": [
            {
                "kind": "algorithm",
                "path": "matrix/mm_2x2x2/algorithm.json",
                "sha256": algorithm_sha,
                "bytes": algorithm_bytes,
                "source_rights": alphaevolve_companion_artifact_rights_record(
                    "algorithm"
                ),
            },
            {
                "kind": "certificate",
                "path": "matrix/mm_2x2x2/certificate.json",
                "sha256": certificate_sha,
                "bytes": certificate_bytes,
                "source_rights": alphaevolve_companion_artifact_rights_record(
                    "certificate"
                ),
            },
            {
                "kind": "notebook",
                "path": "matrix/mm_2x2x2/reproduce.ipynb",
                "sha256": notebook_sha,
                "bytes": notebook_bytes,
                "source_rights": alphaevolve_companion_artifact_rights_record(
                    "notebook"
                ),
            },
        ],
    }
    report_path = base / "report.json"
    report_sha, report_bytes = _write_canonical_json(report_path, report)
    inventory = matrix_result_artifact_inventory(report, root)
    inventory_path = base / "inventory.json"
    inventory_sha, inventory_bytes = _write_canonical_json(inventory_path, inventory)
    return {
        "schema": MATRIX_PUBLICATION_BUNDLE_SCHEMA,
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "target_id": _STRASSEN_TARGET_ID,
        "artifact_root": str(root),
        "report_path": "matrix/mm_2x2x2/report.json",
        "report_sha256": report_sha,
        "report_bytes": report_bytes,
        "report": report,
        "inventory_path": "matrix/mm_2x2x2/inventory.json",
        "inventory_sha256": inventory_sha,
        "inventory_bytes": inventory_bytes,
        "inventory": inventory,
    }


def strassen_2x2_publication_bundle_record(
    artifact_root: str | Path | None = None,
) -> dict[str, Any]:
    """Return the checked-in Strassen 2x2 publication bundle metadata."""
    root = Path(artifact_root) if artifact_root is not None else STRASSEN_2X2_PUBLICATION_BUNDLE_ROOT
    report_path = Path("matrix/mm_2x2x2/report.json")
    inventory_path = Path("matrix/mm_2x2x2/inventory.json")
    report_file = root / report_path
    inventory_file = root / inventory_path
    report_data, _ = _load_report(report_file)
    inventory_data, _ = _load_report(inventory_file)
    report_sha, report_bytes = _file_digest_and_size(report_file)
    inventory_sha, inventory_bytes = _file_digest_and_size(inventory_file)
    return {
        "schema": MATRIX_PUBLICATION_BUNDLE_SCHEMA,
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "target_id": _STRASSEN_TARGET_ID,
        "artifact_root": str(root),
        "report_path": str(report_path).replace("\\", "/"),
        "report_sha256": report_sha,
        "report_bytes": report_bytes,
        "report": report_data or {},
        "inventory_path": str(inventory_path).replace("\\", "/"),
        "inventory_sha256": inventory_sha,
        "inventory_bytes": inventory_bytes,
        "inventory": inventory_data or {},
        "generation_command": (
            "py -3.12 -c \"from libreevolve.problems.benchmarks.matrix_results "
            "import write_strassen_2x2_publication_bundle; "
            "write_strassen_2x2_publication_bundle('libreevolve/problems/benchmarks/"
            "artifacts/strassen_2x2_publication_bundle')\""
        ),
        "generation_seeds": list(STRASSEN_2X2_PUBLICATION_BUNDLE_SEEDS),
    }


def validate_strassen_2x2_publication_bundle(
    artifact_root: str | Path | None = None,
) -> MatrixPublicationBundleValidation:
    """Validate the checked-in Strassen 2x2 publication bundle and regeneration parity."""
    root = Path(artifact_root) if artifact_root is not None else STRASSEN_2X2_PUBLICATION_BUNDLE_ROOT
    bundle = strassen_2x2_publication_bundle_record(root)
    validation = validate_matrix_publication_bundle(bundle)
    issues = list(validation.issues)
    if bundle.get("target_id") != _STRASSEN_TARGET_ID:
        issues.append(
            MatrixResultIssue(
                "invalid_strassen_target_id",
                "Strassen publication bundle must target mm_2x2x2",
            )
        )
    if bundle.get("generation_seeds") != list(STRASSEN_2X2_PUBLICATION_BUNDLE_SEEDS):
        issues.append(
            MatrixResultIssue(
                "invalid_strassen_generation_seeds",
                "Strassen publication bundle must use pinned generation seeds",
            )
        )
    _validate_strassen_regeneration_parity(root, issues)
    return MatrixPublicationBundleValidation(
        ok=not issues,
        target_id=validation.target_id,
        report_ok=validation.report_ok,
        inventory_ok=validation.inventory_ok,
        alphaevolve_comparable=validation.alphaevolve_comparable,
        issues=issues,
    )


def _validate_bundle_seeds(seeds: object) -> list[int]:
    if not isinstance(seeds, (list, tuple)) or not seeds:
        raise ValueError("matrix publication bundle seeds must be a non-empty list")
    normalized: list[int] = []
    seen: set[int] = set()
    for seed in seeds:
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError("matrix publication bundle seeds must be integers")
        if seed in seen:
            raise ValueError("matrix publication bundle seeds must be unique")
        seen.add(seed)
        normalized.append(seed)
    return normalized


def _strassen_algorithm_artifact() -> dict[str, Any]:
    return {
        "schema": "libreevolve.matrix_algorithm.v1",
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "target_id": _STRASSEN_TARGET_ID,
        "dimensions": list(_STRASSEN_DIMENSIONS),
        "algorithm": "strassen_2x2_rank7",
        "rank": len(_STRASSEN_TERMS),
        "coefficient_domain": "integer",
        "input_basis": {"left": list(_A_BASIS), "right": list(_B_BASIS)},
        "output_basis": list(_C_BASIS),
        "rank_terms": [
            {
                "id": term["id"],
                "left": dict(sorted(term["left"].items())),
                "right": dict(sorted(term["right"].items())),
                "output": dict(sorted(term["output"].items())),
            }
            for term in _STRASSEN_TERMS
        ],
    }


def _strassen_certificate_artifact(algorithm_sha256: str) -> dict[str, Any]:
    mismatches = _strassen_tensor_mismatches()
    return {
        "schema": "libreevolve.matrix_exactness_certificate.v1",
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "target_id": _STRASSEN_TARGET_ID,
        "method": "symbolic_tensor_identity",
        "algorithm_sha256": algorithm_sha256,
        "coefficient_domain": "integer",
        "rank": len(_STRASSEN_TERMS),
        "tensor_entry_count": len(_A_BASIS) * len(_B_BASIS) * len(_C_BASIS),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "verified": not mismatches,
    }


def _strassen_notebook_artifact(
    algorithm_sha256: str,
    certificate_sha256: str,
) -> dict[str, Any]:
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Strassen 2x2x2 matrix publication artifact\n",
                    "\n",
                    "This export references the generated algorithm and exactness certificate.\n",
                    f"Algorithm SHA-256: `{algorithm_sha256}`\n",
                    f"Certificate SHA-256: `{certificate_sha256}`\n",
                ],
            }
        ],
        "metadata": {
            "libreevolve": {
                "target_suite": APPENDIX_A_TARGET_SUITE,
                "target_id": _STRASSEN_TARGET_ID,
                "purpose": "artifact_export_pointer",
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def _strassen_tensor_mismatches() -> list[dict[str, Any]]:
    mismatches = []
    for left in _A_BASIS:
        for right in _B_BASIS:
            for output in _C_BASIS:
                actual = sum(
                    term["left"].get(left, 0)
                    * term["right"].get(right, 0)
                    * term["output"].get(output, 0)
                    for term in _STRASSEN_TERMS
                )
                expected = _matrix_multiply_tensor_value(left, right, output)
                if actual != expected:
                    mismatches.append(
                        {
                            "left": left,
                            "right": right,
                            "output": output,
                            "expected": expected,
                            "actual": actual,
                        }
                    )
    return mismatches


def _matrix_multiply_tensor_value(left: str, right: str, output: str) -> int:
    left_row, left_col = int(left[1]) - 1, int(left[2]) - 1
    right_row, right_col = int(right[1]) - 1, int(right[2]) - 1
    output_row, output_col = int(output[1]) - 1, int(output[2]) - 1
    return int(
        left_row == output_row
        and left_col == right_row
        and right_col == output_col
    )


def _write_canonical_json(path: Path, payload: dict[str, Any]) -> tuple[str, int]:
    raw = json.dumps(payload, sort_keys=True, indent=2).encode("utf-8")
    raw += b"\n"
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest(), len(raw)


def _file_digest_and_size(path: Path) -> tuple[str, int]:
    try:
        raw = path.read_bytes()
    except OSError:
        return "", 0
    return hashlib.sha256(raw).hexdigest(), len(raw)


def matrix_result_artifact_inventory(
    report: object | str | Path,
    artifact_root: str | Path,
) -> dict[str, Any]:
    """Verify report artifact references against concrete files under a root."""
    data, read_issues = _load_report(report)
    root = Path(artifact_root)
    records: list[dict[str, Any]] = []
    issues = [
        {"code": issue.code, "message": issue.message}
        for issue in read_issues
    ]
    if data is not None:
        artifacts = data.get("artifacts")
        if isinstance(artifacts, list):
            for artifact in artifacts:
                records.append(_matrix_artifact_inventory_record(artifact, root))
        else:
            issues.append(
                {
                    "code": "invalid_artifacts",
                    "message": "artifacts must be a non-empty list",
                }
            )
    verified_count = sum(1 for record in records if record["status"] == "verified")
    missing_count = sum(1 for record in records if record["status"] == "missing_file")
    mismatch_count = sum(
        1
        for record in records
        if record["status"] in {"hash_mismatch", "bytes_mismatch"}
    )
    invalid_count = sum(
        1
        for record in records
        if record["status"] in {"invalid_artifact", "unsafe_path", "read_error"}
    )
    if not records and data is not None:
        issues.append(
            {
                "code": "empty_artifact_inventory",
                "message": "no artifact records were available to verify",
            }
        )
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return {
        "schema": MATRIX_ARTIFACT_INVENTORY_SCHEMA,
        "report_schema": data.get("schema") if isinstance(data, dict) else None,
        "target_suite": data.get("target_suite") if isinstance(data, dict) else None,
        "target_id": data.get("target_id") if isinstance(data, dict) else None,
        "artifact_root_policy": "safe_relative_report_paths_under_artifact_root",
        "artifact_root_name": root.name,
        "artifact_count": len(records),
        "verified_count": verified_count,
        "missing_count": missing_count,
        "mismatch_count": mismatch_count,
        "invalid_count": invalid_count,
        "records_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "ok": (
            not issues
            and bool(records)
            and verified_count == len(records)
            and missing_count == 0
            and mismatch_count == 0
            and invalid_count == 0
        ),
        "issues": issues,
        "artifacts": records,
    }


def _load_report(report: object | str | Path) -> tuple[dict[str, Any] | None, list[MatrixResultIssue]]:
    if isinstance(report, dict):
        return dict(report), []
    if isinstance(report, (str, Path)):
        path = Path(report)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [MatrixResultIssue("read_error", f"failed to read report: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [MatrixResultIssue("invalid_json", f"invalid report JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [MatrixResultIssue("invalid_shape", "matrix result report must be a JSON object")]


def _validate_headline_target(
    target_suite: str | None,
    target_id: str | None,
    dimensions: object,
    issues: list[MatrixResultIssue],
) -> None:
    if target_suite != APPENDIX_A_TARGET_SUITE:
        issues.append(MatrixResultIssue("invalid_target_suite", "headline evidence must target AlphaEvolve Appendix A"))
    if target_id != MATRIX_HEADLINE_TARGET_ID:
        issues.append(MatrixResultIssue("invalid_headline_target", "headline historicity evidence must target mm_4x4x4"))
    if dimensions != MATRIX_HEADLINE_DIMENSIONS:
        issues.append(MatrixResultIssue("invalid_headline_dimensions", "headline historicity dimensions must be [4, 4, 4]"))
    if target_id == MATRIX_HEADLINE_TARGET_ID and target_suite == APPENDIX_A_TARGET_SUITE:
        _validate_known_target_dimensions(target_id, MATRIX_HEADLINE_DIMENSIONS, issues)


def _validate_headline_source_refs(value: object, issues: list[MatrixResultIssue]) -> int:
    if not isinstance(value, list) or not value:
        issues.append(MatrixResultIssue("invalid_source_refs", "headline source_refs must be a non-empty list"))
        return 0
    for source_ref in value:
        _validate_headline_source_ref(source_ref, issues)
    return len(value)


def _validate_headline_source_ref(value: object, issues: list[MatrixResultIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixResultIssue("invalid_source_ref", "headline source_refs entries must be objects"))
        return
    for field in ("source", "claim"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            issues.append(MatrixResultIssue(f"missing_source_ref_{field}", f"source ref {field} is required"))
    page = value.get("page")
    if isinstance(page, bool) or not isinstance(page, int) or page <= 0:
        issues.append(MatrixResultIssue("invalid_source_ref_page", "source ref page must be a positive integer"))
    span = value.get("span")
    if span is not None and (not isinstance(span, str) or not span.strip()):
        issues.append(MatrixResultIssue("invalid_source_ref_span", "source ref span must be non-empty when present"))


def _validate_headline_claim(
    value: object,
    target_id: str | None,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixResultIssue("invalid_headline_claim", "headline_claim must be an object"))
        return
    if target_id == MATRIX_HEADLINE_TARGET_ID and value.get("target_id") != MATRIX_HEADLINE_TARGET_ID:
        issues.append(MatrixResultIssue("headline_claim_target_mismatch", "headline_claim target_id must match mm_4x4x4"))
    rank = _positive_int(value.get("rank"), "headline_rank", issues)
    if rank is not None and rank != MATRIX_HEADLINE_RANK:
        issues.append(MatrixResultIssue("invalid_headline_rank", "headline rank must be 48"))
    multiplication_count = _positive_int(value.get("multiplication_count"), "multiplication_count", issues)
    if multiplication_count is not None and multiplication_count != MATRIX_HEADLINE_RANK:
        issues.append(MatrixResultIssue("invalid_multiplication_count", "headline multiplication_count must be 48"))
    if value.get("scalar_field") != "complex":
        issues.append(MatrixResultIssue("invalid_headline_scalar_field", "headline scalar_field must be complex"))
    if value.get("characteristic") != "zero":
        issues.append(MatrixResultIssue("invalid_headline_characteristic", "headline characteristic must be zero"))
    for field in (
        "first_characteristic_zero_rank_below_49",
        "rank_below_strassen_recursive",
        "finite_field_only_prior_distinguished",
    ):
        if value.get(field) is not True:
            issues.append(MatrixResultIssue(f"missing_{field}", f"headline claim must mark {field} true"))
    claim_text = value.get("claim_text")
    if not isinstance(claim_text, str) or not claim_text.strip():
        issues.append(MatrixResultIssue("missing_claim_text", "headline claim_text is required"))
    else:
        lowered = claim_text.lower()
        if "56 years" not in lowered:
            issues.append(MatrixResultIssue("missing_56_year_wording", "headline claim_text must preserve the 56 years historicity wording"))
        if "first" not in lowered or "characteristic-zero" not in lowered:
            issues.append(MatrixResultIssue("missing_characteristic_zero_first_wording", "headline claim_text must preserve first characteristic-zero rank-below-49 wording"))
    source_ref = value.get("source_ref")
    if not isinstance(source_ref, str) or not source_ref.strip():
        issues.append(MatrixResultIssue("missing_headline_source_ref", "headline_claim must link to a source ref"))


def _validate_headline_prior_comparisons(
    value: object,
    issues: list[MatrixResultIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(MatrixResultIssue("invalid_prior_comparisons", "prior_comparisons must be a non-empty list"))
        return 0
    records: dict[str, dict[str, Any]] = {}
    for record in value:
        if not isinstance(record, dict):
            issues.append(MatrixResultIssue("invalid_prior_comparison", "prior comparison entries must be objects"))
            continue
        prior_id = record.get("prior_id")
        if not isinstance(prior_id, str) or _ID_RE.fullmatch(prior_id) is None:
            issues.append(MatrixResultIssue("invalid_prior_id", "prior_id must be a stable identifier"))
            continue
        if prior_id in records:
            issues.append(MatrixResultIssue("duplicate_prior_id", "prior comparison prior_id values must be unique"))
        records[prior_id] = record
    _validate_strassen_prior(records.get("strassen_recursive"), issues)
    _validate_fawzi_prior(records.get("fawzi_f2"), issues)
    return len(value)


def _validate_strassen_prior(
    record: dict[str, Any] | None,
    issues: list[MatrixResultIssue],
) -> None:
    if record is None:
        issues.append(MatrixResultIssue("missing_strassen_prior", "headline evidence must compare against recursive Strassen"))
        return
    if record.get("rank") != MATRIX_HEADLINE_BASELINE_RANKS["strassen_recursive"]:
        issues.append(MatrixResultIssue("invalid_strassen_rank", "recursive Strassen comparison rank must be 49"))
    if record.get("field_scope") != "any_field":
        issues.append(MatrixResultIssue("invalid_strassen_field_scope", "recursive Strassen field_scope must be any_field"))
    if record.get("characteristic_scope") != "any_characteristic":
        issues.append(MatrixResultIssue("invalid_strassen_characteristic_scope", "recursive Strassen characteristic_scope must be any_characteristic"))
    if record.get("recursive_applicable") is not True:
        issues.append(MatrixResultIssue("invalid_strassen_recursive_applicability", "recursive Strassen must be marked recursively applicable"))
    if record.get("reference_id") != "95":
        issues.append(MatrixResultIssue("invalid_strassen_reference", "recursive Strassen comparison must cite reference id 95"))


def _validate_fawzi_prior(
    record: dict[str, Any] | None,
    issues: list[MatrixResultIssue],
) -> None:
    if record is None:
        issues.append(MatrixResultIssue("missing_fawzi_prior", "headline evidence must compare against the finite-field Fawzi result"))
        return
    if record.get("rank") != MATRIX_HEADLINE_BASELINE_RANKS["fawzi_f2"]:
        issues.append(MatrixResultIssue("invalid_fawzi_rank", "Fawzi comparison rank must be 47"))
    if record.get("field_scope") != "finite_field_2":
        issues.append(MatrixResultIssue("invalid_fawzi_field_scope", "Fawzi comparison field_scope must be finite_field_2"))
    if record.get("characteristic_scope") != "positive":
        issues.append(MatrixResultIssue("invalid_fawzi_characteristic_scope", "Fawzi comparison characteristic_scope must be positive"))
    if record.get("alphaevolve_comparable_characteristic_zero") is not False:
        issues.append(MatrixResultIssue("invalid_fawzi_zero_characteristic_comparability", "Fawzi comparison must be marked not characteristic-zero comparable"))
    if record.get("reference_id") != "26":
        issues.append(MatrixResultIssue("invalid_fawzi_reference", "Fawzi comparison must cite reference id 26"))


def _validate_headline_evidence_links(
    value: object,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixResultIssue("invalid_evidence_links", "evidence_links must be an object"))
        return
    for field in sorted(MATRIX_HEADLINE_EVIDENCE_LINK_FIELDS):
        if not isinstance(value.get(field), str) or not value[field].strip():
            issues.append(MatrixResultIssue(f"missing_{field}", f"evidence_links.{field} is required"))


def _validate_headline_historicity_runtime_required_fields(
    value: object,
    issues: list[MatrixResultIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                "invalid_required_emission_fields",
                "required_emission_fields must be a non-empty list",
            )
        )
        return 0
    fields: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            issues.append(
                MatrixResultIssue(
                    "invalid_required_emission_field",
                    "required_emission_fields entries must be non-empty strings",
                )
            )
            continue
        if item in seen:
            issues.append(
                MatrixResultIssue(
                    "duplicate_required_emission_field",
                    "required_emission_fields entries must be unique",
                )
            )
            continue
        seen.add(item)
        fields.append(item)
    missing = sorted(set(MATRIX_HEADLINE_HISTORICITY_RUNTIME_REQUIRED_FIELDS) - set(fields))
    if missing:
        issues.append(
            MatrixResultIssue(
                "missing_required_emission_field",
                "required_emission_fields must include headline target, rank, field, source, prior comparison, evidence link, result, artifact, and hash fields",
            )
        )
    return len(fields)


def _validate_headline_historicity_runtime_records(
    records: list[object],
    issues: list[MatrixResultIssue],
) -> None:
    seen: set[tuple[str, str]] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(
                MatrixResultIssue(
                    "invalid_runtime_headline_historicity_record",
                    "emitted headline historicity records must be objects",
                )
            )
            continue
        run_id = _runtime_record_text(record, "run_id", issues)
        candidate_id = _runtime_record_text(record, "candidate_id", issues)
        _runtime_record_text(record, "matrix_result_ref", issues)
        if run_id is not None and candidate_id is not None:
            key = (run_id, candidate_id)
            if key in seen:
                issues.append(
                    MatrixResultIssue(
                        "duplicate_runtime_headline_historicity_record",
                        "run_id and candidate_id must uniquely identify emitted records",
                    )
                )
            else:
                seen.add(key)
        nested = record.get("headline_historicity_evidence")
        nested_validation = validate_matrix_headline_historicity_evidence(nested)
        if not nested_validation.ok:
            issues.extend(
                MatrixResultIssue(
                    f"runtime_record_{index}_headline_historicity_{issue.code}",
                    issue.message,
                )
                for issue in nested_validation.issues
            )


def _validate_companion_selection_scope(
    value: object,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(
            MatrixResultIssue(
                "missing_companion_selection_scope",
                "matrix headline evidence must include companion notebook selection-scope metadata",
            )
        )
        return
    if value.get("claim_id") != MATRIX_HEADLINE_COMPANION_CLAIM_ID:
        issues.append(
            MatrixResultIssue(
                "invalid_companion_selection_claim_id",
                "matrix companion selection scope must link the Appendix A matrix claim",
            )
        )
    report = validate_alphaevolve_companion_selection_scope(value)
    issues.extend(
        MatrixResultIssue(f"companion_selection_{issue.code}", issue.message)
        for issue in report.issues
    )


def _validate_scalar_field_source_ref(value: object, issues: list[MatrixResultIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixResultIssue("invalid_source_ref", "source_refs entries must be objects"))
        return
    for field in ("source", "page", "claim"):
        if field == "page":
            if isinstance(value.get(field), bool) or not isinstance(value.get(field), int) or value[field] <= 0:
                issues.append(MatrixResultIssue("invalid_source_ref_page", "source ref page must be a positive integer"))
        elif not isinstance(value.get(field), str) or not value[field].strip():
            issues.append(MatrixResultIssue(f"missing_source_ref_{field}", f"source ref {field} is required"))


def _validate_tensor_rank_source_ref(value: object, issues: list[MatrixResultIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixResultIssue("invalid_source_ref", "source_refs entries must be objects"))
        return
    for field in ("source", "claim"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            issues.append(MatrixResultIssue(f"missing_source_ref_{field}", f"source ref {field} is required"))
    page = value.get("page")
    if isinstance(page, bool) or not isinstance(page, int) or page <= 0:
        issues.append(MatrixResultIssue("invalid_source_ref_page", "source ref page must be a positive integer"))
    note = value.get("note")
    if note is not None and (not isinstance(note, str) or not note.strip()):
        issues.append(MatrixResultIssue("invalid_source_ref_note", "source ref note must be a non-empty string when present"))


def _validate_tensor_rank_claims(
    value: object,
    issues: list[MatrixResultIssue],
) -> tuple[int, int, int]:
    if not isinstance(value, list) or not value:
        issues.append(MatrixResultIssue("invalid_rank_claims", "rank_claims must be a non-empty list"))
        return 0, 0, 0
    seen: set[str] = set()
    tensor_count = 0
    recursive_count = 0
    for claim in value:
        if not isinstance(claim, dict):
            issues.append(MatrixResultIssue("invalid_rank_claim", "rank claims must be objects"))
            continue
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or _ID_RE.fullmatch(claim_id) is None:
            issues.append(MatrixResultIssue("invalid_rank_claim_id", "claim_id must be a safe identifier"))
        elif claim_id in seen:
            issues.append(MatrixResultIssue("duplicate_rank_claim_id", "claim_id values must be unique"))
        else:
            seen.add(claim_id)
        rank = _positive_int(claim.get("rank"), "rank", issues)
        if rank is None:
            issues.append(MatrixResultIssue("missing_rank", "rank is required for tensor-rank claims"))
        algorithm_kind = claim.get("algorithm_kind")
        if algorithm_kind not in MATRIX_ALGORITHM_KINDS:
            issues.append(MatrixResultIssue("invalid_algorithm_kind", "algorithm_kind must distinguish tensor decompositions from non-tensor algorithms"))
        certificate_scope = claim.get("certificate_scope")
        if certificate_scope not in TENSOR_CERTIFICATE_SCOPES:
            issues.append(MatrixResultIssue("invalid_tensor_certificate_scope", "unsupported tensor-rank certificate scope"))
        recursive_applicable = claim.get("recursive_applicable")
        if not isinstance(recursive_applicable, bool):
            issues.append(MatrixResultIssue("invalid_recursive_applicable", "recursive_applicable must be boolean"))
            recursive_applicable = False
        else:
            if recursive_applicable:
                recursive_count += 1
        if algorithm_kind == "matrix_multiplication_tensor_decomposition":
            tensor_count += 1
            _validate_tensor_decomposition_rank_claim(claim, certificate_scope, recursive_applicable, issues)
        elif algorithm_kind == "non_tensor_multiplication_algorithm":
            _validate_non_tensor_rank_claim(claim, certificate_scope, recursive_applicable, issues)
    return len(value), tensor_count, recursive_count


def _validate_tensor_rank_runtime_required_fields(
    value: object,
    issues: list[MatrixResultIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                "invalid_required_emission_fields",
                "required_emission_fields must be a non-empty list",
            )
        )
        return 0
    fields: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            issues.append(
                MatrixResultIssue(
                    "invalid_required_emission_field",
                    "required_emission_fields entries must be non-empty strings",
                )
            )
            continue
        if item in seen:
            issues.append(
                MatrixResultIssue(
                    "duplicate_required_emission_field",
                    "required_emission_fields entries must be unique",
                )
            )
            continue
        seen.add(item)
        fields.append(item)
    missing = sorted(set(MATRIX_TENSOR_RANK_RUNTIME_REQUIRED_FIELDS) - set(fields))
    if missing:
        issues.append(
            MatrixResultIssue(
                "missing_required_emission_field",
                "required_emission_fields must include algorithm kind, rank, recursive applicability, tensor/certificate, result, artifact, and hash fields",
            )
        )
    return len(fields)


def _validate_tensor_rank_runtime_records(
    records: list[object],
    issues: list[MatrixResultIssue],
) -> None:
    seen: set[tuple[str, str]] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(
                MatrixResultIssue(
                    "invalid_runtime_tensor_rank_record",
                    "emitted tensor-rank records must be objects",
                )
            )
            continue
        run_id = _runtime_record_text(record, "run_id", issues)
        candidate_id = _runtime_record_text(record, "candidate_id", issues)
        _runtime_record_text(record, "matrix_result_ref", issues)
        if run_id is not None and candidate_id is not None:
            key = (run_id, candidate_id)
            if key in seen:
                issues.append(
                    MatrixResultIssue(
                        "duplicate_runtime_tensor_rank_record",
                        "run_id and candidate_id must uniquely identify emitted records",
                    )
                )
            else:
                seen.add(key)
        nested = record.get("tensor_rank_evidence")
        nested_validation = validate_matrix_tensor_rank_evidence(nested)
        if not nested_validation.ok:
            issues.extend(
                MatrixResultIssue(
                    f"runtime_record_{index}_tensor_rank_{issue.code}",
                    issue.message,
                )
                for issue in nested_validation.issues
            )


def _validate_tensor_decomposition_rank_claim(
    claim: dict[str, Any],
    certificate_scope: object,
    recursive_applicable: bool,
    issues: list[MatrixResultIssue],
) -> None:
    if certificate_scope != "matrix_multiplication_tensor_identity":
        issues.append(MatrixResultIssue("invalid_tensor_decomposition_certificate_scope", "tensor decompositions require matrix_multiplication_tensor_identity certificate scope"))
    if recursive_applicable is not True:
        issues.append(MatrixResultIssue("missing_recursive_applicability", "matrix multiplication tensor decompositions must declare recursive_applicable true"))
    if claim.get("tensor_identity_verified") is not True:
        issues.append(MatrixResultIssue("tensor_identity_not_verified", "tensor decompositions must verify the matrix multiplication tensor identity"))
    for field in ("target_tensor_ref", "exactness_certificate_ref"):
        if not isinstance(claim.get(field), str) or not claim[field].strip():
            issues.append(MatrixResultIssue(f"missing_{field}", f"{field} is required for tensor decomposition claims"))
    if claim.get("non_tensor_caveat") is not None:
        issues.append(MatrixResultIssue("unexpected_non_tensor_caveat", "tensor decomposition claims must not carry a non_tensor_caveat"))


def _validate_non_tensor_rank_claim(
    claim: dict[str, Any],
    certificate_scope: object,
    recursive_applicable: bool,
    issues: list[MatrixResultIssue],
) -> None:
    if certificate_scope != "functional_multiplication_only":
        issues.append(MatrixResultIssue("invalid_non_tensor_certificate_scope", "non-tensor algorithms must use functional_multiplication_only certificate scope"))
    if recursive_applicable is not False:
        issues.append(MatrixResultIssue("invalid_non_tensor_recursive_applicability", "non-tensor algorithms must declare recursive_applicable false"))
    caveat = claim.get("non_tensor_caveat")
    if not isinstance(caveat, dict):
        issues.append(MatrixResultIssue("missing_non_tensor_caveat", "non-tensor algorithms require a non_tensor_caveat object"))
        return
    if caveat.get("not_matrix_tensor_decomposition") is not True:
        issues.append(MatrixResultIssue("missing_non_tensor_decomposition_caveat", "non-tensor caveat must mark not_matrix_tensor_decomposition true"))
    if caveat.get("not_recursively_applicable") is not True:
        issues.append(MatrixResultIssue("missing_non_recursive_caveat", "non-tensor caveat must mark not_recursively_applicable true"))
    if not isinstance(caveat.get("source_note_ref"), str) or not caveat["source_note_ref"].strip():
        issues.append(MatrixResultIssue("missing_source_note_ref", "non-tensor caveat must link to source note or footnote provenance"))


def _validate_scalar_field_claims(
    value: object,
    target_id: str | None,
    issues: list[MatrixResultIssue],
) -> tuple[int, int]:
    if not isinstance(value, list) or not value:
        issues.append(MatrixResultIssue("invalid_field_claims", "field_claims must be a non-empty list"))
        return 0, 0
    seen: set[str] = set()
    complex_claim_count = 0
    for claim in value:
        if not isinstance(claim, dict):
            issues.append(MatrixResultIssue("invalid_field_claim", "field claims must be objects"))
            continue
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or _ID_RE.fullmatch(claim_id) is None:
            issues.append(MatrixResultIssue("invalid_field_claim_id", "claim_id must be a safe identifier"))
        elif claim_id in seen:
            issues.append(MatrixResultIssue("duplicate_field_claim_id", "claim_id values must be unique"))
        else:
            seen.add(claim_id)
        field_type = claim.get("scalar_field")
        if field_type not in SCALAR_FIELD_TYPES:
            issues.append(MatrixResultIssue("invalid_scalar_field", "scalar_field must be real, complex, finite_field, or any_field"))
        characteristic = claim.get("characteristic")
        if characteristic not in SCALAR_FIELD_CHARACTERISTICS:
            issues.append(MatrixResultIssue("invalid_characteristic", "characteristic must be zero, positive, or any"))
        applicability = _validate_scalar_field_applicability(claim.get("applicability"), issues)
        certificate_scope = claim.get("certificate_scope")
        if certificate_scope not in SCALAR_FIELD_CERTIFICATE_SCOPES:
            issues.append(MatrixResultIssue("invalid_certificate_scope", "unsupported scalar-field certificate scope"))
        _validate_scalar_field_representation(claim.get("coefficient_representation"), field_type, issues)
        for field in ("algorithm_ref", "certificate_ref"):
            if not isinstance(claim.get(field), str) or not claim[field].strip():
                issues.append(MatrixResultIssue(f"missing_{field}", f"{field} is required for scalar-field claims"))
        if field_type == "complex":
            complex_claim_count += 1
            _validate_complex_scalar_claim(
                claim,
                target_id,
                characteristic,
                applicability,
                certificate_scope,
                issues,
            )
        elif field_type == "finite_field":
            _validate_finite_field_claim(claim, characteristic, applicability, certificate_scope, issues)
    return len(value), complex_claim_count


def _validate_scalar_field_runtime_required_fields(
    value: object,
    issues: list[MatrixResultIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                "invalid_required_emission_fields",
                "required_emission_fields must be a non-empty list",
            )
        )
        return 0
    fields: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            issues.append(
                MatrixResultIssue(
                    "invalid_required_emission_field",
                    "required_emission_fields entries must be non-empty strings",
                )
            )
            continue
        if item in seen:
            issues.append(
                MatrixResultIssue(
                    "duplicate_required_emission_field",
                    "required_emission_fields entries must be unique",
                )
            )
            continue
        seen.add(item)
        fields.append(item)
    missing = sorted(set(MATRIX_SCALAR_FIELD_RUNTIME_REQUIRED_FIELDS) - set(fields))
    if missing:
        issues.append(
            MatrixResultIssue(
                "missing_required_emission_field",
                "required_emission_fields must include scalar-field, characteristic, applicability, representation, certificate, result, artifact, and hash fields",
            )
        )
    return len(fields)


def _validate_scalar_field_runtime_records(
    records: list[object],
    issues: list[MatrixResultIssue],
) -> None:
    seen: set[tuple[str, str]] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(
                MatrixResultIssue(
                    "invalid_runtime_scalar_field_record",
                    "emitted scalar-field records must be objects",
                )
            )
            continue
        run_id = _runtime_record_text(record, "run_id", issues)
        candidate_id = _runtime_record_text(record, "candidate_id", issues)
        _runtime_record_text(record, "matrix_result_ref", issues)
        if run_id is not None and candidate_id is not None:
            key = (run_id, candidate_id)
            if key in seen:
                issues.append(
                    MatrixResultIssue(
                        "duplicate_runtime_scalar_field_record",
                        "run_id and candidate_id must uniquely identify emitted records",
                    )
                )
            else:
                seen.add(key)
        nested = record.get("scalar_field_evidence")
        nested_validation = validate_matrix_scalar_field_evidence(nested)
        if not nested_validation.ok:
            issues.extend(
                MatrixResultIssue(
                    f"runtime_record_{index}_scalar_field_{issue.code}",
                    issue.message,
                )
                for issue in nested_validation.issues
            )


def _validate_scalar_field_applicability(
    value: object,
    issues: list[MatrixResultIssue],
) -> set[str]:
    if not isinstance(value, list) or not value:
        issues.append(MatrixResultIssue("invalid_applicability", "applicability must be a non-empty list"))
        return set()
    applicability: set[str] = set()
    for item in value:
        if item not in SCALAR_FIELD_APPLICABILITY:
            issues.append(MatrixResultIssue("invalid_applicability", "unsupported scalar-field applicability"))
        elif isinstance(item, str):
            applicability.add(item)
    return applicability


def _validate_scalar_field_representation(
    value: object,
    field_type: object,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixResultIssue("invalid_coefficient_representation", "coefficient_representation must be an object"))
        return
    representation = value.get("representation")
    if representation not in SCALAR_FIELD_COEFFICIENT_REPRESENTATIONS:
        issues.append(MatrixResultIssue("invalid_coefficient_representation", "unsupported coefficient representation"))
    if value.get("exact") is not True:
        issues.append(MatrixResultIssue("coefficient_representation_not_exact", "coefficient representation must be exact"))
    if field_type == "complex":
        if representation not in {"complex_integer", "complex_half_integer"}:
            issues.append(MatrixResultIssue("invalid_complex_coefficient_representation", "complex claims require exact complex integer or half-integer representation"))
        real_domain = value.get("real_part_domain")
        imaginary_domain = value.get("imaginary_part_domain")
        if real_domain not in PUBLICATION_COEFFICIENT_DOMAINS or imaginary_domain not in PUBLICATION_COEFFICIENT_DOMAINS:
            issues.append(MatrixResultIssue("invalid_complex_component_domain", "complex coefficient real/imaginary parts must be integer or half_integer"))
    if field_type == "finite_field":
        if representation != "finite_field":
            issues.append(MatrixResultIssue("invalid_finite_field_representation", "finite-field claims require finite_field coefficient representation"))


def _validate_complex_scalar_claim(
    claim: dict[str, Any],
    target_id: str | None,
    characteristic: object,
    applicability: set[str],
    certificate_scope: object,
    issues: list[MatrixResultIssue],
) -> None:
    if target_id is not None and target_id not in PAPER_COMPLEX_TARGET_IDS:
        issues.append(MatrixResultIssue("target_not_paper_complex_valued", "complex-valued Appendix A claim must match a paper-noted complex target"))
    if characteristic != "zero":
        issues.append(MatrixResultIssue("invalid_complex_characteristic", "complex matrix claims must have characteristic zero"))
    if not {"complex_matrices", "real_matrices"}.issubset(applicability):
        issues.append(MatrixResultIssue("missing_complex_real_applicability", "complex claims must cover exact complex and real matrix multiplication applicability"))
    if certificate_scope != "complex_and_real":
        issues.append(MatrixResultIssue("invalid_complex_certificate_scope", "complex claims must use complex_and_real certificate scope"))
    if claim.get("paper_complex_row") is not True:
        issues.append(MatrixResultIssue("missing_paper_complex_row", "complex Appendix A claims must mark the paper complex-valued row caveat"))


def _validate_finite_field_claim(
    claim: dict[str, Any],
    characteristic: object,
    applicability: set[str],
    certificate_scope: object,
    issues: list[MatrixResultIssue],
) -> None:
    if characteristic != "positive":
        issues.append(MatrixResultIssue("invalid_finite_field_characteristic", "finite-field claims must have positive characteristic"))
    prime = claim.get("prime_characteristic")
    if isinstance(prime, bool) or not isinstance(prime, int) or prime <= 1:
        issues.append(MatrixResultIssue("invalid_prime_characteristic", "finite-field claims require a prime_characteristic > 1"))
    field_order = claim.get("field_order")
    if isinstance(field_order, bool) or not isinstance(field_order, int) or field_order <= 1:
        issues.append(MatrixResultIssue("invalid_field_order", "finite-field claims require field_order > 1"))
    if "finite_field_matrices" not in applicability:
        issues.append(MatrixResultIssue("missing_finite_field_applicability", "finite-field claims must cover finite_field_matrices"))
    if certificate_scope != "finite_field_only":
        issues.append(MatrixResultIssue("invalid_finite_field_certificate_scope", "finite-field claims must use finite_field_only certificate scope"))


def _validate_sweep_hyper_library(value: object, issues: list[MatrixResultIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixResultIssue("invalid_hyper_library", "hyper_library must be an object"))
        return
    if value.get("name") != "hyper":
        issues.append(MatrixResultIssue("invalid_hyper_library_name", "hyper_library.name must be hyper"))
    source = value.get("source")
    if not isinstance(source, str) or not source.strip():
        issues.append(MatrixResultIssue("missing_hyper_library_source", "hyper_library.source is required"))


def _validate_sweep_hyperparameters(
    value: object,
    issues: list[MatrixResultIssue],
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    if not isinstance(value, list) or not value:
        issues.append(MatrixResultIssue("invalid_hyperparameters", "hyperparameters must be a non-empty list"))
        return [], {}
    names: list[str] = []
    specs: dict[str, dict[str, Any]] = {}
    seen: set[str] = set()
    for record in value:
        if not isinstance(record, dict):
            issues.append(MatrixResultIssue("invalid_hyperparameter", "hyperparameter records must be objects"))
            continue
        name = record.get("name")
        if not isinstance(name, str) or _ID_RE.fullmatch(name) is None:
            issues.append(MatrixResultIssue("invalid_hyperparameter_name", "hyperparameter name must be a safe identifier"))
            continue
        if name in seen:
            issues.append(MatrixResultIssue("duplicate_hyperparameter_name", "hyperparameter names must be unique"))
            continue
        seen.add(name)
        names.append(name)
        distribution = record.get("distribution")
        if distribution not in SWEEP_DISTRIBUTIONS:
            issues.append(MatrixResultIssue("invalid_hyperparameter_distribution", "unsupported sweep hyperparameter distribution"))
            distribution = None
        dtype = record.get("dtype", "float")
        if dtype not in SWEEP_DTYPES:
            issues.append(MatrixResultIssue("invalid_hyperparameter_dtype", "hyperparameter dtype must be float or int"))
        spec: dict[str, Any] = {"distribution": distribution, "dtype": dtype}
        if distribution in {"uniform", "log_uniform"}:
            low = _finite_number(record.get("low"))
            high = _finite_number(record.get("high"))
            if low is None or high is None:
                issues.append(MatrixResultIssue("invalid_hyperparameter_range", "uniform sweep hyperparameters require finite low/high values"))
            elif low >= high:
                issues.append(MatrixResultIssue("invalid_hyperparameter_range", "hyperparameter low must be less than high"))
            else:
                spec["low"] = low
                spec["high"] = high
        elif distribution == "choice":
            choices = record.get("choices")
            if not isinstance(choices, list) or not choices:
                issues.append(MatrixResultIssue("invalid_hyperparameter_choices", "choice sweep hyperparameters require non-empty choices"))
                choices = []
            spec["choices"] = choices
        specs[name] = spec
    if names and not any(specs[name].get("distribution") == "uniform" for name in names):
        issues.append(MatrixResultIssue("missing_hyper_uniform", "Figure 9 sweep evidence must include at least one hyper.uniform-style range"))
    return names, specs


def _validate_sweep_configurations(
    value: object,
    hyperparameter_names: list[str],
    hyperparameter_specs: dict[str, dict[str, Any]],
    winning_configuration_id: object,
    issues: list[MatrixResultIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(MatrixResultIssue("invalid_sampled_configurations", "sampled_configurations must be a non-empty list"))
        return 0
    if not isinstance(winning_configuration_id, str) or not winning_configuration_id.strip():
        issues.append(MatrixResultIssue("missing_winning_configuration_id", "winning_configuration_id is required"))
        winning_configuration_id = None
    seen: set[str] = set()
    selected_ids: set[str] = set()
    sampled_ids: set[str] = set()
    for record in value:
        if not isinstance(record, dict):
            issues.append(MatrixResultIssue("invalid_sampled_configuration", "sampled configuration records must be objects"))
            continue
        configuration_id = record.get("configuration_id")
        if not isinstance(configuration_id, str) or _ID_RE.fullmatch(configuration_id) is None:
            issues.append(MatrixResultIssue("invalid_configuration_id", "configuration_id must be a safe identifier"))
        elif configuration_id in seen:
            issues.append(MatrixResultIssue("duplicate_configuration_id", "configuration_id values must be unique"))
        else:
            seen.add(configuration_id)
            sampled_ids.add(configuration_id)
        _validate_sweep_configuration_values(
            record.get("hyperparameters"),
            hyperparameter_names,
            hyperparameter_specs,
            issues,
        )
        if _finite_number(record.get("loss")) is None:
            issues.append(MatrixResultIssue("invalid_sweep_loss", "sampled configuration loss must be finite"))
        _positive_int(record.get("rank"), "rank", issues)
        selected = record.get("selected", False)
        if not isinstance(selected, bool):
            issues.append(MatrixResultIssue("invalid_selected_flag", "selected must be boolean when present"))
            selected = False
        if selected:
            if isinstance(configuration_id, str):
                selected_ids.add(configuration_id)
            for field in ("exactness_certificate_ref", "final_decomposition_ref"):
                if not isinstance(record.get(field), str) or not record[field].strip():
                    issues.append(MatrixResultIssue(f"missing_{field}", f"selected sweep configuration must include {field}"))
    if not selected_ids:
        issues.append(MatrixResultIssue("missing_selected_configuration", "at least one sampled configuration must be selected"))
    if isinstance(winning_configuration_id, str):
        if winning_configuration_id not in sampled_ids:
            issues.append(MatrixResultIssue("unknown_winning_configuration", "winning_configuration_id must match a sampled configuration"))
        elif winning_configuration_id not in selected_ids:
            issues.append(MatrixResultIssue("winning_configuration_not_selected", "winning_configuration_id must refer to a selected configuration"))
    return len(value)


def _validate_sweep_space_runtime_required_fields(
    value: object,
    issues: list[MatrixResultIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                "invalid_required_emission_fields",
                "required_emission_fields must be a non-empty list",
            )
        )
        return 0
    fields: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            issues.append(
                MatrixResultIssue(
                    "invalid_required_emission_field",
                    "required_emission_fields entries must be non-empty strings",
                )
            )
            continue
        if item in seen:
            issues.append(
                MatrixResultIssue(
                    "duplicate_required_emission_field",
                    "required_emission_fields entries must be unique",
                )
            )
            continue
        seen.add(item)
        fields.append(item)
    missing = sorted(set(MATRIX_SWEEP_SPACE_RUNTIME_REQUIRED_FIELDS) - set(fields))
    if missing:
        issues.append(
            MatrixResultIssue(
                "missing_required_emission_field",
                "required_emission_fields must include search program, hyperparameter, sampled configuration, certificate, result, artifact, and hash fields",
            )
        )
    return len(fields)


def _validate_sweep_space_runtime_records(
    records: list[object],
    issues: list[MatrixResultIssue],
) -> None:
    seen: set[tuple[str, str]] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(
                MatrixResultIssue(
                    "invalid_runtime_sweep_space_record",
                    "emitted sweep-space records must be objects",
                )
            )
            continue
        run_id = _runtime_record_text(record, "run_id", issues)
        candidate_id = _runtime_record_text(record, "candidate_id", issues)
        target_id = _runtime_record_text(record, "target_id", issues)
        seed = _runtime_record_int(record, "seed", issues)
        search_program_ref = _runtime_record_text(
            record,
            "search_program_ref",
            issues,
        )
        sweep_function_name = _runtime_record_text(
            record,
            "sweep_function_name",
            issues,
        )
        hyper_library = record.get("hyper_library")
        if not isinstance(hyper_library, dict):
            issues.append(
                MatrixResultIssue(
                    "invalid_runtime_record_hyper_library",
                    "emitted runtime sweep-space records must include hyper_library",
                )
            )
            hyper_library = None
        hyperparameters = record.get("hyperparameters")
        if not isinstance(hyperparameters, list) or not hyperparameters:
            issues.append(
                MatrixResultIssue(
                    "invalid_runtime_record_hyperparameters",
                    "emitted runtime sweep-space records must include non-empty hyperparameters",
                )
            )
            hyperparameters = None
        sampled_configurations = record.get("sampled_configurations")
        if not isinstance(sampled_configurations, list) or not sampled_configurations:
            issues.append(
                MatrixResultIssue(
                    "invalid_runtime_record_sampled_configurations",
                    "emitted runtime sweep-space records must include non-empty sampled_configurations",
                )
            )
            sampled_configurations = None
        winning_configuration_id = _runtime_record_text(
            record,
            "winning_configuration_id",
            issues,
        )
        exactness_certificate_ref = _runtime_record_text(
            record,
            "exactness_certificate_ref",
            issues,
        )
        final_decomposition_ref = _runtime_record_text(
            record,
            "final_decomposition_ref",
            issues,
        )
        _runtime_record_text(record, "matrix_result_ref", issues)
        _validate_runtime_artifact_paths(
            record.get("artifact_paths"),
            "sweep_space",
            index,
            issues,
        )
        _validate_runtime_artifact_sha(
            record.get("artifact_sha256"),
            "sweep_space",
            index,
            issues,
        )
        if run_id is not None and candidate_id is not None:
            key = (run_id, candidate_id)
            if key in seen:
                issues.append(
                    MatrixResultIssue(
                        "duplicate_runtime_sweep_space_record",
                        "run_id and candidate_id must uniquely identify emitted records",
                    )
                )
            else:
                seen.add(key)
        nested = record.get("sweep_space_evidence")
        nested_validation = validate_matrix_sweep_space_evidence(nested)
        if not nested_validation.ok:
            issues.extend(
                MatrixResultIssue(
                    f"runtime_record_{index}_sweep_space_{issue.code}",
                    issue.message,
                )
                for issue in nested_validation.issues
            )
        elif isinstance(nested, dict):
            _validate_sweep_space_runtime_record_linkage(
                record_index=index,
                nested=nested,
                target_id=target_id,
                search_program_ref=search_program_ref,
                sweep_function_name=sweep_function_name,
                hyper_library=hyper_library,
                hyperparameters=hyperparameters,
                sampled_configurations=sampled_configurations,
                winning_configuration_id=winning_configuration_id,
                exactness_certificate_ref=exactness_certificate_ref,
                final_decomposition_ref=final_decomposition_ref,
                issues=issues,
            )


def _validate_sweep_space_runtime_record_linkage(
    *,
    record_index: int,
    nested: dict[str, Any],
    target_id: str | None,
    search_program_ref: str | None,
    sweep_function_name: str | None,
    hyper_library: dict[str, Any] | None,
    hyperparameters: list[Any] | None,
    sampled_configurations: list[Any] | None,
    winning_configuration_id: str | None,
    exactness_certificate_ref: str | None,
    final_decomposition_ref: str | None,
    issues: list[MatrixResultIssue],
) -> None:
    if target_id is not None and nested.get("target_id") != target_id:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_sweep_space_target_mismatch",
                "runtime target_id must match nested sweep-space evidence",
            )
        )
    if (
        search_program_ref is not None
        and nested.get("search_program_ref") != search_program_ref
    ):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_sweep_space_search_program_mismatch",
                "runtime search_program_ref must match nested sweep-space evidence",
            )
        )
    if (
        sweep_function_name is not None
        and nested.get("sweep_function_name") != sweep_function_name
    ):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_sweep_space_function_mismatch",
                "runtime sweep_function_name must match nested sweep-space evidence",
            )
        )
    if hyper_library is not None and nested.get("hyper_library") != hyper_library:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_sweep_space_hyper_library_mismatch",
                "runtime hyper_library must match nested sweep-space evidence",
            )
        )
    if hyperparameters is not None and nested.get("hyperparameters") != hyperparameters:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_sweep_space_hyperparameters_mismatch",
                "runtime hyperparameters must match nested sweep-space evidence",
            )
        )
    if (
        sampled_configurations is not None
        and nested.get("sampled_configurations") != sampled_configurations
    ):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_sweep_space_configurations_mismatch",
                "runtime sampled_configurations must match nested sweep-space evidence",
            )
        )
    if (
        winning_configuration_id is not None
        and nested.get("winning_configuration_id") != winning_configuration_id
    ):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_sweep_space_winner_mismatch",
                "runtime winning_configuration_id must match nested sweep-space evidence",
            )
        )
    if winning_configuration_id is None:
        return
    try:
        winner = _selected_sweep_configuration(nested, winning_configuration_id)
    except ValueError:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_sweep_space_missing_winner",
                "runtime winning_configuration_id must identify a selected nested configuration",
            )
        )
        return
    if (
        exactness_certificate_ref is not None
        and winner.get("exactness_certificate_ref") != exactness_certificate_ref
    ):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_sweep_space_certificate_mismatch",
                "runtime exactness_certificate_ref must match the selected nested configuration",
            )
        )
    if (
        final_decomposition_ref is not None
        and winner.get("final_decomposition_ref") != final_decomposition_ref
    ):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_sweep_space_decomposition_mismatch",
                "runtime final_decomposition_ref must match the selected nested configuration",
            )
        )


def _selected_sweep_configuration(
    evidence: dict[str, Any],
    winning_configuration_id: object,
) -> dict[str, Any]:
    if not isinstance(winning_configuration_id, str):
        raise ValueError("winning_configuration_id must be a string")
    configurations = evidence.get("sampled_configurations")
    if not isinstance(configurations, list):
        raise ValueError("sampled_configurations must be a list")
    for configuration in configurations:
        if (
            isinstance(configuration, dict)
            and configuration.get("configuration_id") == winning_configuration_id
            and configuration.get("selected") is True
        ):
            return configuration
    raise ValueError("winning_configuration_id must identify a selected configuration")


def _validate_sweep_configuration_values(
    value: object,
    hyperparameter_names: list[str],
    hyperparameter_specs: dict[str, dict[str, Any]],
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixResultIssue("invalid_configuration_hyperparameters", "sampled configuration hyperparameters must be an object"))
        return
    value_names = set(value)
    missing = [name for name in hyperparameter_names if name not in value_names]
    if missing:
        issues.append(MatrixResultIssue("missing_configuration_hyperparameter", "sampled configuration must include every declared hyperparameter"))
    extra = sorted(value_names - set(hyperparameter_names))
    if extra:
        issues.append(MatrixResultIssue("unknown_configuration_hyperparameter", "sampled configuration contains undeclared hyperparameters"))
    for name in hyperparameter_names:
        if name not in value:
            continue
        spec = hyperparameter_specs.get(name, {})
        distribution = spec.get("distribution")
        observed = value[name]
        if distribution in {"uniform", "log_uniform"}:
            numeric = _finite_number(observed)
            if numeric is None:
                issues.append(MatrixResultIssue("invalid_configuration_hyperparameter_value", "sampled numeric hyperparameter values must be finite"))
                continue
            low = spec.get("low")
            high = spec.get("high")
            if isinstance(low, (int, float)) and isinstance(high, (int, float)) and not (float(low) <= numeric <= float(high)):
                issues.append(MatrixResultIssue("configuration_hyperparameter_out_of_range", "sampled hyperparameter value must be within its declared range"))
        elif distribution == "choice":
            choices = spec.get("choices", [])
            if observed not in choices:
                issues.append(MatrixResultIssue("configuration_hyperparameter_not_in_choices", "sampled choice hyperparameter value must be declared"))


def _finite_number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    as_float = float(value)
    if not math.isfinite(as_float):
        return None
    return as_float


def _validate_near_integrality_prompt(value: object, issues: list[MatrixResultIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixResultIssue("invalid_prompt_instruction", "prompt_instruction must be an object"))
        return
    text = value.get("text")
    if not isinstance(text, str) or not text.strip():
        issues.append(MatrixResultIssue("missing_prompt_instruction_text", "prompt_instruction.text is required"))
    else:
        lowered = text.lower()
        if "near-integral" not in lowered and "near integral" not in lowered:
            issues.append(MatrixResultIssue("missing_near_integral_instruction", "prompt instruction must ask for near-integral solutions"))
        if "matrix" not in lowered or "decomposition" not in lowered:
            issues.append(MatrixResultIssue("missing_matrix_decomposition_instruction", "prompt instruction must reference matrix decompositions"))
    for field in ("prompt_hash", "source"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            issues.append(MatrixResultIssue(f"missing_prompt_{field}", f"prompt_instruction.{field} is required"))


def _validate_rounding_policy(value: object, issues: list[MatrixResultIssue]) -> str | None:
    if not isinstance(value, dict):
        issues.append(MatrixResultIssue("invalid_rounding_policy", "rounding_policy must be an object"))
        return None
    domain = value.get("target_domain")
    if domain not in NEAR_INTEGRAL_ROUNDING_DOMAINS:
        issues.append(MatrixResultIssue("invalid_rounding_target_domain", "rounding target_domain must be integer or half_integer"))
        domain = None
    if value.get("method") != "nearest":
        issues.append(MatrixResultIssue("invalid_rounding_method", "rounding method must be nearest"))
    tolerance = value.get("max_abs_error")
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or not math.isfinite(float(tolerance)) or float(tolerance) < 0:
        issues.append(MatrixResultIssue("invalid_rounding_tolerance", "max_abs_error must be a finite non-negative number"))
    certificate_scope = value.get("certificate_scope")
    if certificate_scope != "rounded_coefficients":
        issues.append(MatrixResultIssue("invalid_certificate_scope", "certificate_scope must be rounded_coefficients"))
    return domain


def _validate_near_integrality_candidates(
    value: object,
    rounding_domain: str | None,
    issues: list[MatrixResultIssue],
) -> tuple[int, int]:
    if not isinstance(value, list) or not value:
        issues.append(MatrixResultIssue("invalid_candidate_records", "candidate_records must be a non-empty list"))
        return 0, 0
    coefficient_count = 0
    seen: set[str] = set()
    for candidate in value:
        if not isinstance(candidate, dict):
            issues.append(MatrixResultIssue("invalid_candidate_record", "candidate records must be objects"))
            continue
        candidate_id = candidate.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            issues.append(MatrixResultIssue("missing_candidate_id", "candidate_id is required"))
        elif candidate_id in seen:
            issues.append(MatrixResultIssue("duplicate_candidate_id", "candidate_id values must be unique"))
        elif candidate_id:
            seen.add(candidate_id)
        raw_coefficients = candidate.get("raw_coefficients")
        rounded_coefficients = candidate.get("rounded_coefficients")
        if not isinstance(raw_coefficients, list) or not raw_coefficients:
            issues.append(MatrixResultIssue("invalid_raw_coefficients", "raw_coefficients must be a non-empty list"))
            raw_coefficients = []
        if not isinstance(rounded_coefficients, list) or not rounded_coefficients:
            issues.append(MatrixResultIssue("invalid_rounded_coefficients", "rounded_coefficients must be a non-empty list"))
            rounded_coefficients = []
        if raw_coefficients and rounded_coefficients and len(raw_coefficients) != len(rounded_coefficients):
            issues.append(MatrixResultIssue("coefficient_count_mismatch", "raw and rounded coefficient counts must match"))
        coefficient_count += min(len(raw_coefficients), len(rounded_coefficients))
        max_abs_error = candidate.get("max_abs_rounding_error")
        computed_error = _validate_coefficient_pairs(raw_coefficients, rounded_coefficients, rounding_domain, issues)
        if computed_error is not None:
            if isinstance(max_abs_error, bool) or not isinstance(max_abs_error, (int, float)) or not math.isfinite(float(max_abs_error)):
                issues.append(MatrixResultIssue("invalid_max_abs_rounding_error", "max_abs_rounding_error must be finite"))
            elif not math.isclose(float(max_abs_error), computed_error, rel_tol=0.0, abs_tol=1e-12):
                issues.append(MatrixResultIssue("max_abs_rounding_error_mismatch", "max_abs_rounding_error must match raw-versus-rounded coefficients"))
        exactness_ref = candidate.get("exactness_certificate_ref")
        if not isinstance(exactness_ref, str) or not exactness_ref.strip():
            issues.append(MatrixResultIssue("missing_exactness_certificate_ref", "candidate must link rounded coefficients to an exactness certificate"))
    return len(value), coefficient_count


def _validate_near_integrality_runtime_required_fields(
    value: object,
    issues: list[MatrixResultIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                "invalid_required_emission_fields",
                "required_emission_fields must be a non-empty list",
            )
        )
        return 0
    fields: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            issues.append(
                MatrixResultIssue(
                    "invalid_required_emission_field",
                    "required_emission_fields entries must be non-empty strings",
                )
            )
            continue
        if item in seen:
            issues.append(
                MatrixResultIssue(
                    "duplicate_required_emission_field",
                    "required_emission_fields entries must be unique",
                )
            )
            continue
        seen.add(item)
        fields.append(item)
    missing = sorted(set(MATRIX_NEAR_INTEGRALITY_RUNTIME_REQUIRED_FIELDS) - set(fields))
    if missing:
        issues.append(
            MatrixResultIssue(
                "missing_required_emission_field",
                "required_emission_fields must include prompt, coefficient, certificate, result, artifact, and hash fields",
            )
        )
    return len(fields)


def _validate_near_integrality_runtime_records(
    records: list[object],
    issues: list[MatrixResultIssue],
) -> None:
    seen: set[tuple[str, str]] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(
                MatrixResultIssue(
                    "invalid_runtime_near_integrality_record",
                    "emitted near-integrality records must be objects",
                )
            )
            continue
        run_id = _runtime_record_text(record, "run_id", issues)
        candidate_id = _runtime_record_text(record, "candidate_id", issues)
        target_id = _runtime_record_text(record, "target_id", issues)
        seed = _runtime_record_int(record, "seed", issues)
        prompt_hash = _runtime_record_text(record, "prompt_hash", issues)
        if prompt_hash is not None and _SHA256_RE.fullmatch(prompt_hash) is None:
            issues.append(
                MatrixResultIssue(
                    "invalid_runtime_record_prompt_hash",
                    "emitted runtime near-integrality records must include SHA-256 prompt_hash",
                )
            )
        prompt_instruction = _runtime_record_text(
            record,
            "prompt_instruction",
            issues,
        )
        raw_coefficients = _runtime_record_coefficients(
            record,
            "raw_coefficients",
            issues,
        )
        rounded_coefficients = _runtime_record_coefficients(
            record,
            "rounded_coefficients",
            issues,
        )
        max_abs_rounding_error = _runtime_record_finite_number(
            record,
            "max_abs_rounding_error",
            issues,
        )
        exactness_certificate_ref = _runtime_record_text(
            record,
            "exactness_certificate_ref",
            issues,
        )
        _runtime_record_text(record, "matrix_result_ref", issues)
        _validate_runtime_artifact_paths(
            record.get("artifact_paths"),
            "near_integrality",
            index,
            issues,
        )
        _validate_runtime_artifact_sha(
            record.get("artifact_sha256"),
            "near_integrality",
            index,
            issues,
        )
        if run_id is not None and candidate_id is not None:
            key = (run_id, candidate_id)
            if key in seen:
                issues.append(
                    MatrixResultIssue(
                        "duplicate_runtime_near_integrality_record",
                        "run_id and candidate_id must uniquely identify emitted records",
                    )
                )
            else:
                seen.add(key)
        nested = record.get("near_integrality_evidence")
        nested_validation = validate_matrix_near_integrality_evidence(nested)
        if not nested_validation.ok:
            issues.extend(
                MatrixResultIssue(
                    f"runtime_record_{index}_near_integrality_{issue.code}",
                    issue.message,
                )
                for issue in nested_validation.issues
            )
        elif isinstance(nested, dict):
            _validate_near_integrality_runtime_record_linkage(
                record_index=index,
                record=record,
                nested=nested,
                target_id=target_id,
                candidate_id=candidate_id,
                seed=seed,
                prompt_hash=prompt_hash,
                prompt_instruction=prompt_instruction,
                raw_coefficients=raw_coefficients,
                rounded_coefficients=rounded_coefficients,
                max_abs_rounding_error=max_abs_rounding_error,
                exactness_certificate_ref=exactness_certificate_ref,
                issues=issues,
            )


def _runtime_record_text(
    record: dict[str, Any],
    field: str,
    issues: list[MatrixResultIssue],
) -> str | None:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        issues.append(
            MatrixResultIssue(
                f"missing_runtime_record_{field}",
                f"emitted runtime near-integrality records must include {field}",
            )
        )
        return None
    return value


def _runtime_record_int(
    record: dict[str, Any],
    field: str,
    issues: list[MatrixResultIssue],
) -> int | None:
    value = record.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        issues.append(
            MatrixResultIssue(
                f"invalid_runtime_record_{field}",
                f"emitted runtime near-integrality records must include integer {field}",
            )
        )
        return None
    return value


def _runtime_record_finite_number(
    record: dict[str, Any],
    field: str,
    issues: list[MatrixResultIssue],
) -> float | None:
    value = record.get(field)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) < 0.0
    ):
        issues.append(
            MatrixResultIssue(
                f"invalid_runtime_record_{field}",
                f"emitted runtime near-integrality records must include finite non-negative {field}",
            )
        )
        return None
    return float(value)


def _runtime_record_coefficients(
    record: dict[str, Any],
    field: str,
    issues: list[MatrixResultIssue],
) -> list[float] | None:
    value = record.get(field)
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                f"invalid_runtime_record_{field}",
                f"emitted runtime near-integrality records must include non-empty {field}",
            )
        )
        return None
    coefficients: list[float] = []
    for item in value:
        if (
            isinstance(item, bool)
            or not isinstance(item, (int, float))
            or not math.isfinite(float(item))
        ):
            issues.append(
                MatrixResultIssue(
                    f"invalid_runtime_record_{field}",
                    f"emitted runtime near-integrality records must include finite numeric {field}",
                )
            )
            return None
        coefficients.append(float(item))
    return coefficients


def _validate_near_integrality_runtime_record_linkage(
    *,
    record_index: int,
    record: dict[str, Any],
    nested: dict[str, Any],
    target_id: str | None,
    candidate_id: str | None,
    seed: int | None,
    prompt_hash: str | None,
    prompt_instruction: str | None,
    raw_coefficients: list[float] | None,
    rounded_coefficients: list[float] | None,
    max_abs_rounding_error: float | None,
    exactness_certificate_ref: str | None,
    issues: list[MatrixResultIssue],
) -> None:
    if target_id is not None and nested.get("target_id") != target_id:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_near_integrality_target_mismatch",
                "runtime target_id must match nested near-integrality evidence",
            )
        )
    prompt = nested.get("prompt_instruction")
    if isinstance(prompt, dict):
        if prompt_hash is not None and prompt.get("prompt_hash") != prompt_hash:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{record_index}_near_integrality_prompt_hash_mismatch",
                    "runtime prompt_hash must match nested near-integrality evidence",
                )
            )
        if (
            prompt_instruction is not None
            and prompt.get("text") != prompt_instruction
        ):
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{record_index}_near_integrality_prompt_instruction_mismatch",
                    "runtime prompt_instruction must match nested near-integrality evidence",
                )
            )
    candidates = nested.get("candidate_records")
    if not isinstance(candidates, list):
        return
    matching = [
        candidate
        for candidate in candidates
        if isinstance(candidate, dict)
        and candidate.get("candidate_id") == candidate_id
    ]
    if not matching:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_near_integrality_missing_candidate",
                "runtime candidate_id must appear in nested near-integrality evidence",
            )
        )
        return
    candidate = matching[0]
    if seed is not None and candidate.get("seed") != seed:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_near_integrality_seed_mismatch",
                "runtime seed must match nested candidate evidence",
            )
        )
    if raw_coefficients is not None and not _coefficients_equal(
        raw_coefficients,
        candidate.get("raw_coefficients"),
    ):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_near_integrality_raw_coefficients_mismatch",
                "runtime raw_coefficients must match nested candidate evidence",
            )
        )
    if rounded_coefficients is not None and not _coefficients_equal(
        rounded_coefficients,
        candidate.get("rounded_coefficients"),
    ):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_near_integrality_rounded_coefficients_mismatch",
                "runtime rounded_coefficients must match nested candidate evidence",
            )
        )
    candidate_error = candidate.get("max_abs_rounding_error")
    if (
        max_abs_rounding_error is not None
        and (
            isinstance(candidate_error, bool)
            or not isinstance(candidate_error, (int, float))
            or not math.isclose(
                max_abs_rounding_error,
                float(candidate_error),
                rel_tol=0.0,
                abs_tol=1e-12,
            )
        )
    ):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_near_integrality_rounding_error_mismatch",
                "runtime max_abs_rounding_error must match nested candidate evidence",
            )
        )
    if (
        exactness_certificate_ref is not None
        and candidate.get("exactness_certificate_ref") != exactness_certificate_ref
    ):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{record_index}_near_integrality_certificate_ref_mismatch",
                "runtime exactness_certificate_ref must match nested candidate evidence",
            )
        )


def _coefficients_equal(left: list[float], right: object) -> bool:
    if not isinstance(right, list) or len(left) != len(right):
        return False
    for left_value, right_value in zip(left, right):
        if (
            isinstance(right_value, bool)
            or not isinstance(right_value, (int, float))
            or not math.isfinite(float(right_value))
            or not math.isclose(
                left_value,
                float(right_value),
                rel_tol=0.0,
                abs_tol=1e-12,
            )
        ):
            return False
    return True


def _validate_matrix_baseline_component_required_fields(
    value: object,
    issues: list[MatrixResultIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                "invalid_required_emission_fields",
                "required_emission_fields must be a non-empty list",
            )
        )
        return 0
    fields: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            issues.append(
                MatrixResultIssue(
                    "invalid_required_emission_field",
                    "required_emission_fields entries must be non-empty strings",
                )
            )
            continue
        if item in seen:
            issues.append(
                MatrixResultIssue(
                    "duplicate_required_emission_field",
                    "required_emission_fields entries must be unique",
                )
            )
            continue
        seen.add(item)
        fields.append(item)
    missing = sorted(set(MATRIX_BASELINE_COMPONENT_RUNTIME_REQUIRED_FIELDS) - set(fields))
    if missing:
        issues.append(
            MatrixResultIssue(
                "missing_required_emission_field",
                "required_emission_fields must include baseline component, optimizer, generation-0, lineage, result, artifact, and hash fields",
            )
        )
    return len(fields)


def _validate_matrix_baseline_component_records(
    records: list[object],
    issues: list[MatrixResultIssue],
) -> None:
    seen: set[tuple[str, str, str]] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(
                MatrixResultIssue(
                    "invalid_runtime_baseline_component_record",
                    "emitted baseline-component records must be objects",
                )
            )
            continue
        run_id = _baseline_component_text_field(record, "run_id", index, issues)
        target_id = _baseline_component_text_field(record, "target_id", index, issues)
        baseline_program_id = _baseline_component_text_field(record, "baseline_program_id", index, issues)
        _baseline_component_text_field(record, "initializer_ref", index, issues)
        _baseline_component_text_field(record, "reconstruction_loss_ref", index, issues)
        _baseline_component_text_field(record, "optimizer_ref", index, issues)
        optimizer_name = _baseline_component_text_field(record, "optimizer_name", index, issues)
        _baseline_component_text_field(record, "optimizer_version", index, issues)
        _baseline_component_text_field(record, "matrix_result_ref", index, issues)
        if target_id is not None and matrix_target_by_id(target_id) is None:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_unknown_target_id",
                    "target_id is not in the AlphaEvolve Appendix A matrix registry",
                )
            )
        if optimizer_name is not None and optimizer_name.lower() != "adam":
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_invalid_optimizer_name",
                    "Section 3.1 baseline-component records must identify the Adam optimizer",
                )
            )
        if run_id is not None and target_id is not None and baseline_program_id is not None:
            key = (run_id, target_id, baseline_program_id)
            if key in seen:
                issues.append(
                    MatrixResultIssue(
                        f"runtime_record_{index}_duplicate_baseline_component_record",
                        "run_id, target_id, and baseline_program_id must uniquely identify emitted baseline records",
                    )
                )
            else:
                seen.add(key)
        component_names = _validate_baseline_component_records(
            record.get("component_records"),
            index,
            issues,
        )
        _validate_optimizer_config(record.get("optimizer_config"), index, issues)
        _validate_mutable_component_scopes(
            record.get("mutable_component_scopes"),
            component_names,
            index,
            issues,
        )
        _validate_fixed_component_hashes(
            record.get("fixed_component_hashes"),
            component_names,
            index,
            issues,
        )
        _validate_generation0_metrics(record.get("generation0_metrics"), index, issues)
        _validate_mutation_lineage(record.get("mutation_lineage"), component_names, index, issues)
        _validate_runtime_artifact_paths(record.get("artifact_paths"), "baseline_component", index, issues)
        _validate_runtime_artifact_sha(record.get("artifact_sha256"), "baseline_component", index, issues)


def _baseline_component_text_field(
    record: dict[str, Any],
    field: str,
    index: int,
    issues: list[MatrixResultIssue],
) -> str | None:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_missing_{field}",
                f"emitted baseline-component records must include {field}",
            )
        )
        return None
    return value


def _validate_baseline_component_records(
    value: object,
    index: int,
    issues: list[MatrixResultIssue],
) -> set[str]:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_component_records",
                "component_records must be a non-empty list",
            )
        )
        return set()
    seen: set[str] = set()
    for component_index, component in enumerate(value):
        if not isinstance(component, dict):
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_invalid_component_record",
                    "component_records entries must be objects",
                )
            )
            continue
        name = component.get("component_name")
        if name not in MATRIX_BASELINE_COMPONENT_REQUIRED_NAMES:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_component_{component_index}_invalid_component_name",
                    "component_name must be initializer, reconstruction_loss, or optimizer",
                )
            )
        elif name in seen:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_component_{component_index}_duplicate_component_name",
                    "component_records must not repeat component_name values",
                )
            )
        else:
            seen.add(name)
        for field in ("component_id", "component_ref"):
            value_text = component.get(field)
            if not isinstance(value_text, str) or not value_text.strip():
                issues.append(
                    MatrixResultIssue(
                        f"runtime_record_{index}_component_{component_index}_missing_{field}",
                        f"component records must include {field}",
                    )
                )
        source_path = component.get("source_path")
        if not isinstance(source_path, str) or _safe_relative_path(source_path) is None:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_component_{component_index}_invalid_source_path",
                    "component source_path must be a safe relative path",
                )
            )
        source_sha = component.get("source_sha256")
        if not isinstance(source_sha, str) or _SHA256_RE.fullmatch(source_sha) is None:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_component_{component_index}_invalid_source_hash",
                    "component source_sha256 must be a lowercase SHA-256 hex digest",
                )
            )
        mutability = component.get("mutability")
        if mutability not in MATRIX_BASELINE_COMPONENT_MUTABILITY:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_component_{component_index}_invalid_mutability",
                    "component mutability must be fixed or mutable",
                )
            )
        config = component.get("config")
        if config is not None and not isinstance(config, dict):
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_component_{component_index}_invalid_config",
                    "component config must be an object when present",
                )
            )
    missing = sorted(MATRIX_BASELINE_COMPONENT_REQUIRED_NAMES - seen)
    if missing:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_missing_required_components",
                "component_records must include initializer, reconstruction_loss, and optimizer",
            )
        )
    return seen


def _validate_optimizer_config(
    value: object,
    index: int,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, dict) or not value:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_optimizer_config",
                "optimizer_config must be a non-empty object",
            )
        )
        return
    for key in ("learning_rate", "beta1", "beta2"):
        number = value.get(key)
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(float(number)):
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_invalid_optimizer_config_{key}",
                    f"optimizer_config {key} must be finite",
                )
            )


def _validate_mutable_component_scopes(
    value: object,
    component_names: set[str],
    index: int,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_mutable_component_scopes",
                "mutable_component_scopes must be a non-empty list",
            )
        )
        return
    seen: set[str] = set()
    for scope in value:
        if not isinstance(scope, str) or not scope.strip():
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_invalid_mutable_component_scope",
                    "mutable_component_scopes entries must be non-empty strings",
                )
            )
            continue
        if scope in seen:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_duplicate_mutable_component_scope",
                    "mutable_component_scopes entries must be unique",
                )
            )
        seen.add(scope)
        if component_names and scope not in component_names:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_unknown_mutable_component_scope",
                    "mutable_component_scopes entries must refer to component_records names",
                )
            )


def _validate_fixed_component_hashes(
    value: object,
    component_names: set[str],
    index: int,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, dict) or not value:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_fixed_component_hashes",
                "fixed_component_hashes must be a non-empty object",
            )
        )
        return
    for key, digest in value.items():
        if not isinstance(key, str) or (component_names and key not in component_names):
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_unknown_fixed_component_hash",
                    "fixed_component_hashes keys must refer to component_records names",
                )
            )
        if not isinstance(digest, str) or _SHA256_RE.fullmatch(digest) is None:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_invalid_fixed_component_hash",
                    "fixed_component_hashes values must be lowercase SHA-256 hex digests",
                )
            )


def _validate_generation0_metrics(
    value: object,
    index: int,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_generation0_metrics",
                "generation0_metrics must be an object",
            )
        )
        return
    rank = value.get("rank")
    if isinstance(rank, bool) or not isinstance(rank, int) or rank <= 0:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_generation0_rank",
                "generation0_metrics rank must be a positive integer",
            )
        )
    score = value.get("score")
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(float(score)):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_generation0_score",
                "generation0_metrics score must be finite",
            )
        )
    if not isinstance(value.get("exact"), bool):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_generation0_exact",
                "generation0_metrics exact must be boolean",
            )
        )


def _validate_mutation_lineage(
    value: object,
    component_names: set[str],
    index: int,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_mutation_lineage",
                "mutation_lineage must be a non-empty list",
            )
        )
        return
    for lineage_index, step in enumerate(value):
        if not isinstance(step, dict):
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_lineage_{lineage_index}_invalid_step",
                    "mutation_lineage entries must be objects",
                )
            )
            continue
        generation = step.get("generation")
        if isinstance(generation, bool) or not isinstance(generation, int) or generation < 0:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_lineage_{lineage_index}_invalid_generation",
                    "mutation lineage generation must be a non-negative integer",
                )
            )
        for field in ("parent_program_id", "child_program_id"):
            value_text = step.get(field)
            if not isinstance(value_text, str) or not value_text.strip():
                issues.append(
                    MatrixResultIssue(
                        f"runtime_record_{index}_lineage_{lineage_index}_missing_{field}",
                        f"mutation lineage entries must include {field}",
                    )
                )
        changed = step.get("changed_component_names")
        if not isinstance(changed, list) or not changed:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_lineage_{lineage_index}_invalid_changed_components",
                    "changed_component_names must be a non-empty list",
                )
            )
            continue
        for name in changed:
            if not isinstance(name, str) or (component_names and name not in component_names):
                issues.append(
                    MatrixResultIssue(
                        f"runtime_record_{index}_lineage_{lineage_index}_unknown_changed_component",
                        "changed_component_names must refer to component_records names",
                    )
                )


def _validate_matrix_cascade_run_runtime_required_fields(
    value: object,
    issues: list[MatrixResultIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                "invalid_required_emission_fields",
                "required_emission_fields must be a non-empty list",
            )
        )
        return 0
    fields: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            issues.append(
                MatrixResultIssue(
                    "invalid_required_emission_field",
                    "required_emission_fields entries must be non-empty strings",
                )
            )
            continue
        if item in seen:
            issues.append(
                MatrixResultIssue(
                    "duplicate_required_emission_field",
                    "required_emission_fields entries must be unique",
                )
            )
            continue
        seen.add(item)
        fields.append(item)
    missing = sorted(set(MATRIX_CASCADE_RUN_RUNTIME_REQUIRED_FIELDS) - set(fields))
    if missing:
        issues.append(
            MatrixResultIssue(
                "missing_required_emission_field",
                "required_emission_fields must include run, target, seed, cascade, stage, result, artifact, and hash fields",
            )
        )
    return len(fields)


def _validate_matrix_cascade_run_runtime_records(
    records: list[object],
    issues: list[MatrixResultIssue],
) -> None:
    seen: set[tuple[str, str, int]] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(
                MatrixResultIssue(
                    "invalid_runtime_cascade_run_record",
                    "emitted cascade-run records must be objects",
                )
            )
            continue
        run_id = _cascade_run_text_field(record, "run_id", index, issues)
        target_id = _cascade_run_text_field(record, "target_id", index, issues)
        _cascade_run_text_field(record, "cascade_id", index, issues)
        _cascade_run_text_field(record, "cascade_version", index, issues)
        _cascade_run_text_field(record, "stop_reason", index, issues)
        _cascade_run_text_field(record, "final_candidate_id", index, issues)
        _cascade_run_text_field(record, "matrix_result_ref", index, issues)
        seed = _cascade_run_int_field(record, "seed", index, issues)
        accepted_final_rank = _cascade_run_positive_int_field(
            record,
            "accepted_final_rank",
            index,
            issues,
        )
        if target_id is not None and matrix_target_by_id(target_id) is None:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_unknown_target_id",
                    "target_id is not in the AlphaEvolve Appendix A matrix registry",
                )
            )
        if run_id is not None and target_id is not None and seed is not None:
            key = (run_id, target_id, seed)
            if key in seen:
                issues.append(
                    MatrixResultIssue(
                        f"runtime_record_{index}_duplicate_cascade_run",
                        "run_id, target_id, and seed must uniquely identify emitted cascade runs",
                    )
                )
            else:
                seen.add(key)
        _validate_matrix_cascade_stage_traces(
            record.get("stage_traces"),
            index,
            issues,
            accepted_final_rank=accepted_final_rank,
            final_candidate_id=record.get("final_candidate_id"),
        )
        _validate_runtime_artifact_paths(record.get("artifact_paths"), "cascade_run", index, issues)
        _validate_runtime_artifact_sha(record.get("artifact_sha256"), "cascade_run", index, issues)

        nested = record.get("matrix_result_report")
        nested_validation = validate_matrix_result_report(nested)
        if not nested_validation.ok:
            issues.extend(
                MatrixResultIssue(
                    f"runtime_record_{index}_matrix_result_{issue.code}",
                    issue.message,
                )
                for issue in nested_validation.issues
            )
            continue
        if isinstance(nested, dict):
            if target_id is not None and nested.get("target_id") != target_id:
                issues.append(
                    MatrixResultIssue(
                        f"runtime_record_{index}_matrix_result_target_mismatch",
                        "matrix_result_report target_id must match the cascade-run target_id",
                    )
                )
            if accepted_final_rank is not None:
                _validate_matrix_cascade_seed_result_match(
                    nested,
                    seed,
                    accepted_final_rank,
                    index,
                    issues,
                )
    _validate_matrix_cascade_run_aggregation(records, issues)


def _cascade_run_text_field(
    record: dict[str, Any],
    field: str,
    index: int,
    issues: list[MatrixResultIssue],
) -> str | None:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_missing_{field}",
                f"emitted cascade-run records must include {field}",
            )
        )
        return None
    return value


def _cascade_run_int_field(
    record: dict[str, Any],
    field: str,
    index: int,
    issues: list[MatrixResultIssue],
) -> int | None:
    value = record.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_{field}",
                f"emitted cascade-run records must include integer {field}",
            )
        )
        return None
    return value


def _cascade_run_positive_int_field(
    record: dict[str, Any],
    field: str,
    index: int,
    issues: list[MatrixResultIssue],
) -> int | None:
    value = _cascade_run_int_field(record, field, index, issues)
    if value is not None and value <= 0:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_{field}",
                f"emitted cascade-run records must include positive {field}",
            )
        )
        return None
    return value


def _validate_matrix_cascade_stage_traces(
    value: object,
    index: int,
    issues: list[MatrixResultIssue],
    *,
    accepted_final_rank: int | None,
    final_candidate_id: object,
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_stage_traces",
                "stage_traces must be a non-empty list",
            )
        )
        return
    seen_labels: set[str] = set()
    last_stage: dict[str, Any] | None = None
    for stage_index, stage in enumerate(value):
        if not isinstance(stage, dict):
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_invalid_stage_trace",
                    "stage_traces entries must be objects",
                )
            )
            continue
        last_stage = stage
        label = stage.get("stage_label")
        if not isinstance(label, str) or not label.strip():
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_stage_{stage_index}_missing_stage_label",
                    "stage trace must include stage_label",
                )
            )
        elif label in seen_labels:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_stage_{stage_index}_duplicate_stage_label",
                    "stage_label values must be unique within a cascade run",
                )
            )
        else:
            seen_labels.add(label)
        for field in ("candidate_id", "stop_reason"):
            value_text = stage.get(field)
            if not isinstance(value_text, str) or not value_text.strip():
                issues.append(
                    MatrixResultIssue(
                        f"runtime_record_{index}_stage_{stage_index}_missing_{field}",
                        f"stage trace must include {field}",
                    )
                )
        threshold = stage.get("threshold")
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not math.isfinite(float(threshold)):
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_stage_{stage_index}_invalid_threshold",
                    "stage threshold must be a finite number",
                )
            )
        rank = stage.get("rank")
        if isinstance(rank, bool) or not isinstance(rank, int) or rank <= 0:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_stage_{stage_index}_invalid_rank",
                    "stage rank must be a positive integer",
                )
            )
        if not isinstance(stage.get("exact"), bool):
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_stage_{stage_index}_invalid_exact",
                    "stage exact flag must be boolean",
                )
            )
    if last_stage is None:
        return
    if (
        accepted_final_rank is not None
        and isinstance(last_stage.get("rank"), int)
        and not isinstance(last_stage.get("rank"), bool)
        and last_stage.get("rank") != accepted_final_rank
    ):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_final_stage_rank_mismatch",
                "final stage rank must match accepted_final_rank",
            )
        )
    if (
        isinstance(final_candidate_id, str)
        and final_candidate_id.strip()
        and isinstance(last_stage.get("candidate_id"), str)
        and last_stage.get("candidate_id") != final_candidate_id
    ):
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_final_stage_candidate_mismatch",
                "final stage candidate_id must match final_candidate_id",
            )
        )


def _validate_matrix_cascade_seed_result_match(
    report: dict[str, Any],
    seed: int | None,
    accepted_final_rank: int,
    index: int,
    issues: list[MatrixResultIssue],
) -> None:
    if seed is None:
        return
    seed_results = report.get("seed_results")
    if not isinstance(seed_results, list):
        return
    for seed_result in seed_results:
        if not isinstance(seed_result, dict) or seed_result.get("seed") != seed:
            continue
        if seed_result.get("rank") != accepted_final_rank:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_matrix_result_seed_rank_mismatch",
                    "accepted_final_rank must match the matching seed result rank",
                )
            )
        return
    issues.append(
        MatrixResultIssue(
            f"runtime_record_{index}_matrix_result_missing_seed",
            "matrix_result_report seed_results must include the cascade-run seed",
        )
    )


def _validate_matrix_cascade_run_aggregation(
    records: list[object],
    issues: list[MatrixResultIssue],
) -> None:
    groups: dict[tuple[str, str, str], list[tuple[int, dict[str, Any]]]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        run_id = record.get("run_id")
        target_id = record.get("target_id")
        matrix_result_ref = record.get("matrix_result_ref")
        if not (
            isinstance(run_id, str)
            and run_id.strip()
            and isinstance(target_id, str)
            and target_id.strip()
            and isinstance(matrix_result_ref, str)
            and matrix_result_ref.strip()
        ):
            continue
        groups.setdefault((run_id, target_id, matrix_result_ref), []).append(
            (index, record)
        )
    for group_index, records_for_group in enumerate(groups.values()):
        reference_report = records_for_group[0][1].get("matrix_result_report")
        reference_validation = validate_matrix_result_report(reference_report)
        if not reference_validation.ok or not isinstance(reference_report, dict):
            continue
        reference_report_sha = _stable_json_sha256(reference_report)
        seed_results = reference_report.get("seed_results")
        if not isinstance(seed_results, list) or not seed_results:
            continue
        expected_seed_to_rank: dict[int, int] = {}
        for seed_result in seed_results:
            if not isinstance(seed_result, dict):
                continue
            seed = seed_result.get("seed")
            rank = seed_result.get("rank")
            if (
                isinstance(seed, int)
                and not isinstance(seed, bool)
                and isinstance(rank, int)
                and not isinstance(rank, bool)
                and rank > 0
            ):
                expected_seed_to_rank[seed] = rank
        observed_seed_to_rank: dict[int, int] = {}
        for record_index, record in records_for_group:
            nested = record.get("matrix_result_report")
            if (
                isinstance(nested, dict)
                and _stable_json_sha256(nested) != reference_report_sha
            ):
                issues.append(
                    MatrixResultIssue(
                        f"runtime_group_{group_index}_matrix_result_report_mismatch",
                        "all emitted records for one run/target/result ref must embed the same matrix_result_report",
                    )
                )
            seed = record.get("seed")
            rank = record.get("accepted_final_rank")
            if (
                isinstance(seed, int)
                and not isinstance(seed, bool)
                and isinstance(rank, int)
                and not isinstance(rank, bool)
                and rank > 0
            ):
                observed_seed_to_rank[seed] = rank
            else:
                issues.append(
                    MatrixResultIssue(
                        f"runtime_record_{record_index}_invalid_aggregation_fields",
                        "emitted records need integer seed and positive accepted_final_rank for aggregation checks",
                    )
                )
        if set(observed_seed_to_rank) != set(expected_seed_to_rank):
            issues.append(
                MatrixResultIssue(
                    f"runtime_group_{group_index}_matrix_result_seed_coverage_mismatch",
                    "emitted cascade records must cover exactly the matrix_result_report seed_results",
                )
            )
            continue
        if not observed_seed_to_rank:
            continue
        computed_best_rank = min(observed_seed_to_rank.values())
        computed_hit_count = sum(
            1 for rank in observed_seed_to_rank.values() if rank == computed_best_rank
        )
        computed_hit_fraction = computed_hit_count / len(observed_seed_to_rank)
        if reference_report.get("best_rank") != computed_best_rank:
            issues.append(
                MatrixResultIssue(
                    f"runtime_group_{group_index}_matrix_result_best_rank_mismatch",
                    "matrix_result_report best_rank must be computed from emitted cascade records",
                )
            )
        if reference_report.get("hit_count") != computed_hit_count:
            issues.append(
                MatrixResultIssue(
                    f"runtime_group_{group_index}_matrix_result_hit_count_mismatch",
                    "matrix_result_report hit_count must be computed from emitted cascade records",
                )
            )
        hit_fraction = reference_report.get("hit_fraction")
        if not (
            isinstance(hit_fraction, (int, float))
            and not isinstance(hit_fraction, bool)
            and math.isclose(
                float(hit_fraction),
                computed_hit_fraction,
                rel_tol=0.0,
                abs_tol=1e-12,
            )
        ):
            issues.append(
                MatrixResultIssue(
                    f"runtime_group_{group_index}_matrix_result_hit_fraction_mismatch",
                    "matrix_result_report hit_fraction must be computed from emitted cascade records",
                )
            )


def _lookup_seed_mapping(
    mapping: dict[int | str, Any] | None,
    seed: int,
    *,
    field_name: str,
) -> Any:
    if not isinstance(mapping, dict):
        raise ValueError(f"{field_name} must be a mapping")
    if seed in mapping:
        return mapping[seed]
    seed_key = str(seed)
    if seed_key in mapping:
        return mapping[seed_key]
    raise ValueError(f"{field_name} missing seed {seed}")


def _stable_json_sha256(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _validate_runtime_artifact_paths(
    value: object,
    label: str,
    index: int,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_{label}_artifact_paths",
                "artifact_paths must be a non-empty list",
            )
        )
        return
    seen: set[str] = set()
    for path in value:
        if not isinstance(path, str) or _safe_relative_path(path) is None:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_invalid_{label}_artifact_path",
                    "artifact_paths entries must be safe relative paths",
                )
            )
            continue
        if path in seen:
            issues.append(
                MatrixResultIssue(
                    f"runtime_record_{index}_duplicate_{label}_artifact_path",
                    "artifact_paths entries must be unique",
                )
            )
        else:
            seen.add(path)


def _validate_runtime_artifact_sha(
    value: object,
    label: str,
    index: int,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        issues.append(
            MatrixResultIssue(
                f"runtime_record_{index}_invalid_{label}_artifact_hash",
                "artifact_sha256 must be a lowercase SHA-256 hex digest",
            )
        )


def _validate_coefficient_pairs(
    raw_coefficients: list[object],
    rounded_coefficients: list[object],
    rounding_domain: str | None,
    issues: list[MatrixResultIssue],
) -> float | None:
    if not raw_coefficients or not rounded_coefficients or len(raw_coefficients) != len(rounded_coefficients):
        return None
    max_error = 0.0
    for raw, rounded in zip(raw_coefficients, rounded_coefficients):
        if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not math.isfinite(float(raw)):
            issues.append(MatrixResultIssue("invalid_raw_coefficient", "raw coefficients must be finite numbers"))
            return None
        if isinstance(rounded, bool) or not isinstance(rounded, (int, float)) or not math.isfinite(float(rounded)):
            issues.append(MatrixResultIssue("invalid_rounded_coefficient", "rounded coefficients must be finite numbers"))
            return None
        rounded_float = float(rounded)
        if rounding_domain == "integer" and not math.isclose(rounded_float, round(rounded_float), rel_tol=0.0, abs_tol=1e-12):
            issues.append(MatrixResultIssue("rounded_coefficient_not_integer", "rounded coefficients must be integers"))
        if rounding_domain == "half_integer" and not math.isclose(rounded_float * 2, round(rounded_float * 2), rel_tol=0.0, abs_tol=1e-12):
            issues.append(MatrixResultIssue("rounded_coefficient_not_half_integer", "rounded coefficients must be integer or half-integer values"))
        max_error = max(max_error, abs(float(raw) - rounded_float))
    return max_error


def _validate_bundle_report_file(
    data: dict[str, Any],
    root: Path,
    issues: list[MatrixResultIssue],
) -> None:
    report_path = _safe_relative_path(data.get("report_path"))
    if report_path is None:
        issues.append(
            MatrixResultIssue(
                "invalid_report_path",
                "report_path must be a safe relative path",
            )
        )
        return
    try:
        resolved_root = root.resolve()
        resolved_path = (resolved_root / report_path).resolve(strict=False)
    except OSError:
        issues.append(
            MatrixResultIssue(
                "invalid_report_path",
                "report_path must be resolvable under artifact_root",
            )
        )
        return
    if not resolved_path.is_relative_to(resolved_root):
        issues.append(
            MatrixResultIssue(
                "report_path_outside_root",
                "report_path must stay under artifact_root",
            )
        )
        return
    if not resolved_path.exists():
        issues.append(
            MatrixResultIssue(
                "missing_report_file",
                "report_path must point to an existing report file",
            )
        )
        return
    if not resolved_path.is_file():
        issues.append(
            MatrixResultIssue(
                "report_path_not_file",
                "report_path must point to a file",
            )
        )
        return
    try:
        raw = resolved_path.read_bytes()
    except OSError as exc:
        issues.append(
            MatrixResultIssue(
                "report_read_error",
                f"failed to read report_path: {exc}",
            )
        )
        return

    expected_sha = data.get("report_sha256")
    actual_sha = hashlib.sha256(raw).hexdigest()
    if not isinstance(expected_sha, str) or _SHA256_RE.fullmatch(expected_sha) is None:
        issues.append(
            MatrixResultIssue(
                "invalid_report_hash",
                "report_sha256 must be a lowercase SHA-256 hex digest",
            )
        )
    elif actual_sha != expected_sha:
        issues.append(
            MatrixResultIssue(
                "report_hash_mismatch",
                "report_sha256 must match the report_path file",
            )
        )

    expected_bytes = data.get("report_bytes")
    actual_bytes = len(raw)
    if (
        isinstance(expected_bytes, bool)
        or not isinstance(expected_bytes, int)
        or expected_bytes <= 0
    ):
        issues.append(
            MatrixResultIssue(
                "invalid_report_bytes",
                "report_bytes must be a positive integer",
            )
        )
    elif actual_bytes != expected_bytes:
        issues.append(
            MatrixResultIssue(
                "report_bytes_mismatch",
                "report_bytes must match the report_path file",
            )
        )

    try:
        file_report = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        issues.append(
            MatrixResultIssue(
                "invalid_report_file_json",
                "report_path must contain a JSON object matching the embedded report",
            )
        )
        return
    if file_report != data.get("report"):
        issues.append(
            MatrixResultIssue(
                "report_file_mismatch",
                "report_path JSON must match the embedded report",
            )
        )


def _validate_bundle_inventory_file(
    data: dict[str, Any],
    root: Path,
    issues: list[MatrixResultIssue],
) -> None:
    if not any(field in data for field in ("inventory_path", "inventory_sha256", "inventory_bytes")):
        return
    inventory_path = _safe_relative_path(data.get("inventory_path"))
    if inventory_path is None:
        issues.append(
            MatrixResultIssue(
                "invalid_inventory_path",
                "inventory_path must be a safe relative path",
            )
        )
        return
    try:
        resolved_root = root.resolve()
        resolved_path = (resolved_root / inventory_path).resolve(strict=False)
    except OSError:
        issues.append(
            MatrixResultIssue(
                "invalid_inventory_path",
                "inventory_path must be resolvable under artifact_root",
            )
        )
        return
    if not resolved_path.is_relative_to(resolved_root):
        issues.append(
            MatrixResultIssue(
                "inventory_path_outside_root",
                "inventory_path must stay under artifact_root",
            )
        )
        return
    if not resolved_path.exists():
        issues.append(
            MatrixResultIssue(
                "missing_inventory_file",
                "inventory_path must point to an existing inventory file",
            )
        )
        return
    if not resolved_path.is_file():
        issues.append(
            MatrixResultIssue(
                "inventory_path_not_file",
                "inventory_path must point to a file",
            )
        )
        return
    try:
        raw = resolved_path.read_bytes()
    except OSError as exc:
        issues.append(
            MatrixResultIssue(
                "inventory_read_error",
                f"failed to read inventory_path: {exc}",
            )
        )
        return

    expected_sha = data.get("inventory_sha256")
    actual_sha = hashlib.sha256(raw).hexdigest()
    if not isinstance(expected_sha, str) or _SHA256_RE.fullmatch(expected_sha) is None:
        issues.append(
            MatrixResultIssue(
                "invalid_inventory_hash",
                "inventory_sha256 must be a lowercase SHA-256 hex digest",
            )
        )
    elif actual_sha != expected_sha:
        issues.append(
            MatrixResultIssue(
                "inventory_hash_mismatch",
                "inventory_sha256 must match the inventory_path file",
            )
        )

    expected_bytes = data.get("inventory_bytes")
    actual_bytes = len(raw)
    if (
        isinstance(expected_bytes, bool)
        or not isinstance(expected_bytes, int)
        or expected_bytes <= 0
    ):
        issues.append(
            MatrixResultIssue(
                "invalid_inventory_bytes",
                "inventory_bytes must be a positive integer",
            )
        )
    elif actual_bytes != expected_bytes:
        issues.append(
            MatrixResultIssue(
                "inventory_bytes_mismatch",
                "inventory_bytes must match the inventory_path file",
            )
        )

    try:
        file_inventory = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        issues.append(
            MatrixResultIssue(
                "invalid_inventory_file_json",
                "inventory_path must contain a JSON object matching the embedded inventory",
            )
        )
        return
    if file_inventory != data.get("inventory"):
        issues.append(
            MatrixResultIssue(
                "inventory_file_mismatch",
                "inventory_path JSON must match the embedded inventory",
            )
        )


def _validate_strassen_regeneration_parity(
    root: Path,
    issues: list[MatrixResultIssue],
) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        generated_root = Path(tmp) / root.name
        write_strassen_2x2_publication_bundle(
            generated_root,
            seeds=STRASSEN_2X2_PUBLICATION_BUNDLE_SEEDS,
        )
        for relative in STRASSEN_2X2_PUBLICATION_BUNDLE_FILES:
            pinned_path = root / relative
            generated_path = generated_root / relative
            try:
                pinned_raw = pinned_path.read_bytes()
            except OSError:
                issues.append(
                    MatrixResultIssue(
                        "missing_strassen_pinned_artifact",
                        f"pinned Strassen artifact is missing: {relative}",
                    )
                )
                continue
            try:
                generated_raw = generated_path.read_bytes()
            except OSError:
                issues.append(
                    MatrixResultIssue(
                        "missing_strassen_generated_artifact",
                        f"generated Strassen artifact is missing: {relative}",
                    )
                )
                continue
            if hashlib.sha256(pinned_raw).hexdigest() != hashlib.sha256(generated_raw).hexdigest():
                issues.append(
                    MatrixResultIssue(
                        "strassen_regeneration_hash_mismatch",
                        f"pinned Strassen artifact does not match regenerated output: {relative}",
                    )
                )


def _validate_matrix_publication_inventory(
    inventory: object,
    bundle: dict[str, Any],
    issues: list[MatrixResultIssue],
) -> bool:
    if not isinstance(inventory, dict):
        return False
    issue_count = len(issues)
    if inventory.get("schema") != MATRIX_ARTIFACT_INVENTORY_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_inventory_schema",
                "inventory schema must be a matrix artifact inventory",
            )
        )
    if inventory.get("ok") is not True:
        issues.append(
            MatrixResultIssue(
                "inventory_not_ok",
                "inventory must have verified all referenced artifacts",
            )
        )
    if (
        bundle.get("target_suite") is not None
        and inventory.get("target_suite") != bundle.get("target_suite")
    ):
        issues.append(
            MatrixResultIssue(
                "inventory_target_suite_mismatch",
                "inventory target_suite must match bundle target_suite",
            )
        )
    report = bundle.get("report")
    if isinstance(report, dict) and inventory.get("report_schema") != report.get("schema"):
        issues.append(
            MatrixResultIssue(
                "inventory_report_schema_mismatch",
                "inventory report_schema must match embedded report schema",
            )
        )
    artifacts = inventory.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        issues.append(
            MatrixResultIssue(
                "invalid_inventory_artifacts",
                "inventory artifacts must be a non-empty list",
            )
        )
        artifacts = []
    records_payload = json.dumps(artifacts, sort_keys=True, separators=(",", ":"))
    records_sha = inventory.get("records_sha256")
    if not isinstance(records_sha, str) or _SHA256_RE.fullmatch(records_sha) is None:
        issues.append(
            MatrixResultIssue(
                "invalid_inventory_records_hash",
                "inventory records_sha256 must be a lowercase SHA-256 hex digest",
            )
        )
    elif hashlib.sha256(records_payload.encode("utf-8")).hexdigest() != records_sha:
        issues.append(
            MatrixResultIssue(
                "inventory_records_hash_mismatch",
                "inventory records_sha256 must match the artifact records",
            )
        )
    expected_counts = {
        "artifact_count": len(artifacts),
        "verified_count": sum(
            1
            for record in artifacts
            if isinstance(record, dict) and record.get("status") == "verified"
        ),
        "missing_count": sum(
            1
            for record in artifacts
            if isinstance(record, dict) and record.get("status") == "missing_file"
        ),
        "mismatch_count": sum(
            1
            for record in artifacts
            if isinstance(record, dict)
            and record.get("status") in {"hash_mismatch", "bytes_mismatch"}
        ),
        "invalid_count": sum(
            1
            for record in artifacts
            if isinstance(record, dict)
            and record.get("status")
            in {"invalid_artifact", "unsafe_path", "read_error"}
        ),
    }
    for field, expected in expected_counts.items():
        value = inventory.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            issues.append(
                MatrixResultIssue(
                    f"invalid_inventory_{field}",
                    f"inventory {field} must be a non-negative integer",
                )
            )
        elif value != expected:
            issues.append(
                MatrixResultIssue(
                    f"inventory_{field}_mismatch",
                    f"inventory {field} must match the artifact records",
                )
            )
    if inventory.get("verified_count") != inventory.get("artifact_count"):
        issues.append(
            MatrixResultIssue(
                "inventory_verified_count_mismatch",
                "inventory verified_count must equal artifact_count",
            )
        )
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        rights = artifact.get("source_rights")
        if not isinstance(rights, dict):
            issues.append(
                MatrixResultIssue(
                    "inventory_artifact_source_rights_missing",
                    "inventory artifact records must include source_rights",
                )
            )
            continue
        rights_report = validate_alphaevolve_companion_artifact_rights(rights)
        issues.extend(
            MatrixResultIssue(
                f"inventory_artifact_source_rights_{issue.code}",
                issue.message,
            )
            for issue in rights_report.issues
        )
    for field in ("missing_count", "mismatch_count", "invalid_count"):
        if inventory.get(field) != 0:
            issues.append(
                MatrixResultIssue(
                    f"inventory_{field}_nonzero",
                    f"inventory {field} must be zero for a publication bundle",
                )
            )
    if inventory.get("issues"):
        issues.append(
            MatrixResultIssue(
                "inventory_has_issues",
                "inventory issues must be empty for a publication bundle",
            )
        )
    return len(issues) == issue_count


def _validate_matrix_suite_publication_required_fields(
    value: object,
    issues: list[MatrixResultIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                "invalid_required_artifact_fields",
                "required_artifact_fields must be a non-empty list",
            )
        )
        return 0
    seen: set[str] = set()
    for field in value:
        if not isinstance(field, str) or not field.strip():
            issues.append(
                MatrixResultIssue(
                    "invalid_required_artifact_field",
                    "required artifact field names must be non-empty strings",
                )
            )
            continue
        if field in seen:
            issues.append(
                MatrixResultIssue(
                    "duplicate_required_artifact_field",
                    "required_artifact_fields must be unique",
                )
            )
        seen.add(field)
    if set(MATRIX_SUITE_PUBLICATION_ARTIFACT_REQUIRED_FIELDS) - seen:
        issues.append(
            MatrixResultIssue(
                "missing_required_artifact_field",
                "required_artifact_fields must include all suite publication artifact fields",
            )
        )
    return len(value)


def _validate_matrix_suite_publication_artifacts(
    value: list[object],
    issues: list[MatrixResultIssue],
) -> None:
    registry_targets = {
        target["id"]: target
        for target in matrix_target_records()
        if isinstance(target.get("id"), str)
    }
    seen: set[str] = set()
    for artifact in value:
        if not isinstance(artifact, dict):
            issues.append(
                MatrixResultIssue(
                    "invalid_suite_publication_artifact",
                    "suite publication artifact records must be objects",
                )
            )
            continue
        target_id = artifact.get("target_id")
        safe_id = target_id if isinstance(target_id, str) else None
        expected = registry_targets.get(safe_id or "")
        if expected is None:
            issues.append(
                MatrixResultIssue(
                    "unknown_suite_publication_target_id",
                    "target_id must belong to the Appendix A matrix registry",
                )
            )
            continue
        if safe_id in seen:
            issues.append(
                MatrixResultIssue(
                    "duplicate_suite_publication_target_id",
                    "suite publication target_id values must be unique",
                )
            )
        seen.add(safe_id)
        if artifact.get("dimensions") != expected.get("dimensions"):
            issues.append(
                MatrixResultIssue(
                    "suite_publication_dimensions_mismatch",
                    "artifact dimensions must match the Appendix A registry target",
                )
            )
        if artifact.get("coefficient_domain") not in PUBLICATION_COEFFICIENT_DOMAINS:
            issues.append(
                MatrixResultIssue(
                    "invalid_suite_publication_coefficient_domain",
                    "suite publication artifacts require integer or half_integer coefficients",
                )
            )
        for field in (
            "target_tensor_ref",
            "algorithm_ref",
            "coefficient_data_ref",
            "exactness_certificate_ref",
            "notebook_ref",
            "per_seed_report_ref",
            "publication_bundle_ref",
        ):
            _validate_safe_ref_field(artifact.get(field), f"invalid_{field}", issues)
        for field in (
            "target_tensor_sha256",
            "algorithm_sha256",
            "coefficient_data_sha256",
            "exactness_certificate_sha256",
            "notebook_sha256",
            "per_seed_report_sha256",
            "artifact_sha256",
        ):
            _validate_hash_field(artifact.get(field), f"invalid_{field}", issues)
        _validate_suite_artifact_paths(artifact.get("artifact_paths"), issues)
        _validate_suite_matrix_result_report(artifact.get("matrix_result_report"), safe_id, issues)
        _validate_suite_artifact_inventory(artifact.get("artifact_inventory"), safe_id, issues)
    for target_id in sorted(set(registry_targets) - seen):
        issues.append(
            MatrixResultIssue(
                "missing_suite_publication_target",
                f"suite publication artifacts must include target {target_id}",
            )
        )


def _validate_safe_ref_field(
    value: object,
    code: str,
    issues: list[MatrixResultIssue],
) -> None:
    if _safe_relative_path(value) is None:
        issues.append(
            MatrixResultIssue(
                code,
                "artifact refs must be safe relative paths",
            )
        )


def _validate_hash_field(
    value: object,
    code: str,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        issues.append(
            MatrixResultIssue(
                code,
                "artifact hashes must be lowercase SHA-256 hex digests",
            )
        )


def _validate_suite_artifact_paths(
    value: object,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(
            MatrixResultIssue(
                "invalid_artifact_paths",
                "artifact_paths must be a non-empty list",
            )
        )
        return
    seen: set[str] = set()
    for path in value:
        if _safe_relative_path(path) is None:
            issues.append(
                MatrixResultIssue(
                    "invalid_artifact_path",
                    "artifact_paths entries must be safe relative paths",
                )
            )
            continue
        assert isinstance(path, str)
        if path in seen:
            issues.append(
                MatrixResultIssue(
                    "duplicate_artifact_path",
                    "artifact_paths entries must be unique",
                )
            )
        seen.add(path)


def _validate_suite_matrix_result_report(
    report: object,
    target_id: str | None,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(report, dict):
        issues.append(
            MatrixResultIssue(
                "invalid_matrix_result_report",
                "matrix_result_report must be an embedded report object",
            )
        )
        return
    validation = validate_matrix_result_report(report)
    issues.extend(
        MatrixResultIssue(
            f"invalid_nested_matrix_result_{issue.code}",
            issue.message,
        )
        for issue in validation.issues
    )
    if target_id is not None and report.get("target_id") != target_id:
        issues.append(
            MatrixResultIssue(
                "matrix_result_target_mismatch",
                "matrix_result_report target_id must match the suite artifact target",
            )
        )
    if validation.ok and not validation.alphaevolve_comparable:
        issues.append(
            MatrixResultIssue(
                "matrix_result_not_alphaevolve_comparable",
                "suite publication artifacts require AlphaEvolve-comparable matrix result reports",
            )
        )


def _validate_suite_artifact_inventory(
    inventory: object,
    target_id: str | None,
    issues: list[MatrixResultIssue],
) -> None:
    if not isinstance(inventory, dict):
        issues.append(
            MatrixResultIssue(
                "invalid_artifact_inventory",
                "artifact_inventory must be an embedded inventory object",
            )
        )
        return
    if inventory.get("schema") != MATRIX_ARTIFACT_INVENTORY_SCHEMA:
        issues.append(
            MatrixResultIssue(
                "invalid_nested_inventory_schema",
                "artifact_inventory schema must be matrix_result_artifact_inventory.v1",
            )
        )
    if inventory.get("target_suite") != APPENDIX_A_TARGET_SUITE:
        issues.append(
            MatrixResultIssue(
                "invalid_nested_inventory_target_suite",
                "artifact_inventory target_suite must be alphaevolve_appendix_a",
            )
        )
    if target_id is not None and inventory.get("target_id") != target_id:
        issues.append(
            MatrixResultIssue(
                "inventory_target_mismatch",
                "artifact_inventory target_id must match the suite artifact target",
            )
        )
    if inventory.get("ok") is not True:
        issues.append(
            MatrixResultIssue(
                "inventory_not_ok",
                "artifact_inventory must verify all referenced files",
            )
        )
    artifact_count = inventory.get("artifact_count")
    verified_count = inventory.get("verified_count")
    if (
        isinstance(artifact_count, bool)
        or isinstance(verified_count, bool)
        or not isinstance(artifact_count, int)
        or not isinstance(verified_count, int)
        or artifact_count <= 0
        or verified_count != artifact_count
    ):
        issues.append(
            MatrixResultIssue(
                "invalid_inventory_counts",
                "artifact_inventory must have positive artifact_count with all artifacts verified",
            )
        )


def _safe_relative_path(value: object) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    if path.is_absolute() or value.startswith(("/", "\\")) or ".." in path.parts:
        return None
    return path


def _matrix_artifact_inventory_record(artifact: object, root: Path) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        return {
            "kind": "unknown",
            "path": "",
            "status": "invalid_artifact",
            "issues": ["invalid_artifact"],
        }
    kind = artifact.get("kind")
    path = artifact.get("path")
    expected_sha = artifact.get("sha256")
    expected_bytes = artifact.get("bytes")
    rights = artifact.get("source_rights")
    record: dict[str, Any] = {
        "kind": kind if isinstance(kind, str) else "unknown",
        "path": path if isinstance(path, str) else "",
        "expected_sha256": expected_sha if isinstance(expected_sha, str) else "",
        "expected_bytes": expected_bytes if isinstance(expected_bytes, int) and not isinstance(expected_bytes, bool) else None,
        "source_rights": rights if isinstance(rights, dict) else None,
        "status": "verified",
        "issues": [],
    }
    if not isinstance(rights, dict):
        record["status"] = "invalid_artifact"
        record["issues"].append("source_rights_missing")
    else:
        rights_report = validate_alphaevolve_companion_artifact_rights(rights)
        if not rights_report.ok:
            record["status"] = "invalid_artifact"
            record["issues"].extend(
                f"source_rights_{issue.code}"
                for issue in rights_report.issues
            )
    path_obj = Path(path) if isinstance(path, str) else None
    if (
        path_obj is None
        or not path
        or path_obj.is_absolute()
        or path.startswith(("/", "\\"))
        or ".." in path_obj.parts
    ):
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_artifact_path")
        return record
    try:
        resolved_root = root.resolve()
        resolved_path = (resolved_root / path_obj).resolve(strict=False)
    except OSError:
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_artifact_path")
        return record
    if not resolved_path.is_relative_to(resolved_root):
        record["status"] = "unsafe_path"
        record["issues"].append("artifact_path_outside_root")
        return record
    if not resolved_path.exists():
        record["status"] = "missing_file"
        record["issues"].append("missing_artifact_file")
        return record
    if not resolved_path.is_file():
        record["status"] = "unsafe_path"
        record["issues"].append("artifact_path_not_file")
        return record
    try:
        raw = resolved_path.read_bytes()
    except OSError:
        record["status"] = "read_error"
        record["issues"].append("artifact_read_error")
        return record
    actual_sha = hashlib.sha256(raw).hexdigest()
    actual_bytes = len(raw)
    record["actual_sha256"] = actual_sha
    record["actual_bytes"] = actual_bytes
    if not isinstance(expected_sha, str) or _SHA256_RE.fullmatch(expected_sha) is None:
        record["status"] = "hash_mismatch"
        record["issues"].append("invalid_expected_artifact_hash")
    elif actual_sha != expected_sha:
        record["status"] = "hash_mismatch"
        record["issues"].append("artifact_hash_mismatch")
    if isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("invalid_expected_artifact_bytes")
    elif actual_bytes != expected_bytes:
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("artifact_bytes_mismatch")
    return record


def _text_field(data: dict[str, Any], field: str, issues: list[MatrixResultIssue]) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or _ID_RE.fullmatch(value) is None:
        issues.append(MatrixResultIssue(f"invalid_{field}", f"{field} must be a stable identifier"))
        return None
    return value


def _positive_int(value: object, field: str, issues: list[MatrixResultIssue]) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        issues.append(MatrixResultIssue(f"invalid_{field}", f"{field} must be a positive integer"))
        return None
    return value


def _nonnegative_int(value: object, field: str, issues: list[MatrixResultIssue]) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        issues.append(MatrixResultIssue(f"invalid_{field}", f"{field} must be a non-negative integer"))
        return None
    return value


def _finite_fraction(value: object, field: str, issues: list[MatrixResultIssue]) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        issues.append(MatrixResultIssue(f"invalid_{field}", f"{field} must be a finite number in [0, 1]"))
        return None
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0.0 or numeric > 1.0:
        issues.append(MatrixResultIssue(f"invalid_{field}", f"{field} must be a finite number in [0, 1]"))
        return None
    return numeric


def _validate_exactness(value: object, issues: list[MatrixResultIssue]) -> str | None:
    if not isinstance(value, dict):
        issues.append(MatrixResultIssue("invalid_exactness_certificate", "exactness_certificate must be an object"))
        return None
    status = value.get("status")
    if value.get("status") not in EXACTNESS_STATUSES:
        issues.append(MatrixResultIssue("invalid_exactness_status", "unsupported exactness status"))
        status = None
    if not isinstance(value.get("method"), str) or not value["method"].strip():
        issues.append(MatrixResultIssue("invalid_exactness_method", "exactness method is required"))
    if value.get("status") == "verified" and not isinstance(value.get("certificate_sha256"), str):
        issues.append(MatrixResultIssue("missing_certificate_hash", "verified exactness requires certificate_sha256"))
    elif isinstance(value.get("certificate_sha256"), str) and _SHA256_RE.fullmatch(value["certificate_sha256"]) is None:
        issues.append(MatrixResultIssue("invalid_certificate_hash", "certificate_sha256 must be a lowercase SHA-256 hex digest"))
    return status if isinstance(status, str) else None


def _validate_seed_results(
    value: object,
    seed_count: int | None,
    best_rank: int | None,
    hit_count: int | None,
    issues: list[MatrixResultIssue],
) -> bool | None:
    if not isinstance(value, list) or not value:
        issues.append(MatrixResultIssue("invalid_seed_results", "seed_results must be a non-empty list"))
        return None
    if seed_count is not None and len(value) != seed_count:
        issues.append(MatrixResultIssue("invalid_seed_result_count", "seed_results length must equal seed_count"))
    seen: set[int] = set()
    achieved = 0
    ranks: list[int] = []
    all_exact = True
    for record in value:
        if not isinstance(record, dict):
            issues.append(MatrixResultIssue("invalid_seed_result", "seed result must be an object"))
            all_exact = False
            continue
        seed = record.get("seed")
        if isinstance(seed, bool) or not isinstance(seed, int):
            issues.append(MatrixResultIssue("invalid_seed", "seed must be an integer"))
        elif seed in seen:
            issues.append(MatrixResultIssue("duplicate_seed", "seed_results must not repeat seeds"))
        else:
            seen.add(seed)
        rank = record.get("rank")
        if isinstance(rank, bool) or not isinstance(rank, int) or rank <= 0:
            issues.append(MatrixResultIssue("invalid_seed_rank", "seed rank must be a positive integer"))
            rank = None
        else:
            ranks.append(rank)
        achieved_best = record.get("achieved_best_rank")
        if not isinstance(achieved_best, bool):
            issues.append(MatrixResultIssue("invalid_achieved_best_rank", "achieved_best_rank must be boolean"))
        elif achieved_best:
            achieved += 1
            if best_rank is not None and rank != best_rank:
                issues.append(MatrixResultIssue("inconsistent_seed_rank", "best-rank seed must use best_rank"))
        elif best_rank is not None and rank == best_rank:
            issues.append(MatrixResultIssue("inconsistent_seed_hit_flag", "seed with best_rank must set achieved_best_rank"))
        if not isinstance(record.get("exact"), bool):
            issues.append(MatrixResultIssue("invalid_seed_exact", "seed exact must be boolean"))
            all_exact = False
        elif record.get("exact") is False:
            all_exact = False
    if best_rank is not None and ranks and min(ranks) != best_rank:
        issues.append(MatrixResultIssue("inconsistent_best_rank", "best_rank must equal the minimum per-seed rank"))
    if hit_count is not None and achieved != hit_count:
        issues.append(MatrixResultIssue("invalid_seed_hit_count", "achieved_best_rank count must equal hit_count"))
    return all_exact


def _validate_artifacts(value: object, issues: list[MatrixResultIssue]) -> set[str]:
    kinds: set[str] = set()
    if not isinstance(value, list) or not value:
        issues.append(MatrixResultIssue("invalid_artifacts", "artifacts must be a non-empty list"))
        return kinds
    for artifact in value:
        if not isinstance(artifact, dict):
            issues.append(MatrixResultIssue("invalid_artifact", "artifact must be an object"))
            continue
        if artifact.get("kind") not in ARTIFACT_KINDS:
            issues.append(MatrixResultIssue("invalid_artifact_kind", "unsupported artifact kind"))
        else:
            kinds.add(artifact["kind"])
        path = artifact.get("path")
        path_obj = Path(path) if isinstance(path, str) else None
        if (
            path_obj is None
            or not path
            or path_obj.is_absolute()
            or path.startswith(("/", "\\"))
            or ".." in path_obj.parts
        ):
            issues.append(MatrixResultIssue("invalid_artifact_path", "artifact path must be safe and relative"))
        sha = artifact.get("sha256")
        if not isinstance(sha, str) or _SHA256_RE.fullmatch(sha) is None:
            issues.append(MatrixResultIssue("invalid_artifact_hash", "artifact sha256 must be a lowercase SHA-256 hex digest"))
        _positive_int(artifact.get("bytes"), "artifact_bytes", issues)
        rights = artifact.get("source_rights")
        if not isinstance(rights, dict):
            issues.append(
                MatrixResultIssue(
                    "artifact_source_rights_missing",
                    "artifact source_rights must be a companion artifact-rights object",
                )
            )
        else:
            rights_report = validate_alphaevolve_companion_artifact_rights(rights)
            issues.extend(
                MatrixResultIssue(
                    f"artifact_source_rights_{issue.code}",
                    issue.message,
                )
                for issue in rights_report.issues
            )
    return kinds


def _validate_known_target_dimensions(
    target_id: str,
    dimensions: list[int],
    issues: list[MatrixResultIssue],
) -> None:
    target = matrix_target_by_id(target_id)
    if target is None:
        issues.append(
            MatrixResultIssue(
                "unknown_target_id",
                "target_id is not in the AlphaEvolve Appendix A matrix registry",
            )
        )
        return
    if target.get("dimensions") != dimensions:
        issues.append(
            MatrixResultIssue(
                "target_dimensions_mismatch",
                "dimensions must match the AlphaEvolve Appendix A matrix registry",
            )
        )


def _exactness_status(value: object) -> str:
    if isinstance(value, dict) and isinstance(value.get("status"), str):
        return value["status"]
    return "unknown"
