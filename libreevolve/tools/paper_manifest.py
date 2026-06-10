from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import logging
import os
import re
import stat
import subprocess
import tempfile
import unicodedata
from contextlib import redirect_stderr
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from pypdf import PdfReader

from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.problems.benchmarks.ablation_registry import (
    REGISTRY_PATH as ABLATION_REGISTRY_PATH,
    validate_ablation_registry,
)
from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    REGISTRY_PATH as APPENDIX_A_MATRIX_REGISTRY_PATH,
    appendix_a_matrix_baseline_citation_boundary_record,
    appendix_a_matrix_curation_record,
    appendix_a_matrix_local_resource_frontier_record,
    appendix_a_matrix_resource_frontier_record,
    appendix_a_matrix_row_note_artifact_boundary_record,
    appendix_a_matrix_subset_scope_artifact_boundary_record,
    validate_appendix_a_matrix_baseline_citation_boundary,
    validate_appendix_a_matrix_curation,
    validate_appendix_a_matrix_local_resource_frontier,
    validate_appendix_a_matrix_resource_frontier,
    validate_appendix_a_matrix_registry,
    validate_appendix_a_matrix_row_note_artifact_boundary,
    validate_appendix_a_matrix_subset_scope_artifact_boundary,
)
from libreevolve.problems.benchmarks.appendix_b_registry import (
    REGISTRY_PATH as APPENDIX_B_REGISTRY_PATH,
    validate_appendix_b_registry,
)
from libreevolve.problems.benchmarks.example_scope import (
    example_benchmark_scope_records,
    validate_example_benchmark_scope,
)
from libreevolve.problems.benchmarks.follow_on_sources import (
    EXPECTED_FOLLOW_ON_REPOSITORY_RIGHTS_MANIFEST_FILE,
    EXPECTED_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_FILE,
    EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE,
    EXPECTED_FOLLOW_ON_TAO_BLOG_MANIFEST_FILE,
    alphaevolve_follow_on_math_source_record,
    validate_alphaevolve_follow_on_repository_rights_manifest,
    validate_alphaevolve_follow_on_runtime_absence_manifest,
    validate_alphaevolve_follow_on_source_manifest,
    validate_alphaevolve_follow_on_tao_blog_manifest,
    validate_alphaevolve_follow_on_math_source,
)
from libreevolve.problems.benchmarks.follow_on_coverage import (
    alphaevolve_follow_on_problem_coverage_record,
    validate_alphaevolve_follow_on_problem_coverage,
)
from libreevolve.problems.benchmarks.theoretical_cs_sources import (
    EXPECTED_THEORETICAL_CS_SOURCE_MANIFEST_FILE,
    validate_alphaevolve_theoretical_cs_source_manifest,
)
from libreevolve.problems.benchmarks.official_deepmind_blog import (
    EXPECTED_OFFICIAL_BLOG_MANIFEST_FILE,
    validate_alphaevolve_official_blog_manifest,
)
from libreevolve.problems.benchmarks.paper_source_versions import (
    EXPECTED_SOURCE_VERSION_MANIFEST_FILE,
    alphaevolve_source_pdf_version_record,
    validate_alphaevolve_source_pdf_version_manifest,
    validate_alphaevolve_source_pdf_version,
)
from libreevolve.problems.benchmarks.paper_source_rights import (
    EXPECTED_SOURCE_RIGHTS_MANIFEST_FILE,
    alphaevolve_source_pdf_rights_record,
    validate_alphaevolve_source_pdf_rights_manifest,
    validate_alphaevolve_source_pdf_rights,
)
from libreevolve.problems.benchmarks.paper_source_identity import (
    PAPER_SOURCE_IDENTITY_MANIFEST_FILE,
    validate_paper_source_identity_manifest,
)
from libreevolve.problems.benchmarks.paper_bibliography import (
    EXPECTED_REFERENCES_BIBLIOGRAPHY_FILE,
    alphaevolve_references_section_record,
    validate_alphaevolve_references_bibliography,
    validate_alphaevolve_references_section,
)
from libreevolve.problems.benchmarks.companion_sources import (
    EXPECTED_COMPANION_SOURCE_MANIFEST_FILE,
    validate_alphaevolve_companion_source_manifest,
)
from libreevolve.problems.benchmarks.paper_artifact_roles import (
    alphaevolve_paper_artifact_linkage_record,
    alphaevolve_paper_artifact_role_records,
    validate_paper_artifact_linkage,
    validate_paper_artifact_roles,
)
from libreevolve.problems.benchmarks.matrix_exhibits import (
    figure9_matrix_diff_artifact_boundary_record,
    matrix_rank_table_artifact_boundary_record,
    validate_figure9_matrix_diff_artifact_boundary,
    validate_matrix_rank_table_artifact_boundary,
)
from libreevolve.problems.benchmarks.matrix_results import (
    matrix_baseline_component_runtime_boundary_record,
    matrix_cascade_run_runtime_boundary_record,
    matrix_headline_historicity_runtime_boundary_record,
    matrix_near_integrality_runtime_boundary_record,
    matrix_scalar_field_runtime_boundary_record,
    matrix_sweep_space_runtime_boundary_record,
    matrix_tensor_rank_runtime_boundary_record,
    validate_strassen_2x2_publication_bundle,
    validate_matrix_baseline_component_runtime_boundary,
    validate_matrix_cascade_run_runtime_boundary,
    validate_matrix_headline_historicity_runtime_boundary,
    validate_matrix_near_integrality_runtime_boundary,
    validate_matrix_scalar_field_runtime_boundary,
    validate_matrix_sweep_space_runtime_boundary,
    validate_matrix_tensor_rank_runtime_boundary,
)


REQUIRED_FIELDS = ("id", "title", "url", "file", "ok", "bytes", "sha256", "message")
SHA256_RE = re.compile(r"[0-9a-f]{64}")
PAPER_ID_RE = re.compile(r"(?:\d{4}\.\d{5}|[a-z0-9][a-z0-9-]{0,94}[a-z0-9])")
ARXIV_ID_RE = re.compile(r"\d{4}\.\d{5}(?:v\d+)?")
PAPER_FILE_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,159}\.pdf")
README_BADGE_RE = re.compile(r"local%20paper%20cache-([A-Za-z0-9]+)(?=-|[?\"'>\s])")
README_COUNT_RE = re.compile(
    r"\b(?:cache of|contains)\s+(\d+)\s+"
    r"(?:papers|(?:locally\s+cached\s+)?pdfs?)\b",
    flags=re.IGNORECASE,
)
LOCAL_PAPER_CACHE_SECTION_RE = re.compile(
    r"<summary><h2>Local Paper Cache\b.*?</details>",
    flags=re.IGNORECASE | re.DOTALL,
)
TODO_COVERAGE_PATH_RE = re.compile(r"`(docs/todo/(?:Completed/)?[A-Za-z0-9_.-]+\.md)`")
COMPLETED_TODO_ITEM_RE = re.compile(r"(?m)^- \[x\] ")
ACTIVE_TODO_GAP_CONTEXT_RE = re.compile(r"(?m)^  - (?:Current gap|Remaining gap|Current evidence):")
ACTIVE_TODO_REQUIRED_RESULT_RE = re.compile(r"(?m)^  - Required result:")
BENCHMARK_IMPLEMENTED_NOT_IMPLEMENTED_RE = re.compile(r"\bnot implemented\b", flags=re.IGNORECASE)
BENCHMARK_IMPLEMENTED_LIMITATION_BOUNDARY_RE = re.compile(
    r"\b(?:but|still|not|no|without|lacks?|missing|remain(?:s)? open|out of scope|smoke-only)\b",
    flags=re.IGNORECASE,
)
LOCAL_ARTIFACT_PATH_RE = re.compile(
    r"`(?:libreevolve/|tests/|README\.md|ROADMAP\.md|papers/|docs/)[^`]+`"
)
BENCHMARK_IMPLEMENTED_LOCAL_ARTIFACT_RE = LOCAL_ARTIFACT_PATH_RE
SOURCE_SPECIFIC_ABSENCE_RE = re.compile(
    r"\bno\s+source-specific\s+([A-Za-z/]+)\s+TODO\b",
    flags=re.IGNORECASE,
)
JSON_DUPLICATE_KEYS_FIELD = "__libreevolve_duplicate_keys__"
MAX_TITLE_CHARS = 240
MAX_DOWNLOAD_MESSAGE_CHARS = 512
PDF_HASH_CHUNK_SIZE = 1024 * 1024
PAPER_DOWNLOAD_CHUNK_SIZE = 1024 * 1024
PAPER_DOWNLOAD_TIMEOUT_SECONDS = 60.0
PAPER_DOWNLOAD_USER_AGENT = "LibreEvolve paper-cache rehydrate/0.1"
ALLOWED_PAPER_URL_HOSTS = frozenset(
    {
        "arxiv.org",
        "www.arxiv.org",
        "web.engr.oregonstate.edu",
    }
)
WINDOWS_RESERVED_NAMES = frozenset(
    {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{index}" for index in range(1, 10)),
        *(f"LPT{index}" for index in range(1, 10)),
    }
)
ACTIVE_TODO_LEDGER_PATHS = (
    "docs/todo/code.md",
    "docs/todo/papers.md",
    "docs/todo/roadmap.md",
    "docs/todo/readme.md",
)
SOURCE_SPECIFIC_TODO_TARGET_PATHS = {
    "code": "docs/todo/code.md",
    "paper": "docs/todo/papers.md",
    "papers": "docs/todo/papers.md",
    "roadmap": "docs/todo/roadmap.md",
    "readme": "docs/todo/readme.md",
}
STATUS_TABLE_HEADER = ("ID", "Title", "Role", "Current LibreEvolve status")
ALLOWED_STATUS_TABLE_ROLES = frozenset(
    {
        "Agentic code-evolution inspiration",
        "AlphaEvolve MARL algorithm-discovery result context",
        "AlphaEvolve compiler-optimization application context",
        "AlphaEvolve complexity-theory result context",
        "AlphaEvolve computer-architecture application context",
        "AlphaEvolve mechanism-design result context",
        "AlphaEvolve-optimized workflow application context",
        "Causal-guidance inspiration",
        "Constructive math benchmark candidate",
        "Domain evolution inspiration",
        "Foundational archive algorithm",
        "Foundational bandit policy",
        "Framework inspiration",
        "Modular search inspiration",
        "Optimization benchmark comparator",
        "Primary specification target",
        "Retrieval/debug loop inspiration",
        "Test-time discovery context",
        "Test-time training inspiration",
    }
)
ALLOWED_STATUS_TABLE_STATUS_PREFIXES = (
    "Background only",
    "Implemented as ",
    "Not implemented as described:",
    "Not implemented; potential future benchmark",
    "Only ",
    "Partially implemented:",
    "Static prompt guidance exists ",
)
STATUS_TABLE_ROLE_STATUS_PREFIXES = {
    "Agentic code-evolution inspiration": ("Not implemented as described:",),
    "AlphaEvolve MARL algorithm-discovery result context": ("Background only",),
    "AlphaEvolve compiler-optimization application context": ("Background only",),
    "AlphaEvolve complexity-theory result context": ("Background only",),
    "AlphaEvolve computer-architecture application context": ("Background only",),
    "AlphaEvolve mechanism-design result context": ("Background only",),
    "AlphaEvolve-optimized workflow application context": ("Background only",),
    "Causal-guidance inspiration": ("Only ",),
    "Constructive math benchmark candidate": ("Not implemented; potential future benchmark",),
    "Domain evolution inspiration": ("Background only",),
    "Foundational archive algorithm": ("Implemented as ",),
    "Foundational bandit policy": ("Implemented as ",),
    "Framework inspiration": ("Not implemented as described:",),
    "Modular search inspiration": ("Static prompt guidance exists ",),
    "Optimization benchmark comparator": ("Not implemented; potential future benchmark",),
    "Primary specification target": ("Partially implemented:",),
    "Retrieval/debug loop inspiration": ("Only ",),
    "Test-time discovery context": ("Background only",),
    "Test-time training inspiration": ("Only ",),
}
STATUS_TABLE_STATUSES_REQUIRING_COMPLETED_EVIDENCE = (
    "Implemented as ",
    "Only ",
    "Partially implemented:",
    "Static prompt guidance exists ",
)
STATUS_TABLE_ALPHAEVOLVE_COMPARABLE_RE = re.compile(r"\bAlphaEvolve-comparable\b", flags=re.IGNORECASE)
STATUS_TABLE_ALPHAEVOLVE_COMPARABLE_BOUNDARY_RE = re.compile(
    r"\b(?:not|no|without|before claiming|requires?|remain(?:s)? open|missing|lacks?)\b"
    r"[^.]{0,160}\bAlphaEvolve-comparable\b"
    r"|\bAlphaEvolve-comparable\b[^.]{0,160}"
    r"\b(?:not|no|without|requires?|remain(?:s)? open|missing|lacks?)\b",
    flags=re.IGNORECASE,
)
STATUS_TABLE_NEGATIVE_IMPLEMENTATION_PREFIXES = (
    "Background only",
    "Not implemented; potential future benchmark",
)
STATUS_TABLE_BACKGROUND_ONLY_PREFIXES = ("Background only",)
STATUS_TABLE_FUTURE_BENCHMARK_PREFIXES = ("Not implemented; potential future benchmark",)
STATUS_TABLE_IMPLEMENTED_STATUS_PREFIXES = ("Implemented as ",)
STATUS_TABLE_LIMITED_STATUS_PREFIXES = ("Only ",)
STATUS_TABLE_PARTIAL_STATUS_PREFIXES = ("Partially implemented:",)
STATUS_TABLE_LIMITATION_BOUNDARY_RE = re.compile(
    r"\b(?:no|not|without|but|while|lacks?|missing|remain(?:s)? open|out of scope|unsupported)\b",
    flags=re.IGNORECASE,
)
STATUS_TABLE_STATIC_GUIDANCE_PREFIXES = ("Static prompt guidance exists ",)
STATUS_TABLE_STATIC_GUIDANCE_EXECUTION_BOUNDARY_RE = re.compile(
    r"\bfalse\s+execution/enforcement\b"
    r"|\b(?:no|not|without)\b[^.]{0,160}"
    r"\b(?:executed|execution|enforced|enforcement)\b",
    flags=re.IGNORECASE,
)
STATUS_TABLE_POSITIVE_IMPLEMENTATION_RE = re.compile(
    r"\b(?:implemented\s+(?:as|local|smoke|support)|implementation\s+exists|"
    r"support\s+exists|is\s+implemented|are\s+implemented|now\s+supports|supports)\b",
    flags=re.IGNORECASE,
)
STATUS_TABLE_NOT_IMPLEMENTED_AS_DESCRIBED_PREFIXES = ("Not implemented as described:",)


@dataclass(frozen=True)
class PaperManifestIssue:
    code: str
    message: str
    row_id: str | None = None


@dataclass(frozen=True)
class ReadmeCountSource:
    source: str
    kind: str
    value: int
    phrase: str


@dataclass(frozen=True)
class PaperAvailability:
    row_id: str
    file: str
    download_ok: bool
    download_message: str
    local_status: str
    git_tracked: bool | None


@dataclass(frozen=True)
class PaperManifestReport:
    ok: bool
    row_count: int
    local_present_count: int
    local_missing_count: int
    local_unique_file_count: int
    availability: list[PaperAvailability]
    issues: list[PaperManifestIssue]


@dataclass(frozen=True)
class PaperRehydrateResult:
    row_id: str
    file: str
    status: str
    bytes: int | None
    sha256: str | None
    message: str


@dataclass(frozen=True)
class PaperRehydrateReport:
    ok: bool
    row_count: int
    verified_existing_count: int
    downloaded_count: int
    failed_count: int
    results: list[PaperRehydrateResult]
    issues: list[PaperManifestIssue]


def validate_paper_manifest(
    root: str | Path = ".",
    *,
    require_local_pdfs: bool = False,
) -> PaperManifestReport:
    root_path = Path(root)
    json_rows, issues = _load_json_manifest(root_path / "papers" / "download_manifest.json", root_path)
    csv_rows, csv_issues = _load_csv_manifest(root_path / "papers" / "download_manifest.csv", root_path)
    issues.extend(csv_issues)

    if len(json_rows) != len(csv_rows):
        issues.append(
            PaperManifestIssue(
                "manifest_count_mismatch",
                f"JSON has {len(json_rows)} rows but CSV has {len(csv_rows)} rows",
            )
        )

    csv_by_id: dict[str, dict[str, Any]] = {}
    for row in csv_rows:
        row_id = str(row.get("id", ""))
        if row_id in csv_by_id:
            issues.append(
                PaperManifestIssue(
                    "duplicate_csv_id",
                    "duplicate CSV paper id",
                    _safe_manifest_label(row_id),
                )
            )
            continue
        csv_by_id[row_id] = row
    git_tracked_files = _git_tracked_files(root_path)
    seen_ids: set[str] = set()
    seen_files: dict[str, str] = {}
    seen_sha256: dict[str, str] = {}
    manifest_file_keys: set[str] = set()
    present_file_keys: set[str] = set()
    local_present_count = 0
    local_missing_count = 0
    availability: list[PaperAvailability] = []

    for index, row in enumerate(json_rows):
        row_id = str(row.get("id", f"row-{index}"))
        row_label = _safe_manifest_label(row_id)
        issues.extend(_validate_row_schema(row, row_label))
        if row_id in seen_ids:
            issues.append(PaperManifestIssue("duplicate_id", "duplicate paper id", row_label))
        seen_ids.add(row_id)

        csv_row = csv_by_id.get(row_id)
        if csv_row is None:
            issues.append(PaperManifestIssue("missing_csv_row", "missing matching CSV row", row_label))
        elif _canonical_row(row) != _canonical_row(csv_row):
            issues.append(PaperManifestIssue("csv_json_mismatch", "CSV row does not match JSON row", row_label))

        sha256 = row.get("sha256")
        if not isinstance(sha256, str) or SHA256_RE.fullmatch(sha256) is None:
            issues.append(
                PaperManifestIssue(
                    "invalid_sha256",
                    "sha256 must be a canonical lowercase 64-hex digest",
                    row_label,
                )
            )
        elif sha256 in seen_sha256:
            issues.append(
                PaperManifestIssue(
                    "duplicate_sha256",
                    f"sha256 also appears in row {seen_sha256[sha256]}",
                    row_label,
                )
            )
        else:
            seen_sha256[sha256] = row_label

        file_value = row.get("file")
        if isinstance(file_value, str):
            paper_path = root_path / file_value
            if not _is_safe_paper_path(file_value):
                issues.append(
                    PaperManifestIssue(
                        "invalid_file_path",
                        "file must be a safe papers/<name>.pdf path",
                        row_label,
                    )
                )
            elif (file_key := _normalized_paper_file_key(file_value)) in seen_files:
                manifest_file_keys.add(file_key)
                issues.append(
                    PaperManifestIssue(
                        "duplicate_file_path",
                        f"file path also appears in row {seen_files[file_key]}",
                        row_label,
                    )
                )
            elif paper_path.exists():
                seen_files[file_key] = row_label
                manifest_file_keys.add(file_key)
                present_file_keys.add(file_key)
                local_present_count += 1
                availability_record = _availability(row, file_value, "present", git_tracked_files)
                availability.append(availability_record)
                if availability_record.git_tracked is True:
                    issues.append(
                        PaperManifestIssue(
                            "tracked_pdf",
                            f"{file_value}: local paper PDFs must stay untracked",
                            row_label,
                        )
                    )
                issues.extend(_validate_local_pdf(row, paper_path, row_label))
            else:
                seen_files[file_key] = row_label
                manifest_file_keys.add(file_key)
                local_missing_count += 1
                availability.append(
                    _availability(row, file_value, "missing", git_tracked_files)
                )
                if require_local_pdfs:
                    issues.append(PaperManifestIssue("missing_pdf", f"missing local PDF {file_value}", row_label))

        if row.get("ok") is False:
            issues.append(PaperManifestIssue("download_failed", "manifest row records a failed download", row_label))

    if require_local_pdfs:
        for file_value in sorted(_local_pdf_files(root_path)):
            if _normalized_paper_file_key(file_value) not in manifest_file_keys:
                issues.append(
                    PaperManifestIssue(
                        "unmanifested_pdf",
                        f"local PDF {file_value} is not listed in the manifests",
                    )
                )

    issues.extend(_validate_appendix_a_matrix_registry_if_present(root_path))
    issues.extend(_validate_appendix_b_registry_if_present(root_path))
    issues.extend(_validate_ablation_registry_if_present(root_path))
    issues.extend(_validate_example_benchmark_scope_records())

    if set(csv_by_id) - seen_ids:
        for row_id in sorted(set(csv_by_id) - seen_ids):
            issues.append(PaperManifestIssue("extra_csv_row", "CSV row has no JSON row", _safe_manifest_label(row_id)))

    status_ids, status_issues = _read_status_table_ids(root_path)
    issues.extend(status_issues)
    if status_ids is not None:
        status_id_set = set(status_ids)
        for row_id in sorted(seen_ids - status_id_set):
            issues.append(
                PaperManifestIssue(
                    "missing_status_table_row",
                    "manifest row is missing from papers/README.md implementation status table",
                    _safe_manifest_label(row_id),
                )
            )
        for row_id in sorted(status_id_set - seen_ids):
            issues.append(
                PaperManifestIssue(
                    "extra_status_table_row",
                    "papers/README.md implementation status row has no manifest row",
                    _safe_manifest_label(row_id),
                )
            )

    expected_count, count_issues = _read_expected_count(root_path)
    issues.extend(count_issues)
    if expected_count is not None and expected_count != len(json_rows):
        issues.append(
            PaperManifestIssue(
                "documented_count_mismatch",
                f"documented paper count is {expected_count} but manifest has {len(json_rows)} rows",
            )
        )
    issues.extend(_validate_root_readme_paper_summary(root_path, seen_ids))
    manifest_rows_by_id = {str(row.get("id")): row for row in json_rows if row.get("id")}
    issues.extend(_validate_paper_source_identity_manifest(root_path, json_rows))
    issues.extend(_validate_alphaevolve_source_pdf_version_manifest(root_path, manifest_rows_by_id))
    issues.extend(_validate_alphaevolve_source_pdf_rights_manifest(root_path, manifest_rows_by_id))
    issues.extend(_validate_alphaevolve_source_pdf_version_record(root_path, manifest_rows_by_id))
    issues.extend(_validate_alphaevolve_source_pdf_rights_record(root_path, manifest_rows_by_id))
    issues.extend(_validate_alphaevolve_references_bibliography(root_path, manifest_rows_by_id, json_rows))
    issues.extend(_validate_alphaevolve_references_section_record(root_path, manifest_rows_by_id))
    issues.extend(_validate_alphaevolve_companion_source_manifest(root_path))
    issues.extend(_validate_alphaevolve_paper_artifact_role_linkage())
    issues.extend(_validate_alphaevolve_follow_on_source_manifest(root_path))
    issues.extend(_validate_alphaevolve_follow_on_repository_rights_manifest(root_path))
    issues.extend(_validate_alphaevolve_follow_on_runtime_absence_manifest(root_path))
    issues.extend(_validate_alphaevolve_follow_on_tao_blog_manifest(root_path))
    issues.extend(_validate_alphaevolve_follow_on_math_source_record(manifest_rows_by_id))
    issues.extend(_validate_alphaevolve_follow_on_problem_coverage_record())
    issues.extend(_validate_alphaevolve_theoretical_cs_source_manifest(root_path))
    issues.extend(_validate_alphaevolve_official_blog_manifest(root_path))
    issues.extend(_validate_todo_coverage_table(root_path, seen_ids, manifest_rows_by_id))
    issues.extend(_validate_todo_absence_wording(root_path, seen_ids))
    issues.extend(_validate_benchmark_coverage_decisions(root_path))

    return PaperManifestReport(
        ok=not issues,
        row_count=len(json_rows),
        local_present_count=local_present_count,
        local_missing_count=local_missing_count,
        local_unique_file_count=len(present_file_keys),
        availability=availability,
        issues=issues,
    )


def _validate_appendix_a_matrix_registry_if_present(root_path: Path) -> list[PaperManifestIssue]:
    try:
        relative_registry = APPENDIX_A_MATRIX_REGISTRY_PATH.relative_to(_repo_root())
    except ValueError:
        relative_registry = Path("libreevolve/problems/benchmarks/alphaevolve_appendix_a_matrix.json")
    registry_path = root_path / relative_registry
    if not registry_path.exists():
        return []
    report = validate_appendix_a_matrix_registry(registry_path)
    issues = [
        PaperManifestIssue(
            f"appendix_a_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.target_id) if issue.target_id else None,
        )
        for issue in report.issues
    ]
    curation_report = validate_appendix_a_matrix_curation(
        appendix_a_matrix_curation_record(registry_path)
    )
    issues.extend(
        PaperManifestIssue(
            f"appendix_a_curation_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.target_id) if issue.target_id else None,
        )
        for issue in curation_report.issues
    )
    baseline_citation_report = validate_appendix_a_matrix_baseline_citation_boundary(
        appendix_a_matrix_baseline_citation_boundary_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"appendix_a_baseline_citation_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.target_id) if issue.target_id else None,
        )
        for issue in baseline_citation_report.issues
    )
    resource_frontier_report = validate_appendix_a_matrix_resource_frontier(
        appendix_a_matrix_resource_frontier_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"appendix_a_resource_frontier_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.attempt_id) if issue.attempt_id else None,
        )
        for issue in resource_frontier_report.issues
    )
    local_resource_frontier_report = validate_appendix_a_matrix_local_resource_frontier(
        appendix_a_matrix_local_resource_frontier_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"appendix_a_local_resource_frontier_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.attempt_id) if issue.attempt_id else None,
        )
        for issue in local_resource_frontier_report.issues
    )
    subset_scope_artifact_report = validate_appendix_a_matrix_subset_scope_artifact_boundary(
        appendix_a_matrix_subset_scope_artifact_boundary_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"appendix_a_subset_scope_artifact_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.subset_id) if issue.subset_id else None,
        )
        for issue in subset_scope_artifact_report.issues
    )
    row_note_artifact_report = validate_appendix_a_matrix_row_note_artifact_boundary(
        appendix_a_matrix_row_note_artifact_boundary_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"appendix_a_row_note_artifact_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.note_id) if issue.note_id else None,
        )
        for issue in row_note_artifact_report.issues
    )
    strassen_bundle_report = validate_strassen_2x2_publication_bundle()
    issues.extend(
        PaperManifestIssue(
            f"matrix_strassen_bundle_{issue.code}",
            issue.message,
        )
        for issue in strassen_bundle_report.issues
    )
    baseline_component_runtime_report = validate_matrix_baseline_component_runtime_boundary(
        matrix_baseline_component_runtime_boundary_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_baseline_component_runtime_{issue.code}",
            issue.message,
        )
        for issue in baseline_component_runtime_report.issues
    )
    cascade_run_runtime_report = validate_matrix_cascade_run_runtime_boundary(
        matrix_cascade_run_runtime_boundary_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_cascade_run_runtime_{issue.code}",
            issue.message,
        )
        for issue in cascade_run_runtime_report.issues
    )
    near_integrality_runtime_report = validate_matrix_near_integrality_runtime_boundary(
        matrix_near_integrality_runtime_boundary_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_near_integrality_runtime_{issue.code}",
            issue.message,
        )
        for issue in near_integrality_runtime_report.issues
    )
    scalar_field_runtime_report = validate_matrix_scalar_field_runtime_boundary(
        matrix_scalar_field_runtime_boundary_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_scalar_field_runtime_{issue.code}",
            issue.message,
        )
        for issue in scalar_field_runtime_report.issues
    )
    sweep_space_runtime_report = validate_matrix_sweep_space_runtime_boundary(
        matrix_sweep_space_runtime_boundary_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_sweep_space_runtime_{issue.code}",
            issue.message,
        )
        for issue in sweep_space_runtime_report.issues
    )
    tensor_rank_runtime_report = validate_matrix_tensor_rank_runtime_boundary(
        matrix_tensor_rank_runtime_boundary_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_tensor_rank_runtime_{issue.code}",
            issue.message,
        )
        for issue in tensor_rank_runtime_report.issues
    )
    headline_runtime_report = validate_matrix_headline_historicity_runtime_boundary(
        matrix_headline_historicity_runtime_boundary_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_headline_historicity_runtime_{issue.code}",
            issue.message,
        )
        for issue in headline_runtime_report.issues
    )
    rank_table_artifact_report = validate_matrix_rank_table_artifact_boundary(
        matrix_rank_table_artifact_boundary_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_rank_table_artifact_{issue.code}",
            issue.message,
        )
        for issue in rank_table_artifact_report.issues
    )
    figure9_artifact_report = validate_figure9_matrix_diff_artifact_boundary(
        figure9_matrix_diff_artifact_boundary_record()
    )
    issues.extend(
        PaperManifestIssue(
            f"figure9_matrix_diff_artifact_{issue.code}",
            issue.message,
        )
        for issue in figure9_artifact_report.issues
    )
    return issues


def _validate_appendix_b_registry_if_present(root_path: Path) -> list[PaperManifestIssue]:
    try:
        relative_registry = APPENDIX_B_REGISTRY_PATH.relative_to(_repo_root())
    except ValueError:
        relative_registry = Path("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json")
    registry_path = root_path / relative_registry
    if not registry_path.exists():
        return []
    report = validate_appendix_b_registry(registry_path, repo_root=root_path)
    return [
        PaperManifestIssue(
            f"appendix_b_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.family_id) if issue.family_id else None,
        )
        for issue in report.issues
    ]


def _validate_ablation_registry_if_present(root_path: Path) -> list[PaperManifestIssue]:
    try:
        relative_registry = ABLATION_REGISTRY_PATH.relative_to(_repo_root())
    except ValueError:
        relative_registry = Path("libreevolve/problems/benchmarks/alphaevolve_ablations.json")
    registry_path = root_path / relative_registry
    if not registry_path.exists():
        return []
    report = validate_ablation_registry(registry_path)
    return [
        PaperManifestIssue(
            f"ablation_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.variant_id) if issue.variant_id else None,
        )
        for issue in report.issues
    ]


def _validate_example_benchmark_scope_records() -> list[PaperManifestIssue]:
    report = validate_example_benchmark_scope(example_benchmark_scope_records())
    return [
        PaperManifestIssue(
            f"example_scope_{issue.code}",
            issue.message,
        )
        for issue in report.issues
    ]


def _validate_paper_source_identity_manifest(
    root_path: Path,
    manifest_rows: list[dict[str, Any]],
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / PAPER_SOURCE_IDENTITY_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "paper_source_identity_manifest_missing",
                    "papers/row_identity.json must emit source-identity rows for the paper cache",
                )
            ]
        return []
    report = validate_paper_source_identity_manifest(
        manifest_path,
        manifest_rows=manifest_rows,
    )
    return [
        PaperManifestIssue(
            f"paper_source_identity_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.row_id) if issue.row_id else None,
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_source_pdf_version_manifest(
    root_path: Path,
    manifest_rows_by_id: dict[str, dict[str, Any]],
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_SOURCE_VERSION_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_source_pdf_version_manifest_missing",
                    "papers/source_versions.json must emit the AlphaEvolve source-version row",
                    "2506.13131",
                )
            ]
        return []
    first_page_text = None
    if is_repo_root:
        pdf_path = root_path / "papers/2506.13131__AlphaEvolve.pdf"
        if pdf_path.exists():
            try:
                first_page_text = _read_pdf_quietly(pdf_path).pages[0].extract_text() or ""
            except Exception as exc:
                return [
                    PaperManifestIssue(
                        "alphaevolve_source_pdf_version_manifest_header_read_error",
                        _safe_pdf_parse_error(exc),
                        "2506.13131",
                    )
                ]
    report = validate_alphaevolve_source_pdf_version_manifest(
        manifest_path,
        first_page_text=first_page_text,
    )
    issues = [
        PaperManifestIssue(
            f"alphaevolve_source_pdf_version_manifest_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]
    record = alphaevolve_source_pdf_version_record()
    row = manifest_rows_by_id.get("2506.13131")
    if row is None:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_source_pdf_version_manifest_missing_manifest_row",
                "source-version manifest requires a matching paper manifest row",
                "2506.13131",
            )
        )
        return issues
    manifest_row = record["manifest_row"]
    for field in ("id", "title", "url", "file", "bytes", "sha256"):
        if row.get(field) != manifest_row[field]:
            issues.append(
                PaperManifestIssue(
                    f"alphaevolve_source_pdf_version_manifest_{field}_mismatch",
                    f"paper manifest row {field} does not match papers/source_versions.json",
                    "2506.13131",
                )
            )
    return issues


def _validate_alphaevolve_source_pdf_rights_manifest(
    root_path: Path,
    manifest_rows_by_id: dict[str, dict[str, Any]],
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_SOURCE_RIGHTS_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_source_pdf_rights_manifest_missing",
                    "papers/source_rights.json must emit AlphaEvolve source-rights rows",
                    "2506.13131",
                )
            ]
        return []
    first_page_text = None
    if is_repo_root:
        pdf_path = root_path / "papers/2506.13131__AlphaEvolve.pdf"
        if pdf_path.exists():
            try:
                first_page_text = _read_pdf_quietly(pdf_path).pages[0].extract_text() or ""
            except Exception as exc:
                return [
                    PaperManifestIssue(
                        "alphaevolve_source_pdf_rights_manifest_text_read_error",
                        _safe_pdf_parse_error(exc),
                        "2506.13131",
                    )
                ]
    report = validate_alphaevolve_source_pdf_rights_manifest(
        manifest_path,
        first_page_text=first_page_text,
    )
    issues = [
        PaperManifestIssue(
            f"alphaevolve_source_pdf_rights_manifest_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]
    record = alphaevolve_source_pdf_rights_record()
    row = manifest_rows_by_id.get("2506.13131")
    if row is None:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_source_pdf_rights_manifest_missing_manifest_row",
                "source-rights manifest requires a matching paper manifest row",
                "2506.13131",
            )
        )
        return issues
    manifest_row = record["manifest_row"]
    for field in ("id", "title", "url", "file", "bytes", "sha256"):
        if row.get(field) != manifest_row[field]:
            issues.append(
                PaperManifestIssue(
                    f"alphaevolve_source_pdf_rights_manifest_{field}_mismatch",
                    f"paper manifest row {field} does not match papers/source_rights.json",
                    "2506.13131",
                )
            )
    return issues


def _validate_alphaevolve_source_pdf_version_record(
    root_path: Path,
    manifest_rows_by_id: dict[str, dict[str, Any]],
) -> list[PaperManifestIssue]:
    record = alphaevolve_source_pdf_version_record()
    report = validate_alphaevolve_source_pdf_version(record)
    issues = [
        PaperManifestIssue(
            f"alphaevolve_source_pdf_version_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    if not is_repo_root:
        return issues
    row = manifest_rows_by_id.get("2506.13131")
    if row is None:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_source_pdf_version_missing_manifest_row",
                "AlphaEvolve source-version record requires a matching manifest row",
                "2506.13131",
            )
        )
        return issues
    manifest_row = record["manifest_row"]
    for field in ("id", "title", "url", "file", "bytes", "sha256"):
        if row.get(field) != manifest_row[field]:
            issues.append(
                PaperManifestIssue(
                    f"alphaevolve_source_pdf_version_manifest_{field}_mismatch",
                    f"manifest row {field} does not match the source-version record",
                    "2506.13131",
                )
            )
    file_value = row.get("file")
    if isinstance(file_value, str):
        pdf_path = root_path / file_value
        if pdf_path.exists():
            try:
                first_page_text = _read_pdf_quietly(pdf_path).pages[0].extract_text() or ""
            except Exception as exc:
                issues.append(
                    PaperManifestIssue(
                        "alphaevolve_source_pdf_version_header_read_error",
                        _safe_pdf_parse_error(exc),
                        "2506.13131",
                    )
                )
            else:
                header_report = validate_alphaevolve_source_pdf_version(
                    record,
                    first_page_text=first_page_text,
                )
                issues.extend(
                    PaperManifestIssue(
                        f"alphaevolve_source_pdf_version_{issue.code}",
                        issue.message,
                        "2506.13131",
                    )
                    for issue in header_report.issues
                )
    return issues


def _validate_alphaevolve_source_pdf_rights_record(
    root_path: Path,
    manifest_rows_by_id: dict[str, dict[str, Any]],
) -> list[PaperManifestIssue]:
    record = alphaevolve_source_pdf_rights_record()
    report = validate_alphaevolve_source_pdf_rights(record)
    issues = [
        PaperManifestIssue(
            f"alphaevolve_source_pdf_rights_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    if not is_repo_root:
        return issues
    row = manifest_rows_by_id.get("2506.13131")
    if row is None:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_source_pdf_rights_missing_manifest_row",
                "AlphaEvolve source-rights record requires a matching manifest row",
                "2506.13131",
            )
        )
        return issues
    manifest_row = record["manifest_row"]
    for field in ("id", "title", "url", "file", "bytes", "sha256"):
        if row.get(field) != manifest_row[field]:
            issues.append(
                PaperManifestIssue(
                    f"alphaevolve_source_pdf_rights_manifest_{field}_mismatch",
                    f"manifest row {field} does not match the source-rights record",
                    "2506.13131",
                )
            )
    file_value = row.get("file")
    if isinstance(file_value, str):
        pdf_path = root_path / file_value
        if pdf_path.exists():
            try:
                first_page_text = _read_pdf_quietly(pdf_path).pages[0].extract_text() or ""
            except Exception as exc:
                issues.append(
                    PaperManifestIssue(
                        "alphaevolve_source_pdf_rights_text_read_error",
                        _safe_pdf_parse_error(exc),
                        "2506.13131",
                    )
                )
            else:
                rights_report = validate_alphaevolve_source_pdf_rights(
                    record,
                    first_page_text=first_page_text,
                )
                issues.extend(
                    PaperManifestIssue(
                        f"alphaevolve_source_pdf_rights_{issue.code}",
                        issue.message,
                        "2506.13131",
                    )
                    for issue in rights_report.issues
                )
    return issues


def _validate_alphaevolve_references_bibliography(
    root_path: Path,
    manifest_rows_by_id: dict[str, dict[str, Any]],
    manifest_rows: list[dict[str, Any]],
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    bibliography_path = root_path / EXPECTED_REFERENCES_BIBLIOGRAPHY_FILE
    if not bibliography_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_references_bibliography_missing",
                    "papers/references.json must emit normalized AlphaEvolve bibliography rows",
                    "2506.13131",
                )
            ]
        return []
    page_text_by_number = None
    if is_repo_root:
        row = manifest_rows_by_id.get("2506.13131")
        file_value = row.get("file") if isinstance(row, dict) else None
        if isinstance(file_value, str):
            pdf_path = root_path / file_value
            if pdf_path.exists():
                try:
                    reader = _read_pdf_quietly(pdf_path)
                    page_text_by_number = {
                        page_number: reader.pages[page_number - 1].extract_text() or ""
                        for page_number in range(23, 34)
                    }
                except Exception as exc:
                    return [
                        PaperManifestIssue(
                            "alphaevolve_references_bibliography_read_error",
                            _safe_pdf_parse_error(exc),
                            "2506.13131",
                        )
                    ]
    report = validate_alphaevolve_references_bibliography(
        bibliography_path,
        page_text_by_number=page_text_by_number,
        manifest_rows=manifest_rows,
    )
    return [
        PaperManifestIssue(
            f"alphaevolve_references_bibliography_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.reference_id) if issue.reference_id else "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_references_section_record(
    root_path: Path,
    manifest_rows_by_id: dict[str, dict[str, Any]],
) -> list[PaperManifestIssue]:
    record = alphaevolve_references_section_record()
    report = validate_alphaevolve_references_section(record)
    issues = [
        PaperManifestIssue(
            f"alphaevolve_references_section_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.reference_id) if issue.reference_id else "2506.13131",
        )
        for issue in report.issues
    ]
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    if not is_repo_root:
        return issues
    row = manifest_rows_by_id.get("2506.13131")
    if row is None:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_references_section_missing_manifest_row",
                "AlphaEvolve references-section record requires a matching manifest row",
                "2506.13131",
            )
        )
        return issues
    file_value = row.get("file")
    if isinstance(file_value, str):
        pdf_path = root_path / file_value
        if pdf_path.exists():
            try:
                reader = _read_pdf_quietly(pdf_path)
                page_text_by_number = {
                    page_number: reader.pages[page_number - 1].extract_text() or ""
                    for page_number in range(23, 33)
                }
            except Exception as exc:
                issues.append(
                    PaperManifestIssue(
                        "alphaevolve_references_section_read_error",
                        _safe_pdf_parse_error(exc),
                        "2506.13131",
                    )
                )
            else:
                references_report = validate_alphaevolve_references_section(
                    record,
                    page_text_by_number=page_text_by_number,
                )
                issues.extend(
                    PaperManifestIssue(
                        f"alphaevolve_references_section_{issue.code}",
                        issue.message,
                        _safe_manifest_label(issue.reference_id) if issue.reference_id else "2506.13131",
                    )
                    for issue in references_report.issues
                )
    return issues


def _validate_alphaevolve_companion_source_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_COMPANION_SOURCE_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_companion_source_manifest_missing",
                    "papers/companion_sources.json must emit the AlphaEvolve companion Colab source row",
                    "2506.13131",
                )
            ]
        return []
    report = validate_alphaevolve_companion_source_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_companion_source_manifest_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_follow_on_math_source_record(
    manifest_rows_by_id: dict[str, dict[str, Any]],
) -> list[PaperManifestIssue]:
    record = alphaevolve_follow_on_math_source_record()
    report = validate_alphaevolve_follow_on_math_source(record)
    issues = [
        PaperManifestIssue(
            f"alphaevolve_follow_on_math_source_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2511.02864",
        )
        for issue in report.issues
    ]
    if "2511.02864" in manifest_rows_by_id:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_follow_on_math_source_manifest_cache_boundary_mismatch",
                "Follow-on source record says arXiv 2511.02864 is not locally cached, but a manifest row exists",
                "2511.02864",
            )
        )
    return issues


def _validate_alphaevolve_paper_artifact_role_linkage() -> list[PaperManifestIssue]:
    role_recordset = alphaevolve_paper_artifact_role_records()
    role_report = validate_paper_artifact_roles(role_recordset)
    issues = [
        PaperManifestIssue(
            f"alphaevolve_paper_artifact_roles_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.artifact_id) if issue.artifact_id else None,
        )
        for issue in role_report.issues
    ]
    linkage_report = validate_paper_artifact_linkage(
        alphaevolve_paper_artifact_linkage_record(role_recordset),
        role_recordset,
    )
    issues.extend(
        PaperManifestIssue(
            f"alphaevolve_paper_artifact_linkage_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.artifact_id) if issue.artifact_id else None,
        )
        for issue in linkage_report.issues
    )
    return issues


def _validate_alphaevolve_follow_on_source_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_follow_on_source_manifest_missing",
                    "papers/follow_on_sources.json must emit the AlphaEvolve follow-on math source row",
                    "2511.02864",
                )
            ]
        return []
    report = validate_alphaevolve_follow_on_source_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_follow_on_source_manifest_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2511.02864",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_follow_on_repository_rights_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_FOLLOW_ON_REPOSITORY_RIGHTS_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_follow_on_repository_rights_manifest_missing",
                    "papers/follow_on_repository_rights.json must emit the problem repository rights row",
                    "2511.02864",
                )
            ]
        return []
    report = validate_alphaevolve_follow_on_repository_rights_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_follow_on_repository_rights_manifest_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2511.02864",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_follow_on_runtime_absence_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_follow_on_runtime_absence_manifest_missing",
                    "papers/follow_on_runtime_absence.json must emit the problem repository runtime-absence row",
                    "2511.02864",
                )
            ]
        return []
    report = validate_alphaevolve_follow_on_runtime_absence_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_follow_on_runtime_absence_manifest_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2511.02864",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_follow_on_tao_blog_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_FOLLOW_ON_TAO_BLOG_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_follow_on_tao_blog_manifest_missing",
                    "papers/follow_on_tao_blog.json must emit the Terence Tao follow-on blog source row",
                    "2511.02864",
                )
            ]
        return []
    report = validate_alphaevolve_follow_on_tao_blog_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_follow_on_tao_blog_manifest_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2511.02864",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_follow_on_problem_coverage_record() -> list[PaperManifestIssue]:
    report = validate_alphaevolve_follow_on_problem_coverage(
        alphaevolve_follow_on_problem_coverage_record()
    )
    return [
        PaperManifestIssue(
            f"alphaevolve_follow_on_problem_coverage_{issue.code}",
            issue.message,
            str(issue.problem_id) if issue.problem_id is not None else "2511.02864",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_theoretical_cs_source_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_THEORETICAL_CS_SOURCE_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_theoretical_cs_source_manifest_missing",
                    "papers/theoretical_cs_sources.json must emit the theoretical-CS proof-element source row",
                    "2509.18057",
                )
            ]
        return []
    report = validate_alphaevolve_theoretical_cs_source_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_theoretical_cs_source_manifest_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2509.18057",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_official_blog_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_OFFICIAL_BLOG_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_official_blog_manifest_missing",
                    "papers/official_deepmind_blog.json must emit the official DeepMind announcement source row",
                    "2506.13131",
                )
            ]
        return []
    report = validate_alphaevolve_official_blog_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_official_blog_manifest_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2506.13131",
        )
        for issue in report.issues
    ]


def rehydrate_paper_cache(
    root: str | Path = ".",
    *,
    force: bool = False,
    timeout: float = PAPER_DOWNLOAD_TIMEOUT_SECONDS,
) -> PaperRehydrateReport:
    root_path = Path(root)
    rows, issues = _load_rehydrate_rows(root_path)
    if timeout <= 0:
        issues.append(PaperManifestIssue("invalid_download_timeout", "download timeout must be positive"))
    if issues:
        return PaperRehydrateReport(
            ok=False,
            row_count=len(rows),
            verified_existing_count=0,
            downloaded_count=0,
            failed_count=0,
            results=[],
            issues=issues,
        )

    results: list[PaperRehydrateResult] = []
    for row in rows:
        row_id = _safe_manifest_label(str(row["id"]))
        file_value = str(row["file"])
        target = root_path / file_value
        if row["ok"] is not True:
            results.append(
                PaperRehydrateResult(
                    row_id=row_id,
                    file=file_value,
                    status="failed",
                    bytes=None,
                    sha256=None,
                    message=_sanitize_download_message(
                        f"manifest row records failed download: {row['message']}"
                    ),
                )
            )
            continue

        existing = _existing_rehydrate_match(row, target, row_id)
        if existing.status == "verified_existing" and not force:
            results.append(existing)
            continue
        if existing.status == "failed":
            results.append(existing)
            continue

        results.append(_download_rehydrate_row(row, root_path, timeout))

    verified_existing_count = sum(1 for result in results if result.status == "verified_existing")
    downloaded_count = sum(1 for result in results if result.status == "downloaded")
    failed_count = sum(1 for result in results if result.status == "failed")
    return PaperRehydrateReport(
        ok=failed_count == 0,
        row_count=len(rows),
        verified_existing_count=verified_existing_count,
        downloaded_count=downloaded_count,
        failed_count=failed_count,
        results=results,
        issues=[],
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the committed paper cache manifests.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to the current directory.")
    parser.add_argument(
        "--require-local-pdfs",
        action="store_true",
        help="Fail when ignored local PDF cache files are absent.",
    )
    parser.add_argument(
        "--rehydrate",
        action="store_true",
        help="Download missing or forced local paper PDFs from the committed manifests.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="With --rehydrate, redownload files even when byte count and SHA-256 already match.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=PAPER_DOWNLOAD_TIMEOUT_SECONDS,
        help=f"Per-paper download timeout in seconds for --rehydrate. Defaults to {PAPER_DOWNLOAD_TIMEOUT_SECONDS:g}.",
    )
    parser.add_argument("--json", action="store_true", help="Print the report as JSON.")
    args = parser.parse_args(argv)

    if args.force and not args.rehydrate:
        parser.error("--force requires --rehydrate")
    if args.rehydrate:
        report = rehydrate_paper_cache(args.root, force=args.force, timeout=args.timeout)
        if args.json:
            print(json.dumps(_rehydrate_report_to_dict(report), indent=2, sort_keys=True))
        else:
            print(
                "paper cache rehydrate: "
                f"{report.row_count} rows, "
                f"{report.verified_existing_count} existing verified, "
                f"{report.downloaded_count} downloaded, "
                f"{report.failed_count} failed"
            )
            for issue in report.issues:
                prefix = f"{issue.row_id}: " if issue.row_id else ""
                print(f"{issue.code}: {prefix}{issue.message}")
            for result in report.results:
                if result.status == "failed":
                    print(f"failed: {result.row_id}: {result.file}: {result.message}")
        return 0 if report.ok else 1

    report = validate_paper_manifest(args.root, require_local_pdfs=args.require_local_pdfs)
    if args.json:
        print(json.dumps(_report_to_dict(report), indent=2, sort_keys=True))
    else:
        print(
            "paper manifest: "
            f"{report.row_count} rows, "
            f"{report.local_unique_file_count} unique local PDFs, "
            f"{report.local_present_count} local PDFs present, "
            f"{report.local_missing_count} missing"
        )
        for issue in report.issues:
            prefix = f"{issue.row_id}: " if issue.row_id else ""
            print(f"{issue.code}: {prefix}{issue.message}")
    return 0 if report.ok else 1


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_rehydrate_rows(root: Path) -> tuple[list[dict[str, Any]], list[PaperManifestIssue]]:
    json_rows, issues = _load_json_manifest(root / "papers" / "download_manifest.json", root)
    csv_rows, csv_issues = _load_csv_manifest(root / "papers" / "download_manifest.csv", root)
    issues.extend(csv_issues)

    if len(json_rows) != len(csv_rows):
        issues.append(
            PaperManifestIssue(
                "manifest_count_mismatch",
                f"JSON has {len(json_rows)} rows but CSV has {len(csv_rows)} rows",
            )
        )
    csv_by_id: dict[str, dict[str, Any]] = {}
    for row in csv_rows:
        row_id = str(row.get("id", ""))
        if row_id in csv_by_id:
            issues.append(PaperManifestIssue("duplicate_csv_id", "duplicate CSV paper id", _safe_manifest_label(row_id)))
            continue
        csv_by_id[row_id] = row

    seen_ids: set[str] = set()
    seen_files: dict[str, str] = {}
    seen_sha256: dict[str, str] = {}
    for index, row in enumerate(json_rows):
        row_id = str(row.get("id", f"row-{index}"))
        row_label = _safe_manifest_label(row_id)
        issues.extend(_validate_row_schema(row, row_label))
        if row_id in seen_ids:
            issues.append(PaperManifestIssue("duplicate_id", "duplicate paper id", row_label))
        seen_ids.add(row_id)

        csv_row = csv_by_id.get(row_id)
        if csv_row is None:
            issues.append(PaperManifestIssue("missing_csv_row", "missing matching CSV row", row_label))
        elif _canonical_row(row) != _canonical_row(csv_row):
            issues.append(PaperManifestIssue("csv_json_mismatch", "CSV row does not match JSON row", row_label))

        file_value = row.get("file")
        if isinstance(file_value, str) and _is_safe_paper_path(file_value):
            file_key = _normalized_paper_file_key(file_value)
            if file_key in seen_files:
                issues.append(
                    PaperManifestIssue(
                        "duplicate_file_path",
                        f"file path also appears in row {seen_files[file_key]}",
                        row_label,
                    )
                )
            else:
                seen_files[file_key] = row_label

        sha256 = row.get("sha256")
        if isinstance(sha256, str) and SHA256_RE.fullmatch(sha256):
            if sha256 in seen_sha256:
                issues.append(
                    PaperManifestIssue(
                        "duplicate_sha256",
                        f"sha256 also appears in row {seen_sha256[sha256]}",
                        row_label,
                    )
                )
            else:
                seen_sha256[sha256] = row_label

    for row_id in sorted(set(csv_by_id) - seen_ids):
        issues.append(PaperManifestIssue("extra_csv_row", "CSV row has no JSON row", _safe_manifest_label(row_id)))
    return json_rows, issues


def _load_json_manifest(path: Path, root: Path) -> tuple[list[dict[str, Any]], list[PaperManifestIssue]]:
    issues: list[PaperManifestIssue] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_json_object_without_duplicate_keys)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [], [PaperManifestIssue("json_manifest_unreadable", _manifest_diagnostic(path, root, exc))]
    if not isinstance(data, list):
        return [], [PaperManifestIssue("json_manifest_schema", "JSON manifest must be a list")]
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(data):
        if isinstance(item, dict):
            row_id = str(item.get("id") or f"row-{index}")
            for key in item.pop(JSON_DUPLICATE_KEYS_FIELD, ()):
                issues.append(
                    PaperManifestIssue(
                        "duplicate_json_key",
                        f"duplicate JSON key {key!r}",
                        _safe_manifest_label(row_id),
                    )
                )
            rows.append(item)
        else:
            issues.append(PaperManifestIssue("json_row_schema", "JSON row must be an object", f"row-{index}"))
    return rows, issues


def _load_csv_manifest(path: Path, root: Path) -> tuple[list[dict[str, Any]], list[PaperManifestIssue]]:
    issues: list[PaperManifestIssue] = []
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, strict=True)
            fieldnames = list(reader.fieldnames or [])
            issues.extend(_validate_csv_header(fieldnames))
            rows = list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        return [], [PaperManifestIssue("csv_manifest_unreadable", _manifest_diagnostic(path, root, exc))]
    normalized_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        row_id = str(row.get("id") or f"row-{index}")
        try:
            normalized_rows.append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "url": row["url"],
                    "file": row["file"],
                    "ok": _parse_csv_bool(row["ok"]),
                    "bytes": int(row["bytes"]),
                    "sha256": row["sha256"],
                    "message": row["message"],
                }
            )
        except (KeyError, TypeError, ValueError) as exc:
            issues.append(PaperManifestIssue("csv_row_schema", f"invalid CSV row: {exc}", row_id))
    return normalized_rows, issues


def _validate_row_schema(row: dict[str, Any], row_id: str) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    missing = [field for field in REQUIRED_FIELDS if field not in row]
    if missing:
        issues.append(PaperManifestIssue("missing_fields", f"missing fields {missing}", row_id))
    extra = sorted(set(row) - set(REQUIRED_FIELDS))
    for field in extra:
        issues.append(
            PaperManifestIssue(
                "unsupported_json_field",
                f"unsupported JSON field {_safe_manifest_label(field)!r}",
                row_id,
            )
        )
    for field in ("id", "title", "url", "file", "sha256", "message"):
        if field in row and not isinstance(row[field], str):
            issues.append(PaperManifestIssue("invalid_field_type", f"{field} must be a string", row_id))
    if "ok" in row and not isinstance(row["ok"], bool):
        issues.append(PaperManifestIssue("invalid_field_type", "ok must be boolean", row_id))
    if "bytes" in row and (isinstance(row["bytes"], bool) or not isinstance(row["bytes"], int) or row["bytes"] < 0):
        issues.append(PaperManifestIssue("invalid_field_type", "bytes must be a non-negative integer", row_id))
    if isinstance(row.get("id"), str):
        issues.extend(_validate_paper_id(row["id"], row_id))
    if isinstance(row.get("title"), str):
        issues.extend(_validate_paper_title(row["title"], row_id))
    if isinstance(row.get("url"), str):
        issues.extend(_validate_paper_url(row["url"], row_id))
    if (
        isinstance(row.get("id"), str)
        and isinstance(row.get("url"), str)
        and isinstance(row.get("file"), str)
    ):
        issues.extend(_validate_paper_row_identity(row["id"], row["url"], row["file"], row_id))
    if isinstance(row.get("message"), str):
        issues.extend(_validate_download_message(row["message"], row_id))
    return issues


def _validate_local_pdf(row: dict[str, Any], path: Path, row_id: str) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    expected_bytes = row.get("bytes")
    expected_sha = row.get("sha256")
    file_label = _paper_file_label(row, path)
    try:
        if _is_link_backed_path(path):
            issues.append(
                PaperManifestIssue(
                    "linked_pdf",
                    f"{file_label}: local PDF must not be a symlink or reparse-point entry",
                    row_id,
                )
            )
            return issues
    except OSError as exc:
        issues.append(
            PaperManifestIssue(
                "local_pdf_stat_error",
                f"{file_label}: could not inspect local PDF link state: {redact_sensitive_text(str(exc))}",
                row_id,
            )
        )
        return issues
    try:
        local_stat = path.stat()
    except OSError as exc:
        issues.append(
            PaperManifestIssue(
                "local_pdf_stat_error",
                f"{file_label}: could not inspect local PDF: {redact_sensitive_text(str(exc))}",
                row_id,
            )
        )
        return issues
    if not stat.S_ISREG(local_stat.st_mode):
        issues.append(
            PaperManifestIssue(
                "local_pdf_not_file",
                f"{file_label}: local PDF must be a regular file",
                row_id,
            )
        )
        return issues
    actual_bytes = local_stat.st_size
    if isinstance(expected_bytes, int) and actual_bytes != expected_bytes:
        issues.append(
            PaperManifestIssue(
                "byte_count_mismatch",
                f"expected {expected_bytes} bytes but found {actual_bytes}",
                row_id,
            )
        )
    try:
        if not _has_pdf_header(path):
            issues.append(
                PaperManifestIssue(
                    "invalid_pdf_header",
                    f"{file_label}: local PDF does not start with %PDF-",
                    row_id,
                )
            )
    except OSError as exc:
        issues.append(
            PaperManifestIssue(
                "local_pdf_read_error",
                f"{file_label}: could not read local PDF header: {redact_sensitive_text(str(exc))}",
                row_id,
            )
        )
        return issues
    try:
        reader = _read_pdf_quietly(path)
        if len(reader.pages) < 1:
            issues.append(
                PaperManifestIssue(
                    "invalid_pdf_structure",
                    f"{file_label}: local PDF has no readable pages",
                    row_id,
                )
            )
    except Exception as exc:
        issues.append(
            PaperManifestIssue(
                "invalid_pdf_structure",
                f"{file_label}: local PDF could not be parsed: {_safe_pdf_parse_error(exc)}",
                row_id,
            )
        )
        return issues
    if isinstance(expected_sha, str) and SHA256_RE.fullmatch(expected_sha):
        try:
            actual_sha = _sha256_file(path)
        except OSError as exc:
            issues.append(
                PaperManifestIssue(
                    "local_pdf_read_error",
                    f"{file_label}: could not read local PDF: {redact_sensitive_text(str(exc))}",
                    row_id,
                )
            )
            return issues
        if actual_sha != expected_sha:
            issues.append(PaperManifestIssue("sha256_mismatch", "local PDF digest does not match manifest", row_id))
    return issues


def _read_expected_count(root: Path) -> tuple[int | None, list[PaperManifestIssue]]:
    count_sources: list[ReadmeCountSource] = []
    issues: list[PaperManifestIssue] = []
    for relative_path in (Path("README.md"), Path("papers") / "README.md"):
        path = root / relative_path
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(
                PaperManifestIssue(
                    "readme_count_source_unreadable",
                    _manifest_diagnostic(path, root, exc),
                )
            )
            continue
        for match in README_COUNT_RE.finditer(text):
            count_sources.append(
                ReadmeCountSource(
                    source=relative_path.as_posix(),
                    kind="prose",
                    value=int(match.group(1)),
                    phrase=match.group(0),
                )
            )
        if relative_path == Path("README.md"):
            for match in README_BADGE_RE.finditer(text):
                raw_count = match.group(1)
                if raw_count.isdigit():
                    count_sources.append(
                        ReadmeCountSource(
                            source=relative_path.as_posix(),
                            kind="badge",
                            value=int(raw_count),
                            phrase="local paper cache badge",
                        )
                    )
                else:
                    issues.append(
                        PaperManifestIssue(
                            "malformed_paper_count_badge",
                            "README local paper cache badge count must be numeric",
                        )
                    )
    counts = {source.value for source in count_sources}
    if len(counts) == 1:
        return next(iter(counts)), issues
    if len(counts) > 1:
        issues.append(
            PaperManifestIssue(
                "documented_count_conflict",
                "documented paper counts disagree: "
                + "; ".join(_format_count_source(source) for source in count_sources),
            )
        )
    return None, issues


def _validate_root_readme_paper_summary(root: Path, manifest_ids: set[str]) -> list[PaperManifestIssue]:
    path = root / "README.md"
    if not path.exists() or not manifest_ids:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    section_match = LOCAL_PAPER_CACHE_SECTION_RE.search(text)
    section = section_match.group(0) if section_match else text
    summary_ids = {row_id for row_id in manifest_ids if row_id in section}
    if not summary_ids:
        return []
    if manifest_ids <= summary_ids:
        return []

    normalized_section = section.casefold()
    has_curated_marker = (
        "curated subset" in normalized_section
        and "papers/readme.md" in normalized_section
        and "complete implementation-status index" in normalized_section
    )
    if has_curated_marker:
        return []
    return [
        PaperManifestIssue(
            "readme_paper_summary_incomplete",
            "README.md local paper cache lists "
            f"{len(summary_ids)} of {len(manifest_ids)} manifest ids without saying the tables are a "
            "curated subset and papers/README.md is the complete implementation-status index",
        )
    ]


def _validate_todo_coverage_table(
    root: Path,
    manifest_ids: set[str],
    manifest_rows_by_id: dict[str, dict[str, Any]] | None = None,
) -> list[PaperManifestIssue]:
    path = root / "papers" / "README.md"
    if not path.exists() or not manifest_ids:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [
            PaperManifestIssue(
                "todo_coverage_table_unreadable",
                _manifest_diagnostic(path, root, exc),
            )
        ]

    section = _markdown_section(text, "## TODO coverage cross-references")
    if section is None:
        return []
    issues = _validate_todo_coverage_scope_text(section)
    status_by_id = _status_table_status_cells(text)

    rows: dict[str, tuple[str, str]] = {}
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3 or cells[0] == "ID" or set(cells[0]) <= {"-", ":"}:
            continue
        row_id = cells[0]
        row_label = _safe_manifest_label(row_id)
        if row_id in rows:
            issues.append(
                PaperManifestIssue(
                    "duplicate_todo_coverage_row",
                    "duplicate papers/README.md TODO coverage row",
                    row_label,
                )
            )
            continue
        rows[row_id] = (cells[1], cells[2])

    for row_id in sorted(manifest_ids - set(rows)):
        issues.append(
            PaperManifestIssue(
                "missing_todo_coverage_row",
                "manifest row is missing from papers/README.md TODO coverage table",
                _safe_manifest_label(row_id),
            )
        )
    for row_id in sorted(set(rows) - manifest_ids):
        issues.append(
            PaperManifestIssue(
                "extra_todo_coverage_row",
                "papers/README.md TODO coverage row has no manifest row",
                _safe_manifest_label(row_id),
            )
        )

    for row_id in sorted(manifest_ids & set(rows)):
        active_cell, completed_cell = rows[row_id]
        issues.extend(_validate_active_todo_coverage_cell(root, row_id, active_cell))
        issues.extend(
            _validate_completed_todo_coverage_cell(
                root,
                row_id,
                completed_cell,
                (manifest_rows_by_id or {}).get(row_id),
            )
        )
        issues.extend(
            _validate_status_evidence_links(
                root,
                row_id,
                active_cell,
                completed_cell,
                status_by_id.get(row_id),
                (manifest_rows_by_id or {}).get(row_id),
            )
        )
    return issues


def _validate_todo_coverage_scope_text(section: str) -> list[PaperManifestIssue]:
    normalized = section.casefold()
    advertises_grouped_labels = (
        "grouped open gap" in normalized
        or "grouped labels are accepted" in normalized
        or "grouped labels are allowed" in normalized
    )
    if advertises_grouped_labels:
        return [
            PaperManifestIssue(
                "todo_coverage_grouped_label_policy_ambiguous",
                "papers/README.md TODO coverage prose must not advertise grouped labels unless a grouped-label taxonomy is validated",
            )
        ]
    return []


def _markdown_section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    section_start: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            section_start = index + 1
            break
    if section_start is None:
        return None
    section_lines: list[str] = []
    for line in lines[section_start:]:
        if line.startswith("## "):
            break
        section_lines.append(line)
    return "\n".join(section_lines)


def _validate_active_todo_coverage_cell(root: Path, row_id: str, cell: str) -> list[PaperManifestIssue]:
    row_label = _safe_manifest_label(row_id)
    listed_paths = set(TODO_COVERAGE_PATH_RE.findall(cell))
    issues: list[PaperManifestIssue] = []
    for relative_path in sorted(listed_paths):
        if relative_path not in ACTIVE_TODO_LEDGER_PATHS:
            issues.append(
                PaperManifestIssue(
                    "invalid_active_todo_coverage_path",
                    f"{relative_path} is not an active TODO ledger path",
                    row_label,
                )
            )
        if not (root / relative_path).exists():
            issues.append(
                PaperManifestIssue(
                    "missing_todo_coverage_path",
                    f"{relative_path} does not exist",
                    row_label,
                )
            )

    expected_paths: set[str] = set()
    for relative_path in ACTIVE_TODO_LEDGER_PATHS:
        todo_path = root / relative_path
        if not todo_path.exists():
            continue
        try:
            text = todo_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(
                PaperManifestIssue(
                    "active_todo_coverage_unreadable",
                    _manifest_diagnostic(todo_path, root, exc),
                    row_label,
                )
            )
            continue
        matching_blocks = [block for block in _open_todo_blocks(text) if row_id in block]
        if matching_blocks:
            expected_paths.add(relative_path)
        for block in matching_blocks:
            if not ACTIVE_TODO_GAP_CONTEXT_RE.search(block):
                issues.append(
                    PaperManifestIssue(
                        "active_todo_coverage_block_missing_gap_context",
                        f"{relative_path} has a row-specific open TODO block without Current/Remaining gap or Current evidence context",
                        row_label,
                    )
                )
            if not ACTIVE_TODO_REQUIRED_RESULT_RE.search(block):
                issues.append(
                    PaperManifestIssue(
                        "active_todo_coverage_block_missing_required_result",
                        f"{relative_path} has a row-specific open TODO block without Required result",
                        row_label,
                    )
                )

    if listed_paths != expected_paths:
        missing = sorted(expected_paths - listed_paths)
        extra = sorted(listed_paths - expected_paths)
        parts: list[str] = []
        if missing:
            parts.append(f"missing active paths {missing}")
        if extra:
            parts.append(f"extra active paths {extra}")
        issues.append(
            PaperManifestIssue(
                "todo_coverage_active_mismatch",
                "; ".join(parts) or "active TODO coverage paths do not match open TODO blocks",
                row_label,
            )
        )
    return issues


def _validate_completed_todo_coverage_cell(
    root: Path,
    row_id: str,
    cell: str,
    manifest_row: dict[str, Any] | None = None,
) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    row_label = _safe_manifest_label(row_id)
    source_tokens = _completed_todo_source_tokens(row_id, manifest_row)
    for relative_path in sorted(TODO_COVERAGE_PATH_RE.findall(cell)):
        if not relative_path.startswith("docs/todo/Completed/"):
            issues.append(
                PaperManifestIssue(
                    "invalid_completed_todo_coverage_path",
                    f"{relative_path} is not a completed TODO ledger path",
                    row_label,
                )
            )
            continue
        todo_path = root / relative_path
        if not todo_path.exists():
            issues.append(
                PaperManifestIssue(
                    "missing_todo_coverage_path",
                    f"{relative_path} does not exist",
                    row_label,
                )
            )
            continue
        try:
            text = todo_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(
                PaperManifestIssue(
                    "completed_todo_coverage_unreadable",
                    _manifest_diagnostic(todo_path, root, exc),
                    row_label,
                )
            )
            continue
        if not COMPLETED_TODO_ITEM_RE.search(text):
            issues.append(
                PaperManifestIssue(
                    "completed_todo_coverage_without_completed_item",
                    f"{relative_path} does not contain a completed checklist item",
                    row_label,
                )
            )
            continue
        if not _completed_todo_blocks_contain_any(text, source_tokens):
            issues.append(
                PaperManifestIssue(
                    "completed_todo_coverage_not_source_specific",
                    f"{relative_path} does not contain a completed checklist item for this paper id or source file",
                    row_label,
                )
            )
    return issues


def _completed_todo_source_tokens(row_id: str, manifest_row: dict[str, Any] | None) -> tuple[str, ...]:
    tokens = [row_id]
    if manifest_row is not None:
        file_value = manifest_row.get("file")
        if isinstance(file_value, str) and file_value:
            tokens.append(file_value)
            tokens.append(Path(file_value).name)
            tokens.append(Path(file_value).stem)
    return tuple(dict.fromkeys(tokens))


def _validate_status_evidence_links(
    root: Path,
    row_id: str,
    active_cell: str,
    completed_cell: str,
    status: str | None,
    manifest_row: dict[str, Any] | None = None,
) -> list[PaperManifestIssue]:
    row_label = _safe_manifest_label(row_id)
    active_paths = TODO_COVERAGE_PATH_RE.findall(active_cell)
    completed_paths = TODO_COVERAGE_PATH_RE.findall(completed_cell)
    issues: list[PaperManifestIssue] = []
    if not active_paths:
        issues.append(
            PaperManifestIssue(
                "missing_active_status_evidence",
                "paper status row must link at least one active TODO evidence path",
                row_label,
            )
        )
    if (
        status is not None
        and status.startswith(STATUS_TABLE_STATUSES_REQUIRING_COMPLETED_EVIDENCE)
        and not completed_paths
    ):
        issues.append(
            PaperManifestIssue(
                "missing_completed_status_evidence",
                "paper status row claims implemented or local-only support without completed evidence paths",
                row_label,
            )
        )
    if status is not None:
        status_artifact_paths = _status_local_artifact_paths(status)
        if status_artifact_paths:
            evidence_text = _status_evidence_text(root, row_id, active_paths + completed_paths, manifest_row)
            missing_artifacts = sorted(path for path in status_artifact_paths if path not in evidence_text)
            if missing_artifacts:
                issues.append(
                    PaperManifestIssue(
                        "status_table_local_artifact_unlinked_evidence",
                        "status local artifact paths must also appear in linked active or completed TODO evidence: "
                        f"{[_safe_manifest_label(path) for path in missing_artifacts]}",
                        row_label,
                    )
                )
    return issues


def _status_local_artifact_paths(status: str) -> set[str]:
    return {match.group(0).strip("`") for match in LOCAL_ARTIFACT_PATH_RE.finditer(status)}


def _status_evidence_text(
    root: Path,
    row_id: str,
    evidence_paths: list[str],
    manifest_row: dict[str, Any] | None,
) -> str:
    source_tokens = _completed_todo_source_tokens(row_id, manifest_row)
    evidence_blocks: list[str] = []
    for relative_path in dict.fromkeys(evidence_paths):
        path = root / relative_path
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        evidence_blocks.extend(block for block in _open_todo_blocks(text) if any(token in block for token in source_tokens))
        evidence_blocks.extend(block for block in _completed_todo_blocks(text) if any(token in block for token in source_tokens))
    return "\n".join(evidence_blocks)


def _status_table_status_cells(text: str) -> dict[str, str]:
    section = _markdown_section(text, "## Implementation status")
    if section is None:
        return {}
    statuses: dict[str, str] = {}
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(STATUS_TABLE_HEADER) or cells[0] == "ID" or set(cells[0]) <= {"-", ":"}:
            continue
        statuses[cells[0]] = cells[3]
    return statuses


def _validate_todo_absence_wording(root: Path, manifest_ids: set[str]) -> list[PaperManifestIssue]:
    if not manifest_ids:
        return []
    issues: list[PaperManifestIssue] = []
    blocks_by_path: dict[str, list[str]] = {}
    for relative_path in ACTIVE_TODO_LEDGER_PATHS:
        todo_path = root / relative_path
        if not todo_path.exists():
            continue
        try:
            text = todo_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(
                PaperManifestIssue(
                    "active_todo_absence_wording_unreadable",
                    _manifest_diagnostic(todo_path, root, exc),
                )
            )
            continue
        blocks_by_path[relative_path] = _open_todo_blocks(text)

    for row_id in sorted(manifest_ids):
        row_label = _safe_manifest_label(row_id)
        active_paths = {
            relative_path
            for relative_path, blocks in blocks_by_path.items()
            if any(row_id in block for block in blocks)
        }
        if not active_paths:
            continue
        for source_path, blocks in blocks_by_path.items():
            for block in blocks:
                if row_id not in block:
                    continue
                for match in SOURCE_SPECIFIC_ABSENCE_RE.finditer(block):
                    for target_name in match.group(1).split("/"):
                        target_path = SOURCE_SPECIFIC_TODO_TARGET_PATHS.get(target_name.casefold())
                        if target_path is None or target_path not in active_paths:
                            continue
                        issues.append(
                            PaperManifestIssue(
                                "stale_source_specific_absence_wording",
                                f"{source_path} says no source-specific {target_name} TODO, "
                                f"but {target_path} has an open TODO block for this paper id",
                                row_label,
                            )
                        )
    return issues


def _validate_benchmark_coverage_decisions(root: Path) -> list[PaperManifestIssue]:
    path = root / "papers" / "README.md"
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [
            PaperManifestIssue(
                "benchmark_coverage_unreadable",
                _manifest_diagnostic(path, root, exc),
            )
        ]
    section = _markdown_section(text, "## Benchmark coverage decisions")
    if section is None or "Implemented:" not in section:
        return []
    implemented_text = section.split("Implemented:", 1)[1].split("\nPlanned or background-only:", 1)[0]
    issues: list[PaperManifestIssue] = []
    for block in _markdown_bullet_blocks(implemented_text):
        summary = block.splitlines()[0].strip()
        if not BENCHMARK_IMPLEMENTED_LOCAL_ARTIFACT_RE.search(block):
            issues.append(
                PaperManifestIssue(
                    "benchmark_implemented_missing_local_artifact",
                    f"Implemented benchmark coverage bullet must cite a local code or artifact path: {summary}",
                )
            )
        if not BENCHMARK_IMPLEMENTED_LIMITATION_BOUNDARY_RE.search(block):
            issues.append(
                PaperManifestIssue(
                    "benchmark_implemented_missing_limitation_boundary",
                    f"Implemented benchmark coverage bullet must state the remaining scope or limitation: {summary}",
                )
            )
        if not BENCHMARK_IMPLEMENTED_NOT_IMPLEMENTED_RE.search(block):
            continue
        issues.append(
            PaperManifestIssue(
                "benchmark_implemented_not_implemented_contradiction",
                f"Implemented benchmark coverage bullet is phrased as not implemented: {summary}",
            )
        )
    return issues


def _open_todo_blocks(text: str) -> list[str]:
    starts = [match.start() for match in re.finditer(r"(?m)^- \[ \] ", text)]
    starts.append(len(text))
    return [text[start:end] for start, end in zip(starts, starts[1:])]


def _markdown_bullet_blocks(text: str) -> list[str]:
    starts = [match.start() for match in re.finditer(r"(?m)^- ", text)]
    starts.append(len(text))
    return [text[start:end] for start, end in zip(starts, starts[1:])]


def _open_todo_blocks_contain(text: str, needle: str) -> bool:
    return any(needle in block for block in _open_todo_blocks(text))


def _completed_todo_blocks(text: str) -> list[str]:
    starts = [match.start() for match in re.finditer(r"(?m)^- \[x\] ", text)]
    starts.append(len(text))
    return [text[start:end] for start, end in zip(starts, starts[1:])]


def _completed_todo_blocks_contain_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(any(needle in block for needle in needles) for block in _completed_todo_blocks(text))


def _format_count_source(source: ReadmeCountSource) -> str:
    phrase = redact_sensitive_text(source.phrase.strip())
    if len(phrase) > 80:
        phrase = f"{phrase[:77]}..."
    return f"{source.source} {source.kind}={source.value} ({phrase})"


def _manifest_diagnostic(path: Path, root: Path, exc: BaseException) -> str:
    label = _manifest_path_label(path, root)
    message = str(exc)
    replacements = {
        str(path): label,
        path.as_posix(): label,
        str(path.absolute()): label,
        path.absolute().as_posix(): label,
    }
    try:
        resolved_path = path.resolve(strict=False)
    except OSError:
        resolved_path = None
    if resolved_path is not None:
        replacements[str(resolved_path)] = label
        replacements[resolved_path.as_posix()] = label
    for raw, safe in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        if raw:
            message = message.replace(raw, safe)
    return f"{label}: {redact_sensitive_text(message)}"


def _manifest_path_label(path: Path, root: Path) -> str:
    try:
        label = path.relative_to(root).as_posix()
    except ValueError:
        label = path.name
    safe_label = redact_sensitive_text(label)
    if safe_label == label:
        return label
    digest = hashlib.sha256(label.encode("utf-8", errors="surrogatepass")).hexdigest()[:12]
    return f"{safe_label}#sha256={digest}"


def _read_status_table_ids(root: Path) -> tuple[list[str] | None, list[PaperManifestIssue]]:
    path = root / "papers" / "README.md"
    if not path.exists():
        return None, []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, [
            PaperManifestIssue(
                "status_table_unreadable",
                _manifest_diagnostic(path, root, exc),
            )
        ]
    in_section = False
    header_seen = False
    ids: list[str] = []
    issues: list[PaperManifestIssue] = []
    seen: set[str] = set()
    table_closed = False
    non_contiguous_reported = False
    for line in text.splitlines():
        if line.strip() == "## Implementation status":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        if not line.startswith("|"):
            if header_seen and ids and line.strip():
                table_closed = True
            continue
        if table_closed and not non_contiguous_reported:
            issues.append(
                PaperManifestIssue(
                    "status_table_non_contiguous",
                    "implementation status rows must be one contiguous markdown table before prose notes",
                )
            )
            non_contiguous_reported = True
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells:
            continue
        if cells[0] == "ID":
            header_seen = True
            if tuple(cells) != STATUS_TABLE_HEADER:
                issues.append(
                    PaperManifestIssue(
                        "status_table_header_mismatch",
                        f"implementation status header must exactly match {list(STATUS_TABLE_HEADER)}",
                    )
                )
            continue
        if set(cells[0]) <= {"-", ":"}:
            continue
        if len(cells) != len(STATUS_TABLE_HEADER):
            row_label = _safe_manifest_label(cells[0]) if cells else None
            issues.append(
                PaperManifestIssue(
                    "status_table_row_shape",
                    "implementation status rows must have exactly four cells",
                    row_label,
                )
            )
            continue
        row_id = cells[0]
        safe_row_id = _safe_manifest_label(row_id)
        issues.extend(_validate_status_table_row_cells(cells, safe_row_id))
        if row_id in seen:
            issues.append(
                PaperManifestIssue(
                    "duplicate_status_table_row",
                    "duplicate papers/README.md implementation status row",
                    safe_row_id,
                )
            )
        seen.add(row_id)
        ids.append(row_id)
    if not in_section or not ids:
        return None, issues
    if not header_seen:
        issues.append(PaperManifestIssue("missing_status_table_header", "implementation status header is missing"))
    return ids, issues


def _validate_status_table_row_cells(cells: list[str], row_id: str) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    for index, field_name in enumerate(STATUS_TABLE_HEADER):
        value = cells[index]
        if not value.strip():
            issues.append(PaperManifestIssue("empty_status_table_cell", f"{field_name} cell must be non-empty", row_id))
        if _has_unsafe_text(value) or redact_sensitive_text(value) != value:
            issues.append(
                PaperManifestIssue(
                    "unsafe_status_table_cell",
                    f"{field_name} cell must be display-safe and secret-free",
                    row_id,
                )
            )
    role = cells[2]
    if role and role not in ALLOWED_STATUS_TABLE_ROLES:
        issues.append(
            PaperManifestIssue(
                "invalid_status_table_role",
                "implementation status role is not in the allowed paper-facing taxonomy",
                row_id,
            )
        )
    status = cells[3]
    if status and not status.startswith(ALLOWED_STATUS_TABLE_STATUS_PREFIXES):
        issues.append(
            PaperManifestIssue(
                "invalid_status_table_status",
                "implementation status must start with an allowed support/status class",
                row_id,
            )
        )
    allowed_status_prefixes = STATUS_TABLE_ROLE_STATUS_PREFIXES.get(role)
    if role and status and allowed_status_prefixes is not None and not status.startswith(allowed_status_prefixes):
        issues.append(
            PaperManifestIssue(
                "status_table_role_status_mismatch",
                "implementation status class is not compatible with the paper-facing role",
                row_id,
            )
        )
    if (
        status
        and STATUS_TABLE_ALPHAEVOLVE_COMPARABLE_RE.search(status)
        and not STATUS_TABLE_ALPHAEVOLVE_COMPARABLE_BOUNDARY_RE.search(status)
    ):
        issues.append(
            PaperManifestIssue(
                "status_table_alphaevolve_comparable_overclaim",
                "AlphaEvolve-comparable status claims must be framed as missing, scoped, or requirement-bound evidence",
                row_id,
            )
        )
    if (
        status
        and status.startswith(STATUS_TABLE_STATUSES_REQUIRING_COMPLETED_EVIDENCE)
        and not LOCAL_ARTIFACT_PATH_RE.search(status)
    ):
        issues.append(
            PaperManifestIssue(
                "status_table_supported_status_missing_local_artifact",
                "implemented, partial, limited, and static-guidance status claims must cite a local code or artifact path",
                row_id,
            )
        )
    for prefix in STATUS_TABLE_NEGATIVE_IMPLEMENTATION_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if STATUS_TABLE_POSITIVE_IMPLEMENTATION_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_negative_status_contradiction",
                    "negative or background-only status classes must not include positive implementation claims",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_BACKGROUND_ONLY_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_LIMITATION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_background_only_missing_boundary",
                    "background-only status classes must name a missing or unsupported paper behavior",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_FUTURE_BENCHMARK_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_LIMITATION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_future_benchmark_missing_boundary",
                    "future-benchmark status classes must name a missing verifier, harness, or unsupported paper behavior",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_IMPLEMENTED_STATUS_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_LIMITATION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_implemented_status_missing_boundary",
                    "implemented status classes must include an explicit scoped, open, or out-of-scope behavior boundary",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_LIMITED_STATUS_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_LIMITATION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_limited_status_missing_boundary",
                    "limited-support status classes must include an explicit missing or unsupported behavior boundary",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_PARTIAL_STATUS_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_LIMITATION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_partial_status_missing_boundary",
                    "partial status classes must include an explicit remaining, missing, or unsupported behavior boundary",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_STATIC_GUIDANCE_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_STATIC_GUIDANCE_EXECUTION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_static_guidance_missing_execution_boundary",
                    "static-guidance status classes must state that the guided operation is not executed or enforced",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_NOT_IMPLEMENTED_AS_DESCRIBED_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_LIMITATION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_not_implemented_missing_boundary",
                    "not-implemented-as-described status classes must name a missing or unsupported paper behavior",
                    row_id,
                )
            )
        break
    return issues


def _canonical_row(row: dict[str, Any]) -> dict[str, Any]:
    return {field: row.get(field) for field in REQUIRED_FIELDS}


def _is_safe_paper_path(value: str) -> bool:
    if "\\" in value or _has_unsafe_text(value):
        return False
    path = PurePosixPath(value)
    name = path.name
    stem = path.stem
    first_stem_segment = stem.split(".", 1)[0].upper()
    return (
        len(path.parts) == 2
        and path.parts[0] == "papers"
        and path.suffix == ".pdf"
        and PAPER_FILE_NAME_RE.fullmatch(name) is not None
        and not name.startswith(".")
        and not name.endswith((".", " "))
        and first_stem_segment not in WINDOWS_RESERVED_NAMES
    )


def _normalized_paper_file_key(value: str) -> str:
    return PurePosixPath(value).as_posix().casefold()


def _json_object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    duplicate_keys: list[str] = []
    for key, value in pairs:
        if key in result:
            duplicate_keys.append(key)
            continue
        result[key] = value
    if duplicate_keys:
        result[JSON_DUPLICATE_KEYS_FIELD] = duplicate_keys
    return result


def _validate_csv_header(fieldnames: list[str]) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    if not fieldnames:
        return [PaperManifestIssue("csv_header_missing", "CSV manifest must include a header")]
    seen: set[str] = set()
    for index, field in enumerate(fieldnames):
        if field in seen:
            issues.append(
                PaperManifestIssue(
                    "duplicate_csv_header",
                    f"duplicate CSV header {field!r} at position {index + 1}",
                )
            )
        seen.add(field)
    missing = [field for field in REQUIRED_FIELDS if field not in fieldnames]
    extra = [field for field in fieldnames if field not in REQUIRED_FIELDS]
    if missing:
        issues.append(PaperManifestIssue("missing_csv_header", f"missing CSV headers {missing}"))
    for field in extra:
        issues.append(
            PaperManifestIssue(
                "unsupported_csv_header",
                f"unsupported CSV header {_safe_manifest_label(field)!r}",
            )
        )
    if fieldnames != list(REQUIRED_FIELDS):
        issues.append(
            PaperManifestIssue(
                "csv_header_order",
                f"CSV headers must exactly match {list(REQUIRED_FIELDS)}",
            )
        )
    return issues


def _validate_paper_id(value: str, row_id: str) -> list[PaperManifestIssue]:
    if (
        not value
        or _has_unsafe_text(value)
        or redact_sensitive_text(value) != value
        or PAPER_ID_RE.fullmatch(value) is None
    ):
        return [
            PaperManifestIssue(
                "invalid_id",
                "id must be an arXiv id or lowercase foundational-paper slug",
                row_id,
            )
        ]
    return []


def _validate_paper_title(value: str, row_id: str) -> list[PaperManifestIssue]:
    if (
        not value.strip()
        or _has_unsafe_text(value)
        or redact_sensitive_text(value) != value
        or len(value) > MAX_TITLE_CHARS
    ):
        return [
            PaperManifestIssue(
                "invalid_title",
                f"title must be non-empty, display-safe, and at most {MAX_TITLE_CHARS} characters",
                row_id,
            )
        ]
    return []


def _validate_paper_url(value: str, row_id: str) -> list[PaperManifestIssue]:
    if _has_unsafe_text(value) or redact_sensitive_text(value) != value:
        return [PaperManifestIssue("invalid_url", "url must be share-safe HTTPS source URL", row_id)]
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.hostname.casefold() not in ALLOWED_PAPER_URL_HOSTS
        or parsed.username is not None
        or parsed.password is not None
    ):
        return [PaperManifestIssue("invalid_url", "url must use an allowed HTTPS paper source host", row_id)]
    return []


def _validate_paper_row_identity(
    row_id_value: str,
    url_value: str,
    file_value: str,
    row_id: str,
) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    if _validate_paper_id(row_id_value, row_id) or not _is_safe_paper_path(file_value):
        return issues
    parsed = urlparse(url_value)
    host = parsed.hostname.casefold() if parsed.hostname else ""
    file_stem = PurePosixPath(file_value).stem
    file_source_id = file_stem.split("__", 1)[0]
    if file_source_id != row_id_value:
        issues.append(
            PaperManifestIssue(
                "file_source_id_mismatch",
                "local PDF filename stem must start with the manifest id before any __ title suffix",
                row_id,
            )
        )
    if host in {"arxiv.org", "www.arxiv.org"}:
        arxiv_id = _arxiv_id_from_url_path(parsed.path)
        if arxiv_id is None:
            issues.append(
                PaperManifestIssue(
                    "missing_arxiv_url_id",
                    "arXiv source URL path must include an arXiv id",
                    row_id,
                )
            )
            return issues
        arxiv_base_id = arxiv_id.split("v", 1)[0]
        if arxiv_base_id != row_id_value:
            issues.append(
                PaperManifestIssue(
                    "arxiv_url_id_mismatch",
                    "arXiv source URL id must match the manifest id",
                    row_id,
                )
            )
    elif file_source_id != row_id_value:
        issues.append(
            PaperManifestIssue(
                "non_arxiv_source_identity_missing",
                "non-arXiv source rows must use the manifest id as the local filename source prefix",
                row_id,
            )
        )
    return issues


def _arxiv_id_from_url_path(path: str) -> str | None:
    parts = [part for part in PurePosixPath(path).parts if part not in {"/", ""}]
    if len(parts) < 2 or parts[0] not in {"abs", "pdf"}:
        return None
    candidate = parts[1]
    if candidate.endswith(".pdf"):
        candidate = candidate[:-4]
    if ARXIV_ID_RE.fullmatch(candidate) is None:
        return None
    return candidate


def _validate_download_message(value: str, row_id: str) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    if _has_unsafe_text(value):
        issues.append(PaperManifestIssue("invalid_message", "message must not contain control characters", row_id))
    if redact_sensitive_text(value) != value:
        issues.append(PaperManifestIssue("unsafe_message", "message must not contain secret-like text", row_id))
    if len(value) > MAX_DOWNLOAD_MESSAGE_CHARS:
        issues.append(
            PaperManifestIssue(
                "message_too_long",
                f"message must be at most {MAX_DOWNLOAD_MESSAGE_CHARS} characters",
                row_id,
            )
        )
    return issues


def _sanitize_download_message(value: Any) -> str:
    text = redact_sensitive_text(str(value))
    text = "".join(" " if _is_control_or_format(character) else character for character in text)
    if len(text) > MAX_DOWNLOAD_MESSAGE_CHARS:
        return text[: MAX_DOWNLOAD_MESSAGE_CHARS - 3] + "..."
    return text


def _safe_manifest_label(value: str) -> str:
    redacted = redact_sensitive_text(value)
    redacted = "".join("?" if _is_control_or_format(character) else character for character in redacted)
    if len(redacted) > 96:
        return redacted[:93] + "..."
    return redacted


def _has_unsafe_text(value: str) -> bool:
    return any(_is_control_or_format(character) for character in value)


def _is_control_or_format(character: str) -> bool:
    category = unicodedata.category(character)
    return category.startswith("C")


def _parse_csv_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise ValueError(f"invalid boolean {value!r}")


def _has_pdf_header(path: Path) -> bool:
    with path.open("rb") as handle:
        return handle.read(5) == b"%PDF-"


def _read_pdf_quietly(path: Path) -> PdfReader:
    pypdf_logger = logging.getLogger("pypdf")
    previous_level = pypdf_logger.level
    pypdf_logger.setLevel(logging.ERROR)
    try:
        with redirect_stderr(io.StringIO()):
            return PdfReader(path, strict=True)
    finally:
        pypdf_logger.setLevel(previous_level)


def _safe_pdf_parse_error(exc: BaseException) -> str:
    message = redact_sensitive_text(str(exc))
    if len(message) > 160:
        message = message[:157] + "..."
    return f"{exc.__class__.__name__}: {message}"


def _is_link_backed_path(path: Path) -> bool:
    if path.is_symlink():
        return True
    local_stat = path.lstat()
    file_attributes = getattr(local_stat, "st_file_attributes", 0)
    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(reparse_point and file_attributes & reparse_point)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(PDF_HASH_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _existing_rehydrate_match(row: dict[str, Any], target: Path, row_id: str) -> PaperRehydrateResult:
    file_value = str(row["file"])
    if not target.exists():
        return PaperRehydrateResult(row_id, file_value, "missing", None, None, "local PDF is missing")
    try:
        if _is_link_backed_path(target):
            return PaperRehydrateResult(
                row_id,
                file_value,
                "failed",
                None,
                None,
                "local PDF path is symlink or reparse-point backed; refusing to overwrite",
            )
    except OSError as exc:
        return PaperRehydrateResult(
            row_id,
            file_value,
            "failed",
            None,
            None,
            _sanitize_download_message(f"could not inspect local PDF link state: {exc}"),
        )
    try:
        local_stat = target.stat()
    except OSError as exc:
        return PaperRehydrateResult(
            row_id,
            file_value,
            "failed",
            None,
            None,
            _sanitize_download_message(f"could not inspect local PDF: {exc}"),
        )
    if not stat.S_ISREG(local_stat.st_mode):
        return PaperRehydrateResult(
            row_id,
            file_value,
            "failed",
            None,
            None,
            "local PDF path exists but is not a regular file; refusing to overwrite",
        )
    try:
        actual_sha = _sha256_file(target)
    except OSError as exc:
        return PaperRehydrateResult(
            row_id,
            file_value,
            "failed",
            local_stat.st_size,
            None,
            _sanitize_download_message(f"could not read local PDF: {exc}"),
        )
    if local_stat.st_size == row["bytes"] and actual_sha == row["sha256"]:
        return PaperRehydrateResult(
            row_id,
            file_value,
            "verified_existing",
            local_stat.st_size,
            actual_sha,
            "byte count and SHA-256 match manifest",
        )
    return PaperRehydrateResult(
        row_id,
        file_value,
        "stale",
        local_stat.st_size,
        actual_sha,
        "local byte count or SHA-256 differs from manifest",
    )


def _download_rehydrate_row(row: dict[str, Any], root: Path, timeout: float) -> PaperRehydrateResult:
    row_id = _safe_manifest_label(str(row["id"]))
    file_value = str(row["file"])
    target = root / file_value
    temp_path: Path | None = None
    bytes_seen = 0
    digest = hashlib.sha256()
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        request = Request(str(row["url"]), headers={"User-Agent": PAPER_DOWNLOAD_USER_AGENT})
        response = urlopen(request, timeout=timeout)
        try:
            status = getattr(response, "status", 200)
            if status >= 400:
                return PaperRehydrateResult(
                    row_id,
                    file_value,
                    "failed",
                    None,
                    None,
                    _sanitize_download_message(f"download returned HTTP {status}"),
                )
            with tempfile.NamedTemporaryFile(
                "wb",
                delete=False,
                dir=target.parent,
                prefix=f".{target.name}.",
                suffix=".download",
            ) as handle:
                temp_path = Path(handle.name)
                while chunk := response.read(PAPER_DOWNLOAD_CHUNK_SIZE):
                    bytes_seen += len(chunk)
                    digest.update(chunk)
                    handle.write(chunk)
        finally:
            close = getattr(response, "close", None)
            if callable(close):
                close()

        actual_sha = digest.hexdigest()
        if bytes_seen != row["bytes"]:
            return PaperRehydrateResult(
                row_id,
                file_value,
                "failed",
                bytes_seen,
                actual_sha,
                f"downloaded byte count {bytes_seen} does not match manifest {row['bytes']}",
            )
        if actual_sha != row["sha256"]:
            return PaperRehydrateResult(
                row_id,
                file_value,
                "failed",
                bytes_seen,
                actual_sha,
                "downloaded SHA-256 does not match manifest",
            )
        os.replace(temp_path, target)
        temp_path = None
        post_download_issues = _validate_local_pdf(row, target, row_id)
        if post_download_issues:
            return PaperRehydrateResult(
                row_id,
                file_value,
                "failed",
                bytes_seen,
                actual_sha,
                "; ".join(issue.code for issue in post_download_issues),
            )
        return PaperRehydrateResult(
            row_id,
            file_value,
            "downloaded",
            bytes_seen,
            actual_sha,
            "downloaded and verified against manifest",
        )
    except Exception as exc:
        return PaperRehydrateResult(
            row_id,
            file_value,
            "failed",
            bytes_seen or None,
            digest.hexdigest() if bytes_seen else None,
            _sanitize_download_message(f"download failed: {exc}"),
        )
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def _local_pdf_files(root: Path) -> set[str]:
    papers = root / "papers"
    if not papers.exists():
        return set()
    files: set[str] = set()
    for path in papers.glob("*.pdf"):
        try:
            is_file = path.is_file()
        except OSError:
            continue
        if is_file:
            files.add(path.relative_to(root).as_posix())
    return files


def _paper_file_label(row: dict[str, Any], path: Path) -> str:
    file_value = row.get("file")
    if isinstance(file_value, str):
        return file_value.replace("\\", "/")
    return str(path)


def _report_to_dict(report: PaperManifestReport) -> dict[str, Any]:
    return {
        "ok": report.ok,
        "row_count": report.row_count,
        "local_present_count": report.local_present_count,
        "local_missing_count": report.local_missing_count,
        "local_unique_file_count": report.local_unique_file_count,
        "availability": [asdict(item) for item in report.availability],
        "issues": [asdict(issue) for issue in report.issues],
    }


def _rehydrate_report_to_dict(report: PaperRehydrateReport) -> dict[str, Any]:
    return {
        "ok": report.ok,
        "row_count": report.row_count,
        "verified_existing_count": report.verified_existing_count,
        "downloaded_count": report.downloaded_count,
        "failed_count": report.failed_count,
        "results": [asdict(result) for result in report.results],
        "issues": [asdict(issue) for issue in report.issues],
    }


def _availability(
    row: dict[str, Any],
    file_value: str,
    local_status: str,
    git_tracked_files: set[str] | None,
) -> PaperAvailability:
    return PaperAvailability(
        row_id=_safe_manifest_label(str(row.get("id", ""))),
        file=file_value,
        download_ok=row.get("ok") is True,
        download_message=_sanitize_download_message(row.get("message", "")),
        local_status=local_status,
        git_tracked=None if git_tracked_files is None else file_value.replace("\\", "/") in git_tracked_files,
    )


def _git_tracked_files(root: Path) -> set[str] | None:
    if not (root / ".git").exists():
        return None
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--", "papers/*.pdf"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return {line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()}


if __name__ == "__main__":
    raise SystemExit(main())
