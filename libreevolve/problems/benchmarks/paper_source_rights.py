from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_SOURCE_PDF_RIGHTS_SCHEMA = "libreevolve.alphaevolve_source_pdf_rights.v1"
ALPHAEVOLVE_SOURCE_PDF_RIGHTS_MANIFEST_SCHEMA = (
    "libreevolve.alphaevolve_source_pdf_rights_manifest.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_TITLE = "AlphaEvolve"
EXPECTED_FILE = "papers/2506.13131__AlphaEvolve.pdf"
EXPECTED_SOURCE_RIGHTS_MANIFEST_FILE = "papers/source_rights.json"
EXPECTED_SOURCE_IDENTITY_MANIFEST_FILE = "papers/row_identity.json"
EXPECTED_FLOATING_PDF_URL = "https://arxiv.org/pdf/2506.13131.pdf"
EXPECTED_RIGHTS_HOLDER = "Google DeepMind"
EXPECTED_COPYRIGHT_YEAR = 2025
EXPECTED_RIGHTS_STATEMENT = "© 2025 Google DeepMind. All rights reserved"
EXPECTED_SOURCE_PAGE = 1
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
class AlphaEvolveSourcePdfRightsIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveSourcePdfRightsValidation:
    ok: bool
    rights_count: int
    rights_text_checked: bool
    issues: list[AlphaEvolveSourcePdfRightsIssue]


def alphaevolve_source_pdf_rights_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_SOURCE_PDF_RIGHTS_SCHEMA,
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
        },
        "rights": {
            "rights_holder": EXPECTED_RIGHTS_HOLDER,
            "copyright_year": EXPECTED_COPYRIGHT_YEAR,
            "rights_statement": EXPECTED_RIGHTS_STATEMENT,
            "source_page": EXPECTED_SOURCE_PAGE,
            "source_location": "page_1_title_page_rights_line",
            "license_identifier": "all_rights_reserved_statement",
            "open_license_declared_in_cached_pdf": False,
            "arxiv_license_url_recorded_in_source_versions": True,
            "arxiv_license_page_cached": False,
            "arxiv_license_terms_recorded": False,
            "reuse_policy": "third_party_paper_source_rights_require_separate_review_before_reproduction",
        },
        "boundary": {
            "distinct_from_libreevolve_license": True,
            "distinct_from_companion_repository_license": True,
            "paper_derived_artifacts_must_carry_source_rights": True,
            "scope": "cached AlphaEvolve source PDF rights, not LibreEvolve repository licensing",
        },
    }


def alphaevolve_source_pdf_rights_manifest_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_SOURCE_PDF_RIGHTS_MANIFEST_SCHEMA,
        "source_rights_count": 1,
        "source_rights_policy": "paper_derived_artifacts_must_carry_source_rights_and_reproduction_policy",
        "sources": [
            {
                "manifest_row_id": EXPECTED_SOURCE_PAPER_ID,
                "source_identity_manifest": EXPECTED_SOURCE_IDENTITY_MANIFEST_FILE,
                "source_rights_record": alphaevolve_source_pdf_rights_record(),
                "paper_derived_artifact_policy": {
                    "artifact_classes": [
                        "excerpt",
                        "table",
                        "figure",
                        "quote",
                        "appendix_claim",
                    ],
                    "reproduction_policy": "third_party_paper_source_rights_require_separate_review_before_reproduction",
                    "must_separate_from_libreevolve_mit_license": True,
                    "must_separate_from_companion_repository_license": True,
                    "publication_ready_without_rights_review": False,
                    "claim_surfaces": [
                        "README.md",
                        "ROADMAP.md",
                        "papers/README.md",
                        "docs/todo/code.md",
                        "docs/todo/papers.md",
                        "docs/todo/readme.md",
                        "docs/todo/roadmap.md",
                    ],
                },
            }
        ],
    }


def validate_alphaevolve_source_pdf_rights(
    recordset: object | str | Path | None = None,
    *,
    first_page_text: str | None = None,
) -> AlphaEvolveSourcePdfRightsValidation:
    data, read_issues = _load_recordset(recordset)
    if read_issues:
        return AlphaEvolveSourcePdfRightsValidation(False, 0, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveSourcePdfRightsIssue] = []
    if data.get("schema") != ALPHAEVOLVE_SOURCE_PDF_RIGHTS_SCHEMA:
        issues.append(AlphaEvolveSourcePdfRightsIssue("invalid_schema", "unsupported AlphaEvolve source-PDF rights schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(AlphaEvolveSourcePdfRightsIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("title") != EXPECTED_TITLE:
        issues.append(AlphaEvolveSourcePdfRightsIssue("invalid_title", "title must be AlphaEvolve"))
    if data.get("source_kind") != "cached_arxiv_pdf":
        issues.append(AlphaEvolveSourcePdfRightsIssue("invalid_source_kind", "source_kind must be cached_arxiv_pdf"))
    _validate_manifest_row(data.get("manifest_row"), issues)
    _validate_rights(data.get("rights"), issues)
    _validate_boundary(data.get("boundary"), issues)
    rights_text_checked = first_page_text is not None
    if first_page_text is not None and _normalize(EXPECTED_RIGHTS_STATEMENT) not in _normalize(first_page_text):
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "missing_expected_rights_statement",
                "first-page text must include the expected AlphaEvolve rights statement",
            )
        )
    return AlphaEvolveSourcePdfRightsValidation(
        ok=not issues,
        rights_count=1 if isinstance(data.get("rights"), dict) else 0,
        rights_text_checked=rights_text_checked,
        issues=issues,
    )


def validate_alphaevolve_source_pdf_rights_manifest(
    recordset: object | str | Path | None = None,
    *,
    first_page_text: str | None = None,
) -> AlphaEvolveSourcePdfRightsValidation:
    data, read_issues = _load_manifest_recordset(recordset)
    if read_issues:
        return AlphaEvolveSourcePdfRightsValidation(False, 0, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveSourcePdfRightsIssue] = []
    if data.get("schema") != ALPHAEVOLVE_SOURCE_PDF_RIGHTS_MANIFEST_SCHEMA:
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "invalid_manifest_schema",
                "unsupported AlphaEvolve source-PDF rights manifest schema",
            )
        )
    if data.get("source_rights_policy") != (
        "paper_derived_artifacts_must_carry_source_rights_and_reproduction_policy"
    ):
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "invalid_manifest_policy",
                "source_rights_policy must require source rights and reproduction policy",
            )
        )
    sources = data.get("sources")
    if not isinstance(sources, list):
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "invalid_manifest_sources",
                "source-rights manifest sources must be a list",
            )
        )
        sources = []
    rights_count = len(sources)
    if data.get("source_rights_count") != rights_count:
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "invalid_manifest_source_rights_count",
                "source_rights_count must equal the number of source-rights records",
            )
        )
    if rights_count != 1:
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "invalid_manifest_source_count",
                "source-rights manifest must contain the cached AlphaEvolve source row",
            )
        )
    for index, source in enumerate(sources):
        _validate_source_rights_manifest_source(source, issues, first_page_text, index)
    return AlphaEvolveSourcePdfRightsValidation(
        ok=not issues,
        rights_count=rights_count,
        rights_text_checked=first_page_text is not None,
        issues=issues,
    )


def render_alphaevolve_source_pdf_rights_summary(recordset: object | str | Path | None = None) -> str:
    validation = validate_alphaevolve_source_pdf_rights(recordset)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve source-PDF rights evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| rights_count | {validation.rights_count} |",
        f"| rights_holder | {EXPECTED_RIGHTS_HOLDER} |",
        f"| copyright_year | {EXPECTED_COPYRIGHT_YEAR} |",
        f"| rights_text_checked | {validation.rights_text_checked} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_manifest_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveSourcePdfRightsIssue]]:
    if recordset is None:
        return alphaevolve_source_pdf_rights_manifest_record(), []
    return _load_recordset(recordset)


def _load_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveSourcePdfRightsIssue]]:
    if recordset is None:
        return alphaevolve_source_pdf_rights_record(), []
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [AlphaEvolveSourcePdfRightsIssue("read_error", f"failed to read source-PDF rights record: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [AlphaEvolveSourcePdfRightsIssue("invalid_json", f"invalid source-PDF rights JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [AlphaEvolveSourcePdfRightsIssue("invalid_shape", "source-PDF rights record must be a JSON object")]


def _validate_source_rights_manifest_source(
    value: object,
    issues: list[AlphaEvolveSourcePdfRightsIssue],
    first_page_text: str | None,
    index: int,
) -> None:
    if not isinstance(value, dict):
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "invalid_manifest_source",
                f"source-rights manifest source {index} must be an object",
            )
        )
        return
    if value.get("manifest_row_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "invalid_manifest_source_row_id",
                "source-rights manifest row id must match the cached AlphaEvolve row",
            )
        )
    if value.get("source_identity_manifest") != EXPECTED_SOURCE_IDENTITY_MANIFEST_FILE:
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "invalid_source_identity_manifest",
                "source-rights manifest must link to the source-identity manifest",
            )
        )
    rights_report = validate_alphaevolve_source_pdf_rights(
        value.get("source_rights_record"),
        first_page_text=first_page_text,
    )
    issues.extend(rights_report.issues)
    _validate_paper_derived_artifact_policy(
        value.get("paper_derived_artifact_policy"),
        issues,
    )


def _validate_paper_derived_artifact_policy(
    value: object,
    issues: list[AlphaEvolveSourcePdfRightsIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "invalid_artifact_policy",
                "paper_derived_artifact_policy must be an object",
            )
        )
        return
    expected_classes = {
        "excerpt",
        "table",
        "figure",
        "quote",
        "appendix_claim",
    }
    classes = value.get("artifact_classes")
    if not isinstance(classes, list) or not all(isinstance(item, str) for item in classes):
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "invalid_artifact_classes",
                "artifact_classes must list paper-derived artifact classes",
            )
        )
    elif set(classes) != expected_classes:
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "artifact_class_mismatch",
                "artifact_classes must cover excerpts, tables, figures, quotes, and appendix claims",
            )
        )
    if value.get("reproduction_policy") != (
        "third_party_paper_source_rights_require_separate_review_before_reproduction"
    ):
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "invalid_reproduction_policy",
                "reproduction_policy must require separate rights review before reproduction",
            )
        )
    for field in (
        "must_separate_from_libreevolve_mit_license",
        "must_separate_from_companion_repository_license",
    ):
        if value.get(field) is not True:
            issues.append(
                AlphaEvolveSourcePdfRightsIssue(
                    f"invalid_artifact_policy_{field}",
                    f"paper_derived_artifact_policy.{field} must be true",
                )
            )
    if value.get("publication_ready_without_rights_review") is not False:
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "invalid_publication_ready_without_rights_review",
                "publication_ready_without_rights_review must be false",
            )
        )
    expected_surfaces = {
        "README.md",
        "ROADMAP.md",
        "papers/README.md",
        "docs/todo/code.md",
        "docs/todo/papers.md",
        "docs/todo/readme.md",
        "docs/todo/roadmap.md",
    }
    surfaces = value.get("claim_surfaces")
    if not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces):
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "invalid_claim_surfaces",
                "claim_surfaces must list docs and TODO claim surfaces",
            )
        )
    elif set(surfaces) != expected_surfaces:
        issues.append(
            AlphaEvolveSourcePdfRightsIssue(
                "claim_surface_mismatch",
                "claim_surfaces must cover docs, papers, and active TODO evidence",
            )
        )


def _validate_manifest_row(value: object, issues: list[AlphaEvolveSourcePdfRightsIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveSourcePdfRightsIssue("invalid_manifest_row", "manifest_row must be an object"))
        return
    expected = {
        "id": EXPECTED_SOURCE_PAPER_ID,
        "title": EXPECTED_TITLE,
        "url": EXPECTED_FLOATING_PDF_URL,
        "file": EXPECTED_FILE,
        "bytes": EXPECTED_BYTES,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(AlphaEvolveSourcePdfRightsIssue(f"invalid_manifest_{field}", f"manifest_row.{field} must match the cached AlphaEvolve PDF row"))
    sha256 = value.get("sha256")
    if not isinstance(sha256, str) or _SHA256_RE.fullmatch(sha256) is None:
        issues.append(AlphaEvolveSourcePdfRightsIssue("invalid_manifest_sha256", "manifest_row.sha256 must be a lowercase 64-hex digest"))
    elif sha256 != EXPECTED_SHA256:
        issues.append(AlphaEvolveSourcePdfRightsIssue("manifest_sha256_drift", "manifest_row.sha256 must match the cached AlphaEvolve PDF digest"))


def _validate_rights(value: object, issues: list[AlphaEvolveSourcePdfRightsIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveSourcePdfRightsIssue("invalid_rights", "rights must be an object"))
        return
    expected = {
        "rights_holder": EXPECTED_RIGHTS_HOLDER,
        "copyright_year": EXPECTED_COPYRIGHT_YEAR,
        "rights_statement": EXPECTED_RIGHTS_STATEMENT,
        "source_page": EXPECTED_SOURCE_PAGE,
        "source_location": "page_1_title_page_rights_line",
        "license_identifier": "all_rights_reserved_statement",
        "open_license_declared_in_cached_pdf": False,
        "arxiv_license_url_recorded_in_source_versions": True,
        "arxiv_license_page_cached": False,
        "arxiv_license_terms_recorded": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(AlphaEvolveSourcePdfRightsIssue(f"invalid_rights_{field}", f"rights.{field} must match the cached AlphaEvolve PDF rights evidence"))
    reuse_policy = value.get("reuse_policy")
    if not isinstance(reuse_policy, str) or "separate_review" not in reuse_policy:
        issues.append(AlphaEvolveSourcePdfRightsIssue("invalid_reuse_policy", "reuse_policy must require separate review before reproduction"))


def _validate_boundary(value: object, issues: list[AlphaEvolveSourcePdfRightsIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveSourcePdfRightsIssue("invalid_boundary", "boundary must be an object"))
        return
    required_true = (
        "distinct_from_libreevolve_license",
        "distinct_from_companion_repository_license",
        "paper_derived_artifacts_must_carry_source_rights",
    )
    for field in required_true:
        if value.get(field) is not True:
            issues.append(AlphaEvolveSourcePdfRightsIssue(f"invalid_boundary_{field}", f"boundary.{field} must be true"))
    scope = value.get("scope")
    if not isinstance(scope, str) or "not LibreEvolve repository licensing" not in scope:
        issues.append(AlphaEvolveSourcePdfRightsIssue("invalid_boundary_scope", "boundary.scope must distinguish source-PDF rights from LibreEvolve licensing"))


def _normalize(value: str) -> str:
    return " ".join(value.split())
