from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REGISTRY_PATH = Path(__file__).with_name("alphaevolve_appendix_a_matrix.json")
REGISTRY_SCHEMA = "libreevolve.alphaevolve_appendix_a_matrix_registry.v1"
TARGET_SUITE = "alphaevolve_appendix_a"
EXPECTED_TARGET_COUNT = 54
OUTCOMES = frozenset({"matched", "surpassed", "fell_behind"})
_ID_RE = re.compile(r"mm_[1-9][0-9]*x[1-9][0-9]*x[1-9][0-9]*")


@dataclass(frozen=True)
class MatrixTargetIssue:
    code: str
    message: str
    target_id: str | None = None


@dataclass(frozen=True)
class MatrixTargetRegistryReport:
    ok: bool
    target_count: int
    matched_count: int
    surpassed_count: int
    fell_behind_count: int
    issues: list[MatrixTargetIssue]


def matrix_target_records(
    path: str | Path = REGISTRY_PATH,
) -> list[dict[str, Any]]:
    data = _load_registry(path)
    targets = data.get("targets")
    if not isinstance(targets, list):
        return []
    return [dict(target) for target in targets if isinstance(target, dict)]


def matrix_target_by_id(
    target_id: str,
    path: str | Path = REGISTRY_PATH,
) -> dict[str, Any] | None:
    for target in matrix_target_records(path):
        if target.get("id") == target_id:
            return target
    return None


def validate_appendix_a_matrix_registry(
    path: str | Path = REGISTRY_PATH,
) -> MatrixTargetRegistryReport:
    issues: list[MatrixTargetIssue] = []
    try:
        data = _load_registry(path)
    except OSError as exc:
        return MatrixTargetRegistryReport(False, 0, 0, 0, 0, [
            MatrixTargetIssue("read_error", f"failed to read registry: {exc}")
        ])
    except json.JSONDecodeError as exc:
        return MatrixTargetRegistryReport(False, 0, 0, 0, 0, [
            MatrixTargetIssue("invalid_json", f"invalid registry JSON: {exc.msg}")
        ])
    if not isinstance(data, dict):
        return MatrixTargetRegistryReport(False, 0, 0, 0, 0, [
            MatrixTargetIssue("invalid_shape", "registry must be a JSON object")
        ])
    if data.get("schema") != REGISTRY_SCHEMA:
        issues.append(MatrixTargetIssue("invalid_schema", "unsupported registry schema"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(MatrixTargetIssue("invalid_source", "source_paper_id must be 2506.13131"))
    if data.get("target_suite") != TARGET_SUITE:
        issues.append(MatrixTargetIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    targets = data.get("targets")
    if not isinstance(targets, list):
        return MatrixTargetRegistryReport(False, 0, 0, 0, 0, issues + [
            MatrixTargetIssue("invalid_targets", "targets must be a list")
        ])
    if len(targets) != EXPECTED_TARGET_COUNT:
        issues.append(MatrixTargetIssue("invalid_target_count", "Appendix A registry must contain 54 targets"))
    seen: set[str] = set()
    outcome_counts = {"matched": 0, "surpassed": 0, "fell_behind": 0}
    for index, target in enumerate(targets):
        target_id = _target_id(target, index)
        if not isinstance(target, dict):
            issues.append(MatrixTargetIssue("invalid_target", "target must be an object", target_id))
            continue
        _validate_target(target, target_id, issues)
        if target_id in seen:
            issues.append(MatrixTargetIssue("duplicate_target", "target ids must be unique", target_id))
        seen.add(target_id)
        outcome = target.get("outcome")
        if isinstance(outcome, str) and outcome in outcome_counts:
            outcome_counts[outcome] += 1
    if outcome_counts != {"matched": 38, "surpassed": 14, "fell_behind": 2}:
        issues.append(
            MatrixTargetIssue(
                "invalid_outcome_counts",
                "Appendix A Table 3 outcome counts must be 38 matched, 14 surpassed, 2 fell_behind",
            )
        )
    return MatrixTargetRegistryReport(
        ok=not issues,
        target_count=len(targets),
        matched_count=outcome_counts["matched"],
        surpassed_count=outcome_counts["surpassed"],
        fell_behind_count=outcome_counts["fell_behind"],
        issues=issues,
    )


def render_appendix_a_matrix_registry_summary(
    path: str | Path = REGISTRY_PATH,
) -> str:
    report = validate_appendix_a_matrix_registry(path)
    status = "ok" if report.ok else "invalid"
    return "\n".join(
        [
            "AlphaEvolve Appendix A matrix target registry",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| schema_status | {status} |",
            f"| target_count | {report.target_count} |",
            f"| matched | {report.matched_count} |",
            f"| surpassed | {report.surpassed_count} |",
            f"| fell_behind | {report.fell_behind_count} |",
        ]
    )


def _load_registry(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _target_id(target: object, index: int) -> str:
    if isinstance(target, dict) and isinstance(target.get("id"), str):
        return target["id"]
    return f"target_{index}"


def _validate_target(
    target: dict[str, Any],
    target_id: str,
    issues: list[MatrixTargetIssue],
) -> None:
    if _ID_RE.fullmatch(target_id) is None:
        issues.append(MatrixTargetIssue("invalid_target_id", "target id must use mm_MxNxP", target_id))
    dimensions = target.get("dimensions")
    if not isinstance(dimensions, list) or len(dimensions) != 3:
        issues.append(MatrixTargetIssue("invalid_dimensions", "dimensions must contain three positive integers", target_id))
        dimensions = None
    else:
        for value in dimensions:
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                issues.append(MatrixTargetIssue("invalid_dimensions", "dimensions must contain three positive integers", target_id))
                dimensions = None
                break
    if dimensions is not None:
        expected_id = "mm_" + "x".join(str(value) for value in dimensions)
        if target_id != expected_id:
            issues.append(MatrixTargetIssue("target_id_dimension_mismatch", "target id must match dimensions", target_id))
        if dimensions != sorted(dimensions):
            issues.append(MatrixTargetIssue("unsorted_dimensions", "Appendix A target dimensions must be sorted", target_id))
    best_known = _positive_int(target.get("best_known_rank"), "best_known_rank", target_id, issues)
    alphaevolve = _positive_int(target.get("alphaevolve_rank"), "alphaevolve_rank", target_id, issues)
    outcome = target.get("outcome")
    if outcome not in OUTCOMES:
        issues.append(MatrixTargetIssue("invalid_outcome", "unsupported outcome", target_id))
    elif best_known is not None and alphaevolve is not None:
        if outcome == "matched" and alphaevolve != best_known:
            issues.append(MatrixTargetIssue("invalid_matched_rank", "matched targets must equal best_known_rank", target_id))
        elif outcome == "surpassed" and alphaevolve >= best_known:
            issues.append(MatrixTargetIssue("invalid_surpassed_rank", "surpassed targets must improve best_known_rank", target_id))
        elif outcome == "fell_behind" and alphaevolve <= best_known:
            issues.append(MatrixTargetIssue("invalid_fell_behind_rank", "fell_behind targets must be worse than best_known_rank", target_id))
    if target.get("exact_algorithm") is not True:
        issues.append(MatrixTargetIssue("missing_exact_algorithm", "Appendix A targets must mark exact_algorithm true", target_id))


def _positive_int(
    value: object,
    field: str,
    target_id: str,
    issues: list[MatrixTargetIssue],
) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        issues.append(MatrixTargetIssue(f"invalid_{field}", f"{field} must be a positive integer", target_id))
        return None
    return value
