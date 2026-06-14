from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pypdf import PdfReader


ALPHAEVOLVE_CACHED_PDF_HEADER_CONSISTENCY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_cached_pdf_header_consistency_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_VERSION_ID = "2506.13131v1"
EXPECTED_PDF_ARTIFACT_PATH = "papers/2506.13131__AlphaEvolve.pdf"
EXPECTED_PDF_BYTES = 3525764
EXPECTED_PDF_SHA256 = (
    "f092c8cbd65da89951ee6496374da9a54963f9035758c25ac6e4625f506df9ad"
)
EXPECTED_BOUNDARY_STATUS = "cached_pdf_header_consistency_recorded_without_refresh_gate"
EXPECTED_FIRST_PAGE_TEXT_CHARS = 3505
EXPECTED_NORMALIZED_FIRST_PAGE_TEXT_CHARS = 3503
EXPECTED_FIRST_PAGE_TEXT_SHA256 = (
    "63d1a313606834b3e02f3b8ba7b39d09204c6b9796df8cca82155a3b0797514b"
)
EXPECTED_NORMALIZED_FIRST_PAGE_TEXT_SHA256 = (
    "b824d50aced8d82d43468d67f3000183490014d3669481a5597d8a0a3e8a8b78"
)
EXPECTED_REQUIRED_MARKERS = {
    "has_arxiv_header": True,
    "has_title": True,
    "has_google_deepmind": True,
    "has_rights_statement": True,
}
EXPECTED_MISSING_EVIDENCE = {
    "metadata_extraction_script_artifact": "not_recorded_locally",
    "automated_cached_pdf_header_refresh_gate": "not_recorded_locally",
}


@dataclass(frozen=True)
class AlphaEvolveCachedPdfHeaderConsistencyBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveCachedPdfHeaderConsistencyBoundaryValidation:
    ok: bool
    boundary_status: str | None
    header_checked: bool
    missing_evidence_count: int
    issues: list[AlphaEvolveCachedPdfHeaderConsistencyBoundaryIssue]


def alphaevolve_cached_pdf_header_consistency_boundary_record() -> dict[str, Any]:
    """Return cached-PDF first-page header consistency evidence."""

    return {
        "schema": ALPHAEVOLVE_CACHED_PDF_HEADER_CONSISTENCY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_version_id": EXPECTED_SOURCE_VERSION_ID,
        "source_claim": (
            "AlphaEvolve source metadata should prove the retained cached PDF "
            "first-page header matches the expected arXiv version and rights "
            "markers."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "pdf_artifact": {
            "path": EXPECTED_PDF_ARTIFACT_PATH,
            "bytes": EXPECTED_PDF_BYTES,
            "sha256": EXPECTED_PDF_SHA256,
            "artifact_retained": True,
        },
        "first_page_extraction": {
            "page_index": 0,
            "tool": "pypdf.PdfReader.pages[0].extract_text",
            "strict_pdf_reader": True,
            "text_chars": EXPECTED_FIRST_PAGE_TEXT_CHARS,
            "normalized_text_chars": EXPECTED_NORMALIZED_FIRST_PAGE_TEXT_CHARS,
            "text_sha256": EXPECTED_FIRST_PAGE_TEXT_SHA256,
            "normalized_text_sha256": EXPECTED_NORMALIZED_FIRST_PAGE_TEXT_SHA256,
            "required_markers": dict(EXPECTED_REQUIRED_MARKERS),
        },
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records cached-PDF first-page header consistency for "
            "the retained AlphaEvolve PDF, including arXiv version, title, "
            "Google DeepMind, and rights markers. It does not claim a reusable "
            "metadata extraction-script artifact or an automated cached-PDF "
            "header refresh gate."
        ),
    }


def validate_alphaevolve_cached_pdf_header_consistency_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveCachedPdfHeaderConsistencyBoundaryValidation:
    data, read_issues, base_dir = _load_boundary(
        alphaevolve_cached_pdf_header_consistency_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveCachedPdfHeaderConsistencyBoundaryValidation(
            False, None, False, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveCachedPdfHeaderConsistencyBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_CACHED_PDF_HEADER_CONSISTENCY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported cached-PDF header boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_version_id") != EXPECTED_SOURCE_VERSION_ID:
        issues.append(_issue("invalid_source_version_id", "source_version_id must be 2506.13131v1"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "first-page header" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must describe cached-PDF first-page header evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "cached-PDF header boundary must not claim refresh readiness"))
    _validate_pdf_artifact(data.get("pdf_artifact"), issues)
    _validate_first_page_extraction(data.get("first_page_extraction"), issues)
    header_checked = False
    if base_dir is not None:
        header_checked = _validate_retained_pdf_header(data, base_dir, issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "cached-PDF first-page header consistency" not in boundary_text
        or "metadata extraction-script artifact" not in boundary_text
        or "automated cached-PDF header refresh gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate cached-PDF header evidence from refresh/extraction gaps"))
    return AlphaEvolveCachedPdfHeaderConsistencyBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        header_checked=header_checked,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_cached_pdf_header_consistency_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_cached_pdf_header_consistency_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve cached-PDF header consistency boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| header_checked | {validation.header_checked} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _validate_pdf_artifact(
    value: object,
    issues: list[AlphaEvolveCachedPdfHeaderConsistencyBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_pdf_artifact", "pdf_artifact must be an object"))
        return
    expected = {
        "path": EXPECTED_PDF_ARTIFACT_PATH,
        "bytes": EXPECTED_PDF_BYTES,
        "sha256": EXPECTED_PDF_SHA256,
        "artifact_retained": True,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_pdf_artifact_{key}", f"pdf_artifact.{key} must be {expected_value}"))


def _validate_first_page_extraction(
    value: object,
    issues: list[AlphaEvolveCachedPdfHeaderConsistencyBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_first_page_extraction", "first_page_extraction must be an object"))
        return
    expected = {
        "page_index": 0,
        "tool": "pypdf.PdfReader.pages[0].extract_text",
        "strict_pdf_reader": True,
        "text_chars": EXPECTED_FIRST_PAGE_TEXT_CHARS,
        "normalized_text_chars": EXPECTED_NORMALIZED_FIRST_PAGE_TEXT_CHARS,
        "text_sha256": EXPECTED_FIRST_PAGE_TEXT_SHA256,
        "normalized_text_sha256": EXPECTED_NORMALIZED_FIRST_PAGE_TEXT_SHA256,
        "required_markers": dict(EXPECTED_REQUIRED_MARKERS),
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_first_page_extraction_{key}", f"first_page_extraction.{key} must be {expected_value}"))


def _validate_retained_pdf_header(
    data: dict[str, Any],
    base_dir: Path,
    issues: list[AlphaEvolveCachedPdfHeaderConsistencyBoundaryIssue],
) -> bool:
    artifact = data.get("pdf_artifact")
    extraction = data.get("first_page_extraction")
    if not isinstance(artifact, dict) or not isinstance(extraction, dict):
        return False
    path_value = artifact.get("path")
    if not isinstance(path_value, str):
        return False
    pdf_path = base_dir / path_value
    try:
        pdf_bytes = pdf_path.read_bytes()
    except OSError as exc:
        issues.append(_issue("missing_pdf_artifact", f"cached PDF artifact could not be read: {exc}"))
        return False
    if len(pdf_bytes) != EXPECTED_PDF_BYTES:
        issues.append(_issue("invalid_pdf_artifact_file_bytes", f"cached PDF artifact must be {EXPECTED_PDF_BYTES} bytes"))
    if hashlib.sha256(pdf_bytes).hexdigest() != EXPECTED_PDF_SHA256:
        issues.append(_issue("invalid_pdf_artifact_file_sha256", f"cached PDF artifact SHA-256 must be {EXPECTED_PDF_SHA256}"))
    try:
        first_page_text = PdfReader(pdf_path, strict=True).pages[0].extract_text() or ""
    except Exception as exc:  # pragma: no cover - exercised by manifest tests with valid PDFs
        issues.append(_issue("pdf_header_read_error", f"cached PDF first page could not be extracted: {exc}"))
        return False
    normalized = " ".join(first_page_text.split())
    if len(first_page_text) != EXPECTED_FIRST_PAGE_TEXT_CHARS:
        issues.append(_issue("invalid_first_page_text_chars", f"first-page text must be {EXPECTED_FIRST_PAGE_TEXT_CHARS} characters"))
    if len(normalized) != EXPECTED_NORMALIZED_FIRST_PAGE_TEXT_CHARS:
        issues.append(_issue("invalid_normalized_first_page_text_chars", f"normalized first-page text must be {EXPECTED_NORMALIZED_FIRST_PAGE_TEXT_CHARS} characters"))
    if hashlib.sha256(first_page_text.encode("utf-8")).hexdigest() != EXPECTED_FIRST_PAGE_TEXT_SHA256:
        issues.append(_issue("invalid_first_page_text_sha256", f"first-page text SHA-256 must be {EXPECTED_FIRST_PAGE_TEXT_SHA256}"))
    if hashlib.sha256(normalized.encode("utf-8")).hexdigest() != EXPECTED_NORMALIZED_FIRST_PAGE_TEXT_SHA256:
        issues.append(_issue("invalid_normalized_first_page_text_sha256", f"normalized first-page text SHA-256 must be {EXPECTED_NORMALIZED_FIRST_PAGE_TEXT_SHA256}"))
    actual_markers = {
        "has_arxiv_header": "arXiv:2506.13131v1 [cs.AI] 16 Jun 2025" in normalized,
        "has_title": "AlphaEvolve: A coding agent for scientific and algorithmic discovery" in normalized,
        "has_google_deepmind": "Google DeepMind" in normalized,
        "has_rights_statement": "All rights reserved" in normalized,
    }
    if actual_markers != EXPECTED_REQUIRED_MARKERS:
        issues.append(_issue("first_page_required_marker_drift", "cached PDF first-page markers must match expected header evidence"))
    if extraction.get("required_markers") != actual_markers:
        issues.append(_issue("first_page_required_marker_record_drift", "recorded first-page markers must match extracted PDF text"))
    return True


def _validate_missing_evidence(
    value: object,
    issues: list[AlphaEvolveCachedPdfHeaderConsistencyBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_missing_evidence_key", f"missing_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_missing_evidence_key", f"missing_evidence has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveCachedPdfHeaderConsistencyBoundaryIssue], Path | None]:
    if isinstance(boundary, dict):
        return dict(boundary), [], None
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")], None
        base_dir = None
    else:
        path = Path(boundary)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")], None
        base_dir = path.parent.parent
    if isinstance(data, dict):
        return data, [], base_dir
    return None, [_issue("invalid_shape", "cached-PDF header boundary must be a JSON object")], None


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveCachedPdfHeaderConsistencyBoundaryIssue:
    return AlphaEvolveCachedPdfHeaderConsistencyBoundaryIssue(code, message)
