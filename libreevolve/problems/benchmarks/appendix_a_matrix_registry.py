from __future__ import annotations

import json
import re
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path
from typing import Any


REGISTRY_PATH = Path(__file__).with_name("alphaevolve_appendix_a_matrix.json")
REGISTRY_SCHEMA = "libreevolve.alphaevolve_appendix_a_matrix_registry.v1"
CURATION_SCHEMA = "libreevolve.alphaevolve_appendix_a_matrix_curation.v1"
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


@dataclass(frozen=True)
class MatrixTargetCurationIssue:
    code: str
    message: str
    target_id: str | None = None


@dataclass(frozen=True)
class MatrixTargetCurationReport:
    ok: bool
    included_target_count: int
    omitted_equivalent_count: int
    outside_rough_rule_count: int
    issues: list[MatrixTargetCurationIssue]


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


def appendix_a_matrix_curation_record(
    path: str | Path = REGISTRY_PATH,
) -> dict[str, Any]:
    targets = matrix_target_records(path)
    included_targets = [_curated_target_record(target) for target in targets]
    omitted_equivalents = [
        omitted
        for target in targets
        for omitted in _omitted_axis_permutation_records(target)
    ]
    return {
        "schema": CURATION_SCHEMA,
        "source_paper_id": "2506.13131",
        "source_section": "AlphaEvolve Appendix A",
        "source_pdf_page": 34,
        "target_suite": TARGET_SUITE,
        "selection_policy": {
            "reported_target_count": EXPECTED_TARGET_COUNT,
            "rough_min_dimension": 2,
            "rough_m_max": 5,
            "rough_n_max": 5,
            "p_cutoff_policy": "reasonable_cutoff_not_numerically_specified_in_paper",
            "paper_wording": "chosen roughly representing sizes where 2 <= m,n <= 5, with some reasonable cutoff for p",
        },
        "symmetry_policy": {
            "canonical_order": "m <= n <= p",
            "axis_permutation_equivalence": True,
            "paper_wording": "equivalent algorithms for any permutations of the three axes",
        },
        "included_targets": included_targets,
        "omitted_equivalent_targets": omitted_equivalents,
    }


def validate_appendix_a_matrix_curation(
    recordset: object | str | Path | None = None,
) -> MatrixTargetCurationReport:
    data, read_issues = _load_curation_recordset(recordset)
    if read_issues:
        return MatrixTargetCurationReport(False, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixTargetCurationIssue] = []
    if data.get("schema") != CURATION_SCHEMA:
        issues.append(MatrixTargetCurationIssue("invalid_schema", "unsupported Appendix A matrix curation schema"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(MatrixTargetCurationIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section") != "AlphaEvolve Appendix A":
        issues.append(MatrixTargetCurationIssue("invalid_source_section", "source_section must be AlphaEvolve Appendix A"))
    if data.get("source_pdf_page") != 34:
        issues.append(MatrixTargetCurationIssue("invalid_source_pdf_page", "source_pdf_page must identify page 34"))
    if data.get("target_suite") != TARGET_SUITE:
        issues.append(MatrixTargetCurationIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    _validate_selection_policy(data.get("selection_policy"), issues)
    _validate_symmetry_policy(data.get("symmetry_policy"), issues)
    included_count, outside_count, included_ids = _validate_included_targets(data.get("included_targets"), issues)
    omitted_count = _validate_omitted_equivalent_targets(data.get("omitted_equivalent_targets"), included_ids, issues)
    return MatrixTargetCurationReport(
        ok=not issues,
        included_target_count=included_count,
        omitted_equivalent_count=omitted_count,
        outside_rough_rule_count=outside_count,
        issues=issues,
    )


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


def render_appendix_a_matrix_curation_summary(
    recordset: object | str | Path | None = None,
) -> str:
    report = validate_appendix_a_matrix_curation(recordset)
    status = "ok" if report.ok else "invalid"
    lines = [
        "AlphaEvolve Appendix A matrix target-suite curation",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| included_target_count | {report.included_target_count} |",
        f"| omitted_equivalent_count | {report.omitted_equivalent_count} |",
        f"| outside_rough_rule_count | {report.outside_rough_rule_count} |",
    ]
    if report.issues:
        lines.extend(["", "Issues:"])
        lines.extend(
            f"- {issue.code}: {issue.message}"
            + (f" ({issue.target_id})" if issue.target_id else "")
            for issue in report.issues
        )
    return "\n".join(lines)


def _load_registry(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_curation_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[MatrixTargetCurationIssue]]:
    if recordset is None:
        return appendix_a_matrix_curation_record(), []
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [MatrixTargetCurationIssue("read_error", f"failed to read curation recordset: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [MatrixTargetCurationIssue("invalid_json", f"invalid curation JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [MatrixTargetCurationIssue("invalid_shape", "curation recordset must be a JSON object")]


def _target_id(target: object, index: int) -> str:
    if isinstance(target, dict) and isinstance(target.get("id"), str):
        return target["id"]
    return f"target_{index}"


def _curated_target_record(target: dict[str, Any]) -> dict[str, Any]:
    dimensions = target.get("dimensions")
    if not isinstance(dimensions, list):
        dimensions = []
    target_id = str(target.get("id", ""))
    inside_rough_rule = (
        len(dimensions) == 3
        and all(isinstance(value, int) and not isinstance(value, bool) for value in dimensions)
        and dimensions[0] >= 2
        and dimensions[1] >= 2
        and dimensions[0] <= 5
        and dimensions[1] <= 5
    )
    return {
        "target_id": target_id,
        "dimensions": list(dimensions),
        "canonical_representative": True,
        "selection_bucket": "rough_rule" if inside_rough_rule else "reported_outside_rough_rule",
        "inclusion_rationale": (
            "within paper rough 2 <= m,n <= 5 selection"
            if inside_rough_rule
            else "reported in Appendix A Table 3 outside the rough 2 <= m,n <= 5 selection"
        ),
    }


def _omitted_axis_permutation_records(target: dict[str, Any]) -> list[dict[str, Any]]:
    dimensions = target.get("dimensions")
    target_id = target.get("id")
    if not isinstance(target_id, str) or not isinstance(dimensions, list) or len(dimensions) != 3:
        return []
    if not all(isinstance(value, int) and not isinstance(value, bool) for value in dimensions):
        return []
    omitted: list[dict[str, Any]] = []
    canonical = tuple(dimensions)
    for permuted in sorted(set(permutations(canonical))):
        if permuted == canonical:
            continue
        omitted.append(
            {
                "canonical_target_id": target_id,
                "omitted_target_id": "mm_" + "x".join(str(value) for value in permuted),
                "dimensions": list(permuted),
                "equivalence": "matrix_tensor_axis_permutation",
            }
        )
    return omitted


def _validate_selection_policy(value: object, issues: list[MatrixTargetCurationIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixTargetCurationIssue("invalid_selection_policy", "selection_policy must be an object"))
        return
    expected = {
        "reported_target_count": EXPECTED_TARGET_COUNT,
        "rough_min_dimension": 2,
        "rough_m_max": 5,
        "rough_n_max": 5,
        "p_cutoff_policy": "reasonable_cutoff_not_numerically_specified_in_paper",
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(MatrixTargetCurationIssue(f"invalid_selection_{key}", f"selection_policy.{key} must match the paper curation record"))
    wording = value.get("paper_wording")
    if not isinstance(wording, str) or "2 <= m,n <= 5" not in wording or "reasonable cutoff" not in wording:
        issues.append(MatrixTargetCurationIssue("missing_selection_paper_wording", "selection_policy.paper_wording must preserve the rough size/cutoff phrase"))


def _validate_symmetry_policy(value: object, issues: list[MatrixTargetCurationIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixTargetCurationIssue("invalid_symmetry_policy", "symmetry_policy must be an object"))
        return
    if value.get("canonical_order") != "m <= n <= p":
        issues.append(MatrixTargetCurationIssue("invalid_canonical_order", "canonical_order must be m <= n <= p"))
    if value.get("axis_permutation_equivalence") is not True:
        issues.append(MatrixTargetCurationIssue("missing_axis_permutation_equivalence", "axis_permutation_equivalence must be true"))
    wording = value.get("paper_wording")
    if not isinstance(wording, str) or "permutations of the three axes" not in wording:
        issues.append(MatrixTargetCurationIssue("missing_symmetry_paper_wording", "symmetry_policy.paper_wording must preserve axis-permutation wording"))


def _validate_included_targets(
    value: object,
    issues: list[MatrixTargetCurationIssue],
) -> tuple[int, int, set[str]]:
    if not isinstance(value, list):
        issues.append(MatrixTargetCurationIssue("invalid_included_targets", "included_targets must be a list"))
        return 0, 0, set()
    registry_targets = {target["id"]: target for target in matrix_target_records() if isinstance(target.get("id"), str)}
    seen: set[str] = set()
    outside_count = 0
    for target in value:
        if not isinstance(target, dict):
            issues.append(MatrixTargetCurationIssue("invalid_included_target", "included target must be an object"))
            continue
        target_id = target.get("target_id")
        safe_id = target_id if isinstance(target_id, str) else None
        if safe_id is None or safe_id not in registry_targets:
            issues.append(MatrixTargetCurationIssue("unknown_included_target", "included target must reference the Appendix A registry", safe_id))
            continue
        if safe_id in seen:
            issues.append(MatrixTargetCurationIssue("duplicate_included_target", "included target ids must be unique", safe_id))
        seen.add(safe_id)
        registry_dimensions = registry_targets[safe_id].get("dimensions")
        if target.get("dimensions") != registry_dimensions:
            issues.append(MatrixTargetCurationIssue("included_target_dimension_mismatch", "included target dimensions must match registry", safe_id))
        if registry_dimensions != sorted(registry_dimensions):
            issues.append(MatrixTargetCurationIssue("included_target_not_sorted", "included target dimensions must be sorted representatives", safe_id))
        if target.get("canonical_representative") is not True:
            issues.append(MatrixTargetCurationIssue("missing_canonical_representative", "included targets must declare canonical_representative true", safe_id))
        bucket = target.get("selection_bucket")
        inside_rule = (
            isinstance(registry_dimensions, list)
            and len(registry_dimensions) == 3
            and registry_dimensions[0] <= 5
            and registry_dimensions[1] <= 5
        )
        expected_bucket = "rough_rule" if inside_rule else "reported_outside_rough_rule"
        if bucket != expected_bucket:
            issues.append(MatrixTargetCurationIssue("invalid_selection_bucket", "selection_bucket must match the paper rough-rule boundary", safe_id))
        if bucket == "reported_outside_rough_rule":
            outside_count += 1
        rationale = target.get("inclusion_rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            issues.append(MatrixTargetCurationIssue("missing_inclusion_rationale", "included target must include an inclusion rationale", safe_id))
    missing = set(registry_targets) - seen
    for target_id in sorted(missing):
        issues.append(MatrixTargetCurationIssue("missing_included_target", "every Appendix A registry target must have curation metadata", target_id))
    return len(value), outside_count, seen


def _validate_omitted_equivalent_targets(
    value: object,
    included_ids: set[str],
    issues: list[MatrixTargetCurationIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(MatrixTargetCurationIssue("invalid_omitted_equivalent_targets", "omitted_equivalent_targets must be a list"))
        return 0
    expected = {
        record["omitted_target_id"]: record
        for target in matrix_target_records()
        for record in _omitted_axis_permutation_records(target)
        if target.get("id") in included_ids
    }
    seen: set[str] = set()
    for record in value:
        if not isinstance(record, dict):
            issues.append(MatrixTargetCurationIssue("invalid_omitted_equivalent_target", "omitted equivalent target must be an object"))
            continue
        omitted_id = record.get("omitted_target_id")
        safe_id = omitted_id if isinstance(omitted_id, str) else None
        if safe_id is None or safe_id not in expected:
            issues.append(MatrixTargetCurationIssue("unknown_omitted_equivalent_target", "omitted equivalent target must be a derived axis permutation", safe_id))
            continue
        if safe_id in seen:
            issues.append(MatrixTargetCurationIssue("duplicate_omitted_equivalent_target", "omitted equivalent target ids must be unique", safe_id))
        seen.add(safe_id)
        if record != expected[safe_id]:
            issues.append(MatrixTargetCurationIssue("omitted_equivalent_target_mismatch", "omitted equivalent target record must match derived axis permutation", safe_id))
    for omitted_id in sorted(set(expected) - seen):
        issues.append(MatrixTargetCurationIssue("missing_omitted_equivalent_target", "all omitted axis-permutation equivalents must be listed", omitted_id))
    return len(value)


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
