from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.follow_on_sources import (
    EXPECTED_DECLARED_PROBLEM_COUNT,
    EXPECTED_FOLLOW_ON_NOTEBOOKS,
    EXPECTED_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_FILE,
    EXPECTED_REPOSITORY_COMMIT,
    EXPECTED_REPOSITORY_NAME,
    EXPECTED_REPOSITORY_URL,
)


ALPHAEVOLVE_FOLLOW_ON_PROBLEM_COVERAGE_SCHEMA = "libreevolve.alphaevolve_follow_on_problem_coverage.v1"
EXPECTED_SNAPSHOT_DATE = "2026-06-08"
EXPECTED_PROBLEM_IDS = tuple(range(1, EXPECTED_DECLARED_PROBLEM_COUNT + 1))
EXPECTED_EXTRA_NUMBERED_PAGE_IDS = (68,)
EXPECTED_OBSERVED_NUMBERED_HTML_COUNT = 68
EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS = {
    "diagnostic_scope": "extra_numbered_page_68_and_duplicate_logic_puzzles_context",
    "diagnosed_page_ids": (67, 68),
    "classification": "page_68_extra_numbered_duplicate_title_outside_declared_67_navigation",
    "classification_complete": True,
    "all_page_diagnostics_complete": False,
    "resource_link_diagnostics_complete_for_diagnosed_pages": True,
    "duplicate_title_groups": (
        {"title": "Logic puzzles", "page_ids": (67, 68), "paper_section": "6.44"},
    ),
    "pages": (
        {
            "page_id": 67,
            "path": "problems/67.html",
            "title": "67. Logic puzzles",
            "title_key": "Logic puzzles",
            "bytes": 12428,
            "sha256": "bd265b4b409493956a3d577bccd17325c468f66a695efc1dffc67dc7e5f468d8",
            "declared_navigation_total_problems": 67,
            "paper_section": "6.44",
            "colab_url": "#",
            "colab_link_status": "under_construction_placeholder",
            "paper_url": "https://arxiv.org/abs/2511.02864",
            "paper_link_status": "valid_follow_on_arxiv",
            "classification": "declared_range_duplicate_title_context_page",
        },
        {
            "page_id": 68,
            "path": "problems/68.html",
            "title": "68. Logic puzzles",
            "title_key": "Logic puzzles",
            "bytes": 9253,
            "sha256": "51eda861f49691d2db5b1ec2775dbd77c5cc47afde791416c9283c23de2ca75d",
            "declared_navigation_total_problems": None,
            "paper_section": "6.44",
            "colab_url": "https://colab.research.google.com/",
            "colab_link_status": "generic_colab_landing_page",
            "paper_url": "#",
            "paper_link_status": "placeholder",
            "classification": "extra_numbered_page_duplicate_title_outside_declared_67_navigation",
        },
    ),
}
EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS = {
    "diagnostic_scope": "all_numbered_pages_resource_links",
    "diagnosed_page_count": EXPECTED_OBSERVED_NUMBERED_HTML_COUNT,
    "resource_link_diagnostics_complete": True,
    "page_hash_inventory_complete": False,
    "colab_link_status_counts": {
        "generic_colab_landing_page": 1,
        "github_notebook_blob_url": 36,
        "google_colab_url": 6,
        "under_construction_placeholder": 25,
    },
    "colab_link_status_page_ids": {
        "generic_colab_landing_page": (68,),
        "github_notebook_blob_url": (
            1, 2, 3, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 27, 28,
            32, 33, 34, 35, 36, 42, 44, 45, 46, 53, 54, 58, 59, 60, 61,
            62, 63, 64, 65,
        ),
        "google_colab_url": (4, 5, 8, 48, 49, 50),
        "under_construction_placeholder": (
            6, 20, 21, 22, 23, 24, 25, 26, 29, 30, 31, 37, 38, 39, 40, 41,
            43, 47, 51, 52, 55, 56, 57, 66, 67,
        ),
    },
    "paper_link_status_counts": {
        "placeholder": 1,
        "valid_follow_on_arxiv": 67,
    },
    "paper_link_status_page_ids": {
        "placeholder": (68,),
        "valid_follow_on_arxiv": tuple(range(1, 68)),
    },
    "navigation_total_problem_counts": {
        "67": 67,
        "missing": 1,
    },
    "missing_navigation_total_problem_page_ids": (68,),
    "duplicate_title_groups": (
        {"title": "Logic puzzles", "page_ids": (67, 68)},
    ),
    "multi_page_paper_section_groups": (
        {"paper_section": "6.18", "page_ids": (33, 34)},
        {"paper_section": "6.19", "page_ids": (35, 36)},
        {"paper_section": "6.2", "page_ids": (2, 3, 4, 5, 6)},
        {"paper_section": "6.25", "page_ids": (42, 43, 44)},
        {"paper_section": "6.29", "page_ids": (48, 49)},
        {"paper_section": "6.42", "page_ids": (62, 63, 64)},
        {"paper_section": "6.44", "page_ids": (66, 67, 68)},
        {"paper_section": "6.5", "page_ids": (9, 10)},
        {"paper_section": "6.6", "page_ids": (11, 12, 13)},
        {"paper_section": "6.7", "page_ids": (14, 15, 16, 17, 18)},
        {"paper_section": "6.9", "page_ids": (20, 21, 22, 23, 24)},
    ),
}
EXPECTED_STATUS_BUCKETS = {
    "world_record": (1, 2, 4, 5, 7, 8, 9, 10, 30, 32, 35, 42, 48, 49, 50, 59, 60, 61, 64),
    "former_record": (3, 36, 38, 44),
    "worse_than_record": (6, 11, 18, 27, 28, 39, 40, 43),
    "matched_optimal": (14, 15, 16, 17, 19, 29, 46, 54, 62, 63, 65, 67),
}
EXPECTED_LISTED_STATUS_COUNT = 43
EXPECTED_UNCLASSIFIED_PROBLEM_IDS = (
    12,
    13,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    31,
    33,
    34,
    37,
    41,
    45,
    47,
    51,
    52,
    53,
    55,
    56,
    57,
    58,
    66,
)
EXPECTED_STATUS_ARTIFACTS = {
    "status.json": {
        "bytes": 261,
        "sha256": "".join(
            [
                "84c1",
                "3884",
                "c9f5",
                "750d",
                "3c07",
                "ec4b",
                "05dd",
                "d909",
                "80a3",
                "b30a",
                "2fe6",
                "e3e4",
                "1a57",
                "5849",
                "f604",
                "c3ce",
            ]
        ),
        "kind": "status_bucket_json",
    },
    "status_grid.png": {
        "bytes": 139376,
        "sha256": "".join(
            [
                "6d4c",
                "dd57",
                "4274",
                "3f75",
                "56e5",
                "c030",
                "5044",
                "667b",
                "4adf",
                "c843",
                "8414",
                "7f1b",
                "b0c9",
                "9b9c",
                "8422",
                "474c",
            ]
        ),
        "kind": "status_grid_image",
    },
    "result_distribution.png": {
        "bytes": 212933,
        "sha256": "".join(
            [
                "2931",
                "6632",
                "dee0",
                "06a4",
                "19b2",
                "e7d0",
                "781f",
                "0b38",
                "67e2",
                "cc20",
                "4a35",
                "8aaa",
                "5856",
                "1e6d",
                "52c5",
                "989a",
            ]
        ),
        "kind": "result_distribution_image",
    },
}
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_COMMIT_RE = re.compile(r"[0-9a-f]{40}")


@dataclass(frozen=True)
class AlphaEvolveFollowOnProblemCoverageIssue:
    code: str
    message: str
    problem_id: int | None = None


@dataclass(frozen=True)
class AlphaEvolveFollowOnProblemCoverageValidation:
    ok: bool
    declared_problem_count: int
    listed_status_count: int
    unclassified_problem_count: int
    status_artifact_count: int
    observed_numbered_html_count: int | None
    issues: list[AlphaEvolveFollowOnProblemCoverageIssue]


def alphaevolve_follow_on_problem_coverage_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_FOLLOW_ON_PROBLEM_COVERAGE_SCHEMA,
        "source_family": "alphaevolve_follow_on_problem_repository_coverage",
        "repository": {
            "name": EXPECTED_REPOSITORY_NAME,
            "url": EXPECTED_REPOSITORY_URL,
            "commit": EXPECTED_REPOSITORY_COMMIT,
            "snapshot_date": EXPECTED_SNAPSHOT_DATE,
            "live_update_policy": "live_repository_snapshot_required",
        },
        "coverage_scope": {
            "declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
            "problem_id_range": [1, EXPECTED_DECLARED_PROBLEM_COUNT],
            "problem_ids": list(EXPECTED_PROBLEM_IDS),
            "problem_pages_declared_complete": True,
            "problem_page_access_mode": "browser_page",
            "notebook_access_mode": "colab_notebook_many_not_all",
            "notebook_inventory_complete": False,
            "page_hash_inventory_complete": False,
            "notebook_hash_inventory_complete": False,
            "artifact_presence_matrix_complete": False,
        },
        "numbered_page_inventory": {
            "observed_numbered_html_count": EXPECTED_OBSERVED_NUMBERED_HTML_COUNT,
            "expected_declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
            "included_problem_ids": list(EXPECTED_PROBLEM_IDS),
            "extra_numbered_page_ids": list(EXPECTED_EXTRA_NUMBERED_PAGE_IDS),
            "count_reconciliation_status": "declared_67_with_extra_numbered_page_68_observed",
            "full_page_link_diagnostics_complete": True,
        },
        "page_discrepancy_diagnostics": {
            "diagnostic_scope": EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["diagnostic_scope"],
            "diagnosed_page_ids": list(EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["diagnosed_page_ids"]),
            "classification": EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["classification"],
            "classification_complete": EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["classification_complete"],
            "all_page_diagnostics_complete": EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["all_page_diagnostics_complete"],
            "resource_link_diagnostics_complete_for_diagnosed_pages": (
                EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["resource_link_diagnostics_complete_for_diagnosed_pages"]
            ),
            "duplicate_title_groups": [
                {
                    "title": group["title"],
                    "page_ids": list(group["page_ids"]),
                    "paper_section": group["paper_section"],
                }
                for group in EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["duplicate_title_groups"]
            ],
            "pages": [
                {
                    **page,
                    "hosted_url": (
                        "https://google-deepmind.github.io/"
                        f"alphaevolve_repository_of_problems/{page['path']}"
                    ),
                    "raw_url": (
                        "https://raw.githubusercontent.com/google-deepmind/"
                        f"alphaevolve_repository_of_problems/{EXPECTED_REPOSITORY_COMMIT}/{page['path']}"
                    ),
                }
                for page in EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["pages"]
            ],
        },
        "all_page_resource_link_diagnostics": {
            "diagnostic_scope": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["diagnostic_scope"],
            "diagnosed_page_count": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["diagnosed_page_count"],
            "resource_link_diagnostics_complete": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
                "resource_link_diagnostics_complete"
            ],
            "page_hash_inventory_complete": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
                "page_hash_inventory_complete"
            ],
            "colab_link_status_counts": dict(
                EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["colab_link_status_counts"]
            ),
            "colab_link_status_page_ids": {
                status: list(page_ids)
                for status, page_ids in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
                    "colab_link_status_page_ids"
                ].items()
            },
            "paper_link_status_counts": dict(
                EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["paper_link_status_counts"]
            ),
            "paper_link_status_page_ids": {
                status: list(page_ids)
                for status, page_ids in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
                    "paper_link_status_page_ids"
                ].items()
            },
            "navigation_total_problem_counts": dict(
                EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["navigation_total_problem_counts"]
            ),
            "missing_navigation_total_problem_page_ids": list(
                EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
                    "missing_navigation_total_problem_page_ids"
                ]
            ),
            "duplicate_title_groups": [
                {"title": group["title"], "page_ids": list(group["page_ids"])}
                for group in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["duplicate_title_groups"]
            ],
            "multi_page_paper_section_groups": [
                {"paper_section": group["paper_section"], "page_ids": list(group["page_ids"])}
                for group in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
                    "multi_page_paper_section_groups"
                ]
            ],
            "claim_boundary": (
                "All 68 numbered pages have resource-link diagnostics, but "
                "this does not claim complete per-page hashes, notebook "
                "mapping, or artifact-presence rows."
            ),
        },
        "notebook_inventory_link": {
            "source_manifest": EXPECTED_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_FILE,
            "source_boundary": "alphaevolve_follow_on_runtime_absence",
            "pinned_notebook_path_count": len(EXPECTED_FOLLOW_ON_NOTEBOOKS),
            "path_inventory_status": "pinned_git_blob_inventory_recorded",
            "problem_id_mapping_complete": False,
            "sha256_inventory_complete": False,
            "absence_reason_inventory_complete": False,
            "claim_boundary": (
                "The follow-on runtime-absence record pins notebook paths and "
                "git blob ids, but does not claim per-problem notebook mapping, "
                "SHA-256 notebook hashes, or absence reasons."
            ),
        },
        "status_artifacts": [
            {
                "path": path,
                "kind": metadata["kind"],
                "bytes": metadata["bytes"],
                "sha256": metadata["sha256"],
            }
            for path, metadata in EXPECTED_STATUS_ARTIFACTS.items()
        ],
        "status_buckets": {
            bucket: list(problem_ids)
            for bucket, problem_ids in EXPECTED_STATUS_BUCKETS.items()
        },
        "status_summary": {
            "listed_problem_count": EXPECTED_LISTED_STATUS_COUNT,
            "unclassified_label": "not_listed_in_status_json",
            "unclassified_problem_ids": list(EXPECTED_UNCLASSIFIED_PROBLEM_IDS),
            "unclassified_problem_count": len(EXPECTED_UNCLASSIFIED_PROBLEM_IDS),
            "bucket_semantics": "repository_status_json_explicit_buckets",
        },
        "remaining_coverage_work": [
            "hash_each_problem_page",
            "discover_notebook_paths_and_absence_reasons",
            "validate_prompt_verifier_initial_final_visualization_flags",
            "attach_status_to_emitted_source_manifest_rows",
        ],
    }


def validate_alphaevolve_follow_on_problem_coverage(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveFollowOnProblemCoverageValidation:
    data, read_issues = _load_recordset(recordset)
    if read_issues:
        return AlphaEvolveFollowOnProblemCoverageValidation(False, 0, 0, 0, 0, None, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveFollowOnProblemCoverageIssue] = []
    if data.get("schema") != ALPHAEVOLVE_FOLLOW_ON_PROBLEM_COVERAGE_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported follow-on problem coverage schema"))
    if data.get("source_family") != "alphaevolve_follow_on_problem_repository_coverage":
        issues.append(_issue("invalid_source_family", "source_family must identify follow-on problem repository coverage"))
    _validate_repository(data.get("repository"), issues)
    declared_problem_count = _validate_coverage_scope(data.get("coverage_scope"), issues)
    observed_numbered_html_count = _validate_numbered_page_inventory(data.get("numbered_page_inventory"), issues)
    _validate_page_discrepancy_diagnostics(data.get("page_discrepancy_diagnostics"), issues)
    _validate_all_page_resource_link_diagnostics(data.get("all_page_resource_link_diagnostics"), issues)
    _validate_notebook_inventory_link(data.get("notebook_inventory_link"), issues)
    status_artifact_count = _validate_status_artifacts(data.get("status_artifacts"), issues)
    listed_status_count = _validate_status_buckets(data.get("status_buckets"), issues)
    unclassified_problem_count = _validate_status_summary(data.get("status_summary"), issues)
    _validate_remaining_coverage_work(data.get("remaining_coverage_work"), issues)
    return AlphaEvolveFollowOnProblemCoverageValidation(
        ok=not issues,
        declared_problem_count=declared_problem_count,
        listed_status_count=listed_status_count,
        unclassified_problem_count=unclassified_problem_count,
        status_artifact_count=status_artifact_count,
        observed_numbered_html_count=observed_numbered_html_count,
        issues=issues,
    )


def render_alphaevolve_follow_on_problem_coverage_summary(recordset: object | str | Path | None = None) -> str:
    validation = validate_alphaevolve_follow_on_problem_coverage(recordset)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve follow-on problem coverage evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| declared_problem_count | {validation.declared_problem_count} |",
        f"| listed_status_count | {validation.listed_status_count} |",
        f"| unclassified_problem_count | {validation.unclassified_problem_count} |",
        f"| status_artifact_count | {validation.status_artifact_count} |",
        f"| observed_numbered_html_count | {validation.observed_numbered_html_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(
            f"- {issue.code}: {issue.message}"
            + (f" (problem {issue.problem_id})" if issue.problem_id is not None else "")
            for issue in validation.issues
        )
    return "\n".join(lines)


def _load_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveFollowOnProblemCoverageIssue]]:
    if recordset is None:
        return alphaevolve_follow_on_problem_coverage_record(), []
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [_issue("read_error", f"failed to read follow-on coverage record: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"invalid follow-on coverage JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [_issue("invalid_shape", "follow-on coverage record must be a JSON object")]


def _validate_repository(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository", "repository must be an object"))
        return
    expected = {
        "name": EXPECTED_REPOSITORY_NAME,
        "url": EXPECTED_REPOSITORY_URL,
        "commit": EXPECTED_REPOSITORY_COMMIT,
        "snapshot_date": EXPECTED_SNAPSHOT_DATE,
        "live_update_policy": "live_repository_snapshot_required",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_repository_{field}", f"repository.{field} must match the pinned coverage snapshot"))
    commit = value.get("commit")
    if not isinstance(commit, str) or _COMMIT_RE.fullmatch(commit) is None:
        issues.append(_issue("invalid_repository_commit_format", "repository.commit must be a 40-character commit hash"))


def _validate_coverage_scope(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_coverage_scope", "coverage_scope must be an object"))
        return 0
    expected = {
        "declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
        "problem_id_range": [1, EXPECTED_DECLARED_PROBLEM_COUNT],
        "problem_ids": list(EXPECTED_PROBLEM_IDS),
        "problem_pages_declared_complete": True,
        "problem_page_access_mode": "browser_page",
        "notebook_access_mode": "colab_notebook_many_not_all",
        "notebook_inventory_complete": False,
        "page_hash_inventory_complete": False,
        "notebook_hash_inventory_complete": False,
        "artifact_presence_matrix_complete": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_coverage_scope_{field}"
            if field.endswith("_complete") and expected_value is False:
                code = f"{field}_overclaim"
            issues.append(_issue(code, f"coverage_scope.{field} must match the current scoped coverage evidence"))
    return int(value.get("declared_problem_count")) if isinstance(value.get("declared_problem_count"), int) else 0


def _validate_numbered_page_inventory(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> int | None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_numbered_page_inventory", "numbered_page_inventory must be an object"))
        return None
    expected = {
        "observed_numbered_html_count": EXPECTED_OBSERVED_NUMBERED_HTML_COUNT,
        "expected_declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
        "included_problem_ids": list(EXPECTED_PROBLEM_IDS),
        "extra_numbered_page_ids": list(EXPECTED_EXTRA_NUMBERED_PAGE_IDS),
        "count_reconciliation_status": "declared_67_with_extra_numbered_page_68_observed",
        "full_page_link_diagnostics_complete": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_numbered_page_inventory_{field}"
            if field == "full_page_link_diagnostics_complete":
                code = "full_page_link_diagnostics_overclaim"
            issues.append(_issue(code, f"numbered_page_inventory.{field} must preserve the pinned page-count boundary"))
    observed = value.get("observed_numbered_html_count")
    return observed if isinstance(observed, int) else None


def _validate_page_discrepancy_diagnostics(
    value: object,
    issues: list[AlphaEvolveFollowOnProblemCoverageIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_page_discrepancy_diagnostics", "page_discrepancy_diagnostics must be an object"))
        return
    expected = {
        "diagnostic_scope": EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["diagnostic_scope"],
        "diagnosed_page_ids": list(EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["diagnosed_page_ids"]),
        "classification": EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["classification"],
        "classification_complete": True,
        "all_page_diagnostics_complete": False,
        "resource_link_diagnostics_complete_for_diagnosed_pages": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_page_discrepancy_diagnostics_{field}"
            if field == "all_page_diagnostics_complete":
                code = "page_discrepancy_all_page_diagnostics_overclaim"
            issues.append(_issue(code, f"page_discrepancy_diagnostics.{field} must preserve the page-68 diagnostic boundary"))
    expected_groups = [
        {
            "title": group["title"],
            "page_ids": list(group["page_ids"]),
            "paper_section": group["paper_section"],
        }
        for group in EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["duplicate_title_groups"]
    ]
    if value.get("duplicate_title_groups") != expected_groups:
        issues.append(_issue("invalid_page_discrepancy_duplicate_title_groups", "page 67 and 68 must remain a duplicate-title diagnostic group"))
    pages = value.get("pages")
    if not isinstance(pages, list):
        issues.append(_issue("invalid_page_discrepancy_pages", "page_discrepancy_diagnostics.pages must be a list"))
        return
    pages_by_id = {
        record.get("page_id"): record
        for record in pages
        if isinstance(record, dict)
    }
    for expected_page in EXPECTED_PAGE_DISCREPANCY_DIAGNOSTICS["pages"]:
        page_id = expected_page["page_id"]
        record = pages_by_id.get(page_id)
        if not isinstance(record, dict):
            issues.append(_issue("missing_page_discrepancy_page", "diagnosed page is missing", page_id))
            continue
        for field, expected_value in expected_page.items():
            if record.get(field) != expected_value:
                issues.append(
                    _issue(
                        f"invalid_page_discrepancy_page_{field}",
                        f"page {page_id} diagnostic field {field} must match the pinned source",
                        page_id,
                    )
                )
        hosted_url = record.get("hosted_url")
        raw_url = record.get("raw_url")
        if not isinstance(hosted_url, str) or f"/{expected_page['path']}" not in hosted_url:
            issues.append(_issue("invalid_page_discrepancy_hosted_url", "diagnosed page must include its hosted URL", page_id))
        if (
            not isinstance(raw_url, str)
            or EXPECTED_REPOSITORY_COMMIT not in raw_url
            or f"/{expected_page['path']}" not in raw_url
        ):
            issues.append(_issue("invalid_page_discrepancy_raw_url", "diagnosed page must include its pinned raw URL", page_id))
    unexpected_page_ids = sorted(page_id for page_id in pages_by_id if page_id not in {67, 68})
    for page_id in unexpected_page_ids:
        issues.append(_issue("unexpected_page_discrepancy_page", "diagnostics are scoped only to pages 67 and 68", page_id))


def _validate_all_page_resource_link_diagnostics(
    value: object,
    issues: list[AlphaEvolveFollowOnProblemCoverageIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_all_page_resource_link_diagnostics", "all_page_resource_link_diagnostics must be an object"))
        return
    expected = {
        "diagnostic_scope": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["diagnostic_scope"],
        "diagnosed_page_count": EXPECTED_OBSERVED_NUMBERED_HTML_COUNT,
        "resource_link_diagnostics_complete": True,
        "page_hash_inventory_complete": False,
        "colab_link_status_counts": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["colab_link_status_counts"],
        "paper_link_status_counts": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["paper_link_status_counts"],
        "navigation_total_problem_counts": EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["navigation_total_problem_counts"],
        "missing_navigation_total_problem_page_ids": list(
            EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["missing_navigation_total_problem_page_ids"]
        ),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_all_page_resource_link_diagnostics_{field}"
            if field == "page_hash_inventory_complete":
                code = "all_page_resource_link_page_hash_inventory_overclaim"
            issues.append(_issue(code, f"all_page_resource_link_diagnostics.{field} must match the pinned all-page link evidence"))
    expected_colab_ids = {
        status: list(page_ids)
        for status, page_ids in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
            "colab_link_status_page_ids"
        ].items()
    }
    if value.get("colab_link_status_page_ids") != expected_colab_ids:
        issues.append(_issue("invalid_all_page_colab_link_status_page_ids", "all-page Colab link page-id buckets must match the pinned source"))
    expected_paper_ids = {
        status: list(page_ids)
        for status, page_ids in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS[
            "paper_link_status_page_ids"
        ].items()
    }
    if value.get("paper_link_status_page_ids") != expected_paper_ids:
        issues.append(_issue("invalid_all_page_paper_link_status_page_ids", "all-page paper link page-id buckets must match the pinned source"))
    expected_title_groups = [
        {"title": group["title"], "page_ids": list(group["page_ids"])}
        for group in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["duplicate_title_groups"]
    ]
    if value.get("duplicate_title_groups") != expected_title_groups:
        issues.append(_issue("invalid_all_page_duplicate_title_groups", "all-page duplicate-title groups must match the pinned source"))
    expected_section_groups = [
        {"paper_section": group["paper_section"], "page_ids": list(group["page_ids"])}
        for group in EXPECTED_ALL_PAGE_RESOURCE_LINK_DIAGNOSTICS["multi_page_paper_section_groups"]
    ]
    if value.get("multi_page_paper_section_groups") != expected_section_groups:
        issues.append(_issue("invalid_all_page_multi_page_paper_section_groups", "multi-page paper-section groups must match the pinned source"))
    claim_boundary = value.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "does not claim" not in claim_boundary
        or "complete per-page hashes" not in claim_boundary
    ):
        issues.append(_issue("missing_all_page_resource_link_claim_boundary", "all-page link diagnostics must preserve page-hash and artifact-row gaps"))


def _validate_notebook_inventory_link(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_notebook_inventory_link", "notebook_inventory_link must be an object"))
        return
    expected = {
        "source_manifest": EXPECTED_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_FILE,
        "source_boundary": "alphaevolve_follow_on_runtime_absence",
        "pinned_notebook_path_count": len(EXPECTED_FOLLOW_ON_NOTEBOOKS),
        "path_inventory_status": "pinned_git_blob_inventory_recorded",
        "problem_id_mapping_complete": False,
        "sha256_inventory_complete": False,
        "absence_reason_inventory_complete": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_notebook_inventory_link_{field}"
            if field.endswith("_complete") and expected_value is False:
                code = f"notebook_inventory_link_{field}_overclaim"
            issues.append(_issue(code, f"notebook_inventory_link.{field} must preserve the pinned notebook-inventory boundary"))
    claim_boundary = value.get("claim_boundary")
    if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary:
        issues.append(_issue("missing_notebook_inventory_link_claim_boundary", "notebook_inventory_link must state that per-problem notebook coverage is not claimed"))


def _validate_status_artifacts(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_status_artifacts", "status_artifacts must be a list"))
        return 0
    records_by_path = {
        str(record.get("path")): record
        for record in value
        if isinstance(record, dict) and isinstance(record.get("path"), str)
    }
    for path, expected in EXPECTED_STATUS_ARTIFACTS.items():
        record = records_by_path.get(path)
        if record is None:
            issues.append(_issue("missing_status_artifact", f"status artifact {path} is missing"))
            continue
        if record.get("kind") != expected["kind"]:
            issues.append(_issue("invalid_status_artifact_kind", f"status artifact {path} has the wrong kind"))
        if record.get("bytes") != expected["bytes"]:
            issues.append(_issue("invalid_status_artifact_bytes", f"status artifact {path} byte count must match the pinned snapshot"))
        sha256 = record.get("sha256")
        if not isinstance(sha256, str) or _SHA256_RE.fullmatch(sha256) is None:
            issues.append(_issue("invalid_status_artifact_sha256", f"status artifact {path} must have a lowercase 64-hex digest"))
        elif sha256 != expected["sha256"]:
            issues.append(_issue("status_artifact_sha256_drift", f"status artifact {path} digest must match the pinned snapshot"))
    for path in sorted(set(records_by_path) - set(EXPECTED_STATUS_ARTIFACTS)):
        issues.append(_issue("unexpected_status_artifact", f"unexpected status artifact {path}"))
    return len(records_by_path)


def _validate_status_buckets(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_status_buckets", "status_buckets must be an object"))
        return 0
    listed: list[int] = []
    for bucket, expected_ids in EXPECTED_STATUS_BUCKETS.items():
        actual = value.get(bucket)
        if actual != list(expected_ids):
            issues.append(_issue("status_bucket_membership_drift", f"status_buckets.{bucket} must match the pinned status.json membership"))
        if isinstance(actual, list):
            listed.extend(problem_id for problem_id in actual if isinstance(problem_id, int))
    if set(value) != set(EXPECTED_STATUS_BUCKETS):
        issues.append(_issue("invalid_status_bucket_names", "status_buckets must contain exactly the pinned status.json bucket names"))
    duplicates = sorted(problem_id for problem_id in set(listed) if listed.count(problem_id) > 1)
    for problem_id in duplicates:
        issues.append(_issue("duplicate_status_problem_id", "problem id appears in multiple status buckets", problem_id))
    for problem_id in sorted(problem_id for problem_id in listed if problem_id not in EXPECTED_PROBLEM_IDS):
        issues.append(_issue("status_problem_id_out_of_range", "status bucket problem id is outside the declared 1..67 range", problem_id))
    if len(listed) != EXPECTED_LISTED_STATUS_COUNT:
        issues.append(_issue("invalid_listed_status_count", "listed status problem count must match the pinned status.json count"))
    return len(listed)


def _validate_status_summary(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_status_summary", "status_summary must be an object"))
        return 0
    expected = {
        "listed_problem_count": EXPECTED_LISTED_STATUS_COUNT,
        "unclassified_label": "not_listed_in_status_json",
        "unclassified_problem_ids": list(EXPECTED_UNCLASSIFIED_PROBLEM_IDS),
        "unclassified_problem_count": len(EXPECTED_UNCLASSIFIED_PROBLEM_IDS),
        "bucket_semantics": "repository_status_json_explicit_buckets",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_status_summary_{field}", f"status_summary.{field} must match the pinned coverage summary"))
    actual = value.get("unclassified_problem_ids")
    return len(actual) if isinstance(actual, list) else 0


def _validate_remaining_coverage_work(value: object, issues: list[AlphaEvolveFollowOnProblemCoverageIssue]) -> None:
    required = {
        "hash_each_problem_page",
        "discover_notebook_paths_and_absence_reasons",
        "validate_prompt_verifier_initial_final_visualization_flags",
        "attach_status_to_emitted_source_manifest_rows",
    }
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(_issue("invalid_remaining_coverage_work", "remaining_coverage_work must be a list of remaining work ids"))
        return
    for work_id in sorted(required - set(value)):
        issues.append(_issue("missing_remaining_coverage_work", f"remaining_coverage_work is missing {work_id}"))


def _issue(
    code: str,
    message: str,
    problem_id: int | None = None,
) -> AlphaEvolveFollowOnProblemCoverageIssue:
    return AlphaEvolveFollowOnProblemCoverageIssue(code, message, problem_id)
