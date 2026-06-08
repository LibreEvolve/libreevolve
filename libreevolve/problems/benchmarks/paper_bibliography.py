from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_REFERENCES_SECTION_SCHEMA = "libreevolve.alphaevolve_references_section.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_TITLE = "AlphaEvolve"
EXPECTED_FILE = "papers/2506.13131__AlphaEvolve.pdf"
EXPECTED_SECTION_TITLE = "References"
EXPECTED_FIRST_PAGE = 23
EXPECTED_LAST_PAGE = 32
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
