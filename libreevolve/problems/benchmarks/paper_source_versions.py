from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_SOURCE_PDF_VERSION_SCHEMA = "libreevolve.alphaevolve_source_pdf_version.v1"
ALPHAEVOLVE_SOURCE_PDF_VERSION_MANIFEST_SCHEMA = (
    "libreevolve.alphaevolve_source_pdf_version_manifest.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_TITLE = "AlphaEvolve"
EXPECTED_FILE = "papers/2506.13131__AlphaEvolve.pdf"
EXPECTED_SOURCE_VERSION_MANIFEST_FILE = "papers/source_versions.json"
EXPECTED_FLOATING_PDF_URL = "https://arxiv.org/pdf/2506.13131.pdf"
EXPECTED_VERSIONED_ABS_URL = "https://arxiv.org/abs/2506.13131v1"
EXPECTED_VERSIONED_PDF_URL = "https://arxiv.org/pdf/2506.13131v1"
EXPECTED_ARXIV_VERSION = 1
EXPECTED_ARXIV_VERSIONED_ID = "2506.13131v1"
EXPECTED_ARXIV_CATEGORY = "cs.AI"
EXPECTED_ARXIV_SUBJECTS = ("cs.AI", "cs.LG", "cs.NE")
EXPECTED_POSTED_DATE = "2025-06-16"
EXPECTED_SUBMITTED_TIMESTAMP_UTC = "2025-06-16T06:37:18Z"
EXPECTED_ARXIV_DOI = "10.48550/arXiv.2506.13131"
EXPECTED_AUTHOR_COUNT = 18
EXPECTED_TEX_SOURCE_URL = "https://arxiv.org/e-print/2506.13131"
EXPECTED_ARXIV_LICENSE_URL = "https://creativecommons.org/licenses/by-nc-nd/4.0/"
EXPECTED_HEADER_PAGE = 1
EXPECTED_HEADER_PHRASE = "arXiv:2506.13131v1 [cs.AI] 16 Jun 2025"
EXPECTED_BYTES = 3525764
EXPECTED_SHA256 = "".join(
    [
        "f092",
        "c8cb",
        "d65d",
        "a899",
        "51ee",
        "6496",
        "374d",
        "a9a5",
        "4963",
        "f903",
        "5758",
        "c25a",
        "c6e4",
        "625f",
        "506d",
        "f9ad",
    ]
)
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class AlphaEvolveSourcePdfVersionIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveSourcePdfVersionValidation:
    ok: bool
    source_count: int
    header_checked: bool
    issues: list[AlphaEvolveSourcePdfVersionIssue]


def alphaevolve_source_pdf_version_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_SOURCE_PDF_VERSION_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "title": EXPECTED_TITLE,
        "source_kind": "cached_arxiv_pdf",
        "manifest_row": {
            "id": EXPECTED_SOURCE_PAPER_ID,
            "title": EXPECTED_TITLE,
            "url": EXPECTED_FLOATING_PDF_URL,
            "file": EXPECTED_FILE,
            "bytes": EXPECTED_BYTES,
            "sha256": EXPECTED_SHA256,
            "url_kind": "floating_arxiv_pdf_url",
        },
        "arxiv_source": {
            "arxiv_id": EXPECTED_SOURCE_PAPER_ID,
            "version": EXPECTED_ARXIV_VERSION,
            "versioned_id": EXPECTED_ARXIV_VERSIONED_ID,
            "category": EXPECTED_ARXIV_CATEGORY,
            "subjects": list(EXPECTED_ARXIV_SUBJECTS),
            "posted_date": EXPECTED_POSTED_DATE,
            "submitted_timestamp_utc": EXPECTED_SUBMITTED_TIMESTAMP_UTC,
            "doi": EXPECTED_ARXIV_DOI,
            "author_count": EXPECTED_AUTHOR_COUNT,
            "floating_pdf_url": EXPECTED_FLOATING_PDF_URL,
            "versioned_abs_url": EXPECTED_VERSIONED_ABS_URL,
            "versioned_pdf_url": EXPECTED_VERSIONED_PDF_URL,
            "tex_source_url": EXPECTED_TEX_SOURCE_URL,
            "license_url": EXPECTED_ARXIV_LICENSE_URL,
            "abstract_page_metadata_status": "manual_current_as_of_2026-06-13_without_html_snapshot",
            "expected_header_page": EXPECTED_HEADER_PAGE,
            "expected_header_phrase": EXPECTED_HEADER_PHRASE,
        },
        "audit_policy": {
            "manifest_url_requires_header_version_check": True,
            "claim_audits_must_name_source_version": True,
            "floating_url_refresh_is_not_silent_version_change": True,
            "arxiv_abs_html_snapshot_required_for_live_metadata_claims": True,
            "datacite_doi_resolution_not_snapshotted": True,
            "tex_source_not_cached": True,
            "arxiv_license_page_not_cached": True,
            "submission_history_refresh_gate_not_implemented": True,
            "scope": "AlphaEvolve source PDF identity, not result-version provenance",
        },
    }


def alphaevolve_source_pdf_version_manifest_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_SOURCE_PDF_VERSION_MANIFEST_SCHEMA,
        "source_version_count": 1,
        "sources": [
            {
                "manifest_row_id": EXPECTED_SOURCE_PAPER_ID,
                "source_version_id": EXPECTED_ARXIV_VERSIONED_ID,
                "source_record": alphaevolve_source_pdf_version_record(),
                "claim_artifact_links": {
                    "source_version_used_by": [
                        "README.md",
                        "ROADMAP.md",
                        "papers/README.md",
                        "docs/todo/code.md",
                        "docs/todo/papers.md",
                        "docs/todo/readme.md",
                        "docs/todo/roadmap.md",
                    ],
                    "policy": "paper_claim_audits_must_name_the_source_version_id",
                },
            }
        ],
    }


def validate_alphaevolve_source_pdf_version(
    recordset: object | str | Path | None = None,
    *,
    first_page_text: str | None = None,
) -> AlphaEvolveSourcePdfVersionValidation:
    data, read_issues = _load_recordset(recordset)
    if read_issues:
        return AlphaEvolveSourcePdfVersionValidation(False, 0, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveSourcePdfVersionIssue] = []
    if data.get("schema") != ALPHAEVOLVE_SOURCE_PDF_VERSION_SCHEMA:
        issues.append(AlphaEvolveSourcePdfVersionIssue("invalid_schema", "unsupported AlphaEvolve source-PDF version schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(AlphaEvolveSourcePdfVersionIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("title") != EXPECTED_TITLE:
        issues.append(AlphaEvolveSourcePdfVersionIssue("invalid_title", "title must be AlphaEvolve"))
    if data.get("source_kind") != "cached_arxiv_pdf":
        issues.append(AlphaEvolveSourcePdfVersionIssue("invalid_source_kind", "source_kind must be cached_arxiv_pdf"))
    _validate_manifest_row(data.get("manifest_row"), issues)
    _validate_arxiv_source(data.get("arxiv_source"), issues)
    _validate_audit_policy(data.get("audit_policy"), issues)
    header_checked = first_page_text is not None
    if first_page_text is not None and _normalize_header(EXPECTED_HEADER_PHRASE) not in _normalize_header(first_page_text):
        issues.append(
            AlphaEvolveSourcePdfVersionIssue(
                "missing_expected_header_phrase",
                "first-page text must include the expected arXiv version/category/date header",
            )
        )
    return AlphaEvolveSourcePdfVersionValidation(
        ok=not issues,
        source_count=1 if isinstance(data.get("arxiv_source"), dict) else 0,
        header_checked=header_checked,
        issues=issues,
    )


def validate_alphaevolve_source_pdf_version_manifest(
    recordset: object | str | Path | None = None,
    *,
    first_page_text: str | None = None,
) -> AlphaEvolveSourcePdfVersionValidation:
    data, read_issues = _load_manifest_recordset(recordset)
    if read_issues:
        return AlphaEvolveSourcePdfVersionValidation(False, 0, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveSourcePdfVersionIssue] = []
    if data.get("schema") != ALPHAEVOLVE_SOURCE_PDF_VERSION_MANIFEST_SCHEMA:
        issues.append(
            AlphaEvolveSourcePdfVersionIssue(
                "invalid_manifest_schema",
                "unsupported AlphaEvolve source-PDF version manifest schema",
            )
        )
    sources = data.get("sources")
    if not isinstance(sources, list):
        issues.append(
            AlphaEvolveSourcePdfVersionIssue(
                "invalid_manifest_sources",
                "source-version manifest sources must be a list",
            )
        )
        sources = []
    source_count = len(sources)
    if data.get("source_version_count") != source_count:
        issues.append(
            AlphaEvolveSourcePdfVersionIssue(
                "invalid_manifest_source_version_count",
                "source_version_count must equal the number of source records",
            )
        )
    if source_count != 1:
        issues.append(
            AlphaEvolveSourcePdfVersionIssue(
                "invalid_manifest_source_count",
                "source-version manifest must contain the cached AlphaEvolve source row",
            )
        )
    for index, source in enumerate(sources):
        _validate_source_version_manifest_source(source, issues, first_page_text, index)
    return AlphaEvolveSourcePdfVersionValidation(
        ok=not issues,
        source_count=source_count,
        header_checked=first_page_text is not None,
        issues=issues,
    )


def render_alphaevolve_source_pdf_version_summary(recordset: object | str | Path | None = None) -> str:
    validation = validate_alphaevolve_source_pdf_version(recordset)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve source-PDF version evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| source_count | {validation.source_count} |",
        f"| arxiv_version | v{EXPECTED_ARXIV_VERSION} |",
        f"| posted_date | {EXPECTED_POSTED_DATE} |",
        f"| header_checked | {validation.header_checked} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_manifest_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveSourcePdfVersionIssue]]:
    if recordset is None:
        return alphaevolve_source_pdf_version_manifest_record(), []
    return _load_recordset(recordset)


def _load_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveSourcePdfVersionIssue]]:
    if recordset is None:
        return alphaevolve_source_pdf_version_record(), []
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [AlphaEvolveSourcePdfVersionIssue("read_error", f"failed to read source-PDF version record: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [AlphaEvolveSourcePdfVersionIssue("invalid_json", f"invalid source-PDF version JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [AlphaEvolveSourcePdfVersionIssue("invalid_shape", "source-PDF version record must be a JSON object")]


def _validate_source_version_manifest_source(
    value: object,
    issues: list[AlphaEvolveSourcePdfVersionIssue],
    first_page_text: str | None,
    index: int,
) -> None:
    if not isinstance(value, dict):
        issues.append(
            AlphaEvolveSourcePdfVersionIssue(
                "invalid_manifest_source",
                f"source-version manifest source {index} must be an object",
            )
        )
        return
    if value.get("manifest_row_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(
            AlphaEvolveSourcePdfVersionIssue(
                "invalid_manifest_source_row_id",
                "source-version manifest row id must match the cached AlphaEvolve row",
            )
        )
    if value.get("source_version_id") != EXPECTED_ARXIV_VERSIONED_ID:
        issues.append(
            AlphaEvolveSourcePdfVersionIssue(
                "invalid_manifest_source_version_id",
                "source-version manifest must name the audited arXiv version id",
            )
        )
    source_record = value.get("source_record")
    record_report = validate_alphaevolve_source_pdf_version(
        source_record,
        first_page_text=first_page_text,
    )
    issues.extend(record_report.issues)
    _validate_claim_artifact_links(value.get("claim_artifact_links"), issues)


def _validate_claim_artifact_links(
    value: object,
    issues: list[AlphaEvolveSourcePdfVersionIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(
            AlphaEvolveSourcePdfVersionIssue(
                "invalid_claim_artifact_links",
                "claim_artifact_links must be an object",
            )
        )
        return
    expected_surfaces = {
        "README.md",
        "ROADMAP.md",
        "papers/README.md",
        "docs/todo/code.md",
        "docs/todo/papers.md",
        "docs/todo/readme.md",
        "docs/todo/roadmap.md",
    }
    surfaces = value.get("source_version_used_by")
    if not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces):
        issues.append(
            AlphaEvolveSourcePdfVersionIssue(
                "invalid_claim_artifact_surfaces",
                "source_version_used_by must list paper-claim artifact surfaces",
            )
        )
    elif set(surfaces) != expected_surfaces:
        issues.append(
            AlphaEvolveSourcePdfVersionIssue(
                "claim_artifact_surface_mismatch",
                "source_version_used_by must cover docs, papers, and active TODO evidence",
            )
        )
    if value.get("policy") != "paper_claim_audits_must_name_the_source_version_id":
        issues.append(
            AlphaEvolveSourcePdfVersionIssue(
                "invalid_claim_artifact_policy",
                "claim artifact policy must require source version ids",
            )
        )


def _validate_manifest_row(value: object, issues: list[AlphaEvolveSourcePdfVersionIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveSourcePdfVersionIssue("invalid_manifest_row", "manifest_row must be an object"))
        return
    expected = {
        "id": EXPECTED_SOURCE_PAPER_ID,
        "title": EXPECTED_TITLE,
        "url": EXPECTED_FLOATING_PDF_URL,
        "file": EXPECTED_FILE,
        "bytes": EXPECTED_BYTES,
        "url_kind": "floating_arxiv_pdf_url",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(AlphaEvolveSourcePdfVersionIssue(f"invalid_manifest_{field}", f"manifest_row.{field} must match the cached AlphaEvolve PDF row"))
    sha256 = value.get("sha256")
    if not isinstance(sha256, str) or _SHA256_RE.fullmatch(sha256) is None:
        issues.append(AlphaEvolveSourcePdfVersionIssue("invalid_manifest_sha256", "manifest_row.sha256 must be a lowercase 64-hex digest"))
    elif sha256 != EXPECTED_SHA256:
        issues.append(AlphaEvolveSourcePdfVersionIssue("manifest_sha256_drift", "manifest_row.sha256 must match the cached AlphaEvolve PDF digest"))


def _validate_arxiv_source(value: object, issues: list[AlphaEvolveSourcePdfVersionIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveSourcePdfVersionIssue("invalid_arxiv_source", "arxiv_source must be an object"))
        return
    expected = {
        "arxiv_id": EXPECTED_SOURCE_PAPER_ID,
        "version": EXPECTED_ARXIV_VERSION,
        "versioned_id": EXPECTED_ARXIV_VERSIONED_ID,
        "category": EXPECTED_ARXIV_CATEGORY,
        "subjects": list(EXPECTED_ARXIV_SUBJECTS),
        "posted_date": EXPECTED_POSTED_DATE,
        "submitted_timestamp_utc": EXPECTED_SUBMITTED_TIMESTAMP_UTC,
        "doi": EXPECTED_ARXIV_DOI,
        "author_count": EXPECTED_AUTHOR_COUNT,
        "floating_pdf_url": EXPECTED_FLOATING_PDF_URL,
        "versioned_abs_url": EXPECTED_VERSIONED_ABS_URL,
        "versioned_pdf_url": EXPECTED_VERSIONED_PDF_URL,
        "tex_source_url": EXPECTED_TEX_SOURCE_URL,
        "license_url": EXPECTED_ARXIV_LICENSE_URL,
        "abstract_page_metadata_status": "manual_current_as_of_2026-06-13_without_html_snapshot",
        "expected_header_page": EXPECTED_HEADER_PAGE,
        "expected_header_phrase": EXPECTED_HEADER_PHRASE,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(AlphaEvolveSourcePdfVersionIssue(f"invalid_arxiv_{field}", f"arxiv_source.{field} must match the audited AlphaEvolve PDF header"))


def _validate_audit_policy(value: object, issues: list[AlphaEvolveSourcePdfVersionIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveSourcePdfVersionIssue("invalid_audit_policy", "audit_policy must be an object"))
        return
    required_true = (
        "manifest_url_requires_header_version_check",
        "claim_audits_must_name_source_version",
        "floating_url_refresh_is_not_silent_version_change",
        "arxiv_abs_html_snapshot_required_for_live_metadata_claims",
        "datacite_doi_resolution_not_snapshotted",
        "tex_source_not_cached",
        "arxiv_license_page_not_cached",
        "submission_history_refresh_gate_not_implemented",
    )
    for field in required_true:
        if value.get(field) is not True:
            issues.append(AlphaEvolveSourcePdfVersionIssue(f"invalid_audit_policy_{field}", f"audit_policy.{field} must be true"))
    scope = value.get("scope")
    if not isinstance(scope, str) or "not result-version provenance" not in scope:
        issues.append(AlphaEvolveSourcePdfVersionIssue("invalid_audit_policy_scope", "audit_policy.scope must distinguish source-PDF versioning from result-version provenance"))


def _normalize_header(value: str) -> str:
    return " ".join(value.split())
