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
from libreevolve.problems.benchmarks.appendix_b_registry import (
    REGISTRY_PATH as APPENDIX_B_REGISTRY_PATH,
    validate_appendix_b_registry,
)


REQUIRED_FIELDS = ("id", "title", "url", "file", "ok", "bytes", "sha256", "message")
SHA256_RE = re.compile(r"[0-9a-f]{64}")
PAPER_ID_RE = re.compile(r"(?:\d{4}\.\d{5}|[a-z0-9][a-z0-9-]{0,94}[a-z0-9])")
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

    issues.extend(_validate_appendix_b_registry_if_present(root_path))
    issues.extend(_validate_ablation_registry_if_present(root_path))

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
    issues.extend(_validate_todo_coverage_table(root_path, seen_ids))
    issues.extend(_validate_todo_absence_wording(root_path, seen_ids))

    return PaperManifestReport(
        ok=not issues,
        row_count=len(json_rows),
        local_present_count=local_present_count,
        local_missing_count=local_missing_count,
        local_unique_file_count=len(present_file_keys),
        availability=availability,
        issues=issues,
    )


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


def _validate_todo_coverage_table(root: Path, manifest_ids: set[str]) -> list[PaperManifestIssue]:
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

    rows: dict[str, tuple[str, str]] = {}
    issues: list[PaperManifestIssue] = []
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
        issues.extend(_validate_completed_todo_coverage_cell(root, row_id, completed_cell))
    return issues


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
        if _open_todo_blocks_contain(text, row_id):
            expected_paths.add(relative_path)

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


def _validate_completed_todo_coverage_cell(root: Path, row_id: str, cell: str) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    row_label = _safe_manifest_label(row_id)
    for relative_path in sorted(TODO_COVERAGE_PATH_RE.findall(cell)):
        if not relative_path.startswith("docs/todo/Completed/"):
            issues.append(
                PaperManifestIssue(
                    "invalid_completed_todo_coverage_path",
                    f"{relative_path} is not a completed TODO ledger path",
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
    return issues


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


def _open_todo_blocks(text: str) -> list[str]:
    starts = [match.start() for match in re.finditer(r"(?m)^- \[ \] ", text)]
    starts.append(len(text))
    return [text[start:end] for start, end in zip(starts, starts[1:])]


def _open_todo_blocks_contain(text: str, needle: str) -> bool:
    return any(needle in block for block in _open_todo_blocks(text))


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
    ids: list[str] = []
    issues: list[PaperManifestIssue] = []
    seen: set[str] = set()
    for line in text.splitlines():
        if line.strip() == "## Implementation status":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or cells[0] == "ID" or set(cells[0]) <= {"-", ":"}:
            continue
        row_id = cells[0]
        safe_row_id = _safe_manifest_label(row_id)
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
    return ids, issues


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
