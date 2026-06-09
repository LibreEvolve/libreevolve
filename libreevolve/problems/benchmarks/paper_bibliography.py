from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_REFERENCES_SECTION_SCHEMA = "libreevolve.alphaevolve_references_section.v1"
ALPHAEVOLVE_REFERENCES_BIBLIOGRAPHY_SCHEMA = (
    "libreevolve.alphaevolve_references_bibliography.v1"
)
EXPECTED_REFERENCES_BIBLIOGRAPHY_FILE = "papers/references.json"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_TITLE = "AlphaEvolve"
EXPECTED_FILE = "papers/2506.13131__AlphaEvolve.pdf"
EXPECTED_SECTION_TITLE = "References"
EXPECTED_FIRST_PAGE = 23
EXPECTED_LAST_PAGE = 32
EXPECTED_BIBLIOGRAPHY_LAST_PAGE = 33
EXPECTED_REFERENCE_COUNT = 120
EXPECTED_REFERENCE_IDS = tuple(str(index) for index in range(1, EXPECTED_REFERENCE_COUNT + 1))
EXPECTED_PAGE_RANGES = (
    {"source_page": 23, "first_reference_id": "1", "last_reference_id": "9", "reference_count": 9},
    {"source_page": 24, "first_reference_id": "10", "last_reference_id": "22", "reference_count": 13},
    {"source_page": 25, "first_reference_id": "23", "last_reference_id": "35", "reference_count": 13},
    {"source_page": 26, "first_reference_id": "36", "last_reference_id": "47", "reference_count": 12},
    {"source_page": 27, "first_reference_id": "48", "last_reference_id": "60", "reference_count": 13},
    {"source_page": 28, "first_reference_id": "61", "last_reference_id": "71", "reference_count": 11},
    {"source_page": 29, "first_reference_id": "72", "last_reference_id": "83", "reference_count": 12},
    {"source_page": 30, "first_reference_id": "84", "last_reference_id": "95", "reference_count": 12},
    {"source_page": 31, "first_reference_id": "96", "last_reference_id": "108", "reference_count": 13},
    {"source_page": 32, "first_reference_id": "109", "last_reference_id": "120", "reference_count": 12},
)
EXPECTED_ANCHORS = {
    "1": "Accurate structure prediction of biomolecular interactions",
    "3": "AI achieves silver-medal standard solving",
    "8": "A survey on the kissing numbers",
    "49": "Consequences of the Moosbauer-Poole algorithms",
    "90": "Can LLMs generate novel research ideas",
    "120": "Hypothesis generation with large language models",
}
_REFERENCE_MARKER_RE = re.compile(r"(?m)^\[(\d+)\]")
_ARXIV_ID_RE = re.compile(r"arXiv:(\d{4}\.\d{5})(?:v\d+)?", flags=re.IGNORECASE)
_DOI_RE = re.compile(r"\bdoi:\s*(.+)$", flags=re.IGNORECASE)
_URL_RE = re.compile(r"\b(?:URL)?(https?://\S+)", flags=re.IGNORECASE)
_YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")


@dataclass(frozen=True)
class AlphaEvolveReferencesSectionIssue:
    code: str
    message: str
    reference_id: str | None = None


@dataclass(frozen=True)
class AlphaEvolveReferencesSectionValidation:
    ok: bool
    reference_count: int
    page_count: int
    source_text_checked: bool
    issues: list[AlphaEvolveReferencesSectionIssue]


def alphaevolve_references_section_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_REFERENCES_SECTION_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "title": EXPECTED_TITLE,
        "source_file": EXPECTED_FILE,
        "section_title": EXPECTED_SECTION_TITLE,
        "source_page_span": {
            "first_page": EXPECTED_FIRST_PAGE,
            "last_page": EXPECTED_LAST_PAGE,
        },
        "reference_count": EXPECTED_REFERENCE_COUNT,
        "reference_ids": list(EXPECTED_REFERENCE_IDS),
        "page_ranges": [dict(row) for row in EXPECTED_PAGE_RANGES],
        "source_anchors": [
            {"reference_id": reference_id, "required_phrase": phrase}
            for reference_id, phrase in EXPECTED_ANCHORS.items()
        ],
        "normalization_status": {
            "stable_reference_ids_complete": True,
            "author_title_venue_fields_complete": False,
            "claim_links_complete": False,
            "manifest_titles_authoritative": False,
        },
    }


def alphaevolve_references_bibliography_record(
    page_text_by_number: dict[int, str],
    *,
    manifest_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    manifest_ids = {
        str(row.get("id"))
        for row in (manifest_rows or [])
        if isinstance(row.get("id"), str)
    }
    references = [
        _normalized_reference_entry(reference_id, raw_text, source_page, manifest_ids)
        for reference_id, raw_text, source_page in _reference_text_entries(page_text_by_number)
    ]
    return {
        "schema": ALPHAEVOLVE_REFERENCES_BIBLIOGRAPHY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "title": EXPECTED_TITLE,
        "source_file": EXPECTED_FILE,
        "source_section": EXPECTED_SECTION_TITLE,
        "source_page_span": {
            "first_page": EXPECTED_FIRST_PAGE,
            "last_page": EXPECTED_BIBLIOGRAPHY_LAST_PAGE,
        },
        "reference_count": len(references),
        "bibliography_policy": "pdf_references_are_authoritative_bibliography_metadata_not_download_manifest_titles",
        "field_policy": {
            "raw_citation_required": True,
            "author_title_venue_year_fields_required": True,
            "doi_url_arxiv_fields_nullable": True,
            "local_cache_linkage_required": True,
            "claim_links_complete": False,
        },
        "references": references,
    }


def validate_alphaevolve_references_section(
    recordset: object | str | Path | None = None,
    *,
    page_text_by_number: dict[int, str] | None = None,
) -> AlphaEvolveReferencesSectionValidation:
    data, read_issues = _load_recordset(recordset)
    if read_issues:
        return AlphaEvolveReferencesSectionValidation(False, 0, 0, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveReferencesSectionIssue] = []
    if data.get("schema") != ALPHAEVOLVE_REFERENCES_SECTION_SCHEMA:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_schema", "unsupported AlphaEvolve references-section schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("title") != EXPECTED_TITLE:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_title", "title must be AlphaEvolve"))
    if data.get("source_file") != EXPECTED_FILE:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_source_file", "source_file must identify the cached AlphaEvolve PDF"))
    if data.get("section_title") != EXPECTED_SECTION_TITLE:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_section_title", "section_title must be References"))
    _validate_source_page_span(data.get("source_page_span"), issues)
    reference_count = _validate_reference_ids(data.get("reference_ids"), data.get("reference_count"), issues)
    page_count = _validate_page_ranges(data.get("page_ranges"), issues)
    _validate_source_anchors(data.get("source_anchors"), issues)
    _validate_normalization_status(data.get("normalization_status"), issues)
    source_text_checked = page_text_by_number is not None
    if page_text_by_number is not None:
        _validate_extracted_page_text(page_text_by_number, issues)
    return AlphaEvolveReferencesSectionValidation(
        ok=not issues,
        reference_count=reference_count,
        page_count=page_count,
        source_text_checked=source_text_checked,
        issues=issues,
    )


def validate_alphaevolve_references_bibliography(
    recordset: object | str | Path,
    *,
    page_text_by_number: dict[int, str] | None = None,
    manifest_rows: list[dict[str, Any]] | None = None,
) -> AlphaEvolveReferencesSectionValidation:
    data, read_issues = _load_recordset(recordset)
    if read_issues:
        return AlphaEvolveReferencesSectionValidation(False, 0, 0, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveReferencesSectionIssue] = []
    if data.get("schema") != ALPHAEVOLVE_REFERENCES_BIBLIOGRAPHY_SCHEMA:
        issues.append(
            AlphaEvolveReferencesSectionIssue(
                "invalid_bibliography_schema",
                "unsupported AlphaEvolve references bibliography schema",
            )
        )
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("title") != EXPECTED_TITLE:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_title", "title must be AlphaEvolve"))
    if data.get("source_file") != EXPECTED_FILE:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_source_file", "source_file must identify the cached AlphaEvolve PDF"))
    if data.get("source_section") != EXPECTED_SECTION_TITLE:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_source_section", "source_section must be References"))
    _validate_bibliography_source_page_span(data.get("source_page_span"), issues)
    if data.get("bibliography_policy") != (
        "pdf_references_are_authoritative_bibliography_metadata_not_download_manifest_titles"
    ):
        issues.append(
            AlphaEvolveReferencesSectionIssue(
                "invalid_bibliography_policy",
                "bibliography_policy must distinguish PDF references from manifest display titles",
            )
        )
    _validate_bibliography_field_policy(data.get("field_policy"), issues)
    references = data.get("references")
    if not isinstance(references, list):
        issues.append(
            AlphaEvolveReferencesSectionIssue(
                "invalid_references",
                "references must be a list",
            )
        )
        references = []
    if data.get("reference_count") != EXPECTED_REFERENCE_COUNT:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_reference_count", "reference_count must be 120"))
    if len(references) != EXPECTED_REFERENCE_COUNT:
        issues.append(
            AlphaEvolveReferencesSectionIssue(
                "invalid_reference_row_count",
                "references must contain 120 normalized rows",
            )
        )
    _validate_bibliography_rows(references, issues, manifest_rows)
    source_text_checked = page_text_by_number is not None
    if page_text_by_number is not None:
        expected = alphaevolve_references_bibliography_record(
            page_text_by_number,
            manifest_rows=manifest_rows,
        )
        expected_by_id = {
            row["reference_id"]: row
            for row in expected["references"]
        }
        for row in references:
            if not isinstance(row, dict):
                continue
            reference_id = row.get("reference_id")
            if isinstance(reference_id, str) and expected_by_id.get(reference_id) != row:
                issues.append(
                    AlphaEvolveReferencesSectionIssue(
                        "bibliography_row_text_mismatch",
                        "bibliography row does not match the cached PDF reference text",
                        reference_id,
                    )
                )
    return AlphaEvolveReferencesSectionValidation(
        ok=not issues,
        reference_count=len(references),
        page_count=len({row.get("source_page") for row in references if isinstance(row, dict)}),
        source_text_checked=source_text_checked,
        issues=issues,
    )


def render_alphaevolve_references_section_summary(recordset: object | str | Path | None = None) -> str:
    validation = validate_alphaevolve_references_section(recordset)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve references-section evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| reference_count | {validation.reference_count} |",
        f"| page_count | {validation.page_count} |",
        f"| source_text_checked | {validation.source_text_checked} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(
            f"- {issue.code}: {issue.message}"
            + (f" ({issue.reference_id})" if issue.reference_id else "")
            for issue in validation.issues
        )
    return "\n".join(lines)


def _reference_text_entries(
    page_text_by_number: dict[int, str],
) -> list[tuple[str, str, int]]:
    source_page_by_reference_id: dict[str, int] = {}
    parts: list[str] = []
    for page in range(EXPECTED_FIRST_PAGE, EXPECTED_BIBLIOGRAPHY_LAST_PAGE + 1):
        page_text = _strip_page_noise(page_text_by_number.get(page, ""))
        for reference_id in _REFERENCE_MARKER_RE.findall(page_text):
            source_page_by_reference_id.setdefault(reference_id, page)
        parts.append(page_text)
    combined = "\n".join(parts)
    matches = list(_REFERENCE_MARKER_RE.finditer(combined))
    entries: list[tuple[str, str, int]] = []
    for index, match in enumerate(matches):
        reference_id = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(combined)
        raw_text = _normalize(combined[match.end() : end])
        entries.append((reference_id, raw_text, source_page_by_reference_id.get(reference_id, EXPECTED_FIRST_PAGE)))
    return entries


def _strip_page_noise(value: str) -> str:
    lines = []
    for line in value.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "AlphaEvolve: A coding agent for scientific and algorithmic discovery":
            continue
        if stripped.isdigit() and EXPECTED_FIRST_PAGE <= int(stripped) <= EXPECTED_BIBLIOGRAPHY_LAST_PAGE:
            continue
        if stripped == EXPECTED_SECTION_TITLE:
            continue
        lines.append(line)
    return "\n".join(lines)


def _normalized_reference_entry(
    reference_id: str,
    raw_text: str,
    source_page: int,
    manifest_ids: set[str],
) -> dict[str, Any]:
    arxiv_match = _ARXIV_ID_RE.search(raw_text)
    arxiv_id = arxiv_match.group(1) if arxiv_match else None
    doi_match = _DOI_RE.search(raw_text)
    url_match = _URL_RE.search(raw_text)
    years = _YEAR_RE.findall(raw_text)
    linked_manifest_row_id = arxiv_id if arxiv_id in manifest_ids else None
    return {
        "reference_id": reference_id,
        "source_page": source_page,
        "source_section": EXPECTED_SECTION_TITLE,
        "raw_citation": raw_text,
        "authors": _authors_from_raw_citation(raw_text),
        "title_text": _title_from_raw_citation(raw_text),
        "venue_text": _venue_from_raw_citation(raw_text),
        "year": int(years[-1]) if years else None,
        "doi": _clean_identifier(doi_match.group(1)) if doi_match else None,
        "url": _clean_identifier(url_match.group(1)) if url_match else None,
        "arxiv_id": arxiv_id,
        "local_cache": {
            "status": "present" if linked_manifest_row_id else "absent",
            "manifest_row_id": linked_manifest_row_id,
        },
        "citation_use_category": _citation_use_category(reference_id),
    }


def _authors_from_raw_citation(raw_text: str) -> str:
    boundary = _first_sentence_boundary(raw_text)
    return raw_text[:boundary].strip(" .") if boundary > 0 else raw_text


def _title_from_raw_citation(raw_text: str) -> str:
    boundary = _first_sentence_boundary(raw_text)
    if boundary <= 0:
        return raw_text
    remaining = raw_text[boundary:].lstrip(" .")
    next_boundary = _next_bibliography_boundary(remaining)
    return remaining[:next_boundary].strip(" .") if next_boundary > 0 else remaining


def _venue_from_raw_citation(raw_text: str) -> str | None:
    boundary = _first_sentence_boundary(raw_text)
    if boundary <= 0:
        return None
    remaining = raw_text[boundary:].lstrip(" .")
    title_boundary = _next_bibliography_boundary(remaining)
    if title_boundary <= 0:
        return None
    venue = remaining[title_boundary:].lstrip(" .")
    return venue or None


def _first_sentence_boundary(value: str) -> int:
    # Avoid splitting on initials by requiring at least two lowercase letters before
    # the boundary or a known collective-author word such as "team".
    for match in re.finditer(r"\.\s*", value):
        prefix = value[: match.start()].rstrip()
        next_text = value[match.end() :].lstrip()
        if not next_text:
            continue
        last_word = prefix.split()[-1] if prefix.split() else ""
        if len(last_word.strip(",")) > 2 or last_word.lower().strip(",") in {"al", "team", "teams"}:
            return match.end()
    return -1


def _next_bibliography_boundary(value: str) -> int:
    for marker in (". In", ". Nature", ". Science", ". arXiv", ". Proceedings", ". Advances"):
        index = value.find(marker)
        if index > 0:
            return index
    match = re.search(r"\.(?:\s|[A-Z])", value)
    return match.start() if match else -1


def _clean_identifier(value: str) -> str:
    return value.rstrip(".,);").replace(" ", "")


def _citation_use_category(reference_id: str) -> str:
    number = int(reference_id)
    if number in {23, 83, 99}:
        return "main_text_mathematical_discovery_context"
    if number in {26, 42, 47, 48, 49, 52, 72, 91, 92, 93, 95}:
        return "matrix_multiplication_context"
    if number in {8, 17, 25, 29, 31, 33, 39, 40, 70, 104, 107}:
        return "appendix_b_constructive_math_context"
    if number in {74}:
        return "archive_algorithm_context"
    if number in {83, 84}:
        return "alphatensor_funsearch_context"
    return "background_or_related_work"


def _load_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveReferencesSectionIssue]]:
    if recordset is None:
        return alphaevolve_references_section_record(), []
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [AlphaEvolveReferencesSectionIssue("read_error", f"failed to read references-section record: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [AlphaEvolveReferencesSectionIssue("invalid_json", f"invalid references-section JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [AlphaEvolveReferencesSectionIssue("invalid_shape", "references-section record must be a JSON object")]


def _validate_source_page_span(value: object, issues: list[AlphaEvolveReferencesSectionIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_source_page_span", "source_page_span must be an object"))
        return
    if value.get("first_page") != EXPECTED_FIRST_PAGE:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_first_page", "references section must start on page 23"))
    if value.get("last_page") != EXPECTED_LAST_PAGE:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_last_page", "references section must end on page 32"))


def _validate_bibliography_source_page_span(value: object, issues: list[AlphaEvolveReferencesSectionIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_source_page_span", "source_page_span must be an object"))
        return
    if value.get("first_page") != EXPECTED_FIRST_PAGE:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_first_page", "bibliography must start on page 23"))
    if value.get("last_page") != EXPECTED_BIBLIOGRAPHY_LAST_PAGE:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_last_page", "bibliography must include the reference 120 continuation on page 33"))


def _validate_reference_ids(
    value: object,
    declared_count: object,
    issues: list[AlphaEvolveReferencesSectionIssue],
) -> int:
    if declared_count != EXPECTED_REFERENCE_COUNT:
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_reference_count", "reference_count must be 120"))
    if not isinstance(value, list):
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_reference_ids", "reference_ids must be a list"))
        return 0
    ids = [item for item in value if isinstance(item, str)]
    if ids != list(EXPECTED_REFERENCE_IDS):
        issues.append(AlphaEvolveReferencesSectionIssue("reference_ids_mismatch", "reference_ids must be contiguous strings 1 through 120"))
    if len(ids) != len(set(ids)):
        issues.append(AlphaEvolveReferencesSectionIssue("duplicate_reference_id", "reference_ids must not contain duplicates"))
    return len(value)


def _validate_page_ranges(value: object, issues: list[AlphaEvolveReferencesSectionIssue]) -> int:
    if not isinstance(value, list):
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_page_ranges", "page_ranges must be a list"))
        return 0
    expected_rows = [dict(row) for row in EXPECTED_PAGE_RANGES]
    if value != expected_rows:
        issues.append(AlphaEvolveReferencesSectionIssue("page_ranges_mismatch", "page_ranges must preserve the reference marker ranges for pages 23-32"))
    return len(value)


def _validate_source_anchors(value: object, issues: list[AlphaEvolveReferencesSectionIssue]) -> None:
    if not isinstance(value, list):
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_source_anchors", "source_anchors must be a list"))
        return
    anchors = {
        item.get("reference_id"): item.get("required_phrase")
        for item in value
        if isinstance(item, dict)
    }
    for reference_id, phrase in EXPECTED_ANCHORS.items():
        if anchors.get(reference_id) != phrase:
            issues.append(
                AlphaEvolveReferencesSectionIssue(
                    "missing_source_anchor",
                    "source_anchors must preserve required reference phrases",
                    reference_id,
                )
            )


def _validate_normalization_status(value: object, issues: list[AlphaEvolveReferencesSectionIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_normalization_status", "normalization_status must be an object"))
        return
    expected = {
        "stable_reference_ids_complete": True,
        "author_title_venue_fields_complete": False,
        "claim_links_complete": False,
        "manifest_titles_authoritative": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(AlphaEvolveReferencesSectionIssue(f"invalid_normalization_{field}", f"normalization_status.{field} must preserve the bibliography boundary"))


def _validate_bibliography_field_policy(value: object, issues: list[AlphaEvolveReferencesSectionIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveReferencesSectionIssue("invalid_field_policy", "field_policy must be an object"))
        return
    expected = {
        "raw_citation_required": True,
        "author_title_venue_year_fields_required": True,
        "doi_url_arxiv_fields_nullable": True,
        "local_cache_linkage_required": True,
        "claim_links_complete": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(
                AlphaEvolveReferencesSectionIssue(
                    f"invalid_field_policy_{field}",
                    f"field_policy.{field} must preserve the bibliography boundary",
                )
            )


def _validate_bibliography_rows(
    references: list[object],
    issues: list[AlphaEvolveReferencesSectionIssue],
    manifest_rows: list[dict[str, Any]] | None,
) -> None:
    expected_ids = list(EXPECTED_REFERENCE_IDS)
    ids: list[str] = []
    manifest_ids = {
        str(row.get("id"))
        for row in (manifest_rows or [])
        if isinstance(row.get("id"), str)
    }
    for index, row in enumerate(references):
        if not isinstance(row, dict):
            issues.append(
                AlphaEvolveReferencesSectionIssue(
                    "invalid_reference_row",
                    f"reference row {index} must be an object",
                )
            )
            continue
        reference_id = row.get("reference_id")
        if not isinstance(reference_id, str):
            issues.append(AlphaEvolveReferencesSectionIssue("invalid_reference_id", "reference_id must be a string"))
            continue
        ids.append(reference_id)
        _validate_bibliography_row(row, issues, manifest_ids)
    if ids != expected_ids:
        issues.append(
            AlphaEvolveReferencesSectionIssue(
                "bibliography_reference_ids_mismatch",
                "bibliography reference ids must be contiguous strings 1 through 120",
            )
        )


def _validate_bibliography_row(
    row: dict[str, Any],
    issues: list[AlphaEvolveReferencesSectionIssue],
    manifest_ids: set[str],
) -> None:
    reference_id = str(row.get("reference_id"))
    for field in ("raw_citation", "authors", "title_text", "source_section", "citation_use_category"):
        if not isinstance(row.get(field), str) or not row.get(field):
            issues.append(
                AlphaEvolveReferencesSectionIssue(
                    f"invalid_reference_{field}",
                    f"reference {field} must be a non-empty string",
                    reference_id,
                )
            )
    if row.get("source_section") != EXPECTED_SECTION_TITLE:
        issues.append(
            AlphaEvolveReferencesSectionIssue(
                "invalid_reference_source_section",
                "reference source_section must be References",
                reference_id,
            )
        )
    source_page = row.get("source_page")
    if not isinstance(source_page, int) or not EXPECTED_FIRST_PAGE <= source_page <= EXPECTED_LAST_PAGE:
        issues.append(
            AlphaEvolveReferencesSectionIssue(
                "invalid_reference_source_page",
                "reference source_page must be a References page",
                reference_id,
            )
        )
    year = row.get("year")
    if year is not None and (not isinstance(year, int) or year < 1800 or year > 2100):
        issues.append(
            AlphaEvolveReferencesSectionIssue(
                "invalid_reference_year",
                "reference year must be null or a plausible integer year",
                reference_id,
            )
        )
    for nullable_field in ("venue_text", "doi", "url", "arxiv_id"):
        if row.get(nullable_field) is not None and not isinstance(row.get(nullable_field), str):
            issues.append(
                AlphaEvolveReferencesSectionIssue(
                    f"invalid_reference_{nullable_field}",
                    f"reference {nullable_field} must be null or a string",
                    reference_id,
                )
            )
    cache = row.get("local_cache")
    if not isinstance(cache, dict):
        issues.append(
            AlphaEvolveReferencesSectionIssue(
                "invalid_reference_local_cache",
                "reference local_cache must be an object",
                reference_id,
            )
        )
        return
    cache_status = cache.get("status")
    manifest_row_id = cache.get("manifest_row_id")
    if cache_status not in {"present", "absent"}:
        issues.append(
            AlphaEvolveReferencesSectionIssue(
                "invalid_reference_local_cache_status",
                "local_cache.status must be present or absent",
                reference_id,
            )
        )
    if cache_status == "present" and manifest_row_id not in manifest_ids:
        issues.append(
            AlphaEvolveReferencesSectionIssue(
                "invalid_reference_local_cache_manifest_row_id",
                "present local_cache rows must name a paper manifest id",
                reference_id,
            )
        )
    if cache_status == "absent" and manifest_row_id is not None:
        issues.append(
            AlphaEvolveReferencesSectionIssue(
                "invalid_absent_reference_local_cache_manifest_row_id",
                "absent local_cache rows must not name a manifest id",
                reference_id,
            )
        )


def _validate_extracted_page_text(
    page_text_by_number: dict[int, str],
    issues: list[AlphaEvolveReferencesSectionIssue],
) -> None:
    for page in range(EXPECTED_FIRST_PAGE, EXPECTED_LAST_PAGE + 1):
        if page not in page_text_by_number:
            issues.append(AlphaEvolveReferencesSectionIssue("missing_reference_page_text", "missing extracted text for a References page"))
    combined = "\n".join(page_text_by_number.get(page, "") for page in range(EXPECTED_FIRST_PAGE, EXPECTED_LAST_PAGE + 1))
    if EXPECTED_SECTION_TITLE not in page_text_by_number.get(EXPECTED_FIRST_PAGE, ""):
        issues.append(AlphaEvolveReferencesSectionIssue("missing_references_heading", "page 23 text must contain the References heading"))
    markers = _REFERENCE_MARKER_RE.findall(combined)
    if markers != list(EXPECTED_REFERENCE_IDS):
        issues.append(AlphaEvolveReferencesSectionIssue("extracted_reference_ids_mismatch", "extracted reference markers must be contiguous [1] through [120]"))
    for row in EXPECTED_PAGE_RANGES:
        page = row["source_page"]
        page_markers = _REFERENCE_MARKER_RE.findall(page_text_by_number.get(page, ""))
        expected_markers = list(range(int(row["first_reference_id"]), int(row["last_reference_id"]) + 1))
        if page_markers != [str(marker) for marker in expected_markers]:
            issues.append(
                AlphaEvolveReferencesSectionIssue(
                    "extracted_page_range_mismatch",
                    "extracted page marker range does not match the recorded References page range",
                )
            )
    normalized_text = _normalize(combined)
    for reference_id, phrase in EXPECTED_ANCHORS.items():
        if _normalize(phrase) not in normalized_text:
            issues.append(
                AlphaEvolveReferencesSectionIssue(
                    "missing_extracted_anchor_phrase",
                    "extracted References text must include the required anchor phrase",
                    reference_id,
                )
            )


def _normalize(value: str) -> str:
    return " ".join(value.split())
