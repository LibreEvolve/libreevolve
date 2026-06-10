from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path
from typing import Any


REGISTRY_PATH = Path(__file__).with_name("alphaevolve_appendix_a_matrix.json")
REGISTRY_SCHEMA = "libreevolve.alphaevolve_appendix_a_matrix_registry.v1"
CURATION_SCHEMA = "libreevolve.alphaevolve_appendix_a_matrix_curation.v1"
EXCLUDED_TARGET_CURATION_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_appendix_a_matrix_excluded_target_curation_boundary.v1"
BASELINE_CITATION_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_appendix_a_matrix_baseline_citation_boundary.v1"
RESOURCE_FRONTIER_SCHEMA = "libreevolve.alphaevolve_appendix_a_matrix_resource_frontier.v1"
LOCAL_RESOURCE_FRONTIER_SCHEMA = "libreevolve.alphaevolve_appendix_a_matrix_local_resource_frontier.v1"
SUBSET_SCOPE_SCHEMA = "libreevolve.alphaevolve_matrix_subset_scope.v1"
SUBSET_SCOPE_ARTIFACT_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_matrix_subset_scope_artifact_boundary.v1"
ROW_NOTE_SCHEMA = "libreevolve.alphaevolve_appendix_a_matrix_row_notes.v1"
ROW_NOTE_ARTIFACT_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_appendix_a_matrix_row_note_artifact_boundary.v1"
TARGET_SUITE = "alphaevolve_appendix_a"
EXPECTED_TARGET_COUNT = 54
OUTCOMES = frozenset({"matched", "surpassed", "fell_behind"})
EXCLUDED_TARGET_CURATION_STATUSES = frozenset({"not_recorded_locally", "recorded"})
EXCLUDED_TARGET_CURATION_REQUIRED_FIELDS = (
    "excluded_target_id",
    "dimensions",
    "canonical_order",
    "exclusion_class",
    "exclusion_reason",
    "source_basis",
    "source_pdf_page",
    "rough_rule_relation",
    "p_cutoff_relation",
    "symmetry_equivalence_status",
    "local_attempt_ref",
    "resource_frontier_ref",
    "artifact_paths",
    "artifact_sha256",
)
EXCLUDED_TARGET_CURATION_CLASSES = frozenset(
    {
        "outside_rough_mn_rule",
        "beyond_unspecified_p_cutoff",
        "resource_frontier_excluded",
        "not_selected_by_paper_curation",
    }
)
BASELINE_CITATION_STATUSES = frozenset({"not_recorded_locally", "recorded"})
BASELINE_CITATION_REQUIRED_FIELDS = (
    "target_id",
    "dimensions",
    "best_known_rank",
    "cited_reference_id",
    "source_table",
    "source_pdf_page",
    "source_artifact_path",
    "source_artifact_sha256",
    "applicability_caveats",
    "finite_field_or_characteristic_scope",
    "report_baseline_source_ref",
)
SUBSET_SCOPE_ARTIFACT_STATUSES = frozenset({"not_emitted_by_local_report_export", "emitted"})
SUBSET_SCOPE_ARTIFACT_REQUIRED_FIELDS = (
    "subset_scope_id",
    "source_table",
    "source_pdf_page",
    "source_phrase",
    "inclusion_predicate",
    "row_count",
    "outcome_counts",
    "out_of_scope_target_ids",
    "fell_behind_target_ids",
    "subset_scope_evidence",
    "artifact_paths",
    "artifact_sha256",
)
ROW_NOTE_ARTIFACT_STATUSES = frozenset({"not_emitted_by_local_report_export", "emitted"})
ROW_NOTE_ARTIFACT_REQUIRED_FIELDS = (
    "note_id",
    "note_type",
    "target_id",
    "dimensions",
    "alphaevolve_rank",
    "concurrent_rank",
    "cited_reference_id",
    "relationship_to_alphaevolve",
    "source_table",
    "source_pdf_page",
    "note_text",
    "exclusive_priority_claim_safe",
    "docs_caveat",
    "row_note_evidence",
    "artifact_paths",
    "artifact_sha256",
)
_ID_RE = re.compile(r"mm_[1-9][0-9]*x[1-9][0-9]*x[1-9][0-9]*")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
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
class MatrixExcludedTargetCurationBoundaryReport:
    ok: bool
    curation_status: str | None
    excluded_target_count: int
    required_field_count: int
    issues: list[MatrixTargetCurationIssue]


@dataclass(frozen=True)
class MatrixBaselineCitationBoundaryReport:
    ok: bool
    citation_status: str | None
    citation_count: int
    required_field_count: int
    issues: list[MatrixTargetIssue]


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
class MatrixSubsetScopeArtifactBoundaryReport:
    ok: bool
    artifact_status: str | None
    emitted_artifact_count: int
    required_field_count: int
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


@dataclass(frozen=True)
class MatrixRowNoteArtifactBoundaryReport:
    ok: bool
    artifact_status: str | None
    emitted_artifact_count: int
    required_field_count: int
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


def appendix_a_matrix_excluded_target_curation_boundary_record() -> dict[str, Any]:
    return {
        "schema": EXCLUDED_TARGET_CURATION_BOUNDARY_SCHEMA,
        "curation_schema": CURATION_SCHEMA,
        "source_paper_id": "2506.13131",
        "source_section": "AlphaEvolve Appendix A",
        "source_pdf_page": 34,
        "target_suite": TARGET_SUITE,
        "curation_status": "not_recorded_locally",
        "required_excluded_target_fields": list(EXCLUDED_TARGET_CURATION_REQUIRED_FIELDS),
        "excluded_non_equivalent_targets": [],
        "coverage_policy": {
            "status": "not_exhaustive",
            "boundary": (
                "Appendix A gives rough size-selection wording and an "
                "unspecified p cutoff, but local metadata does not enumerate "
                "or justify every excluded non-equivalent matrix target."
            ),
        },
        "claim_boundary": (
            "This is an excluded-target curation boundary. It does not claim "
            "local metadata justifies every non-equivalent matrix size that is "
            "outside the reported Appendix A target suite."
        ),
    }


def appendix_a_matrix_excluded_target_curation_boundary_from_records(
    excluded_targets: list[dict[str, Any]],
    *,
    coverage_status: str = "partial_with_scope",
    coverage_scope: str,
) -> dict[str, Any]:
    """Build a recorded excluded-target curation boundary."""
    boundary = appendix_a_matrix_excluded_target_curation_boundary_record()
    boundary.update(
        {
            "curation_status": "recorded",
            "excluded_non_equivalent_targets": copy.deepcopy(excluded_targets),
            "coverage_policy": {
                "status": coverage_status,
                "scope": coverage_scope,
            },
            "claim_boundary": (
                "Recorded metadata justifies excluded non-equivalent Appendix "
                "A matrix targets for the declared coverage scope; this does "
                "not claim local metadata exhaustively covers every possible "
                "larger matrix target unless coverage_policy says so."
            ),
        }
    )
    report = validate_appendix_a_matrix_excluded_target_curation_boundary(boundary)
    if not report.ok:
        messages = "; ".join(issue.message for issue in report.issues)
        raise ValueError(f"excluded-target curation boundary is invalid: {messages}")
    return boundary


def validate_appendix_a_matrix_excluded_target_curation_boundary(
    boundary: object | str | Path | None = None,
) -> MatrixExcludedTargetCurationBoundaryReport:
    if boundary is None:
        boundary = appendix_a_matrix_excluded_target_curation_boundary_record()
    data, read_issues = _load_excluded_target_curation_boundary(boundary)
    if read_issues:
        return MatrixExcludedTargetCurationBoundaryReport(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixTargetCurationIssue] = []
    if data.get("schema") != EXCLUDED_TARGET_CURATION_BOUNDARY_SCHEMA:
        issues.append(MatrixTargetCurationIssue("invalid_schema", "unsupported Appendix A matrix excluded-target curation boundary schema"))
    if data.get("curation_schema") != CURATION_SCHEMA:
        issues.append(MatrixTargetCurationIssue("invalid_curation_schema", "curation_schema must identify Appendix A matrix curation records"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(MatrixTargetCurationIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section") != "AlphaEvolve Appendix A":
        issues.append(MatrixTargetCurationIssue("invalid_source_section", "source_section must be AlphaEvolve Appendix A"))
    if data.get("source_pdf_page") != 34:
        issues.append(MatrixTargetCurationIssue("invalid_source_pdf_page", "source_pdf_page must identify page 34"))
    if data.get("target_suite") != TARGET_SUITE:
        issues.append(MatrixTargetCurationIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    status = data.get("curation_status")
    if status not in EXCLUDED_TARGET_CURATION_STATUSES:
        issues.append(MatrixTargetCurationIssue("invalid_curation_status", "curation_status must be a known excluded-target curation status"))
    required_field_count = _validate_excluded_target_required_fields(data.get("required_excluded_target_fields"), issues)
    _validate_excluded_target_coverage_policy(data.get("coverage_policy"), status, issues)
    excluded_targets = data.get("excluded_non_equivalent_targets")
    if not isinstance(excluded_targets, list):
        issues.append(MatrixTargetCurationIssue("invalid_excluded_non_equivalent_targets", "excluded_non_equivalent_targets must be a list"))
        excluded_count = 0
    else:
        excluded_count = len(excluded_targets)
        if status == "not_recorded_locally":
            if excluded_targets:
                issues.append(MatrixTargetCurationIssue("unexpected_excluded_targets", "absence boundary must not include excluded non-equivalent target records"))
            claim_boundary = data.get("claim_boundary")
            if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary:
                issues.append(MatrixTargetCurationIssue("missing_claim_boundary", "absence boundary must state that it does not claim local excluded-target justifications"))
        elif status == "recorded":
            if not excluded_targets:
                issues.append(MatrixTargetCurationIssue("missing_excluded_targets", "recorded status requires excluded non-equivalent target records"))
            _validate_excluded_target_records(excluded_targets, issues)
    return MatrixExcludedTargetCurationBoundaryReport(
        ok=not issues,
        curation_status=status if isinstance(status, str) else None,
        excluded_target_count=excluded_count,
        required_field_count=required_field_count,
        issues=issues,
    )


def appendix_a_matrix_baseline_citation_boundary_record() -> dict[str, Any]:
    return {
        "schema": BASELINE_CITATION_BOUNDARY_SCHEMA,
        "registry_schema": REGISTRY_SCHEMA,
        "source_paper_id": "2506.13131",
        "target_suite": TARGET_SUITE,
        "citation_status": "not_recorded_locally",
        "required_citation_fields": list(BASELINE_CITATION_REQUIRED_FIELDS),
        "baseline_citations": [],
        "claim_boundary": (
            "This is an Appendix A matrix best-known-rank citation boundary. "
            "It does not claim local metadata records the cited prior-work "
            "source behind each best-known rank."
        ),
    }


def appendix_a_matrix_baseline_citation_boundary_from_citations(
    citations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a recorded Appendix A baseline-citation boundary."""
    boundary = appendix_a_matrix_baseline_citation_boundary_record()
    boundary.update(
        {
            "citation_status": "recorded",
            "baseline_citations": copy.deepcopy(citations),
            "claim_boundary": (
                "Recorded metadata links each Appendix A matrix target to the "
                "cited prior-work source behind its best-known-rank baseline."
            ),
        }
    )
    report = validate_appendix_a_matrix_baseline_citation_boundary(boundary)
    if not report.ok:
        messages = "; ".join(issue.message for issue in report.issues)
        raise ValueError(f"baseline citation boundary is invalid: {messages}")
    return boundary


def validate_appendix_a_matrix_baseline_citation_boundary(
    boundary: object | str | Path | None = None,
) -> MatrixBaselineCitationBoundaryReport:
    if boundary is None:
        boundary = appendix_a_matrix_baseline_citation_boundary_record()
    data, read_issues = _load_baseline_citation_boundary(boundary)
    if read_issues:
        return MatrixBaselineCitationBoundaryReport(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixTargetIssue] = []
    if data.get("schema") != BASELINE_CITATION_BOUNDARY_SCHEMA:
        issues.append(MatrixTargetIssue("invalid_schema", "unsupported Appendix A matrix baseline-citation boundary schema"))
    if data.get("registry_schema") != REGISTRY_SCHEMA:
        issues.append(MatrixTargetIssue("invalid_registry_schema", "registry_schema must identify Appendix A matrix registry records"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(MatrixTargetIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("target_suite") != TARGET_SUITE:
        issues.append(MatrixTargetIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    status = data.get("citation_status")
    if status not in BASELINE_CITATION_STATUSES:
        issues.append(MatrixTargetIssue("invalid_citation_status", "citation_status must be a known baseline-citation status"))
    required_field_count = _validate_baseline_citation_required_fields(data.get("required_citation_fields"), issues)
    citations = data.get("baseline_citations")
    if not isinstance(citations, list):
        issues.append(MatrixTargetIssue("invalid_baseline_citations", "baseline_citations must be a list"))
        citation_count = 0
    else:
        citation_count = len(citations)
        if status == "not_recorded_locally":
            if citations:
                issues.append(MatrixTargetIssue("unexpected_baseline_citations", "absence boundary must not include baseline citation records"))
            boundary_text = data.get("claim_boundary")
            if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
                issues.append(MatrixTargetIssue("missing_claim_boundary", "absence boundary must state that it does not claim local baseline-citation metadata"))
        elif status == "recorded":
            if len(citations) != EXPECTED_TARGET_COUNT:
                issues.append(MatrixTargetIssue("missing_baseline_citations", "recorded status requires one baseline citation for each Appendix A matrix target"))
            _validate_baseline_citation_records(citations, issues)
    return MatrixBaselineCitationBoundaryReport(
        ok=not issues,
        citation_status=status if isinstance(status, str) else None,
        citation_count=citation_count,
        required_field_count=required_field_count,
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


def appendix_a_matrix_local_resource_frontier_record() -> dict[str, Any]:
    return {
        "schema": LOCAL_RESOURCE_FRONTIER_SCHEMA,
        "source_paper_id": "2506.13131",
        "target_suite": TARGET_SUITE,
        "paper_frontier_observation_ref": "paper_beyond_5x5x5_single_gpu_1000_seeds",
        "local_frontier_status": "not_executed_locally",
        "required_attempt_fields": [
            "target_id",
            "dimensions",
            "seed_count",
            "accelerator_profile",
            "gpu_memory_bytes",
            "resource_status",
            "oom_or_exhaustion_diagnostics",
            "reduced_seed_policy",
            "artifact_paths",
            "artifact_sha256",
        ],
        "local_attempts": [],
        "excluded_target_policy": {
            "status": "not_defined",
            "boundary": (
                "No local larger-target matrix scaling attempts, attempted-versus-excluded "
                "target identities, measured GPU memory profiles, OOM diagnostics, or "
                "reduced-seed tradeoffs have been recorded."
            ),
        },
        "claim_boundary": (
            "This is a local absence/readiness boundary. It does not claim that "
            "LibreEvolve has reproduced AlphaEvolve's larger-target OOM/resource frontier."
        ),
    }


def appendix_a_matrix_local_resource_frontier_from_attempts(
    local_attempts: list[dict[str, Any]],
    *,
    excluded_target_policy_status: str = "defined",
    excluded_target_policy_boundary: str | None = None,
) -> dict[str, Any]:
    """Build a recorded local resource-frontier boundary from attempts."""
    boundary = appendix_a_matrix_local_resource_frontier_record()
    policy_boundary = (
        excluded_target_policy_boundary
        if excluded_target_policy_boundary is not None
        else (
            "No local larger-target matrix scaling attempts are excluded from "
            "the declared local attempt policy; recorded attempts are limited "
            "to the supplied rows."
        )
    )
    boundary.update(
        {
            "local_frontier_status": "attempts_recorded",
            "local_attempts": copy.deepcopy(local_attempts),
            "excluded_target_policy": {
                "status": excluded_target_policy_status,
                "boundary": policy_boundary,
            },
            "claim_boundary": (
                "Recorded local attempts preserve larger-target matrix "
                "resource-frontier diagnostics for the supplied rows; this "
                "does not claim LibreEvolve reproduced AlphaEvolve's full "
                "Appendix A OOM/resource frontier."
            ),
        }
    )
    report = validate_appendix_a_matrix_local_resource_frontier(boundary)
    if not report.ok:
        messages = "; ".join(issue.message for issue in report.issues)
        raise ValueError(f"local matrix resource-frontier boundary is invalid: {messages}")
    return boundary


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


def appendix_a_matrix_subset_scope_artifact_boundary_record() -> dict[str, Any]:
    return {
        "schema": SUBSET_SCOPE_ARTIFACT_BOUNDARY_SCHEMA,
        "subset_scope_schema": SUBSET_SCOPE_SCHEMA,
        "source_paper_id": "2506.13131",
        "target_suite": TARGET_SUITE,
        "artifact_status": "not_emitted_by_local_report_export",
        "local_export_scope": "matrix_subset_scope_report_export",
        "required_artifact_fields": list(SUBSET_SCOPE_ARTIFACT_REQUIRED_FIELDS),
        "emitted_artifacts": [],
        "claim_boundary": (
            "This is a matrix subset-scope artifact availability boundary. "
            "It does not claim local report/export code emits named "
            "Appendix A, Table 2, or m,n,p <= 5 subset-scope artifacts."
        ),
    }


def appendix_a_matrix_subset_scope_artifact_boundary_from_records(
    recordset: dict[str, Any] | None = None,
    *,
    artifact_paths_by_subset_id: dict[str, list[str]] | None = None,
    artifact_sha256_by_subset_id: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build emitted subset-scope artifacts from validated subset evidence."""
    subset_scope_evidence = (
        appendix_a_matrix_subset_scope_record()
        if recordset is None
        else copy.deepcopy(recordset)
    )
    subset_report = validate_appendix_a_matrix_subset_scope(subset_scope_evidence)
    if not subset_report.ok:
        messages = "; ".join(issue.message for issue in subset_report.issues)
        raise ValueError(f"subset-scope evidence is invalid: {messages}")
    artifacts: list[dict[str, Any]] = []
    subsets = subset_scope_evidence.get("subsets", [])
    assert isinstance(subsets, list)
    for subset in subsets:
        assert isinstance(subset, dict)
        subset_id = subset["subset_id"]
        paths = (
            artifact_paths_by_subset_id.get(subset_id)
            if artifact_paths_by_subset_id is not None
            else None
        )
        artifact_paths = (
            copy.deepcopy(paths)
            if paths is not None
            else [f"tables/{subset_id}_subset_scope.json"]
        )
        artifact_payload = {
            "subset_scope_id": subset_id,
            "source_table": subset["source_table"],
            "source_pdf_page": subset["source_pdf_page"],
            "source_phrase": subset["source_phrase"],
            "inclusion_predicate": subset["inclusion_predicate"],
            "row_count": subset["row_count"],
            "outcome_counts": copy.deepcopy(subset["outcome_counts"]),
            "out_of_scope_target_ids": copy.deepcopy(
                subset["out_of_scope_target_ids"]
            ),
            "fell_behind_target_ids": copy.deepcopy(
                subset["fell_behind_target_ids"]
            ),
            "subset_scope_evidence": copy.deepcopy(subset_scope_evidence),
            "artifact_paths": artifact_paths,
        }
        artifact_hash = (
            artifact_sha256_by_subset_id.get(subset_id)
            if artifact_sha256_by_subset_id is not None
            else None
        )
        artifact_payload["artifact_sha256"] = (
            artifact_hash
            if artifact_hash is not None
            else _stable_json_sha256(artifact_payload)
        )
        artifacts.append(artifact_payload)
    boundary = appendix_a_matrix_subset_scope_artifact_boundary_record()
    boundary.update(
        {
            "artifact_status": "emitted",
            "emitted_artifacts": artifacts,
            "claim_boundary": (
                "Emitted artifacts preserve Appendix A, Table 2, and "
                "m,n,p <= 5 matrix subset-scope evidence; this still does "
                "not claim local report/export code emits them."
            ),
        }
    )
    boundary_report = validate_appendix_a_matrix_subset_scope_artifact_boundary(
        boundary
    )
    if not boundary_report.ok:
        messages = "; ".join(issue.message for issue in boundary_report.issues)
        raise ValueError(f"subset-scope artifact boundary is invalid: {messages}")
    return boundary


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


def validate_appendix_a_matrix_subset_scope_artifact_boundary(
    boundary: object | str | Path | None = None,
) -> MatrixSubsetScopeArtifactBoundaryReport:
    if boundary is None:
        boundary = appendix_a_matrix_subset_scope_artifact_boundary_record()
    data, read_issues = _load_subset_scope_artifact_boundary(boundary)
    if read_issues:
        return MatrixSubsetScopeArtifactBoundaryReport(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixSubsetScopeIssue] = []
    if data.get("schema") != SUBSET_SCOPE_ARTIFACT_BOUNDARY_SCHEMA:
        issues.append(MatrixSubsetScopeIssue("invalid_schema", "unsupported matrix subset-scope artifact boundary schema"))
    if data.get("subset_scope_schema") != SUBSET_SCOPE_SCHEMA:
        issues.append(MatrixSubsetScopeIssue("invalid_subset_scope_schema", "subset_scope_schema must identify matrix subset-scope evidence"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(MatrixSubsetScopeIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("target_suite") != TARGET_SUITE:
        issues.append(MatrixSubsetScopeIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    status = data.get("artifact_status")
    if status not in SUBSET_SCOPE_ARTIFACT_STATUSES:
        issues.append(MatrixSubsetScopeIssue("invalid_artifact_status", "artifact_status must be a known matrix subset-scope artifact status"))
    if not isinstance(data.get("local_export_scope"), str) or not data["local_export_scope"].strip():
        issues.append(MatrixSubsetScopeIssue("missing_local_export_scope", "local_export_scope is required"))
    required_field_count = _validate_subset_scope_artifact_required_fields(data.get("required_artifact_fields"), issues)
    artifacts = data.get("emitted_artifacts")
    if not isinstance(artifacts, list):
        issues.append(MatrixSubsetScopeIssue("invalid_emitted_artifacts", "emitted_artifacts must be a list"))
        artifact_count = 0
    else:
        artifact_count = len(artifacts)
        if status == "not_emitted_by_local_report_export":
            if artifacts:
                issues.append(MatrixSubsetScopeIssue("unexpected_emitted_artifacts", "absence boundary must not include emitted subset-scope artifacts"))
            claim_boundary = data.get("claim_boundary")
            if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary:
                issues.append(MatrixSubsetScopeIssue("missing_claim_boundary", "absence boundary must state that it does not claim local subset-scope artifact emission"))
        elif status == "emitted":
            if not artifacts:
                issues.append(MatrixSubsetScopeIssue("missing_subset_scope_artifacts", "emitted status requires matrix subset-scope artifact records"))
            for artifact in artifacts:
                _validate_subset_scope_artifact_record(artifact, issues)
    return MatrixSubsetScopeArtifactBoundaryReport(
        ok=not issues,
        artifact_status=status if isinstance(status, str) else None,
        emitted_artifact_count=artifact_count,
        required_field_count=required_field_count,
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


def appendix_a_matrix_row_note_artifact_boundary_record() -> dict[str, Any]:
    return {
        "schema": ROW_NOTE_ARTIFACT_BOUNDARY_SCHEMA,
        "row_note_schema": ROW_NOTE_SCHEMA,
        "source_paper_id": "2506.13131",
        "target_suite": TARGET_SUITE,
        "artifact_status": "not_emitted_by_local_report_export",
        "local_export_scope": "matrix_row_note_report_export",
        "required_artifact_fields": list(ROW_NOTE_ARTIFACT_REQUIRED_FIELDS),
        "emitted_artifacts": [],
        "claim_boundary": (
            "This is an Appendix A matrix row-note artifact availability "
            "boundary. It does not claim local report/export code emits the "
            "mm_4x5x6 concurrent-work caveat artifact."
        ),
    }


def appendix_a_matrix_row_note_artifact_boundary_from_records(
    recordset: dict[str, Any] | None = None,
    *,
    artifact_paths_by_note_id: dict[str, list[str]] | None = None,
    artifact_sha256_by_note_id: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build an emitted row-note artifact boundary from row-note evidence."""
    row_note_evidence = (
        appendix_a_matrix_row_note_records()
        if recordset is None
        else copy.deepcopy(recordset)
    )
    note_report = validate_appendix_a_matrix_row_notes(row_note_evidence)
    if not note_report.ok:
        messages = "; ".join(issue.message for issue in note_report.issues)
        raise ValueError(f"row-note evidence is invalid: {messages}")
    artifacts: list[dict[str, Any]] = []
    notes = row_note_evidence.get("row_notes", [])
    assert isinstance(notes, list)
    for note in notes:
        assert isinstance(note, dict)
        note_id = note["note_id"]
        target_id = note["target_id"]
        paths = (
            artifact_paths_by_note_id.get(note_id)
            if artifact_paths_by_note_id is not None
            else None
        )
        artifact_paths = (
            copy.deepcopy(paths)
            if paths is not None
            else [f"tables/{target_id}_row_note.json"]
        )
        artifact_payload = {
            **copy.deepcopy(note),
            "row_note_evidence": copy.deepcopy(row_note_evidence),
            "artifact_paths": artifact_paths,
        }
        artifact_hash = (
            artifact_sha256_by_note_id.get(note_id)
            if artifact_sha256_by_note_id is not None
            else None
        )
        artifact_payload["artifact_sha256"] = (
            artifact_hash
            if artifact_hash is not None
            else _stable_json_sha256(artifact_payload)
        )
        artifacts.append(artifact_payload)
    boundary = appendix_a_matrix_row_note_artifact_boundary_record()
    boundary.update(
        {
            "artifact_status": "emitted",
            "emitted_artifacts": artifacts,
            "claim_boundary": (
                "Emitted artifacts preserve Appendix A matrix row-note caveats "
                "and link each artifact back to validated row-note evidence; "
                "this still does not claim local report/export code emits them."
            ),
        }
    )
    boundary_report = validate_appendix_a_matrix_row_note_artifact_boundary(boundary)
    if not boundary_report.ok:
        messages = "; ".join(issue.message for issue in boundary_report.issues)
        raise ValueError(f"row-note artifact boundary is invalid: {messages}")
    return boundary


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


def validate_appendix_a_matrix_row_note_artifact_boundary(
    boundary: object | str | Path | None = None,
) -> MatrixRowNoteArtifactBoundaryReport:
    if boundary is None:
        boundary = appendix_a_matrix_row_note_artifact_boundary_record()
    data, read_issues = _load_row_note_artifact_boundary(boundary)
    if read_issues:
        return MatrixRowNoteArtifactBoundaryReport(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixRowNoteIssue] = []
    if data.get("schema") != ROW_NOTE_ARTIFACT_BOUNDARY_SCHEMA:
        issues.append(MatrixRowNoteIssue("invalid_schema", "unsupported Appendix A matrix row-note artifact boundary schema"))
    if data.get("row_note_schema") != ROW_NOTE_SCHEMA:
        issues.append(MatrixRowNoteIssue("invalid_row_note_schema", "row_note_schema must identify Appendix A matrix row-note evidence"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(MatrixRowNoteIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("target_suite") != TARGET_SUITE:
        issues.append(MatrixRowNoteIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    status = data.get("artifact_status")
    if status not in ROW_NOTE_ARTIFACT_STATUSES:
        issues.append(MatrixRowNoteIssue("invalid_artifact_status", "artifact_status must be a known matrix row-note artifact status"))
    if not isinstance(data.get("local_export_scope"), str) or not data["local_export_scope"].strip():
        issues.append(MatrixRowNoteIssue("missing_local_export_scope", "local_export_scope is required"))
    required_field_count = _validate_row_note_artifact_required_fields(data.get("required_artifact_fields"), issues)
    artifacts = data.get("emitted_artifacts")
    if not isinstance(artifacts, list):
        issues.append(MatrixRowNoteIssue("invalid_emitted_artifacts", "emitted_artifacts must be a list"))
        artifact_count = 0
    else:
        artifact_count = len(artifacts)
        if status == "not_emitted_by_local_report_export":
            if artifacts:
                issues.append(MatrixRowNoteIssue("unexpected_emitted_artifacts", "absence boundary must not include emitted row-note artifacts"))
            claim_boundary = data.get("claim_boundary")
            if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary:
                issues.append(MatrixRowNoteIssue("missing_claim_boundary", "absence boundary must state that it does not claim local row-note artifact emission"))
        elif status == "emitted":
            if not artifacts:
                issues.append(MatrixRowNoteIssue("missing_row_note_artifacts", "emitted status requires Appendix A matrix row-note artifact records"))
            for artifact in artifacts:
                _validate_row_note_artifact_record(artifact, issues)
    return MatrixRowNoteArtifactBoundaryReport(
        ok=not issues,
        artifact_status=status if isinstance(status, str) else None,
        emitted_artifact_count=artifact_count,
        required_field_count=required_field_count,
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


def validate_appendix_a_matrix_local_resource_frontier(
    recordset: object | str | Path | None = None,
) -> MatrixResourceFrontierReport:
    data, read_issues = _load_resource_frontier_recordset(recordset)
    if read_issues:
        return MatrixResourceFrontierReport(False, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixResourceFrontierIssue] = []
    if data.get("schema") != LOCAL_RESOURCE_FRONTIER_SCHEMA:
        issues.append(MatrixResourceFrontierIssue("invalid_schema", "unsupported local Appendix A matrix resource-frontier schema"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(MatrixResourceFrontierIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("target_suite") != TARGET_SUITE:
        issues.append(MatrixResourceFrontierIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    if data.get("paper_frontier_observation_ref") != "paper_beyond_5x5x5_single_gpu_1000_seeds":
        issues.append(MatrixResourceFrontierIssue("invalid_paper_frontier_ref", "local frontier record must link the paper-only OOM observation"))
    required_fields = data.get("required_attempt_fields")
    if (
        not isinstance(required_fields, list)
        or not required_fields
        or not all(isinstance(field, str) and field.strip() for field in required_fields)
    ):
        issues.append(MatrixResourceFrontierIssue("invalid_required_attempt_fields", "required_attempt_fields must be a non-empty string list"))
    status = data.get("local_frontier_status")
    if status not in {"not_executed_locally", "attempts_recorded"}:
        issues.append(MatrixResourceFrontierIssue("invalid_local_frontier_status", "local_frontier_status must be not_executed_locally or attempts_recorded"))
    attempt_count, artifact_count = _validate_local_frontier_attempts(data.get("local_attempts"), status, issues)
    _validate_excluded_target_policy(data.get("excluded_target_policy"), status, issues)
    claim_boundary = data.get("claim_boundary")
    if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary:
        issues.append(MatrixResourceFrontierIssue("missing_claim_boundary", "claim_boundary must state that local OOM/resource-frontier reproduction is not claimed"))
    return MatrixResourceFrontierReport(
        ok=not issues,
        attempted_scope_count=attempt_count,
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


def render_appendix_a_matrix_excluded_target_curation_boundary_summary(
    boundary: object | str | Path | None = None,
) -> str:
    report = validate_appendix_a_matrix_excluded_target_curation_boundary(boundary)
    status = "ok" if report.ok else "invalid"
    lines = [
        "AlphaEvolve Appendix A matrix excluded-target curation boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| curation_status | {report.curation_status or '<unknown>'} |",
        f"| excluded_target_count | {report.excluded_target_count} |",
        f"| required_field_count | {report.required_field_count} |",
    ]
    if report.issues:
        lines.extend(["", "Issues:"])
        lines.extend(
            f"- {issue.code}: {issue.message}"
            + (f" ({issue.target_id})" if issue.target_id else "")
            for issue in report.issues
        )
    return "\n".join(lines)


def render_appendix_a_matrix_baseline_citation_boundary_summary(
    boundary: object | str | Path | None = None,
) -> str:
    report = validate_appendix_a_matrix_baseline_citation_boundary(boundary)
    status = "ok" if report.ok else "invalid"
    lines = [
        "AlphaEvolve Appendix A matrix baseline-citation boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| citation_status | {report.citation_status or '<unknown>'} |",
        f"| citation_count | {report.citation_count} |",
        f"| required_field_count | {report.required_field_count} |",
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


def render_appendix_a_matrix_local_resource_frontier_summary(
    recordset: object | str | Path | None = None,
) -> str:
    report = validate_appendix_a_matrix_local_resource_frontier(recordset)
    data, _ = _load_resource_frontier_recordset(
        appendix_a_matrix_local_resource_frontier_record() if recordset is None else recordset
    )
    status = "ok" if report.ok else "invalid"
    lines = [
        "AlphaEvolve Appendix A local matrix resource frontier",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| local_frontier_status | {(data or {}).get('local_frontier_status', '<unknown>')} |",
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


def render_appendix_a_matrix_subset_scope_artifact_boundary_summary(
    boundary: object | str | Path | None = None,
) -> str:
    report = validate_appendix_a_matrix_subset_scope_artifact_boundary(boundary)
    status = "ok" if report.ok else "invalid"
    lines = [
        "AlphaEvolve matrix subset-scope artifact boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| artifact_status | {report.artifact_status or '<unknown>'} |",
        f"| emitted_artifact_count | {report.emitted_artifact_count} |",
        f"| required_field_count | {report.required_field_count} |",
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


def render_appendix_a_matrix_row_note_artifact_boundary_summary(
    boundary: object | str | Path | None = None,
) -> str:
    report = validate_appendix_a_matrix_row_note_artifact_boundary(boundary)
    status = "ok" if report.ok else "invalid"
    lines = [
        "AlphaEvolve Appendix A matrix row-note artifact boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| artifact_status | {report.artifact_status or '<unknown>'} |",
        f"| emitted_artifact_count | {report.emitted_artifact_count} |",
        f"| required_field_count | {report.required_field_count} |",
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


def _load_excluded_target_curation_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[MatrixTargetCurationIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, (str, Path)):
        path = Path(boundary)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [MatrixTargetCurationIssue("read_error", f"failed to read excluded-target curation boundary: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [MatrixTargetCurationIssue("invalid_json", f"invalid excluded-target curation boundary JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [MatrixTargetCurationIssue("invalid_shape", "excluded-target curation boundary must be a JSON object")]


def _load_baseline_citation_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[MatrixTargetIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, (str, Path)):
        path = Path(boundary)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [MatrixTargetIssue("read_error", f"failed to read baseline-citation boundary: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [MatrixTargetIssue("invalid_json", f"invalid baseline-citation boundary JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [MatrixTargetIssue("invalid_shape", "baseline-citation boundary must be a JSON object")]


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


def _load_subset_scope_artifact_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[MatrixSubsetScopeIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, (str, Path)):
        path = Path(boundary)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [MatrixSubsetScopeIssue("read_error", f"failed to read subset-scope artifact boundary: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [MatrixSubsetScopeIssue("invalid_json", f"invalid subset-scope artifact boundary JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [MatrixSubsetScopeIssue("invalid_shape", "subset-scope artifact boundary must be a JSON object")]


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


def _load_row_note_artifact_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[MatrixRowNoteIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, (str, Path)):
        path = Path(boundary)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [MatrixRowNoteIssue("read_error", f"failed to read row-note artifact boundary: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [MatrixRowNoteIssue("invalid_json", f"invalid row-note artifact boundary JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [MatrixRowNoteIssue("invalid_shape", "row-note artifact boundary must be a JSON object")]


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


def _validate_baseline_citation_required_fields(
    value: object,
    issues: list[MatrixTargetIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(MatrixTargetIssue("invalid_required_citation_fields", "required_citation_fields must be a non-empty list"))
        return 0
    seen: set[str] = set()
    for field in value:
        if not isinstance(field, str) or not field.strip():
            issues.append(MatrixTargetIssue("invalid_required_citation_field", "required citation field names must be non-empty strings"))
            continue
        if field in seen:
            issues.append(MatrixTargetIssue("duplicate_required_citation_field", "required_citation_fields must be unique"))
        seen.add(field)
    if set(BASELINE_CITATION_REQUIRED_FIELDS) - seen:
        issues.append(MatrixTargetIssue("missing_required_citation_field", "required_citation_fields must include all baseline-citation fields"))
    return len(value)


def _validate_baseline_citation_records(
    value: list[object],
    issues: list[MatrixTargetIssue],
) -> None:
    targets = matrix_target_records()
    expected_by_id = {target["id"]: target for target in targets if isinstance(target.get("id"), str)}
    seen: set[str] = set()
    for citation in value:
        if not isinstance(citation, dict):
            issues.append(MatrixTargetIssue("invalid_baseline_citation", "baseline citation records must be objects"))
            continue
        target_id = citation.get("target_id")
        safe_id = target_id if isinstance(target_id, str) else None
        expected = expected_by_id.get(safe_id or "")
        if expected is None:
            issues.append(MatrixTargetIssue("unknown_baseline_target_id", "baseline citation target_id must belong to Appendix A matrix registry", safe_id))
            continue
        if safe_id in seen:
            issues.append(MatrixTargetIssue("duplicate_baseline_target_id", "baseline citation target_id values must be unique", safe_id))
        seen.add(safe_id)
        if citation.get("dimensions") != expected.get("dimensions"):
            issues.append(MatrixTargetIssue("invalid_baseline_dimensions", "baseline citation dimensions must match the registry target", safe_id))
        if citation.get("best_known_rank") != expected.get("best_known_rank"):
            issues.append(MatrixTargetIssue("invalid_baseline_rank", "baseline citation best_known_rank must match the registry target", safe_id))
        reference_id = citation.get("cited_reference_id")
        if not isinstance(reference_id, str) or not reference_id.isdigit() or not 1 <= int(reference_id) <= 120:
            issues.append(MatrixTargetIssue("invalid_cited_reference_id", "cited_reference_id must be a paper bibliography id from 1 through 120", safe_id))
        if not isinstance(citation.get("source_table"), str) or not citation["source_table"].strip():
            issues.append(MatrixTargetIssue("missing_source_table", "source_table is required", safe_id))
        if isinstance(citation.get("source_pdf_page"), bool) or not isinstance(citation.get("source_pdf_page"), int) or citation["source_pdf_page"] <= 0:
            issues.append(MatrixTargetIssue("invalid_source_pdf_page", "source_pdf_page must be a positive integer", safe_id))
        for field in ("applicability_caveats", "finite_field_or_characteristic_scope", "report_baseline_source_ref"):
            if not isinstance(citation.get(field), str) or not citation[field].strip():
                issues.append(MatrixTargetIssue(f"missing_{field}", f"{field} is required", safe_id))
        report_ref = citation.get("report_baseline_source_ref")
        if (
            isinstance(report_ref, str)
            and isinstance(reference_id, str)
            and reference_id.isdigit()
            and (safe_id not in report_ref or f"ref{reference_id}" not in report_ref)
        ):
            issues.append(
                MatrixTargetIssue(
                    "invalid_report_baseline_source_ref",
                    "report_baseline_source_ref must include the target id and cited reference id",
                    safe_id,
                )
            )
        _validate_baseline_citation_artifact_path(citation.get("source_artifact_path"), safe_id, issues)
        source_hash = citation.get("source_artifact_sha256")
        if not isinstance(source_hash, str) or _SHA256_RE.fullmatch(source_hash) is None:
            issues.append(MatrixTargetIssue("invalid_source_artifact_sha256", "source_artifact_sha256 must be a lowercase SHA-256 hex digest", safe_id))
    for target_id in sorted(set(expected_by_id) - seen):
        issues.append(MatrixTargetIssue("missing_baseline_target_citation", "each Appendix A matrix target must have a baseline citation record", target_id))


def _validate_baseline_citation_artifact_path(
    value: object,
    target_id: str | None,
    issues: list[MatrixTargetIssue],
) -> None:
    path_obj = Path(value) if isinstance(value, str) else None
    if (
        path_obj is None
        or not value
        or path_obj.is_absolute()
        or value.startswith(("/", "\\"))
        or ".." in path_obj.parts
    ):
        issues.append(MatrixTargetIssue("invalid_source_artifact_path", "source_artifact_path must be a safe relative path", target_id))


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


def _validate_excluded_target_required_fields(
    value: object,
    issues: list[MatrixTargetCurationIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(MatrixTargetCurationIssue("invalid_required_excluded_target_fields", "required_excluded_target_fields must be a non-empty list"))
        return 0
    seen: set[str] = set()
    for field in value:
        if not isinstance(field, str) or not field.strip():
            issues.append(MatrixTargetCurationIssue("invalid_required_excluded_target_field", "required excluded-target field names must be non-empty strings"))
            continue
        if field in seen:
            issues.append(MatrixTargetCurationIssue("duplicate_required_excluded_target_field", "required_excluded_target_fields must be unique"))
        seen.add(field)
    if set(EXCLUDED_TARGET_CURATION_REQUIRED_FIELDS) - seen:
        issues.append(MatrixTargetCurationIssue("missing_required_excluded_target_field", "required_excluded_target_fields must include all excluded-target curation fields"))
    return len(value)


def _validate_excluded_target_coverage_policy(
    value: object,
    status: object,
    issues: list[MatrixTargetCurationIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixTargetCurationIssue("invalid_coverage_policy", "coverage_policy must be an object"))
        return
    policy_status = value.get("status")
    if status == "not_recorded_locally":
        if policy_status != "not_exhaustive":
            issues.append(MatrixTargetCurationIssue("invalid_coverage_policy_status", "absence boundary must mark coverage policy not_exhaustive"))
        boundary = value.get("boundary")
        if not isinstance(boundary, str) or "does not enumerate" not in boundary or "excluded non-equivalent" not in boundary:
            issues.append(MatrixTargetCurationIssue("missing_coverage_boundary", "coverage policy must preserve the excluded non-equivalent target boundary"))
    elif status == "recorded":
        if policy_status not in {"exhaustive_over_declared_finite_scope", "partial_with_scope"}:
            issues.append(MatrixTargetCurationIssue("invalid_coverage_policy_status", "recorded coverage must state exhaustive_over_declared_finite_scope or partial_with_scope"))
        scope = value.get("scope")
        if not isinstance(scope, str) or not scope.strip():
            issues.append(MatrixTargetCurationIssue("missing_coverage_scope", "recorded coverage policy must define the finite or partial scope"))


def _validate_excluded_target_records(
    value: list[object],
    issues: list[MatrixTargetCurationIssue],
) -> None:
    registry_ids = {target["id"] for target in matrix_target_records() if isinstance(target.get("id"), str)}
    omitted_equivalent_ids = {
        record["omitted_target_id"]
        for target in matrix_target_records()
        for record in _omitted_axis_permutation_records(target)
    }
    seen: set[str] = set()
    for record in value:
        if not isinstance(record, dict):
            issues.append(MatrixTargetCurationIssue("invalid_excluded_target", "excluded target records must be objects"))
            continue
        target_id = record.get("excluded_target_id")
        safe_id = target_id if isinstance(target_id, str) else None
        if safe_id is None or _ID_RE.fullmatch(safe_id) is None:
            issues.append(MatrixTargetCurationIssue("invalid_excluded_target_id", "excluded_target_id must use mm_MxNxP syntax", safe_id))
            continue
        if safe_id in seen:
            issues.append(MatrixTargetCurationIssue("duplicate_excluded_target_id", "excluded target ids must be unique", safe_id))
        seen.add(safe_id)
        if safe_id in registry_ids:
            issues.append(MatrixTargetCurationIssue("excluded_target_in_registry", "excluded target must not be one of the reported Appendix A targets", safe_id))
        if safe_id in omitted_equivalent_ids:
            issues.append(MatrixTargetCurationIssue("excluded_target_is_symmetry_equivalent", "excluded target boundary is only for non-equivalent targets, not axis-permutation omissions", safe_id))
        dimensions = _validate_excluded_target_dimensions(record.get("dimensions"), safe_id, issues)
        if dimensions is not None:
            expected_id = "mm_" + "x".join(str(value) for value in dimensions)
            if safe_id != expected_id:
                issues.append(MatrixTargetCurationIssue("excluded_target_id_dimension_mismatch", "excluded_target_id must match dimensions", safe_id))
            if dimensions != sorted(dimensions):
                issues.append(MatrixTargetCurationIssue("excluded_target_not_canonical", "excluded target dimensions must use sorted canonical order", safe_id))
        if record.get("canonical_order") != "m <= n <= p":
            issues.append(MatrixTargetCurationIssue("invalid_excluded_target_canonical_order", "canonical_order must be m <= n <= p", safe_id))
        if record.get("exclusion_class") not in EXCLUDED_TARGET_CURATION_CLASSES:
            issues.append(MatrixTargetCurationIssue("invalid_exclusion_class", "exclusion_class must be a known excluded-target class", safe_id))
        for field in (
            "exclusion_reason",
            "source_basis",
            "rough_rule_relation",
            "p_cutoff_relation",
            "symmetry_equivalence_status",
            "local_attempt_ref",
            "resource_frontier_ref",
        ):
            if not isinstance(record.get(field), str) or not record[field].strip():
                issues.append(MatrixTargetCurationIssue(f"missing_{field}", f"{field} is required", safe_id))
        if record.get("symmetry_equivalence_status") != "non_equivalent_to_reported_sorted_representatives":
            issues.append(MatrixTargetCurationIssue("invalid_symmetry_equivalence_status", "excluded target records must be non-equivalent to reported sorted representatives", safe_id))
        if isinstance(record.get("source_pdf_page"), bool) or not isinstance(record.get("source_pdf_page"), int) or record["source_pdf_page"] <= 0:
            issues.append(MatrixTargetCurationIssue("invalid_excluded_target_source_pdf_page", "source_pdf_page must be a positive integer", safe_id))
        _validate_excluded_target_artifact_paths(record.get("artifact_paths"), safe_id, issues)
        artifact_hash = record.get("artifact_sha256")
        if not isinstance(artifact_hash, str) or _SHA256_RE.fullmatch(artifact_hash) is None:
            issues.append(MatrixTargetCurationIssue("invalid_excluded_target_artifact_sha256", "artifact_sha256 must be a lowercase SHA-256 hex digest", safe_id))


def _validate_excluded_target_dimensions(
    value: object,
    target_id: str | None,
    issues: list[MatrixTargetCurationIssue],
) -> list[int] | None:
    if (
        not isinstance(value, list)
        or len(value) != 3
        or any(isinstance(item, bool) or not isinstance(item, int) or item < 2 for item in value)
    ):
        issues.append(MatrixTargetCurationIssue("invalid_excluded_target_dimensions", "dimensions must be three positive matrix dimensions >= 2", target_id))
        return None
    return list(value)


def _validate_excluded_target_artifact_paths(
    value: object,
    target_id: str | None,
    issues: list[MatrixTargetCurationIssue],
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(MatrixTargetCurationIssue("invalid_excluded_target_artifact_paths", "artifact_paths must be a non-empty list", target_id))
        return
    seen: set[str] = set()
    for path in value:
        path_obj = Path(path) if isinstance(path, str) else None
        if (
            path_obj is None
            or not path
            or path_obj.is_absolute()
            or path.startswith(("/", "\\"))
            or ".." in path_obj.parts
        ):
            issues.append(MatrixTargetCurationIssue("invalid_excluded_target_artifact_path", "artifact_paths entries must be safe relative paths", target_id))
            continue
        if path in seen:
            issues.append(MatrixTargetCurationIssue("duplicate_excluded_target_artifact_path", "artifact_paths entries must be unique", target_id))
        seen.add(path)


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


def _validate_subset_scope_artifact_required_fields(
    value: object,
    issues: list[MatrixSubsetScopeIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(MatrixSubsetScopeIssue("invalid_required_artifact_fields", "required_artifact_fields must be a non-empty list"))
        return 0
    seen: set[str] = set()
    for field in value:
        if not isinstance(field, str) or not field.strip():
            issues.append(MatrixSubsetScopeIssue("invalid_required_artifact_field", "required artifact field names must be non-empty strings"))
            continue
        if field in seen:
            issues.append(MatrixSubsetScopeIssue("duplicate_required_artifact_field", "required_artifact_fields must be unique"))
        seen.add(field)
    if set(SUBSET_SCOPE_ARTIFACT_REQUIRED_FIELDS) - seen:
        issues.append(MatrixSubsetScopeIssue("missing_required_artifact_field", "required_artifact_fields must include all matrix subset-scope artifact fields"))
    return len(value)


def _validate_subset_scope_artifact_record(
    artifact: object,
    issues: list[MatrixSubsetScopeIssue],
) -> None:
    if not isinstance(artifact, dict):
        issues.append(MatrixSubsetScopeIssue("invalid_subset_scope_artifact", "emitted subset-scope artifact records must be objects"))
        return
    subset_id = artifact.get("subset_scope_id")
    safe_id = subset_id if isinstance(subset_id, str) else None
    expected = _expected_subset_scope_records().get(safe_id or "")
    if expected is None:
        issues.append(MatrixSubsetScopeIssue("invalid_subset_scope_id", "subset_scope_id must identify a required matrix subset scope", safe_id))
    else:
        for field in (
            "source_table",
            "source_pdf_page",
            "source_phrase",
            "inclusion_predicate",
            "row_count",
            "outcome_counts",
            "out_of_scope_target_ids",
            "fell_behind_target_ids",
        ):
            if artifact.get(field) != expected[field]:
                issues.append(MatrixSubsetScopeIssue(f"invalid_artifact_{field}", f"artifact {field} must match subset-scope evidence", safe_id))
    _validate_subset_scope_artifact_paths(artifact.get("artifact_paths"), safe_id, issues)
    artifact_hash = artifact.get("artifact_sha256")
    if not isinstance(artifact_hash, str) or _SHA256_RE.fullmatch(artifact_hash) is None:
        issues.append(MatrixSubsetScopeIssue("invalid_artifact_sha256", "artifact_sha256 must be a lowercase SHA-256 hex digest", safe_id))
    subset_report = validate_appendix_a_matrix_subset_scope(artifact.get("subset_scope_evidence"))
    issues.extend(
        MatrixSubsetScopeIssue(f"invalid_nested_subset_scope_{issue.code}", issue.message, issue.subset_id)
        for issue in subset_report.issues
    )
    nested = artifact.get("subset_scope_evidence")
    nested_subsets = nested.get("subsets") if isinstance(nested, dict) else None
    if isinstance(nested_subsets, list) and safe_id is not None:
        matching_subsets = [
            subset
            for subset in nested_subsets
            if isinstance(subset, dict) and subset.get("subset_id") == safe_id
        ]
        if not matching_subsets:
            issues.append(
                MatrixSubsetScopeIssue(
                    "missing_nested_artifact_subset",
                    "subset_scope_evidence must include the artifact subset_scope_id",
                    safe_id,
                )
            )
        else:
            nested_subset = matching_subsets[0]
            for field in (
                "source_table",
                "source_pdf_page",
                "source_phrase",
                "inclusion_predicate",
                "row_count",
                "outcome_counts",
                "out_of_scope_target_ids",
                "fell_behind_target_ids",
            ):
                if artifact.get(field) != nested_subset.get(field):
                    issues.append(
                        MatrixSubsetScopeIssue(
                            f"invalid_artifact_nested_{field}",
                            f"artifact {field} must match its nested subset-scope evidence",
                            safe_id,
                        )
                    )


def _validate_subset_scope_artifact_paths(
    value: object,
    subset_id: str | None,
    issues: list[MatrixSubsetScopeIssue],
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(MatrixSubsetScopeIssue("invalid_artifact_paths", "artifact_paths must be a non-empty list", subset_id))
        return
    seen: set[str] = set()
    for path in value:
        path_obj = Path(path) if isinstance(path, str) else None
        if (
            path_obj is None
            or not path
            or path_obj.is_absolute()
            or path.startswith(("/", "\\"))
            or ".." in path_obj.parts
        ):
            issues.append(MatrixSubsetScopeIssue("invalid_artifact_path", "artifact_paths entries must be safe relative paths", subset_id))
            continue
        if path in seen:
            issues.append(MatrixSubsetScopeIssue("duplicate_artifact_path", "artifact_paths entries must be unique", subset_id))
        seen.add(path)


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


def _validate_row_note_artifact_required_fields(
    value: object,
    issues: list[MatrixRowNoteIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(MatrixRowNoteIssue("invalid_required_artifact_fields", "required_artifact_fields must be a non-empty list"))
        return 0
    seen: set[str] = set()
    for field in value:
        if not isinstance(field, str) or not field.strip():
            issues.append(MatrixRowNoteIssue("invalid_required_artifact_field", "required artifact field names must be non-empty strings"))
            continue
        if field in seen:
            issues.append(MatrixRowNoteIssue("duplicate_required_artifact_field", "required_artifact_fields must be unique"))
        seen.add(field)
    if set(ROW_NOTE_ARTIFACT_REQUIRED_FIELDS) - seen:
        issues.append(MatrixRowNoteIssue("missing_required_artifact_field", "required_artifact_fields must include all matrix row-note artifact fields"))
    return len(value)


def _validate_row_note_artifact_record(
    artifact: object,
    issues: list[MatrixRowNoteIssue],
) -> None:
    if not isinstance(artifact, dict):
        issues.append(MatrixRowNoteIssue("invalid_row_note_artifact", "emitted row-note artifact records must be objects"))
        return
    note_id = artifact.get("note_id")
    safe_id = note_id if isinstance(note_id, str) else None
    expected = appendix_a_matrix_row_note_records()["row_notes"][0]
    for field in (
        "note_id",
        "note_type",
        "target_id",
        "dimensions",
        "alphaevolve_rank",
        "concurrent_rank",
        "cited_reference_id",
        "relationship_to_alphaevolve",
        "source_table",
        "source_pdf_page",
        "note_text",
        "exclusive_priority_claim_safe",
        "docs_caveat",
    ):
        if artifact.get(field) != expected[field]:
            issues.append(MatrixRowNoteIssue(f"invalid_artifact_{field}", f"artifact {field} must match row-note evidence", safe_id))
    _validate_row_note_artifact_paths(artifact.get("artifact_paths"), safe_id, issues)
    artifact_hash = artifact.get("artifact_sha256")
    if not isinstance(artifact_hash, str) or _SHA256_RE.fullmatch(artifact_hash) is None:
        issues.append(MatrixRowNoteIssue("invalid_artifact_sha256", "artifact_sha256 must be a lowercase SHA-256 hex digest", safe_id))
    row_note_report = validate_appendix_a_matrix_row_notes(artifact.get("row_note_evidence"))
    issues.extend(
        MatrixRowNoteIssue(f"invalid_nested_row_note_{issue.code}", issue.message, issue.note_id)
        for issue in row_note_report.issues
    )
    nested = artifact.get("row_note_evidence")
    nested_notes = nested.get("row_notes") if isinstance(nested, dict) else None
    if isinstance(nested_notes, list) and safe_id is not None:
        matching_notes = [
            note
            for note in nested_notes
            if isinstance(note, dict) and note.get("note_id") == safe_id
        ]
        if not matching_notes:
            issues.append(
                MatrixRowNoteIssue(
                    "missing_nested_artifact_row_note",
                    "row_note_evidence must include the artifact note_id",
                    safe_id,
                )
            )
        else:
            nested_note = matching_notes[0]
            for field in (
                "note_type",
                "target_id",
                "dimensions",
                "alphaevolve_rank",
                "concurrent_rank",
                "cited_reference_id",
                "relationship_to_alphaevolve",
                "source_table",
                "source_pdf_page",
                "note_text",
                "exclusive_priority_claim_safe",
                "docs_caveat",
            ):
                if artifact.get(field) != nested_note.get(field):
                    issues.append(
                        MatrixRowNoteIssue(
                            f"invalid_artifact_nested_{field}",
                            f"artifact {field} must match its nested row-note evidence",
                            safe_id,
                        )
                    )


def _stable_json_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_row_note_artifact_paths(
    value: object,
    note_id: str | None,
    issues: list[MatrixRowNoteIssue],
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(MatrixRowNoteIssue("invalid_artifact_paths", "artifact_paths must be a non-empty list", note_id))
        return
    seen: set[str] = set()
    for path in value:
        path_obj = Path(path) if isinstance(path, str) else None
        if (
            path_obj is None
            or not path
            or path_obj.is_absolute()
            or path.startswith(("/", "\\"))
            or ".." in path_obj.parts
        ):
            issues.append(MatrixRowNoteIssue("invalid_artifact_path", "artifact_paths entries must be safe relative paths", note_id))
            continue
        if path in seen:
            issues.append(MatrixRowNoteIssue("duplicate_artifact_path", "artifact_paths entries must be unique", note_id))
        seen.add(path)


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


def _validate_local_frontier_attempts(
    value: object,
    status: object,
    issues: list[MatrixResourceFrontierIssue],
) -> tuple[int, int]:
    if not isinstance(value, list):
        issues.append(MatrixResourceFrontierIssue("invalid_local_attempts", "local_attempts must be a list"))
        return 0, 0
    if status == "not_executed_locally":
        if value:
            issues.append(MatrixResourceFrontierIssue("unexpected_local_attempts", "not_executed_locally records must not include local attempts"))
        return len(value), 0
    artifact_count = 0
    for attempt in value:
        if not isinstance(attempt, dict):
            issues.append(MatrixResourceFrontierIssue("invalid_local_attempt", "local attempts must be objects"))
            continue
        attempt_id = attempt.get("attempt_id") if isinstance(attempt.get("attempt_id"), str) else None
        if not isinstance(attempt.get("target_id"), str) or _ID_RE.fullmatch(attempt["target_id"]) is None:
            issues.append(MatrixResourceFrontierIssue("invalid_local_target_id", "local attempts must identify a matrix target id", attempt_id))
        dimensions = attempt.get("dimensions")
        if not isinstance(dimensions, list) or len(dimensions) != 3 or any(not isinstance(item, int) or isinstance(item, bool) or item <= 0 for item in dimensions):
            issues.append(MatrixResourceFrontierIssue("invalid_local_dimensions", "local attempts must include three positive integer dimensions", attempt_id))
        if not isinstance(attempt.get("seed_count"), int) or isinstance(attempt.get("seed_count"), bool) or attempt["seed_count"] <= 0:
            issues.append(MatrixResourceFrontierIssue("invalid_local_seed_count", "local attempts must include a positive seed_count", attempt_id))
        if not isinstance(attempt.get("accelerator_profile"), str) or not attempt["accelerator_profile"].strip():
            issues.append(MatrixResourceFrontierIssue("missing_local_accelerator_profile", "local attempts must include accelerator_profile", attempt_id))
        if not isinstance(attempt.get("gpu_memory_bytes"), int) or isinstance(attempt.get("gpu_memory_bytes"), bool) or attempt["gpu_memory_bytes"] < 0:
            issues.append(MatrixResourceFrontierIssue("invalid_local_gpu_memory_bytes", "local attempts must include non-negative gpu_memory_bytes", attempt_id))
        if attempt.get("resource_status") not in {"completed", "out_of_memory", "resource_exhausted"}:
            issues.append(MatrixResourceFrontierIssue("invalid_local_resource_status", "local resource_status must be completed, out_of_memory, or resource_exhausted", attempt_id))
        if not isinstance(attempt.get("oom_or_exhaustion_diagnostics"), str) or not attempt["oom_or_exhaustion_diagnostics"].strip():
            issues.append(MatrixResourceFrontierIssue("missing_local_oom_diagnostics", "local attempts must include OOM or exhaustion diagnostics", attempt_id))
        artifact_paths = attempt.get("artifact_paths")
        if not isinstance(artifact_paths, list) or not all(isinstance(path, str) and path.startswith("runs/") for path in artifact_paths):
            issues.append(MatrixResourceFrontierIssue("invalid_local_artifact_paths", "local artifact paths must be run artifacts under runs/", attempt_id))
        else:
            artifact_count += len(artifact_paths)
        artifact_hashes = attempt.get("artifact_sha256")
        if not isinstance(artifact_hashes, list) or len(artifact_hashes) != (len(artifact_paths) if isinstance(artifact_paths, list) else -1):
            issues.append(MatrixResourceFrontierIssue("invalid_local_artifact_hashes", "artifact_sha256 must align with artifact_paths", attempt_id))
        elif any(not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None for digest in artifact_hashes):
            issues.append(MatrixResourceFrontierIssue("invalid_local_artifact_hashes", "artifact_sha256 values must be lowercase SHA-256 digests", attempt_id))
    if status == "attempts_recorded" and not value:
        issues.append(MatrixResourceFrontierIssue("missing_local_attempts", "attempts_recorded records must include at least one local attempt"))
    return len(value), artifact_count


def _validate_excluded_target_policy(
    value: object,
    status: object,
    issues: list[MatrixResourceFrontierIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixResourceFrontierIssue("invalid_excluded_target_policy", "excluded_target_policy must be an object"))
        return
    policy_status = value.get("status")
    if status == "not_executed_locally" and policy_status != "not_defined":
        issues.append(MatrixResourceFrontierIssue("invalid_excluded_target_policy_status", "not_executed_locally records must keep excluded target policy not_defined"))
    if status == "attempts_recorded" and policy_status not in {"defined", "not_defined"}:
        issues.append(MatrixResourceFrontierIssue("invalid_excluded_target_policy_status", "excluded target policy status must be defined or not_defined"))
    boundary = value.get("boundary")
    if not isinstance(boundary, str) or "No local larger-target matrix scaling attempts" not in boundary:
        issues.append(MatrixResourceFrontierIssue("missing_excluded_target_boundary", "excluded target policy must preserve the current local absence boundary"))


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
