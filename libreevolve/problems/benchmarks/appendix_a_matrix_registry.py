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
RESOURCE_FRONTIER_SCHEMA = "libreevolve.alphaevolve_appendix_a_matrix_resource_frontier.v1"
SUBSET_SCOPE_SCHEMA = "libreevolve.alphaevolve_matrix_subset_scope.v1"
ROW_NOTE_SCHEMA = "libreevolve.alphaevolve_appendix_a_matrix_row_notes.v1"
TARGET_SUITE = "alphaevolve_appendix_a"
EXPECTED_TARGET_COUNT = 54
OUTCOMES = frozenset({"matched", "surpassed", "fell_behind"})
_ID_RE = re.compile(r"mm_[1-9][0-9]*x[1-9][0-9]*x[1-9][0-9]*")
TABLE_2_SELECTED_TARGET_IDS = (
    "mm_2x4x5",
    "mm_2x4x7",
    "mm_2x4x8",
    "mm_2x5x6",
    "mm_3x3x3",
    "mm_3x4x6",
    "mm_3x4x7",
    "mm_3x4x8",
    "mm_3x5x6",
    "mm_3x5x7",
    "mm_4x4x4",
    "mm_4x4x5",
    "mm_4x4x7",
    "mm_4x4x8",
    "mm_4x5x6",
    "mm_5x5x5",
)


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


@dataclass(frozen=True)
class MatrixResourceFrontierIssue:
    code: str
    message: str
    attempt_id: str | None = None


@dataclass(frozen=True)
class MatrixResourceFrontierReport:
    ok: bool
    attempted_scope_count: int
    local_artifact_count: int
    issues: list[MatrixResourceFrontierIssue]


@dataclass(frozen=True)
class MatrixSubsetScopeIssue:
    code: str
    message: str
    subset_id: str | None = None


@dataclass(frozen=True)
class MatrixSubsetScopeReport:
    ok: bool
    subset_count: int
    main_text_target_count: int
    full_table_target_count: int
    full_table_fell_behind_count: int
    issues: list[MatrixSubsetScopeIssue]


@dataclass(frozen=True)
class MatrixRowNoteIssue:
    code: str
    message: str
    note_id: str | None = None


@dataclass(frozen=True)
class MatrixRowNoteReport:
    ok: bool
    note_count: int
    concurrent_work_note_count: int
    affected_target_count: int
    issues: list[MatrixRowNoteIssue]


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


def appendix_a_matrix_resource_frontier_record() -> dict[str, Any]:
    return {
        "schema": RESOURCE_FRONTIER_SCHEMA,
        "source_paper_id": "2506.13131",
        "source_section": "AlphaEvolve Appendix A",
        "source_pdf_page": 34,
        "target_suite": TARGET_SUITE,
        "frontier_observations": [
            {
                "attempt_id": "paper_beyond_5x5x5_single_gpu_1000_seeds",
                "target_scope": "sizes_beyond_5x5x5",
                "seed_count": 1000,
                "accelerator_profile": "single_gpu_accelerator",
                "resource_status": "often_out_of_memory",
                "extension_requirement": "further_optimization_required",
                "source_phrase": (
                    "sizes beyond <5,5,5> on 1000 random seeds on evaluators "
                    "with a single GPU accelerator often run out of memory"
                ),
                "local_execution_evidence": False,
                "local_artifacts": [],
            }
        ],
    }


def appendix_a_matrix_subset_scope_record(
    path: str | Path = REGISTRY_PATH,
) -> dict[str, Any]:
    targets = matrix_target_records(path)
    all_ids = [target["id"] for target in targets if isinstance(target.get("id"), str)]
    main_text_ids = [
        target["id"]
        for target in targets
        if isinstance(target.get("id"), str)
        and isinstance(target.get("dimensions"), list)
        and all(isinstance(value, int) and not isinstance(value, bool) and value <= 5 for value in target["dimensions"])
    ]
    return {
        "schema": SUBSET_SCOPE_SCHEMA,
        "source_paper_id": "2506.13131",
        "target_suite": TARGET_SUITE,
        "subsets": [
            _subset_scope_record(
                subset_id="appendix_a_full",
                inclusion_predicate="all_appendix_a_table3_rows",
                source_table="Appendix A Table 3",
                source_pdf_page=34,
                source_phrase="Table 3 in appendix for full results",
                target_ids=all_ids,
                all_target_ids=all_ids,
                targets=targets,
            ),
            _subset_scope_record(
                subset_id="main_text_mnp_le_5",
                inclusion_predicate="all_dimensions_le_5",
                source_table="Table 2 caption",
                source_pdf_page=9,
                source_phrase=(
                    "Beyond the examples shown here, for all parameters "
                    "m, n, p <= 5, AlphaEvolve either matched or surpassed "
                    "the best known solutions"
                ),
                target_ids=main_text_ids,
                all_target_ids=all_ids,
                targets=targets,
            ),
            _subset_scope_record(
                subset_id="table_2_selected",
                inclusion_predicate="explicit_table_2_displayed_rows",
                source_table="Table 2",
                source_pdf_page=9,
                source_phrase="Upper bounds on the rank of the tensor examples shown in Table 2",
                target_ids=list(TABLE_2_SELECTED_TARGET_IDS),
                all_target_ids=all_ids,
                targets=targets,
            ),
        ],
    }


def validate_appendix_a_matrix_subset_scope(
    recordset: object | str | Path | None = None,
) -> MatrixSubsetScopeReport:
    data, read_issues = _load_subset_scope_recordset(recordset)
    if read_issues:
        return MatrixSubsetScopeReport(False, 0, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixSubsetScopeIssue] = []
    if data.get("schema") != SUBSET_SCOPE_SCHEMA:
        issues.append(MatrixSubsetScopeIssue("invalid_schema", "unsupported Appendix A matrix subset-scope schema"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(MatrixSubsetScopeIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("target_suite") != TARGET_SUITE:
        issues.append(MatrixSubsetScopeIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    subset_reports = _validate_subset_scope_records(data.get("subsets"), issues)
    main_text = subset_reports.get("main_text_mnp_le_5", {})
    full_table = subset_reports.get("appendix_a_full", {})
    return MatrixSubsetScopeReport(
        ok=not issues,
        subset_count=len(subset_reports),
        main_text_target_count=int(main_text.get("row_count", 0)),
        full_table_target_count=int(full_table.get("row_count", 0)),
        full_table_fell_behind_count=int(full_table.get("fell_behind_count", 0)),
        issues=issues,
    )


def appendix_a_matrix_row_note_records(
    path: str | Path = REGISTRY_PATH,
) -> dict[str, Any]:
    target = matrix_target_by_id("mm_4x5x6", path)
    return {
        "schema": ROW_NOTE_SCHEMA,
        "source_paper_id": "2506.13131",
        "target_suite": TARGET_SUITE,
        "source_section": "AlphaEvolve Appendix A Table 3",
        "source_pdf_page": 34,
        "row_notes": [
            {
                "note_id": "concurrent_work_rank90_mm_4x5x6",
                "note_type": "concurrent_work",
                "target_id": "mm_4x5x6",
                "dimensions": [4, 5, 6],
                "alphaevolve_rank": target.get("alphaevolve_rank") if isinstance(target, dict) else 90,
                "concurrent_rank": 90,
                "cited_reference_id": "49",
                "relationship_to_alphaevolve": "independently_matched_alphaevolve_rank",
                "source_table": "Appendix A Table 3",
                "source_pdf_page": 34,
                "note_text": "Concurrent work [49] has also found a rank-90 algorithm for <4, 5, 6>.",
                "exclusive_priority_claim_safe": False,
                "docs_caveat": "Do not claim exclusive SOTA priority for mm_4x5x6 without noting concurrent work [49].",
            }
        ],
    }


def validate_appendix_a_matrix_row_notes(
    recordset: object | str | Path | None = None,
) -> MatrixRowNoteReport:
    data, read_issues = _load_row_note_recordset(recordset)
    if read_issues:
        return MatrixRowNoteReport(False, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixRowNoteIssue] = []
    if data.get("schema") != ROW_NOTE_SCHEMA:
        issues.append(MatrixRowNoteIssue("invalid_schema", "unsupported Appendix A matrix row-note schema"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(MatrixRowNoteIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("target_suite") != TARGET_SUITE:
        issues.append(MatrixRowNoteIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    if data.get("source_section") != "AlphaEvolve Appendix A Table 3":
        issues.append(MatrixRowNoteIssue("invalid_source_section", "source_section must identify Appendix A Table 3"))
    if data.get("source_pdf_page") != 34:
        issues.append(MatrixRowNoteIssue("invalid_source_pdf_page", "row-note source_pdf_page must be 34"))
    note_count, concurrent_count, affected_count = _validate_row_notes(data.get("row_notes"), issues)
    return MatrixRowNoteReport(
        ok=not issues,
        note_count=note_count,
        concurrent_work_note_count=concurrent_count,
        affected_target_count=affected_count,
        issues=issues,
    )


def validate_appendix_a_matrix_resource_frontier(
    recordset: object | str | Path | None = None,
) -> MatrixResourceFrontierReport:
    data, read_issues = _load_resource_frontier_recordset(recordset)
    if read_issues:
        return MatrixResourceFrontierReport(False, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResourceFrontierIssue] = []
    if data.get("schema") != RESOURCE_FRONTIER_SCHEMA:
        issues.append(MatrixResourceFrontierIssue("invalid_schema", "unsupported Appendix A matrix resource-frontier schema"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(MatrixResourceFrontierIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section") != "AlphaEvolve Appendix A":
        issues.append(MatrixResourceFrontierIssue("invalid_source_section", "source_section must be AlphaEvolve Appendix A"))
    if data.get("source_pdf_page") != 34:
        issues.append(MatrixResourceFrontierIssue("invalid_source_pdf_page", "source_pdf_page must identify page 34"))
    if data.get("target_suite") != TARGET_SUITE:
        issues.append(MatrixResourceFrontierIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    attempted_count, artifact_count = _validate_frontier_observations(data.get("frontier_observations"), issues)
    return MatrixResourceFrontierReport(
        ok=not issues,
        attempted_scope_count=attempted_count,
        local_artifact_count=artifact_count,
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


def render_appendix_a_matrix_resource_frontier_summary(
    recordset: object | str | Path | None = None,
) -> str:
    report = validate_appendix_a_matrix_resource_frontier(recordset)
    status = "ok" if report.ok else "invalid"
    lines = [
        "AlphaEvolve Appendix A matrix resource frontier",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| attempted_scope_count | {report.attempted_scope_count} |",
        f"| local_artifact_count | {report.local_artifact_count} |",
    ]
    if report.issues:
        lines.extend(["", "Issues:"])
        lines.extend(
            f"- {issue.code}: {issue.message}"
            + (f" ({issue.attempt_id})" if issue.attempt_id else "")
            for issue in report.issues
        )
    return "\n".join(lines)


def render_appendix_a_matrix_subset_scope_summary(
    recordset: object | str | Path | None = None,
) -> str:
    report = validate_appendix_a_matrix_subset_scope(recordset)
    status = "ok" if report.ok else "invalid"
    lines = [
        "AlphaEvolve matrix subset-scope evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| subset_count | {report.subset_count} |",
        f"| main_text_target_count | {report.main_text_target_count} |",
        f"| full_table_target_count | {report.full_table_target_count} |",
        f"| full_table_fell_behind_count | {report.full_table_fell_behind_count} |",
    ]
    if report.issues:
        lines.extend(["", "Issues:"])
        lines.extend(
            f"- {issue.code}: {issue.message}"
            + (f" ({issue.subset_id})" if issue.subset_id else "")
            for issue in report.issues
        )
    return "\n".join(lines)


def render_appendix_a_matrix_row_note_summary(
    recordset: object | str | Path | None = None,
) -> str:
    report = validate_appendix_a_matrix_row_notes(recordset)
    status = "ok" if report.ok else "invalid"
    lines = [
        "AlphaEvolve Appendix A matrix row-note evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| note_count | {report.note_count} |",
        f"| concurrent_work_note_count | {report.concurrent_work_note_count} |",
        f"| affected_target_count | {report.affected_target_count} |",
    ]
    if report.issues:
        lines.extend(["", "Issues:"])
        lines.extend(
            f"- {issue.code}: {issue.message}"
            + (f" ({issue.note_id})" if issue.note_id else "")
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


def _load_resource_frontier_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[MatrixResourceFrontierIssue]]:
    if recordset is None:
        return appendix_a_matrix_resource_frontier_record(), []
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [MatrixResourceFrontierIssue("read_error", f"failed to read resource-frontier recordset: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [MatrixResourceFrontierIssue("invalid_json", f"invalid resource-frontier JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [MatrixResourceFrontierIssue("invalid_shape", "resource-frontier recordset must be a JSON object")]


def _load_subset_scope_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[MatrixSubsetScopeIssue]]:
    if recordset is None:
        return appendix_a_matrix_subset_scope_record(), []
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [MatrixSubsetScopeIssue("read_error", f"failed to read subset-scope recordset: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [MatrixSubsetScopeIssue("invalid_json", f"invalid subset-scope JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [MatrixSubsetScopeIssue("invalid_shape", "subset-scope recordset must be a JSON object")]


def _load_row_note_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[MatrixRowNoteIssue]]:
    if recordset is None:
        return appendix_a_matrix_row_note_records(), []
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [MatrixRowNoteIssue("read_error", f"failed to read row-note recordset: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [MatrixRowNoteIssue("invalid_json", f"invalid row-note JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [MatrixRowNoteIssue("invalid_shape", "row-note recordset must be a JSON object")]


def _target_id(target: object, index: int) -> str:
    if isinstance(target, dict) and isinstance(target.get("id"), str):
        return target["id"]
    return f"target_{index}"


def _subset_scope_record(
    *,
    subset_id: str,
    inclusion_predicate: str,
    source_table: str,
    source_pdf_page: int,
    source_phrase: str,
    target_ids: list[str],
    all_target_ids: list[str],
    targets: list[dict[str, Any]],
) -> dict[str, Any]:
    targets_by_id = {target["id"]: target for target in targets if isinstance(target.get("id"), str)}
    outcome_counts = _outcome_counts(targets_by_id[target_id] for target_id in target_ids)
    fell_behind_ids = [
        target_id
        for target_id in target_ids
        if targets_by_id[target_id].get("outcome") == "fell_behind"
    ]
    return {
        "subset_id": subset_id,
        "inclusion_predicate": inclusion_predicate,
        "source_table": source_table,
        "source_pdf_page": source_pdf_page,
        "source_phrase": source_phrase,
        "target_ids": target_ids,
        "row_count": len(target_ids),
        "outcome_counts": outcome_counts,
        "all_matched_or_surpassed": not fell_behind_ids,
        "fell_behind_target_ids": fell_behind_ids,
        "out_of_scope_target_ids": [target_id for target_id in all_target_ids if target_id not in set(target_ids)],
    }


def _outcome_counts(targets: Any) -> dict[str, int]:
    counts = {"matched": 0, "surpassed": 0, "fell_behind": 0}
    for target in targets:
        outcome = target.get("outcome") if isinstance(target, dict) else None
        if outcome in counts:
            counts[outcome] += 1
    return counts


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


def _validate_subset_scope_records(
    value: object,
    issues: list[MatrixSubsetScopeIssue],
) -> dict[str, dict[str, int]]:
    if not isinstance(value, list) or not value:
        issues.append(MatrixSubsetScopeIssue("invalid_subsets", "subsets must be a non-empty list"))
        return {}
    expected = _expected_subset_scope_records()
    seen: set[str] = set()
    reports: dict[str, dict[str, int]] = {}
    for subset in value:
        if not isinstance(subset, dict):
            issues.append(MatrixSubsetScopeIssue("invalid_subset", "subset records must be objects"))
            continue
        subset_id = subset.get("subset_id")
        safe_id = subset_id if isinstance(subset_id, str) else None
        if safe_id not in expected:
            issues.append(MatrixSubsetScopeIssue("unknown_subset_id", "subset_id must be one of the required matrix scope ids", safe_id))
            continue
        if safe_id in seen:
            issues.append(MatrixSubsetScopeIssue("duplicate_subset_id", "subset_id values must be unique", safe_id))
        seen.add(safe_id)
        expected_subset = expected[safe_id]
        _validate_subset_scope_record(subset, expected_subset, issues)
        outcome_counts = subset.get("outcome_counts")
        fell_behind_ids = subset.get("fell_behind_target_ids")
        reports[safe_id] = {
            "row_count": subset.get("row_count") if isinstance(subset.get("row_count"), int) else 0,
            "fell_behind_count": len(fell_behind_ids) if isinstance(fell_behind_ids, list) else 0,
            "matched_count": outcome_counts.get("matched", 0) if isinstance(outcome_counts, dict) else 0,
            "surpassed_count": outcome_counts.get("surpassed", 0) if isinstance(outcome_counts, dict) else 0,
        }
    for subset_id in sorted(set(expected) - seen):
        issues.append(MatrixSubsetScopeIssue("missing_subset", "required matrix subset-scope record is missing", subset_id))
    return reports


def _expected_subset_scope_records() -> dict[str, dict[str, Any]]:
    targets = matrix_target_records()
    all_ids = [target["id"] for target in targets if isinstance(target.get("id"), str)]
    main_text_ids = [
        target["id"]
        for target in targets
        if isinstance(target.get("id"), str)
        and isinstance(target.get("dimensions"), list)
        and all(isinstance(value, int) and not isinstance(value, bool) and value <= 5 for value in target["dimensions"])
    ]
    return {
        record["subset_id"]: record
        for record in (
            _subset_scope_record(
                subset_id="appendix_a_full",
                inclusion_predicate="all_appendix_a_table3_rows",
                source_table="Appendix A Table 3",
                source_pdf_page=34,
                source_phrase="Table 3 in appendix for full results",
                target_ids=all_ids,
                all_target_ids=all_ids,
                targets=targets,
            ),
            _subset_scope_record(
                subset_id="main_text_mnp_le_5",
                inclusion_predicate="all_dimensions_le_5",
                source_table="Table 2 caption",
                source_pdf_page=9,
                source_phrase=(
                    "Beyond the examples shown here, for all parameters "
                    "m, n, p <= 5, AlphaEvolve either matched or surpassed "
                    "the best known solutions"
                ),
                target_ids=main_text_ids,
                all_target_ids=all_ids,
                targets=targets,
            ),
            _subset_scope_record(
                subset_id="table_2_selected",
                inclusion_predicate="explicit_table_2_displayed_rows",
                source_table="Table 2",
                source_pdf_page=9,
                source_phrase="Upper bounds on the rank of the tensor examples shown in Table 2",
                target_ids=list(TABLE_2_SELECTED_TARGET_IDS),
                all_target_ids=all_ids,
                targets=targets,
            ),
        )
    }


def _validate_subset_scope_record(
    subset: dict[str, Any],
    expected: dict[str, Any],
    issues: list[MatrixSubsetScopeIssue],
) -> None:
    subset_id = expected["subset_id"]
    for field in ("inclusion_predicate", "source_table", "source_pdf_page"):
        if subset.get(field) != expected[field]:
            issues.append(MatrixSubsetScopeIssue(f"invalid_{field}", f"{field} must match the paper-backed subset scope", subset_id))
    source_phrase = subset.get("source_phrase")
    if not isinstance(source_phrase, str) or not source_phrase.strip():
        issues.append(MatrixSubsetScopeIssue("missing_source_phrase", "source_phrase must preserve table/caption linkage", subset_id))
    else:
        _validate_subset_source_phrase(subset_id, source_phrase, issues)
    target_ids = subset.get("target_ids")
    if not isinstance(target_ids, list) or not all(isinstance(target_id, str) for target_id in target_ids):
        issues.append(MatrixSubsetScopeIssue("invalid_target_ids", "target_ids must be a list of target ids", subset_id))
        target_ids = []
    if target_ids != expected["target_ids"]:
        issues.append(MatrixSubsetScopeIssue("target_ids_mismatch", "target_ids must exactly match the declared subset predicate", subset_id))
    if len(target_ids) != len(set(target_ids)):
        issues.append(MatrixSubsetScopeIssue("duplicate_target_id", "target_ids must be unique", subset_id))
    if subset.get("row_count") != expected["row_count"]:
        issues.append(MatrixSubsetScopeIssue("invalid_row_count", "row_count must match target_ids", subset_id))
    if subset.get("outcome_counts") != expected["outcome_counts"]:
        issues.append(MatrixSubsetScopeIssue("invalid_outcome_counts", "outcome_counts must match the selected registry rows", subset_id))
    if subset.get("all_matched_or_surpassed") != expected["all_matched_or_surpassed"]:
        issues.append(MatrixSubsetScopeIssue("invalid_all_matched_or_surpassed", "all_matched_or_surpassed must reflect whether the subset has fell_behind rows", subset_id))
    if subset.get("fell_behind_target_ids") != expected["fell_behind_target_ids"]:
        issues.append(MatrixSubsetScopeIssue("invalid_fell_behind_target_ids", "fell_behind_target_ids must match the selected registry rows", subset_id))
    if subset.get("out_of_scope_target_ids") != expected["out_of_scope_target_ids"]:
        issues.append(MatrixSubsetScopeIssue("invalid_out_of_scope_target_ids", "out_of_scope_target_ids must list Appendix A rows outside the subset", subset_id))
    if subset_id == "main_text_mnp_le_5" and subset.get("fell_behind_target_ids"):
        issues.append(MatrixSubsetScopeIssue("main_text_subset_has_fell_behind", "main_text_mnp_le_5 must preserve the all matched/surpassed claim", subset_id))
    if subset_id == "appendix_a_full" and subset.get("all_matched_or_surpassed") is True:
        issues.append(MatrixSubsetScopeIssue("full_table_overclaims_all_matched", "appendix_a_full must not claim all rows matched or surpassed", subset_id))


def _validate_subset_source_phrase(
    subset_id: str,
    source_phrase: str,
    issues: list[MatrixSubsetScopeIssue],
) -> None:
    if subset_id == "main_text_mnp_le_5":
        if "m, n, p <= 5" not in source_phrase or "matched or surpassed" not in source_phrase:
            issues.append(MatrixSubsetScopeIssue("missing_main_text_source_phrase", "main_text subset must preserve the m,n,p <= 5 matched/surpassed caption phrase", subset_id))
    elif subset_id == "table_2_selected":
        if "Table 2" not in source_phrase or "rank" not in source_phrase:
            issues.append(MatrixSubsetScopeIssue("missing_table2_source_phrase", "table_2_selected must preserve Table 2 rank-table linkage", subset_id))
    elif subset_id == "appendix_a_full":
        if "Table 3" not in source_phrase or "full results" not in source_phrase:
            issues.append(MatrixSubsetScopeIssue("missing_appendix_full_source_phrase", "appendix_a_full must preserve Appendix A full-results linkage", subset_id))


def _validate_row_notes(
    value: object,
    issues: list[MatrixRowNoteIssue],
) -> tuple[int, int, int]:
    if not isinstance(value, list) or not value:
        issues.append(MatrixRowNoteIssue("invalid_row_notes", "row_notes must be a non-empty list"))
        return 0, 0, 0
    seen: set[str] = set()
    concurrent_count = 0
    affected_targets: set[str] = set()
    required_seen = False
    for note in value:
        if not isinstance(note, dict):
            issues.append(MatrixRowNoteIssue("invalid_row_note", "row note entries must be objects"))
            continue
        note_id = note.get("note_id")
        safe_id = note_id if isinstance(note_id, str) else None
        if safe_id != "concurrent_work_rank90_mm_4x5x6":
            issues.append(MatrixRowNoteIssue("invalid_note_id", "row-note note_id must identify the mm_4x5x6 concurrent-work note", safe_id))
        else:
            required_seen = True
        if safe_id in seen:
            issues.append(MatrixRowNoteIssue("duplicate_note_id", "row note ids must be unique", safe_id))
        if safe_id is not None:
            seen.add(safe_id)
        if note.get("note_type") == "concurrent_work":
            concurrent_count += 1
        _validate_concurrent_work_row_note(note, safe_id, issues)
        target_id = note.get("target_id")
        if isinstance(target_id, str):
            affected_targets.add(target_id)
    if not required_seen:
        issues.append(MatrixRowNoteIssue("missing_concurrent_work_note", "mm_4x5x6 concurrent-work note is required"))
    return len(value), concurrent_count, len(affected_targets)


def _validate_concurrent_work_row_note(
    note: dict[str, Any],
    note_id: str | None,
    issues: list[MatrixRowNoteIssue],
) -> None:
    target = matrix_target_by_id("mm_4x5x6")
    if note.get("note_type") != "concurrent_work":
        issues.append(MatrixRowNoteIssue("invalid_note_type", "mm_4x5x6 note_type must be concurrent_work", note_id))
    if note.get("target_id") != "mm_4x5x6":
        issues.append(MatrixRowNoteIssue("invalid_note_target_id", "concurrent-work note must target mm_4x5x6", note_id))
    if note.get("dimensions") != [4, 5, 6]:
        issues.append(MatrixRowNoteIssue("invalid_note_dimensions", "concurrent-work note dimensions must be [4, 5, 6]", note_id))
    if isinstance(target, dict):
        if note.get("alphaevolve_rank") != target.get("alphaevolve_rank"):
            issues.append(MatrixRowNoteIssue("alphaevolve_rank_mismatch", "row note alphaevolve_rank must match registry", note_id))
        if target.get("outcome") != "surpassed":
            issues.append(MatrixRowNoteIssue("target_outcome_mismatch", "mm_4x5x6 registry row must remain surpassed", note_id))
    if note.get("concurrent_rank") != 90:
        issues.append(MatrixRowNoteIssue("invalid_concurrent_rank", "concurrent work rank must be 90", note_id))
    if note.get("cited_reference_id") != "49":
        issues.append(MatrixRowNoteIssue("invalid_cited_reference_id", "concurrent-work note must cite reference id 49", note_id))
    if note.get("relationship_to_alphaevolve") != "independently_matched_alphaevolve_rank":
        issues.append(MatrixRowNoteIssue("invalid_relationship", "relationship must mark independent match of AlphaEvolve rank", note_id))
    if note.get("source_table") != "Appendix A Table 3":
        issues.append(MatrixRowNoteIssue("invalid_source_table", "row note must link to Appendix A Table 3", note_id))
    if note.get("source_pdf_page") != 34:
        issues.append(MatrixRowNoteIssue("invalid_note_source_pdf_page", "row note source_pdf_page must be 34", note_id))
    note_text = note.get("note_text")
    if not isinstance(note_text, str) or not note_text.strip():
        issues.append(MatrixRowNoteIssue("missing_note_text", "row note text is required", note_id))
    else:
        if "Concurrent work [49]" not in note_text or "rank-90" not in note_text or "<4, 5, 6>" not in note_text:
            issues.append(MatrixRowNoteIssue("missing_concurrent_note_text", "row note text must preserve concurrent work, reference, rank, and target wording", note_id))
    if note.get("exclusive_priority_claim_safe") is not False:
        issues.append(MatrixRowNoteIssue("invalid_exclusive_priority_flag", "concurrent-work notes must mark exclusive priority claims unsafe", note_id))
    docs_caveat = note.get("docs_caveat")
    if not isinstance(docs_caveat, str) or not docs_caveat.strip():
        issues.append(MatrixRowNoteIssue("missing_docs_caveat", "row note must include a docs caveat", note_id))
    else:
        lowered = docs_caveat.lower()
        if "exclusive" not in lowered or "concurrent work [49]" not in docs_caveat:
            issues.append(MatrixRowNoteIssue("missing_exclusive_priority_caveat", "docs caveat must warn against exclusive priority claims and cite concurrent work [49]", note_id))


def _validate_frontier_observations(
    value: object,
    issues: list[MatrixResourceFrontierIssue],
) -> tuple[int, int]:
    if not isinstance(value, list):
        issues.append(MatrixResourceFrontierIssue("invalid_frontier_observations", "frontier_observations must be a list"))
        return 0, 0
    seen: set[str] = set()
    artifact_count = 0
    for observation in value:
        if not isinstance(observation, dict):
            issues.append(MatrixResourceFrontierIssue("invalid_frontier_observation", "frontier observation must be an object"))
            continue
        attempt_id = observation.get("attempt_id")
        safe_id = attempt_id if isinstance(attempt_id, str) else None
        if safe_id != "paper_beyond_5x5x5_single_gpu_1000_seeds":
            issues.append(MatrixResourceFrontierIssue("invalid_attempt_id", "attempt_id must identify the Appendix A larger-target boundary", safe_id))
            continue
        if safe_id in seen:
            issues.append(MatrixResourceFrontierIssue("duplicate_attempt_id", "frontier observation attempt_id values must be unique", safe_id))
        seen.add(safe_id)
        if observation.get("target_scope") != "sizes_beyond_5x5x5":
            issues.append(MatrixResourceFrontierIssue("invalid_target_scope", "target_scope must be sizes_beyond_5x5x5", safe_id))
        if observation.get("seed_count") != 1000:
            issues.append(MatrixResourceFrontierIssue("invalid_seed_count", "seed_count must preserve the paper's 1000 random seed statement", safe_id))
        if observation.get("accelerator_profile") != "single_gpu_accelerator":
            issues.append(MatrixResourceFrontierIssue("invalid_accelerator_profile", "accelerator_profile must preserve the single GPU accelerator statement", safe_id))
        if observation.get("resource_status") != "often_out_of_memory":
            issues.append(MatrixResourceFrontierIssue("invalid_resource_status", "resource_status must preserve the out-of-memory observation", safe_id))
        if observation.get("extension_requirement") != "further_optimization_required":
            issues.append(MatrixResourceFrontierIssue("invalid_extension_requirement", "extension_requirement must preserve the further-optimization statement", safe_id))
        source_phrase = observation.get("source_phrase")
        if (
            not isinstance(source_phrase, str)
            or "beyond <5,5,5>" not in source_phrase
            or "1000 random seeds" not in source_phrase
            or "single GPU accelerator" not in source_phrase
            or "out of memory" not in source_phrase
        ):
            issues.append(MatrixResourceFrontierIssue("missing_source_phrase", "source_phrase must preserve target, seed, GPU, and OOM wording", safe_id))
        local_execution = observation.get("local_execution_evidence")
        local_artifacts = observation.get("local_artifacts")
        if local_execution is not False:
            issues.append(MatrixResourceFrontierIssue("local_execution_overclaim", "paper-only frontier observations must not claim local execution evidence", safe_id))
        if not isinstance(local_artifacts, list):
            issues.append(MatrixResourceFrontierIssue("invalid_local_artifacts", "local_artifacts must be a list", safe_id))
        else:
            artifact_count += len(local_artifacts)
            if local_artifacts:
                issues.append(MatrixResourceFrontierIssue("unexpected_local_artifacts", "paper-only frontier observations must not declare local artifacts", safe_id))
    if "paper_beyond_5x5x5_single_gpu_1000_seeds" not in seen:
        issues.append(MatrixResourceFrontierIssue("missing_frontier_observation", "Appendix A larger-target OOM observation is required"))
    return len(value), artifact_count


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
