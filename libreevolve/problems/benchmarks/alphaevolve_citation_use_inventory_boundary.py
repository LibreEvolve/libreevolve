from __future__ import annotations

import hashlib
import json
import re
import tarfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.alphaevolve_tex_archive_retention_boundary import (
    EXPECTED_ARCHIVE_ARTIFACT_PATH,
    EXPECTED_RESPONSE_BYTES,
    EXPECTED_RESPONSE_SHA256,
)
from libreevolve.problems.benchmarks.paper_bibliography import (
    EXPECTED_REFERENCE_COUNT,
    EXPECTED_REFERENCES_BIBLIOGRAPHY_FILE,
    EXPECTED_SOURCE_PAPER_ID,
)


ALPHAEVOLVE_CITATION_USE_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_citation_use_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "tex_citation_use_inventory_complete_without_semantic_claim_mapping"
)
EXPECTED_ENTRYPOINT = "main.tex"
EXPECTED_TEX_CLOSURE_FILES = (
    "main.tex",
    "preamble.tex",
    "introduction.tex",
    "methods.tex",
    "grounding_example.tex",
    "results.tex",
    "discovered_program.tex",
    "ablations.tex",
    "related_work.tex",
    "discussion.tex",
    "acknowledgement.tex",
    "authors.tex",
    "appendix.tex",
    "discovered_program_appendix.tex",
)
EXPECTED_CITATION_OCCURRENCE_COUNT = 195
EXPECTED_CITATION_KEY_LINK_COUNT = 240
EXPECTED_UNIQUE_CITED_KEY_COUNT = 120
EXPECTED_BIBTEX_ENTRY_COUNT = 172
EXPECTED_UNUSED_BIBTEX_ENTRY_COUNT = 52
EXPECTED_CITATION_COMMAND_COUNTS = {
    "authoryearcite": 1,
    "authoryearcitet": 1,
    "cite": 49,
    "citep": 134,
    "citet": 10,
}
EXPECTED_CITATION_SOURCE_FILE_COUNTS = {
    "appendix.tex": 81,
    "discussion.tex": 2,
    "introduction.tex": 16,
    "main.tex": 1,
    "methods.tex": 4,
    "related_work.tex": 54,
    "results.tex": 37,
}
_CITATION_COMMAND_ARITIES = {
    "cite": 1,
    "citeauthor": 1,
    "citep": 1,
    "citet": 1,
    "citeyear": 1,
    "authoryearcite": 1,
    "authoryearcitet": 1,
    "authoryearcitetwo": 2,
}
_TODO_SPECS = (
    {
        "todo_id": "whole_paper_citation_semantics_code",
        "path": "docs/todo/code.md",
        "required_phrase": (
            "Add exhaustive implementation-evidence mapping for AlphaEvolve"
        ),
    },
    {
        "todo_id": "whole_paper_citation_semantics_paper",
        "path": "docs/todo/papers.md",
        "required_phrase": (
            "Extend the bounded AlphaEvolve claim inventories to the whole paper."
        ),
    },
)
_COMMAND_RE = re.compile(r"\\([A-Za-z@]+)\*?")
_INPUT_RE = re.compile(r"\\input\b\s*\{")
_SECTION_COMMAND_LEVELS = {
    "section": 1,
    "subsection": 2,
    "subsubsection": 3,
}


@dataclass(frozen=True)
class AlphaEvolveCitationUseInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveCitationUseInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    citation_occurrence_count: int
    citation_key_link_count: int
    unique_cited_key_count: int
    unresolved_citation_key_count: int
    semantic_gap_count: int
    issues: list[AlphaEvolveCitationUseInventoryBoundaryIssue]


def alphaevolve_citation_use_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Inventory every logical citation use in the retained AlphaEvolve TeX."""

    root_path = Path(root)
    source_artifact, archive_texts, source_errors = _read_source_archive(root_path)
    tex_texts = {
        name: text
        for name, text in archive_texts.items()
        if name.casefold().endswith(".tex")
    }
    closure = _tex_dependency_closure(tex_texts, EXPECTED_ENTRYPOINT)
    citation_records, parse_errors, unknown_commands = _citation_records(
        tex_texts,
        closure,
        archive_texts.get("main.bbl", ""),
    )
    bibtex_keys = _bibtex_entry_keys(archive_texts.get("literature.bib", ""))
    compiled_keys = _compiled_bibliography_keys(
        archive_texts.get("main.bbl", "")
    )
    reference_ids, reference_manifest_error = _reference_manifest_ids(root_path)
    source_errors = [*source_errors]
    if reference_manifest_error:
        source_errors.append(reference_manifest_error)

    compiled_reference_records = [
        {
            "reference_id": str(index),
            "citation_key": key,
            "bibtex_entry_present": key in set(bibtex_keys),
            "pdf_reference_manifest_present": str(index) in reference_ids,
        }
        for index, key in enumerate(compiled_keys, start=1)
    ]
    compiled_reference_by_key = {
        row["citation_key"]: row for row in compiled_reference_records
    }
    for record in citation_records:
        links = []
        for key in record["citation_keys"]:
            compiled = compiled_reference_by_key.get(key)
            links.append(
                {
                    "citation_key": key,
                    "reference_id": (
                        compiled["reference_id"] if compiled is not None else None
                    ),
                    "bibtex_entry_present": key in set(bibtex_keys),
                    "compiled_bibliography_present": compiled is not None,
                    "pdf_reference_manifest_present": bool(
                        compiled
                        and compiled["reference_id"] in reference_ids
                    ),
                }
            )
        record["reference_links"] = links
        record["all_keys_resolved"] = bool(links) and all(
            link["bibtex_entry_present"]
            and link["compiled_bibliography_present"]
            and link["pdf_reference_manifest_present"]
            for link in links
        )

    cited_keys = [
        key for record in citation_records for key in record["citation_keys"]
    ]
    command_counts = Counter(record["command"] for record in citation_records)
    source_file_counts = Counter(
        record["source_file"] for record in citation_records
    )
    unresolved_keys = sorted(
        {
            link["citation_key"]
            for record in citation_records
            for link in record["reference_links"]
            if not (
                link["bibtex_entry_present"]
                and link["compiled_bibliography_present"]
                and link["pdf_reference_manifest_present"]
            )
        }
    )
    uncited_compiled_keys = sorted(set(compiled_keys) - set(cited_keys))
    unused_bibtex_keys = sorted(set(bibtex_keys) - set(cited_keys))
    missing_compiled_bibtex_keys = sorted(set(compiled_keys) - set(bibtex_keys))
    todo_refs = [_todo_ref(root_path, spec) for spec in _TODO_SPECS]
    todo_ownership_ready = all(
        ref["exists"] and ref["required_phrase_present"] for ref in todo_refs
    )
    semantic_gap_count = len(citation_records)
    todo_owned_semantic_gap_count = (
        semantic_gap_count if todo_ownership_ready else 0
    )
    source_closure_records = [
        {
            "path": name,
            "sha256": hashlib.sha256(
                archive_texts.get(name, "").encode("utf-8")
            ).hexdigest(),
            "citation_occurrence_count": source_file_counts[name],
        }
        for name in closure
    ]
    inventory_ready = (
        source_artifact["identity_ok"]
        and not source_errors
        and not parse_errors
        and not unknown_commands
        and tuple(closure) == EXPECTED_TEX_CLOSURE_FILES
        and len(citation_records) == EXPECTED_CITATION_OCCURRENCE_COUNT
        and len(cited_keys) == EXPECTED_CITATION_KEY_LINK_COUNT
        and len(set(cited_keys)) == EXPECTED_UNIQUE_CITED_KEY_COUNT
        and dict(sorted(command_counts.items()))
        == EXPECTED_CITATION_COMMAND_COUNTS
        and dict(sorted(source_file_counts.items()))
        == EXPECTED_CITATION_SOURCE_FILE_COUNTS
        and len(bibtex_keys) == EXPECTED_BIBTEX_ENTRY_COUNT
        and len(compiled_keys) == EXPECTED_REFERENCE_COUNT
        and len(reference_ids) == EXPECTED_REFERENCE_COUNT
        and len(unused_bibtex_keys) == EXPECTED_UNUSED_BIBTEX_ENTRY_COUNT
        and not unresolved_keys
        and not uncited_compiled_keys
        and not missing_compiled_bibtex_keys
        and len(set(bibtex_keys)) == len(bibtex_keys)
        and len(set(compiled_keys)) == len(compiled_keys)
        and todo_owned_semantic_gap_count == semantic_gap_count
    )
    return {
        "schema": ALPHAEVOLVE_CITATION_USE_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "citation_linkage_inventory_ready": inventory_ready,
        "semantic_claim_mapping_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_errors": source_errors,
        "parse_errors": parse_errors,
        "unknown_citation_like_commands": unknown_commands,
        "source_closure": {
            "entrypoint": EXPECTED_ENTRYPOINT,
            "file_count": len(closure),
            "files": source_closure_records,
        },
        "bibliography_sources": {
            "bibtex_member": "literature.bib",
            "bibtex_entry_count": len(bibtex_keys),
            "compiled_bibliography_member": "main.bbl",
            "compiled_bibliography_entry_count": len(compiled_keys),
            "pdf_reference_manifest": EXPECTED_REFERENCES_BIBLIOGRAPHY_FILE,
            "pdf_reference_manifest_entry_count": len(reference_ids),
        },
        "citation_occurrence_count": len(citation_records),
        "citation_key_link_count": len(cited_keys),
        "unique_cited_key_count": len(set(cited_keys)),
        "citation_command_counts": dict(sorted(command_counts.items())),
        "citation_source_file_counts": dict(sorted(source_file_counts.items())),
        "unresolved_citation_keys": unresolved_keys,
        "uncited_compiled_bibliography_keys": uncited_compiled_keys,
        "missing_compiled_bibtex_keys": missing_compiled_bibtex_keys,
        "unused_bibtex_entry_count": len(unused_bibtex_keys),
        "unused_bibtex_keys": unused_bibtex_keys,
        "compiled_reference_records": compiled_reference_records,
        "citation_use_records": citation_records,
        "semantic_gap_count": semantic_gap_count,
        "todo_owned_semantic_gap_count": todo_owned_semantic_gap_count,
        "active_todo_refs": todo_refs,
        "inventory_scope": {
            "included": [
                "recursive TeX input closure rooted at main.tex",
                "logical citation commands outside preamble macro definitions",
                "source file, line, column, section path, command text, optional notes, and citation keys for every use",
                "citation-key linkage through main.bbl ordinal order to all 120 papers/references.json rows",
                "all compiled, cited, unresolved, and unused literature.bib keys",
            ],
            "excluded": [
                "semantic classification of what proposition each citation supports",
                "classification of citation uses as implementation requirements, background, limitations, or result provenance",
                "independent recompilation of the TeX archive or comparison of rendered bibliography text",
                "verification of cited external sources or their claims",
                "equation, footnote, caption, paragraph, and sentence-level claim exhaustiveness",
                "AlphaEvolve result reproduction or system parity",
            ],
        },
        "claim_boundary": (
            "This sidecar certifies lexical citation-use and bibliography-key "
            "linkage for 195 logical citation occurrences, 240 citation-key "
            "links, all 120 compiled references, and 52 unused BibTeX entries "
            "in the retained AlphaEvolve TeX archive. It does not classify "
            "citation semantics, prove claim-to-source sufficiency, verify "
            "external references, inventory equations or footnotes, reproduce "
            "published results, or establish AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_citation_use_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveCitationUseInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_citation_use_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveCitationUseInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_citation_use_inventory_boundary_record(root)
    issues: list[AlphaEvolveCitationUseInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_CITATION_USE_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported citation-use inventory schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("semantic_claim_mapping_ready") is not False:
        issues.append(_issue("semantic_mapping_overclaim", "citation linkage must not claim semantic claim mapping"))
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(_issue("parity_overclaim", "citation linkage must not claim AlphaEvolve parity"))
    for key in (
        "source_artifact",
        "source_errors",
        "parse_errors",
        "unknown_citation_like_commands",
        "source_closure",
        "bibliography_sources",
        "citation_occurrence_count",
        "citation_key_link_count",
        "unique_cited_key_count",
        "citation_command_counts",
        "citation_source_file_counts",
        "unresolved_citation_keys",
        "uncited_compiled_bibliography_keys",
        "missing_compiled_bibtex_keys",
        "unused_bibtex_entry_count",
        "unused_bibtex_keys",
        "compiled_reference_records",
        "citation_use_records",
        "semantic_gap_count",
        "todo_owned_semantic_gap_count",
        "active_todo_refs",
        "inventory_scope",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from the retained TeX citation inventory"))
    if data.get("citation_linkage_inventory_ready") is not expected[
        "citation_linkage_inventory_ready"
    ]:
        issues.append(_issue("invalid_citation_linkage_inventory_ready", "citation linkage readiness does not match source, parser, bibliography, and TODO checks"))
    if not expected["source_artifact"]["identity_ok"]:
        issues.append(_issue("source_archive_identity_mismatch", "retained AlphaEvolve TeX archive identity does not match the pinned source"))
    if expected["source_errors"]:
        issues.append(_issue("source_inventory_incomplete", "citation inventory source inputs are incomplete"))
    if expected["parse_errors"] or expected["unknown_citation_like_commands"]:
        issues.append(_issue("citation_parse_incomplete", "one or more citation-like commands were not parsed"))
    if expected["unresolved_citation_keys"]:
        issues.append(_issue("unresolved_citation_key", "one or more citation keys do not resolve through BibTeX, BBL, and PDF bibliography records"))
    if expected["todo_owned_semantic_gap_count"] != expected["semantic_gap_count"]:
        issues.append(_issue("unowned_semantic_gap", "citation semantic-classification gaps require active code and paper TODO ownership"))
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "195 logical citation occurrences" not in claim_boundary
        or "240 citation-key links" not in claim_boundary
        or "52 unused BibTeX entries" not in claim_boundary
        or "does not classify citation semantics" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate lexical linkage from semantic mapping and parity"))
    return AlphaEvolveCitationUseInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=(
            data.get("boundary_status")
            if isinstance(data.get("boundary_status"), str)
            else None
        ),
        citation_occurrence_count=(
            data.get("citation_occurrence_count")
            if isinstance(data.get("citation_occurrence_count"), int)
            else 0
        ),
        citation_key_link_count=(
            data.get("citation_key_link_count")
            if isinstance(data.get("citation_key_link_count"), int)
            else 0
        ),
        unique_cited_key_count=(
            data.get("unique_cited_key_count")
            if isinstance(data.get("unique_cited_key_count"), int)
            else 0
        ),
        unresolved_citation_key_count=len(expected["unresolved_citation_keys"]),
        semantic_gap_count=(
            data.get("semantic_gap_count")
            if isinstance(data.get("semantic_gap_count"), int)
            else 0
        ),
        issues=issues,
    )


def render_alphaevolve_citation_use_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_citation_use_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve citation-use inventory boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| citation_occurrence_count | {validation.citation_occurrence_count} |",
        f"| citation_key_link_count | {validation.citation_key_link_count} |",
        f"| unique_cited_key_count | {validation.unique_cited_key_count} |",
        f"| unresolved_citation_key_count | {validation.unresolved_citation_key_count} |",
        f"| semantic_gap_count | {validation.semantic_gap_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _read_source_archive(
    root: Path,
) -> tuple[dict[str, Any], dict[str, str], list[str]]:
    archive_path = root / EXPECTED_ARCHIVE_ARTIFACT_PATH
    digest_builder = hashlib.sha256()
    actual_bytes = 0
    try:
        with archive_path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                actual_bytes += len(chunk)
                digest_builder.update(chunk)
    except OSError as exc:
        return (
            {
                "path": EXPECTED_ARCHIVE_ARTIFACT_PATH,
                "exists": False,
                "expected_bytes": EXPECTED_RESPONSE_BYTES,
                "actual_bytes": None,
                "expected_sha256": EXPECTED_RESPONSE_SHA256,
                "actual_sha256": None,
                "identity_ok": False,
            },
            {},
            [f"archive_read_error:{type(exc).__name__}"],
        )
    digest = digest_builder.hexdigest()
    identity_ok = (
        actual_bytes == EXPECTED_RESPONSE_BYTES
        and digest == EXPECTED_RESPONSE_SHA256
    )
    texts: dict[str, str] = {}
    errors: list[str] = []
    try:
        with tarfile.open(archive_path, mode="r:gz") as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                name = member.name.replace("\\", "/").removeprefix("./")
                if not (
                    name.casefold().endswith(".tex")
                    or name in {"main.bbl", "literature.bib"}
                ):
                    continue
                extracted = archive.extractfile(member)
                if extracted is None:
                    errors.append(f"archive_member_read_error:{name}")
                    continue
                try:
                    texts[name] = extracted.read().decode("utf-8")
                except UnicodeDecodeError:
                    errors.append(f"archive_member_decode_error:{name}")
    except (OSError, tarfile.TarError) as exc:
        errors.append(f"archive_parse_error:{type(exc).__name__}")
    for required in (EXPECTED_ENTRYPOINT, "main.bbl", "literature.bib"):
        if required not in texts:
            errors.append(f"missing_archive_member:{required}")
    return (
        {
            "path": EXPECTED_ARCHIVE_ARTIFACT_PATH,
            "exists": True,
            "expected_bytes": EXPECTED_RESPONSE_BYTES,
            "actual_bytes": actual_bytes,
            "expected_sha256": EXPECTED_RESPONSE_SHA256,
            "actual_sha256": digest,
            "identity_ok": identity_ok,
        },
        texts,
        sorted(set(errors)),
    )


def _tex_dependency_closure(
    tex_texts: dict[str, str],
    entrypoint: str,
) -> list[str]:
    closure: list[str] = []
    seen: set[str] = set()

    def visit(name: str) -> None:
        normalized = name.strip().replace("\\", "/")
        if not normalized.casefold().endswith(".tex"):
            normalized += ".tex"
        if normalized in seen or normalized not in tex_texts:
            return
        seen.add(normalized)
        closure.append(normalized)
        text = _strip_tex_comments(tex_texts[normalized])
        for match in _INPUT_RE.finditer(text):
            value, _ = _consume_group(text, match.end() - 1, "{", "}")
            if value:
                visit(value)

    visit(entrypoint)
    return closure


def _citation_records(
    tex_texts: dict[str, str],
    closure: list[str],
    bbl_text: str,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    compiled_keys = _compiled_bibliography_keys(bbl_text)
    records: list[dict[str, Any]] = []
    parse_errors: list[str] = []
    unknown_commands: set[str] = set()
    for source_file in closure:
        if source_file == "preamble.tex":
            continue
        source_text = _strip_tex_comments(tex_texts.get(source_file, ""))
        headings = _section_headings(source_text)
        for match in _COMMAND_RE.finditer(source_text):
            command = match.group(1)
            if "cite" in command.casefold() and command not in _CITATION_COMMAND_ARITIES:
                unknown_commands.add(command)
                continue
            arity = _CITATION_COMMAND_ARITIES.get(command)
            if arity is None:
                continue
            notes, arguments, end = _command_arguments(
                source_text, match.end(), arity
            )
            if len(arguments) != arity:
                parse_errors.append(
                    f"malformed_citation:{source_file}:{_line_number(source_text, match.start())}:{command}"
                )
                continue
            citation_keys = [
                key.strip()
                for argument in arguments
                for key in argument.split(",")
                if key.strip()
            ]
            if not citation_keys:
                parse_errors.append(
                    f"empty_citation:{source_file}:{_line_number(source_text, match.start())}:{command}"
                )
                continue
            start = match.start()
            line_start = source_text.rfind("\n", 0, start) + 1
            line_end = source_text.find("\n", start)
            if line_end < 0:
                line_end = len(source_text)
            context_start = max(0, start - 120)
            context_end = min(len(source_text), end + 120)
            section_path = _section_path_at(headings, start)
            if source_file == "main.tex" and not section_path:
                section_path = ["Abstract"]
            records.append(
                {
                    "citation_use_id": f"tex_citation_{len(records) + 1:04d}",
                    "source_file": source_file,
                    "source_line": _line_number(source_text, start),
                    "source_column": start - line_start + 1,
                    "section_path": section_path,
                    "command": command,
                    "command_text": source_text[start:end],
                    "optional_arguments": notes,
                    "citation_keys": citation_keys,
                    "context_excerpt": _normalize_whitespace(
                        source_text[context_start:context_end]
                    ),
                    "source_line_sha256": hashlib.sha256(
                        source_text[line_start:line_end].encode("utf-8")
                    ).hexdigest(),
                    "compiled_key_candidates": [
                        key for key in citation_keys if key in set(compiled_keys)
                    ],
                    "semantic_classification_status": "unclassified",
                    "implementation_relevance_status": "not_assessed",
                }
            )
    return records, sorted(parse_errors), sorted(unknown_commands)


def _section_headings(text: str) -> list[tuple[int, int, str]]:
    headings: list[tuple[int, int, str]] = []
    for match in _COMMAND_RE.finditer(text):
        command = match.group(1)
        level = _SECTION_COMMAND_LEVELS.get(command)
        if level is None:
            continue
        _, arguments, _ = _command_arguments(text, match.end(), 1)
        if arguments:
            headings.append(
                (match.start(), level, _normalize_whitespace(arguments[0]))
            )
    return headings


def _section_path_at(
    headings: list[tuple[int, int, str]],
    offset: int,
) -> list[str]:
    path_by_level: dict[int, str] = {}
    for position, level, title in headings:
        if position > offset:
            break
        path_by_level[level] = title
        for deeper in tuple(key for key in path_by_level if key > level):
            del path_by_level[deeper]
    return [path_by_level[level] for level in sorted(path_by_level)]


def _compiled_bibliography_keys(text: str) -> list[str]:
    sanitized = _strip_tex_comments(text)
    keys: list[str] = []
    for match in re.finditer(r"\\bibitem\b", sanitized):
        position = _skip_whitespace(sanitized, match.end())
        if position < len(sanitized) and sanitized[position] == "[":
            _, position = _consume_group(sanitized, position, "[", "]")
            position = _skip_whitespace(sanitized, position)
        key, _ = _consume_group(sanitized, position, "{", "}")
        if key is not None and key.strip():
            keys.append(key.strip())
    return keys


def _bibtex_entry_keys(text: str) -> list[str]:
    keys: list[str] = []
    entry_re = re.compile(r"@([A-Za-z]+)\s*([({])")
    for match in entry_re.finditer(text):
        entry_type = match.group(1).casefold()
        if entry_type in {"comment", "preamble", "string"}:
            continue
        position = _skip_whitespace(text, match.end())
        key_end = text.find(",", position)
        if key_end < 0:
            continue
        key = text[position:key_end].strip()
        if key and not any(character.isspace() for character in key):
            keys.append(key)
    return keys


def _reference_manifest_ids(root: Path) -> tuple[set[str], str | None]:
    path = root / EXPECTED_REFERENCES_BIBLIOGRAPHY_FILE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return set(), f"reference_manifest_read_error:{type(exc).__name__}"
    references = data.get("references") if isinstance(data, dict) else None
    if not isinstance(references, list):
        return set(), "reference_manifest_invalid_shape"
    ids = {
        row.get("reference_id")
        for row in references
        if isinstance(row, dict) and isinstance(row.get("reference_id"), str)
    }
    return ids, None


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


def _command_arguments(
    text: str,
    position: int,
    arity: int,
) -> tuple[list[str], list[str], int]:
    position = _skip_whitespace(text, position)
    notes: list[str] = []
    while position < len(text) and text[position] == "[":
        value, next_position = _consume_group(text, position, "[", "]")
        if value is None:
            break
        notes.append(value)
        position = _skip_whitespace(text, next_position)
    arguments: list[str] = []
    for _ in range(arity):
        value, next_position = _consume_group(text, position, "{", "}")
        if value is None:
            break
        arguments.append(value)
        position = _skip_whitespace(text, next_position)
    return notes, arguments, position


def _consume_group(
    text: str,
    position: int,
    opener: str,
    closer: str,
) -> tuple[str | None, int]:
    if position >= len(text) or text[position] != opener:
        return None, position
    depth = 1
    cursor = position + 1
    while cursor < len(text):
        character = text[cursor]
        if character == "\\":
            cursor += 2
            continue
        if character == opener:
            depth += 1
        elif character == closer:
            depth -= 1
            if depth == 0:
                return text[position + 1 : cursor], cursor + 1
        cursor += 1
    return None, position


def _strip_tex_comments(text: str) -> str:
    characters = list(text)
    index = 0
    while index < len(characters):
        if characters[index] != "%":
            index += 1
            continue
        slash_count = 0
        cursor = index - 1
        while cursor >= 0 and characters[cursor] == "\\":
            slash_count += 1
            cursor -= 1
        if slash_count % 2:
            index += 1
            continue
        cursor = index
        while cursor < len(characters) and characters[cursor] not in "\r\n":
            characters[cursor] = " "
            cursor += 1
        index = cursor
    return "".join(characters)


def _skip_whitespace(text: str, position: int) -> int:
    while position < len(text) and text[position].isspace():
        position += 1
    return position


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[
    dict[str, Any] | None,
    list[AlphaEvolveCitationUseInventoryBoundaryIssue],
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
    return None, [_issue("invalid_shape", "citation-use inventory must be a JSON object")]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveCitationUseInventoryBoundaryIssue:
    return AlphaEvolveCitationUseInventoryBoundaryIssue(code, message)
