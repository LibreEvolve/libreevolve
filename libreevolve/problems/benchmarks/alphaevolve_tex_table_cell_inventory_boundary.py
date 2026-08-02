from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.alphaevolve_citation_use_inventory_boundary import (
    EXPECTED_ENTRYPOINT,
    EXPECTED_TEX_CLOSURE_FILES,
    _consume_group,
    _normalize_whitespace,
    _read_source_archive,
    _section_headings,
    _section_path_at,
    _skip_whitespace,
    _strip_tex_comments,
    _tex_dependency_closure,
)
from libreevolve.problems.benchmarks.paper_bibliography import (
    EXPECTED_SOURCE_PAPER_ID,
)


ALPHAEVOLVE_TEX_TABLE_CELL_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_tex_table_cell_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "tex_table_rows_and_cells_dispositioned_without_citation_semantics_or_"
    "result_reproduction"
)
EXPECTED_TABLE_COUNT = 3
EXPECTED_TABULAR_BLOCK_COUNT = 5
EXPECTED_ROW_COUNT = 83
EXPECTED_DATA_ROW_COUNT = 78
EXPECTED_HEADER_ROW_COUNT = 5
EXPECTED_CELL_COUNT = 240
EXPECTED_BOUNDED_CLAIM_COMPONENT_CELL_COUNT = 218
EXPECTED_SOURCE_CONTEXT_ONLY_CELL_COUNT = 8
EXPECTED_STRUCTURAL_HEADER_CELL_COUNT = 14
EXPECTED_ROW_CLAIM_REF_COUNT = 78
EXPECTED_CELL_CLAIM_REF_COUNT = 218
EXPECTED_UNIQUE_MAPPED_CLAIM_COUNT = 78
EXPECTED_CITATION_OCCURRENCE_COUNT = 71
EXPECTED_CITATION_KEY_LINK_COUNT = 72

_SOURCE_INVENTORY_PATH = "papers/alphaevolve_source_inventory_boundary.json"
_CLAIM_INVENTORY_PATHS = {
    "table_1": "papers/alphaevolve_system_requirement_inventory_boundary.json",
    "table_2": "papers/alphaevolve_matrix_result_claim_inventory_boundary.json",
    "table_3": "papers/alphaevolve_appendix_a_claim_inventory_boundary.json",
}
_TODO_SPECS = (
    {
        "todo_id": "whole_paper_semantics_code",
        "path": "docs/todo/code.md",
        "required_phrase": "Add exhaustive implementation-evidence mapping for AlphaEvolve",
    },
    {
        "todo_id": "whole_paper_semantics_paper",
        "path": "docs/todo/papers.md",
        "required_phrase": "Extend the bounded AlphaEvolve claim inventories to the whole paper.",
    },
    {
        "todo_id": "whole_paper_semantics_roadmap",
        "path": "docs/todo/roadmap.md",
        "required_phrase": "whole-paper requirement",
    },
)

_TABLE_1_ROWS = (
    ("evolves single function", "table1_entire_code_file"),
    ("evolves up to 10-20 lines of code", "table1_hundreds_of_lines"),
    ("evolves code in Python", "table1_any_language"),
    (
        "needs fast evaluation",
        "table1_expensive_parallel_accelerated_evaluation",
    ),
    ("millions of LLM samples used", "table1_thousands_of_samples_suffice"),
    ("small LLMs used; no benefit from larger", "table1_benefits_from_sota_models"),
    (
        "minimal context (only previous solutions)",
        "table1_rich_context_and_feedback",
    ),
    ("optimizes single metric", "table1_multiple_metrics"),
)
_TABLE_2_CLAIM_IDS = {
    (2, 4, 5): "table2_mm_2x4x5_rank32",
    (2, 4, 7): "table2_mm_2x4x7_rank45",
    (2, 4, 8): "table2_mm_2x4x8_rank51",
    (2, 5, 6): "table2_mm_2x5x6_rank47",
    (3, 3, 3): "table2_mm_3x3x3_rank23",
    (3, 4, 6): "table2_mm_3x4x6_rank54",
    (3, 4, 7): "table2_mm_3x4x7_rank63",
    (3, 4, 8): "table2_mm_3x4x8_rank74",
    (3, 5, 6): "table2_mm_3x5x6_rank68",
    (3, 5, 7): "table2_mm_3x5x7_rank80",
    (4, 4, 4): "table2_mm_4x4x4_rank48",
    (4, 4, 5): "table2_mm_4x4x5_rank61",
    (4, 4, 7): "table2_mm_4x4x7_rank85",
    (4, 4, 8): "table2_mm_4x4x8_rank96",
    (4, 5, 6): "table2_mm_4x5x6_rank90",
    (5, 5, 5): "table2_mm_5x5x5_rank93",
}
_TABULAR_SPECS = {
    ("introduction.tex", 1): {
        "table_id": "table_1",
        "table_label": "tab:funsearch-vs-alphaevolve",
        "source_page": 2,
        "expected_column_count": 2,
        "expected_data_row_count": 8,
        "header_roles": ("comparison_baseline_header", "alphaevolve_header"),
    },
    ("results.tex", 1): {
        "table_id": "table_2",
        "table_label": "tab:relaxed-opt-results",
        "source_page": 9,
        "expected_column_count": 3,
        "expected_data_row_count": 16,
        "header_roles": (
            "matrix_target_header",
            "best_known_reference_header",
            "alphaevolve_result_header",
        ),
    },
    ("appendix.tex", 1): {
        "table_id": "table_3",
        "table_label": "tab:relaxed-opt-results-appendix",
        "source_page": 34,
        "expected_column_count": 3,
        "expected_data_row_count": 18,
        "header_roles": (
            "matrix_target_header",
            "best_known_reference_header",
            "alphaevolve_result_header",
        ),
    },
    ("appendix.tex", 2): {
        "table_id": "table_3",
        "table_label": "tab:relaxed-opt-results-appendix",
        "source_page": 34,
        "expected_column_count": 3,
        "expected_data_row_count": 18,
        "header_roles": (
            "matrix_target_header",
            "best_known_reference_header",
            "alphaevolve_result_header",
        ),
    },
    ("appendix.tex", 3): {
        "table_id": "table_3",
        "table_label": "tab:relaxed-opt-results-appendix",
        "source_page": 34,
        "expected_column_count": 3,
        "expected_data_row_count": 18,
        "header_roles": (
            "matrix_target_header",
            "best_known_reference_header",
            "alphaevolve_result_header",
        ),
    },
}
_EXPECTED_TABLE_BREAKDOWN = {
    "table_1": {
        "tabular_block_count": 1,
        "row_count": 9,
        "data_row_count": 8,
        "header_row_count": 1,
        "cell_count": 18,
    },
    "table_2": {
        "tabular_block_count": 1,
        "row_count": 17,
        "data_row_count": 16,
        "header_row_count": 1,
        "cell_count": 51,
    },
    "table_3": {
        "tabular_block_count": 3,
        "row_count": 57,
        "data_row_count": 54,
        "header_row_count": 3,
        "cell_count": 171,
    },
}

_TABULAR_BEGIN_RE = re.compile(r"\\begin\s*\{tabular\}")
_TABLE_BEGIN_RE = re.compile(r"\\begin\s*\{table\}")
_TABLE_RULE_RE = re.compile(r"\\(?:toprule|midrule|bottomrule)\b")
_MATRIX_TARGET_RE = re.compile(
    r"\\langle\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\\rangle"
)
_CITATION_RE = re.compile(
    r"\\(?:cite|citep|citet|citeauthor|citeyear|authoryearcite|authoryearcitet)\*?"
    r"(?:\s*\[[^\]]*\])*\s*\{([^{}]+)\}"
)


@dataclass(frozen=True)
class AlphaEvolveTexTableCellInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveTexTableCellInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    table_count: int
    tabular_block_count: int
    row_count: int
    cell_count: int
    unmapped_row_count: int
    unmapped_cell_count: int
    unresolved_reference_count: int
    issues: list[AlphaEvolveTexTableCellInventoryBoundaryIssue]


def alphaevolve_tex_table_cell_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Inventory and disposition every retained AlphaEvolve table row and cell."""

    root_path = Path(root)
    source_artifact, archive_texts, source_errors = _read_source_archive(root_path)
    tex_texts = {
        name: text
        for name, text in archive_texts.items()
        if name.casefold().endswith(".tex")
    }
    closure = _tex_dependency_closure(tex_texts, EXPECTED_ENTRYPOINT)
    parsed_blocks, parse_errors = _parse_tabular_blocks(tex_texts, closure)
    claim_ids, named_span_ids, reference_errors = _reference_ids(root_path)
    blocks, rows, cells, disposition_errors = _disposition_records(
        parsed_blocks,
        claim_ids,
        named_span_ids,
    )
    source_errors = sorted(set([*source_errors, *reference_errors]))
    parse_errors = sorted(set([*parse_errors, *disposition_errors]))
    table_environment_count = sum(
        len(_TABLE_BEGIN_RE.findall(_strip_tex_comments(tex_texts.get(name, ""))))
        for name in closure
    )
    table_breakdown = _table_breakdown(blocks, rows, cells)
    row_disposition_counts = Counter(row["disposition"] for row in rows)
    cell_disposition_counts = Counter(cell["disposition"] for cell in cells)
    row_claim_ref_count = sum(len(row["claim_refs"]) for row in rows)
    cell_claim_ref_count = sum(len(cell["claim_refs"]) for cell in cells)
    unique_mapped_claim_ids = sorted(
        {
            ref["claim_id"]
            for row in rows
            for ref in row["claim_refs"]
        }
    )
    unresolved_reference_count = sum(
        1
        for record in [*rows, *cells]
        for ref in [*record["claim_refs"], *record["named_span_refs"]]
        if not ref["resolved"]
    )
    citation_occurrence_count = sum(
        cell["citation_occurrence_count"] for cell in cells
    )
    citation_key_link_count = sum(len(cell["citation_keys"]) for cell in cells)
    unmapped_row_count = row_disposition_counts["unmapped"]
    unmapped_cell_count = cell_disposition_counts["unmapped"]
    todo_refs = [_todo_ref(root_path, spec) for spec in _TODO_SPECS]
    todo_ownership_ready = all(
        ref["exists"] and ref["required_phrase_present"] for ref in todo_refs
    )
    row_cell_inventory_ready = (
        source_artifact["identity_ok"]
        and not source_errors
        and not parse_errors
        and tuple(closure) == EXPECTED_TEX_CLOSURE_FILES
        and table_environment_count == EXPECTED_TABLE_COUNT
        and len(blocks) == EXPECTED_TABULAR_BLOCK_COUNT
        and len(rows) == EXPECTED_ROW_COUNT
        and row_disposition_counts["bounded_claim_row"]
        == EXPECTED_DATA_ROW_COUNT
        and row_disposition_counts["structural_header_row"]
        == EXPECTED_HEADER_ROW_COUNT
        and len(cells) == EXPECTED_CELL_COUNT
        and table_breakdown == _EXPECTED_TABLE_BREAKDOWN
    )
    semantic_disposition_ready = (
        row_cell_inventory_ready
        and cell_disposition_counts["bounded_claim_component"]
        == EXPECTED_BOUNDED_CLAIM_COMPONENT_CELL_COUNT
        and cell_disposition_counts["source_context_only_baseline_cell"]
        == EXPECTED_SOURCE_CONTEXT_ONLY_CELL_COUNT
        and cell_disposition_counts["structural_header_cell"]
        == EXPECTED_STRUCTURAL_HEADER_CELL_COUNT
        and row_claim_ref_count == EXPECTED_ROW_CLAIM_REF_COUNT
        and cell_claim_ref_count == EXPECTED_CELL_CLAIM_REF_COUNT
        and len(unique_mapped_claim_ids) == EXPECTED_UNIQUE_MAPPED_CLAIM_COUNT
        and citation_occurrence_count == EXPECTED_CITATION_OCCURRENCE_COUNT
        and citation_key_link_count == EXPECTED_CITATION_KEY_LINK_COUNT
        and unmapped_row_count == 0
        and unmapped_cell_count == 0
        and unresolved_reference_count == 0
        and todo_ownership_ready
    )
    return {
        "schema": ALPHAEVOLVE_TEX_TABLE_CELL_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "row_cell_inventory_ready": row_cell_inventory_ready,
        "table_cell_semantic_disposition_ready": semantic_disposition_ready,
        "citation_semantic_mapping_ready": False,
        "table_result_reproduction_ready": False,
        "whole_paper_proposition_exhaustiveness_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_errors": source_errors,
        "parse_errors": parse_errors,
        "source_closure": {
            "entrypoint": EXPECTED_ENTRYPOINT,
            "file_count": len(closure),
            "files": [
                {
                    "path": name,
                    "sha256": hashlib.sha256(
                        archive_texts.get(name, "").encode("utf-8")
                    ).hexdigest(),
                }
                for name in closure
            ],
        },
        "table_count": table_environment_count,
        "tabular_block_count": len(blocks),
        "row_count": len(rows),
        "data_row_count": row_disposition_counts["bounded_claim_row"],
        "header_row_count": row_disposition_counts["structural_header_row"],
        "cell_count": len(cells),
        "bounded_claim_component_cell_count": cell_disposition_counts[
            "bounded_claim_component"
        ],
        "source_context_only_cell_count": cell_disposition_counts[
            "source_context_only_baseline_cell"
        ],
        "structural_header_cell_count": cell_disposition_counts[
            "structural_header_cell"
        ],
        "row_claim_ref_count": row_claim_ref_count,
        "cell_claim_ref_count": cell_claim_ref_count,
        "unique_mapped_claim_count": len(unique_mapped_claim_ids),
        "unique_mapped_claim_ids": unique_mapped_claim_ids,
        "citation_occurrence_count": citation_occurrence_count,
        "citation_key_link_count": citation_key_link_count,
        "unmapped_row_count": unmapped_row_count,
        "unmapped_cell_count": unmapped_cell_count,
        "unresolved_reference_count": unresolved_reference_count,
        "new_claim_count": 0,
        "table_breakdown": table_breakdown,
        "tabular_block_records": blocks,
        "row_records": rows,
        "cell_records": cells,
        "active_todo_refs": todo_refs,
        "todo_ownership_ready": todo_ownership_ready,
        "inventory_scope": {
            "included": [
                "all three table environments in the recursive main.tex closure",
                "all five tabular blocks and their 83 rows",
                "all 240 top-level cells with source anchors and hashes",
                "all 78 data rows mapped to existing bounded claim ids",
                "cell-level bounded-claim, source-context-only, or structural-header disposition",
                "lexical citation keys retained for every citation-bearing cell",
            ],
            "excluded": [
                "semantic sufficiency, relevance, or correctness of cited sources",
                "independent verification of best-known baseline values",
                "reproduction of AlphaEvolve matrix decompositions or ranks",
                "sentence, paragraph, inline-math, code-listing-line, and image-pixel proposition exhaustiveness",
                "independent reviewer proof or AlphaEvolve system parity",
            ],
        },
        "claim_boundary": (
            "This sidecar certifies source-pinned row and cell disposition for "
            "all 83 rows and 240 cells in the retained AlphaEvolve Tables 1-3. "
            "All 78 data rows map to existing bounded claim ids; 218 cells are "
            "bounded-claim components, eight are FunSearch baseline context, "
            "and 14 are structural headers. It adds zero claims and does not "
            "establish citation sufficiency, baseline correctness, table-result "
            "reproduction, whole-paper proposition exhaustiveness, or "
            "AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_tex_table_cell_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveTexTableCellInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_tex_table_cell_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveTexTableCellInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_tex_table_cell_inventory_boundary_record(root)
    issues: list[AlphaEvolveTexTableCellInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_TEX_TABLE_CELL_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported TeX table-cell inventory schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    for key, code in (
        ("citation_semantic_mapping_ready", "citation_semantic_overclaim"),
        ("table_result_reproduction_ready", "table_reproduction_overclaim"),
        ("whole_paper_proposition_exhaustiveness_ready", "proposition_exhaustiveness_overclaim"),
        ("alphaevolve_parity_claim_ready", "parity_overclaim"),
    ):
        if data.get(key) is not False:
            issues.append(_issue(code, f"{key} must remain false for table-cell disposition evidence"))
    if data.get("new_claim_count") != 0:
        issues.append(_issue("new_claim_overclaim", "table-cell disposition must add zero bounded claims"))
    for key in (
        "source_artifact",
        "source_errors",
        "parse_errors",
        "source_closure",
        "table_count",
        "tabular_block_count",
        "row_count",
        "data_row_count",
        "header_row_count",
        "cell_count",
        "bounded_claim_component_cell_count",
        "source_context_only_cell_count",
        "structural_header_cell_count",
        "row_claim_ref_count",
        "cell_claim_ref_count",
        "unique_mapped_claim_count",
        "unique_mapped_claim_ids",
        "citation_occurrence_count",
        "citation_key_link_count",
        "unmapped_row_count",
        "unmapped_cell_count",
        "unresolved_reference_count",
        "table_breakdown",
        "tabular_block_records",
        "row_records",
        "cell_records",
        "active_todo_refs",
        "todo_ownership_ready",
        "inventory_scope",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from the retained TeX table-cell inventory"))
    for key in ("row_cell_inventory_ready", "table_cell_semantic_disposition_ready"):
        if data.get(key) is not expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} does not match source, parser, reference, and TODO checks"))
    if not expected["source_artifact"]["identity_ok"]:
        issues.append(_issue("source_archive_identity_mismatch", "retained AlphaEvolve TeX archive identity does not match the pinned source"))
    if expected["source_errors"]:
        issues.append(_issue("source_inventory_incomplete", "TeX table-cell inventory inputs are incomplete"))
    if expected["parse_errors"]:
        issues.append(_issue("table_cell_parse_incomplete", "one or more retained table rows or cells lack a stable disposition"))
    if expected["unresolved_reference_count"]:
        issues.append(_issue("unresolved_table_cell_reference", "one or more claim or named-span references are unresolved"))
    if not expected["todo_ownership_ready"]:
        issues.append(_issue("unowned_remaining_semantic_gap", "remaining proposition and reproduction gaps require active TODO ownership"))
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "all 83 rows and 240 cells" not in claim_boundary
        or "All 78 data rows" not in claim_boundary
        or "adds zero claims" not in claim_boundary
        or "does not establish citation sufficiency" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate table-cell disposition from citation, reproduction, and parity claims"))
    return AlphaEvolveTexTableCellInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        table_count=data.get("table_count") if isinstance(data.get("table_count"), int) else 0,
        tabular_block_count=data.get("tabular_block_count") if isinstance(data.get("tabular_block_count"), int) else 0,
        row_count=data.get("row_count") if isinstance(data.get("row_count"), int) else 0,
        cell_count=data.get("cell_count") if isinstance(data.get("cell_count"), int) else 0,
        unmapped_row_count=data.get("unmapped_row_count") if isinstance(data.get("unmapped_row_count"), int) else 0,
        unmapped_cell_count=data.get("unmapped_cell_count") if isinstance(data.get("unmapped_cell_count"), int) else 0,
        unresolved_reference_count=data.get("unresolved_reference_count") if isinstance(data.get("unresolved_reference_count"), int) else 0,
        issues=issues,
    )


def render_alphaevolve_tex_table_cell_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_tex_table_cell_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve TeX table-cell inventory boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| table_count | {validation.table_count} |",
        f"| tabular_block_count | {validation.tabular_block_count} |",
        f"| row_count | {validation.row_count} |",
        f"| cell_count | {validation.cell_count} |",
        f"| unmapped_row_count | {validation.unmapped_row_count} |",
        f"| unmapped_cell_count | {validation.unmapped_cell_count} |",
        f"| unresolved_reference_count | {validation.unresolved_reference_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _parse_tabular_blocks(
    tex_texts: dict[str, str],
    closure: list[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    blocks: list[dict[str, Any]] = []
    errors: list[str] = []
    for file_index, source_file in enumerate(closure):
        text = _strip_tex_comments(tex_texts.get(source_file, ""))
        headings = _section_headings(text)
        ordinal = 0
        for match in _TABULAR_BEGIN_RE.finditer(text):
            ordinal += 1
            position = _skip_whitespace(text, match.end())
            column_spec, body_start = _consume_group(text, position, "{", "}")
            if column_spec is None:
                errors.append(f"malformed_tabular_columns:{source_file}:{_line_number(text, match.start())}")
                continue
            end_match = re.search(r"\\end\s*\{tabular\}", text[body_start:])
            if end_match is None:
                errors.append(f"unterminated_tabular:{source_file}:{_line_number(text, match.start())}")
                continue
            body_end = body_start + end_match.start()
            command_end = body_start + end_match.end()
            row_records, row_errors = _parse_rows(
                text,
                body_start,
                body_end,
                source_file,
                file_index,
                ordinal,
                headings,
            )
            errors.extend(row_errors)
            blocks.append(
                {
                    "_file_index": file_index,
                    "_offset": match.start(),
                    "lookup_key": (source_file, ordinal),
                    "source_file": source_file,
                    "source_line": _line_number(text, match.start()),
                    "source_column": _column_number(text, match.start()),
                    "section_path": _section_path_at(headings, match.start()),
                    "column_spec": column_spec,
                    "command_sha256": hashlib.sha256(
                        text[match.start() : command_end].encode("utf-8")
                    ).hexdigest(),
                    "row_records": row_records,
                }
            )
    blocks.sort(key=lambda row: (row["_file_index"], row["_offset"]))
    for block in blocks:
        block.pop("_file_index")
        block.pop("_offset")
    return blocks, errors


def _parse_rows(
    text: str,
    body_start: int,
    body_end: int,
    source_file: str,
    file_index: int,
    tabular_ordinal: int,
    headings: list[tuple[int, int, str]],
) -> tuple[list[dict[str, Any]], list[str]]:
    body = text[body_start:body_end]
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for raw_start, raw_end, raw_text in _split_top_level(body, "\\\\"):
        sanitized = _TABLE_RULE_RE.sub(
            lambda match: " " * len(match.group(0)), raw_text
        )
        left_trim = len(sanitized) - len(sanitized.lstrip())
        right = len(sanitized.rstrip())
        if left_trim >= right:
            continue
        row_start = body_start + raw_start + left_trim
        row_end = body_start + raw_start + right
        row_text = text[row_start:row_end]
        cells = []
        for cell_start, cell_end, cell_text in _split_top_level(
            sanitized[left_trim:right], "&"
        ):
            cell_left_trim = len(cell_text) - len(cell_text.lstrip())
            cell_right = len(cell_text.rstrip())
            if cell_left_trim >= cell_right:
                continue
            absolute_start = row_start + cell_start + cell_left_trim
            absolute_end = row_start + cell_start + cell_right
            raw_cell_text = text[absolute_start:absolute_end]
            citation_keys = _citation_keys(raw_cell_text)
            cells.append(
                {
                    "source_file": source_file,
                    "source_line": _line_number(text, absolute_start),
                    "source_column": _column_number(text, absolute_start),
                    "section_path": _section_path_at(headings, absolute_start),
                    "raw_text": raw_cell_text,
                    "normalized_text": _normalize_whitespace(raw_cell_text),
                    "text_sha256": hashlib.sha256(
                        raw_cell_text.encode("utf-8")
                    ).hexdigest(),
                    "citation_occurrence_count": len(
                        _CITATION_RE.findall(raw_cell_text)
                    ),
                    "citation_keys": citation_keys,
                }
            )
        if not cells:
            errors.append(
                f"empty_tabular_row:{source_file}:{_line_number(text, row_start)}"
            )
            continue
        rows.append(
            {
                "_file_index": file_index,
                "_offset": row_start,
                "source_file": source_file,
                "source_line": _line_number(text, row_start),
                "source_column": _column_number(text, row_start),
                "section_path": _section_path_at(headings, row_start),
                "tabular_ordinal": tabular_ordinal,
                "raw_text": row_text,
                "normalized_text": _normalize_whitespace(row_text),
                "text_sha256": hashlib.sha256(row_text.encode("utf-8")).hexdigest(),
                "cells": cells,
            }
        )
    return rows, errors


def _disposition_records(
    parsed_blocks: list[dict[str, Any]],
    claim_ids: dict[str, set[str]],
    named_span_ids: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    blocks: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    cells: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_specs: set[tuple[str, int]] = set()
    table_data_indices: Counter[str] = Counter()
    table_header_indices: Counter[str] = Counter()
    for parsed_block in parsed_blocks:
        lookup_key = parsed_block["lookup_key"]
        spec = _TABULAR_SPECS.get(lookup_key)
        if spec is None:
            errors.append(f"unmapped_tabular_block:{lookup_key[0]}:{lookup_key[1]}")
            continue
        seen_specs.add(lookup_key)
        table_id = spec["table_id"]
        block_id = f"{table_id}_tabular_{sum(1 for block in blocks if block['table_id'] == table_id) + 1}"
        expected_columns = spec["expected_column_count"]
        parsed_rows = parsed_block["row_records"]
        if len(parsed_rows) != spec["expected_data_row_count"] + 1:
            errors.append(f"unexpected_row_count:{block_id}:{len(parsed_rows)}")
        block = dict(parsed_block)
        block.pop("lookup_key")
        block.pop("row_records")
        block.update(
            {
                "tabular_block_id": block_id,
                "table_id": table_id,
                "table_label": spec["table_label"],
                "source_page": spec["source_page"],
                "expected_column_count": expected_columns,
                "row_count": len(parsed_rows),
            }
        )
        blocks.append(block)
        for block_row_index, parsed_row in enumerate(parsed_rows):
            if len(parsed_row["cells"]) != expected_columns:
                errors.append(
                    f"unexpected_cell_count:{block_id}:{block_row_index}:{len(parsed_row['cells'])}"
                )
            is_header = block_row_index == 0
            if is_header:
                table_header_indices[table_id] += 1
                table_row_id = f"{table_id}_header_{table_header_indices[table_id]:02d}"
                claim_id = None
                row_disposition = "structural_header_row"
            else:
                table_data_indices[table_id] += 1
                table_row_id = f"{table_id}_data_{table_data_indices[table_id]:03d}"
                claim_id, mapping_error = _row_claim_id(
                    table_id,
                    table_data_indices[table_id],
                    parsed_row["cells"],
                )
                if mapping_error:
                    errors.append(f"{mapping_error}:{table_row_id}")
                row_disposition = "bounded_claim_row" if claim_id else "unmapped"
            row_claim_refs = _claim_ref_records(table_id, claim_id, claim_ids)
            row_named_span_refs = (
                [_named_span_ref(table_id, named_span_ids)] if is_header else []
            )
            row = dict(parsed_row)
            parsed_cells = row.pop("cells")
            row.pop("_file_index")
            row.pop("_offset")
            row.update(
                {
                    "table_row_id": table_row_id,
                    "tabular_block_id": block_id,
                    "table_id": table_id,
                    "table_label": spec["table_label"],
                    "source_page": spec["source_page"],
                    "row_kind": "header" if is_header else "data",
                    "disposition": row_disposition,
                    "claim_refs": row_claim_refs,
                    "named_span_refs": row_named_span_refs,
                    "cell_count": len(parsed_cells),
                }
            )
            rows.append(row)
            for column_index, parsed_cell in enumerate(parsed_cells):
                cell = dict(parsed_cell)
                if is_header:
                    semantic_role = spec["header_roles"][column_index]
                    disposition = "structural_header_cell"
                    cell_claim_refs: list[dict[str, Any]] = []
                    cell_named_span_refs = [
                        _named_span_ref(table_id, named_span_ids)
                    ]
                elif table_id == "table_1" and column_index == 0:
                    semantic_role = "funsearch_baseline_context"
                    disposition = "source_context_only_baseline_cell"
                    cell_claim_refs = []
                    cell_named_span_refs = []
                else:
                    semantic_role = _data_cell_role(table_id, column_index)
                    disposition = "bounded_claim_component" if claim_id else "unmapped"
                    cell_claim_refs = _claim_ref_records(
                        table_id, claim_id, claim_ids
                    )
                    cell_named_span_refs = []
                cell.update(
                    {
                        "table_cell_id": f"{table_row_id}_cell_{column_index + 1:02d}",
                        "table_row_id": table_row_id,
                        "tabular_block_id": block_id,
                        "table_id": table_id,
                        "table_label": spec["table_label"],
                        "source_page": spec["source_page"],
                        "column_index": column_index,
                        "semantic_role": semantic_role,
                        "disposition": disposition,
                        "claim_refs": cell_claim_refs,
                        "named_span_refs": cell_named_span_refs,
                        "citation_semantic_status": (
                            "unclassified" if cell["citation_occurrence_count"] else "not_applicable"
                        ),
                    }
                )
                cells.append(cell)
    for lookup_key in _TABULAR_SPECS:
        if lookup_key not in seen_specs:
            errors.append(f"missing_tabular_block:{lookup_key[0]}:{lookup_key[1]}")
    return blocks, rows, cells, errors


def _row_claim_id(
    table_id: str,
    data_index: int,
    cells: list[dict[str, Any]],
) -> tuple[str | None, str | None]:
    if table_id == "table_1":
        if not 1 <= data_index <= len(_TABLE_1_ROWS):
            return None, "unexpected_table_1_data_index"
        expected_anchor, claim_id = _TABLE_1_ROWS[data_index - 1]
        if expected_anchor not in cells[0]["normalized_text"]:
            return None, "table_1_row_anchor_mismatch"
        return claim_id, None
    target = _matrix_target(cells[0]["normalized_text"])
    if target is None:
        return None, f"missing_{table_id}_matrix_target"
    if table_id == "table_2":
        claim_id = _TABLE_2_CLAIM_IDS.get(target)
        return (
            (claim_id, None)
            if claim_id
            else (None, "unexpected_table_2_matrix_target")
        )
    if table_id == "table_3":
        return f"table3_mm_{target[0]}x{target[1]}x{target[2]}_rank_result", None
    return None, "unknown_table_id"


def _data_cell_role(table_id: str, column_index: int) -> str:
    if table_id == "table_1":
        return "alphaevolve_capability_component"
    return (
        "matrix_target_component",
        "best_known_baseline_component",
        "alphaevolve_result_component",
    )[column_index]


def _claim_ref_records(
    table_id: str,
    claim_id: str | None,
    claim_ids: dict[str, set[str]],
) -> list[dict[str, Any]]:
    if claim_id is None:
        return []
    path = _CLAIM_INVENTORY_PATHS[table_id]
    return [
        {
            "inventory_path": path,
            "claim_id": claim_id,
            "resolved": claim_id in claim_ids.get(path, set()),
        }
    ]


def _named_span_ref(table_id: str, named_span_ids: set[str]) -> dict[str, Any]:
    return {
        "inventory_path": _SOURCE_INVENTORY_PATH,
        "span_id": table_id,
        "resolved": table_id in named_span_ids,
    }


def _reference_ids(
    root: Path,
) -> tuple[dict[str, set[str]], set[str], list[str]]:
    claim_ids: dict[str, set[str]] = {}
    errors: list[str] = []
    for path in _CLAIM_INVENTORY_PATHS.values():
        data, error = _read_json_object(root / path)
        if error:
            errors.append(f"claim_inventory_{error}:{path}")
            claim_ids[path] = set()
            continue
        ids: set[str] = set()
        for collection in ("claim_records", "requirement_records"):
            records = data.get(collection)
            if not isinstance(records, list):
                continue
            for record in records:
                if not isinstance(record, dict):
                    continue
                value = record.get("claim_id", record.get("requirement_id"))
                if isinstance(value, str):
                    ids.add(value)
        claim_ids[path] = ids
    source_data, source_error = _read_json_object(root / _SOURCE_INVENTORY_PATH)
    if source_error:
        errors.append(f"source_inventory_{source_error}:{_SOURCE_INVENTORY_PATH}")
        named_span_ids: set[str] = set()
    else:
        records = source_data.get("span_records")
        named_span_ids = (
            {
                record["span_id"]
                for record in records
                if isinstance(record, dict)
                and isinstance(record.get("span_id"), str)
            }
            if isinstance(records, list)
            else set()
        )
    return claim_ids, named_span_ids, errors


def _table_breakdown(
    blocks: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    cells: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    return {
        table_id: {
            "tabular_block_count": sum(
                block["table_id"] == table_id for block in blocks
            ),
            "row_count": sum(row["table_id"] == table_id for row in rows),
            "data_row_count": sum(
                row["table_id"] == table_id and row["row_kind"] == "data"
                for row in rows
            ),
            "header_row_count": sum(
                row["table_id"] == table_id and row["row_kind"] == "header"
                for row in rows
            ),
            "cell_count": sum(cell["table_id"] == table_id for cell in cells),
        }
        for table_id in ("table_1", "table_2", "table_3")
    }


def _split_top_level(
    text: str,
    delimiter: str,
) -> list[tuple[int, int, str]]:
    segments: list[tuple[int, int, str]] = []
    start = 0
    depth = 0
    index = 0
    while index < len(text):
        character = text[index]
        if character == "\\":
            if (
                delimiter == "\\\\"
                and index + 1 < len(text)
                and text[index + 1] == "\\"
                and depth == 0
            ):
                segments.append((start, index, text[start:index]))
                index += 2
                start = index
                continue
            index += 2
            continue
        if character == "{":
            depth += 1
        elif character == "}" and depth:
            depth -= 1
        elif delimiter == "&" and character == "&" and depth == 0:
            segments.append((start, index, text[start:index]))
            index += 1
            start = index
            continue
        index += 1
    segments.append((start, len(text), text[start:]))
    return segments


def _matrix_target(value: str) -> tuple[int, int, int] | None:
    match = _MATRIX_TARGET_RE.search(value)
    return tuple(map(int, match.groups())) if match else None


def _citation_keys(value: str) -> list[str]:
    return [
        key.strip()
        for argument in _CITATION_RE.findall(value)
        for key in argument.split(",")
        if key.strip()
    ]


def _read_json_object(path: Path) -> tuple[dict[str, Any], str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {}, f"read_error_{type(exc).__name__}"
    if not isinstance(data, dict):
        return {}, "invalid_shape"
    return data, None


def _todo_ref(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = root / spec["path"]
    try:
        text = path.read_text(encoding="utf-8")
        exists = path.is_file()
    except (OSError, UnicodeDecodeError):
        text = ""
        exists = False
    return {
        **spec,
        "exists": exists,
        "required_phrase_present": spec["required_phrase"] in text,
    }


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _column_number(text: str, offset: int) -> int:
    return offset - text.rfind("\n", 0, offset)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[
    dict[str, Any] | None,
    list[AlphaEvolveTexTableCellInventoryBoundaryIssue],
]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")]
    else:
        try:
            data = json.loads(Path(boundary).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")]
    if isinstance(data, dict):
        return data, []
    return None, [_issue("invalid_shape", "TeX table-cell inventory must be a JSON object")]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveTexTableCellInventoryBoundaryIssue:
    return AlphaEvolveTexTableCellInventoryBoundaryIssue(code, message)
