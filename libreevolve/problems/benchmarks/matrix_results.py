from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MATRIX_RESULT_SCHEMA = "libreevolve.matrix_result_report.v1"
COEFFICIENT_DOMAINS = frozenset({"integer", "half_integer", "rational", "float"})
PUBLICATION_COEFFICIENT_DOMAINS = frozenset({"integer", "half_integer"})
EXACTNESS_STATUSES = frozenset({"verified", "failed", "not_checked"})
ARTIFACT_KINDS = frozenset({"algorithm", "certificate", "summary", "notebook"})
_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


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
    _text_field(data, "target_suite", issues)
    dimensions = data.get("dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        issues.append(MatrixResultIssue("invalid_dimensions", "dimensions must be a non-empty list"))
    else:
        for value in dimensions:
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                issues.append(MatrixResultIssue("invalid_dimensions", "dimensions must be positive integers"))
                break
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


def _exactness_status(value: object) -> str:
    if isinstance(value, dict) and isinstance(value.get("status"), str):
        return value["status"]
    return "unknown"
