from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import re

from libreevolve.core.diff import apply_diff, parse_diff_blocks, _strip_fences

EVOLVE_BLOCK_START = "# EVOLVE-BLOCK-START"
EVOLVE_BLOCK_END = "# EVOLVE-BLOCK-END"
_BLOCK_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]+$")

_BLOCK_SECTION_PATTERN = re.compile(
    r"<<<BLOCK[ \t]*(.*?)\n(.*?)\n>>>BLOCK", re.DOTALL
)
_FILE_SECTION_PATTERN = re.compile(
    r"<<<FILE[ \t]*(.*?)\n(.*?)>>>FILE", re.DOTALL
)


@dataclass
class CandidateWorkspace:
    """A candidate represented as a text file set.

    The `primary_file` keeps the existing single-string API meaningful: legacy
    validators and prompts still see the primary file as `code`.
    """

    files: dict[str, str] = field(default_factory=dict)
    primary_file: str = "main.py"

    def __post_init__(self) -> None:
        normalized_files: dict[str, str] = {}
        for raw_path, content in self.files.items():
            path = normalize_candidate_path(raw_path)
            if path in normalized_files:
                raise ValueError(
                    "Duplicate candidate path after normalization: "
                    f"{raw_path!r} -> {path!r}"
                )
            normalized_files[path] = content
        self.files = normalized_files
        self.primary_file = normalize_candidate_path(self.primary_file)
        if not self.files:
            self.files[self.primary_file] = ""
        if self.primary_file not in self.files:
            self.primary_file = sorted(self.files)[0]

    @classmethod
    def from_code(cls, code: str, path: str = "main.py") -> "CandidateWorkspace":
        path = normalize_candidate_path(path)
        return cls(files={path: code}, primary_file=path)

    @classmethod
    def from_dict(cls, data: dict) -> "CandidateWorkspace":
        return cls(
            files={str(k): str(v) for k, v in data.get("files", {}).items()},
            primary_file=str(data.get("primary_file", "main.py")),
        )

    @property
    def code(self) -> str:
        return self.files[self.primary_file]

    def to_dict(self) -> dict:
        return {"primary_file": self.primary_file, "files": dict(self.files)}

    def materialize(self, root: Path) -> Path:
        targets: dict[str, str] = {}
        for rel in self.files:
            target = safe_candidate_path(root, rel)
            key = os.path.normcase(str(target))
            if key in targets:
                raise ValueError(
                    "Candidate paths collide when materialized: "
                    f"{targets[key]!r} and {rel!r}"
                )
            targets[key] = rel
        for rel, content in self.files.items():
            target = safe_candidate_path(root, rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        return safe_candidate_path(root, self.primary_file)


def normalize_candidate_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip().lstrip("/")
    parts = [p for p in normalized.split("/") if p and p != "."]
    if not parts or any(p == ".." or ":" in p for p in parts):
        raise ValueError(f"Unsafe candidate path: {path!r}")
    return "/".join(parts)


def safe_candidate_path(root: Path, rel_path: str) -> Path:
    rel = normalize_candidate_path(rel_path)
    root_resolved = root.resolve()
    target = (root_resolved / rel).resolve()
    if root_resolved != target and root_resolved not in target.parents:
        raise ValueError(f"Candidate path escapes workspace: {rel_path!r}")
    return target


@dataclass(frozen=True)
class EvolveBlock:
    name: str
    start: int
    content_start: int
    content_end: int
    end: int
    content: str


def extract_evolve_blocks(code: str) -> list[EvolveBlock]:
    """Return marked evolvable regions while preserving surrounding skeleton."""
    return _parse_evolve_blocks(code)[0]


def validate_evolve_blocks(code: str) -> str | None:
    """Return an error code when EVOLVE-BLOCK markers are malformed."""
    return _parse_evolve_blocks(code)[1]


def has_evolve_blocks(code: str) -> bool:
    return bool(extract_evolve_blocks(code))


def apply_candidate_mutation(
    code: str, mutation_text: str, mutation_mode: str = "diff"
) -> tuple[str, str | None]:
    """Apply an LLM mutation response to a candidate program.

    `diff` mode applies SEARCH/REPLACE blocks. When EVOLVE-BLOCK markers are
    present, matches are restricted to marked regions so the skeleton is
    preserved.

    `full` mode replaces the whole candidate when no evolve blocks are present.
    With one evolve block, it replaces only that block's content. With multiple
    evolve blocks, the response must contain one or more named sections:

        <<<BLOCK block_0
        replacement code
        >>>BLOCK
    """
    marker_error = validate_evolve_blocks(code)
    if marker_error is not None:
        return code, f"malformed_evolve_blocks:{marker_error}"
    if mutation_mode == "diff":
        return _apply_diff_to_candidate(code, mutation_text)
    if mutation_mode == "full":
        return _apply_full_replacement(code, mutation_text)
    return code, "unknown_mutation_mode"


def apply_workspace_mutation(
    workspace: CandidateWorkspace, mutation_text: str, mutation_mode: str = "diff"
) -> tuple[CandidateWorkspace, str | None]:
    """Apply a mutation to one or more files in a workspace candidate.

    Without `<<<FILE path ... >>>FILE` sections, mutation applies to the primary
    file for backward compatibility. With file sections, each section is routed
    to that file; unknown files can be created by `full` mode. File-section
    headers can also request topology operations:

        <<<FILE DELETE path/to/file.py
        >>>FILE

        <<<FILE MOVE old.py -> new.py
        >>>FILE

        <<<FILE PRIMARY path/to/main.py
        >>>FILE
    """

    normalized_text = _strip_fences(mutation_text.replace("\r\n", "\n"))
    envelope_error = _validate_section_envelopes(
        normalized_text, "<<<FILE", ">>>FILE", "file"
    )
    if envelope_error is not None:
        return workspace, envelope_error
    sections = _parse_file_sections(normalized_text)
    if not sections:
        code, err = apply_candidate_mutation(
            workspace.code, mutation_text, mutation_mode=mutation_mode
        )
        if err is not None:
            return workspace, err
        files = dict(workspace.files)
        files[workspace.primary_file] = code
        return CandidateWorkspace(files, workspace.primary_file), None

    parsed_sections: list[tuple[dict, str]] = []
    for header, body in sections:
        spec, err = _parse_file_section_header(header)
        if err is not None:
            return workspace, err
        parsed_sections.append((spec, body))
    duplicate_edit = _find_duplicate_edit_section_path(parsed_sections)
    if duplicate_edit is not None:
        return workspace, f"{duplicate_edit}:duplicate_file_section"

    files = dict(workspace.files)
    primary_file = workspace.primary_file
    changed = False
    for spec, body in parsed_sections:
        op = spec["op"]
        rel_path = spec["path"]
        if op == "delete":
            if rel_path not in files:
                return workspace, f"{rel_path}:missing_source"
            if len(files) == 1:
                return workspace, f"{rel_path}:cannot_delete_last_file"
            del files[rel_path]
            if primary_file == rel_path:
                primary_file = sorted(files)[0]
            changed = True
            continue

        if op == "move":
            target_path = spec["target"]
            if rel_path not in files:
                return workspace, f"{rel_path}:missing_source"
            if target_path in files:
                return workspace, f"{target_path}:target_exists"
            files[target_path] = files.pop(rel_path)
            if primary_file == rel_path:
                primary_file = target_path
            changed = True
            continue

        if op == "primary":
            if rel_path not in files:
                return workspace, f"{rel_path}:missing_primary"
            if primary_file != rel_path:
                primary_file = rel_path
                changed = True
            continue

        current = files.get(rel_path, "")
        if mutation_mode == "full" and rel_path not in files:
            new_code, err = body.strip("\n"), None
        else:
            new_code, err = apply_candidate_mutation(current, body, mutation_mode)
        if err is not None:
            return workspace, f"{rel_path}:{err}"
        if new_code != current:
            files[rel_path] = new_code
            changed = True
    if not changed:
        return workspace, "no_valid_changes"
    return CandidateWorkspace(files, primary_file), None


def _parse_file_sections(mutation_text: str) -> list[tuple[str, str]]:
    text = _strip_fences(mutation_text.replace("\r\n", "\n"))
    return [(name.strip(), body.rstrip("\n")) for name, body in _FILE_SECTION_PATTERN.findall(text)]


def _parse_file_section_header(header: str) -> tuple[dict, str | None]:
    raw = header.strip()
    if not raw:
        return {}, "empty_path:unsafe_path"

    command, _, remainder = raw.partition(" ")
    command_upper = command.upper()
    if command_upper == "DELETE":
        return _parse_single_path_op("delete", remainder)
    if command_upper in {"MOVE", "RENAME"}:
        return _parse_move_op(remainder)
    if command_upper == "PRIMARY":
        return _parse_single_path_op("primary", remainder)
    try:
        return {"op": "edit", "path": normalize_candidate_path(raw)}, None
    except ValueError:
        return {}, f"{raw}:unsafe_path"


def _find_duplicate_edit_section_path(sections: list[tuple[dict, str]]) -> str | None:
    seen: set[str] = set()
    for spec, _ in sections:
        if spec.get("op") != "edit":
            continue
        path = spec["path"]
        if path in seen:
            return path
        seen.add(path)
    return None


def _parse_single_path_op(op: str, raw_path: str) -> tuple[dict, str | None]:
    raw_path = raw_path.strip()
    if not raw_path:
        return {}, f"{op}:empty_path"
    try:
        return {"op": op, "path": normalize_candidate_path(raw_path)}, None
    except ValueError:
        return {}, f"{raw_path}:unsafe_path"


def _parse_move_op(remainder: str) -> tuple[dict, str | None]:
    source, sep, target = remainder.partition("->")
    if not sep:
        return {}, "move:missing_target"
    source = source.strip()
    target = target.strip()
    if not source:
        return {}, "move:empty_source"
    if not target:
        return {}, "move:empty_target"
    try:
        source_path = normalize_candidate_path(source)
        target_path = normalize_candidate_path(target)
    except ValueError:
        bad_path = source if "source_path" not in locals() else target
        return {}, f"{bad_path}:unsafe_path"
    if source_path == target_path:
        return {}, f"{source_path}:no_valid_changes"
    return {"op": "move", "path": source_path, "target": target_path}, None


def _validate_section_envelopes(
    text: str, start_marker: str, end_marker: str, label: str
) -> str | None:
    open_section = False
    matches = sorted(
        [(match.start(), "start") for match in re.finditer(re.escape(start_marker), text)]
        + [(match.start(), "end") for match in re.finditer(re.escape(end_marker), text)]
    )
    for _, kind in matches:
        if kind == "start":
            if open_section:
                return f"malformed_{label}_sections:nested_start"
            open_section = True
        else:
            if not open_section:
                return f"malformed_{label}_sections:orphan_end"
            open_section = False
    if open_section:
        return f"malformed_{label}_sections:missing_end"
    return None


def _parse_evolve_blocks(code: str) -> tuple[list[EvolveBlock], str | None]:
    blocks: list[EvolveBlock] = []
    seen_names: set[str] = set()
    open_block: tuple[str, int, int] | None = None
    offset = 0
    idx = 0
    for line in code.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith(EVOLVE_BLOCK_START):
            if open_block is not None:
                return blocks, "nested_start"
            raw_name = stripped[len(EVOLVE_BLOCK_START):].strip()
            name = raw_name or f"block_{idx}"
            if not _BLOCK_NAME_PATTERN.fullmatch(name):
                return blocks, "invalid_name"
            if name in seen_names:
                return blocks, "duplicate_name"
            content_start = offset + len(line)
            open_block = (name, offset, content_start)
        elif stripped.startswith(EVOLVE_BLOCK_END):
            if stripped != EVOLVE_BLOCK_END:
                return blocks, "invalid_end_marker"
            if open_block is None:
                return blocks, "orphan_end"
            name, start, content_start = open_block
            content_end = offset
            if content_end > content_start and code[content_end - 1] == "\n":
                content_end -= 1
            end = offset + len(line)
            blocks.append(
                EvolveBlock(
                    name=name,
                    start=start,
                    content_start=content_start,
                    content_end=content_end,
                    end=end,
                    content=code[content_start:content_end],
                )
            )
            seen_names.add(name)
            idx += 1
            open_block = None
        offset += len(line)
    if open_block is not None:
        return blocks, "missing_end"
    return blocks, None


def _apply_diff_to_candidate(code: str, diff_text: str) -> tuple[str, str | None]:
    blocks = extract_evolve_blocks(code)
    if not blocks:
        return apply_diff(code, diff_text)

    diff_blocks = _parse_diff_blocks(diff_text)
    if not diff_blocks:
        return code, "no_diff_blocks"
    result = code
    for search, replace in diff_blocks:
        found = False
        for block in extract_evolve_blocks(result):
            if search and search in block.content:
                new_content = block.content.replace(search, replace, 1)
                result = (
                    result[: block.content_start]
                    + new_content
                    + result[block.content_end :]
                )
                found = True
                break
        if not found:
            return code, "search_not_found"
    if result == code:
        return code, "no_valid_changes"
    return result, None


def _parse_diff_blocks(diff_text: str) -> list[tuple[str, str]]:
    return parse_diff_blocks(diff_text)


def _apply_full_replacement(code: str, mutation_text: str) -> tuple[str, str | None]:
    replacement = _strip_fences(mutation_text.replace("\r\n", "\n")).strip("\n")
    blocks = extract_evolve_blocks(code)
    if not blocks:
        return (replacement, None) if replacement != code else (code, "no_valid_changes")
    if len(blocks) == 1:
        block = blocks[0]
        if replacement == block.content:
            return code, "no_valid_changes"
        return code[: block.content_start] + replacement + code[block.content_end :], None

    envelope_error = _validate_section_envelopes(
        replacement, "<<<BLOCK", ">>>BLOCK", "block"
    )
    if envelope_error is not None:
        return code, envelope_error
    sections: dict[str, str] = {}
    for raw_name, body in _BLOCK_SECTION_PATTERN.findall(replacement):
        name = raw_name.strip()
        if not name:
            return code, "malformed_block_sections:empty_name"
        if not _BLOCK_NAME_PATTERN.fullmatch(name):
            return code, "malformed_block_sections:invalid_name"
        if name in sections:
            return code, "malformed_block_sections:duplicate_name"
        sections[name] = body.rstrip("\n")
    if not sections:
        return code, "missing_block_sections"
    result = code
    for block in reversed(blocks):
        if block.name not in sections:
            continue
        result = result[: block.content_start] + sections[block.name] + result[block.content_end :]
    if result == code:
        return code, "no_valid_changes"
    return result, None
