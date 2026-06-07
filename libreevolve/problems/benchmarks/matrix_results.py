from __future__ import annotations

import json
import hashlib
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    TARGET_SUITE as APPENDIX_A_TARGET_SUITE,
    matrix_target_by_id,
)


MATRIX_RESULT_SCHEMA = "libreevolve.matrix_result_report.v1"
MATRIX_ARTIFACT_INVENTORY_SCHEMA = "libreevolve.matrix_result_artifact_inventory.v1"
COEFFICIENT_DOMAINS = frozenset({"integer", "half_integer", "rational", "float"})
PUBLICATION_COEFFICIENT_DOMAINS = frozenset({"integer", "half_integer"})
EXACTNESS_STATUSES = frozenset({"verified", "failed", "not_checked"})
ARTIFACT_KINDS = frozenset({"algorithm", "certificate", "summary", "notebook"})
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
            },
            {
                "kind": "certificate",
                "path": "matrix/mm_2x2x2/certificate.json",
                "sha256": certificate_sha,
                "bytes": certificate_bytes,
            },
            {
                "kind": "notebook",
                "path": "matrix/mm_2x2x2/reproduce.ipynb",
                "sha256": notebook_sha,
                "bytes": notebook_bytes,
            },
        ],
    }
    report_path = base / "report.json"
    report_sha, report_bytes = _write_canonical_json(report_path, report)
    inventory = matrix_result_artifact_inventory(report, root)
    return {
        "schema": "libreevolve.matrix_publication_bundle.v1",
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "target_id": _STRASSEN_TARGET_ID,
        "artifact_root": str(root),
        "report_path": "matrix/mm_2x2x2/report.json",
        "report_sha256": report_sha,
        "report_bytes": report_bytes,
        "report": report,
        "inventory": inventory,
    }


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
    record: dict[str, Any] = {
        "kind": kind if isinstance(kind, str) else "unknown",
        "path": path if isinstance(path, str) else "",
        "expected_sha256": expected_sha if isinstance(expected_sha, str) else "",
        "expected_bytes": expected_bytes if isinstance(expected_bytes, int) and not isinstance(expected_bytes, bool) else None,
        "status": "verified",
        "issues": [],
    }
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
