from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from libreevolve.core.diff import apply_diff, parse_diff_blocks, _strip_fences

EVOLVE_BLOCK_START = "# EVOLVE-BLOCK-START"
EVOLVE_BLOCK_END = "# EVOLVE-BLOCK-END"

_BLOCK_SECTION_PATTERN = re.compile(
    r"<<<BLOCK\s+([A-Za-z0-9_.:-]+)\s*\n(.*?)\n>>>BLOCK", re.DOTALL
)
_FILE_SECTION_PATTERN = re.compile(
    r"<<<FILE\s+([A-Za-z0-9_./\\:-]+)\s*\n(.*?)\n>>>FILE", re.DOTALL
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
        self.files = {normalize_candidate_path(k): v for k, v in self.files.items()}
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
    blocks: list[EvolveBlock] = []
    pos = 0
    idx = 0
    while True:
        start = code.find(EVOLVE_BLOCK_START, pos)
        if start < 0:
            break
        start_line_end = code.find("\n", start)
        if start_line_end < 0:
            break
        marker_line = code[start:start_line_end]
        parts = marker_line.split(maxsplit=2)
        name = parts[2].strip() if len(parts) >= 3 else f"block_{idx}"
        content_start = start_line_end + 1
        end_marker = code.find(EVOLVE_BLOCK_END, content_start)
        if end_marker < 0:
            break
        content_end = end_marker
        if content_end > content_start and code[content_end - 1] == "\n":
            content_end -= 1
        end_line_end = code.find("\n", end_marker)
        end = len(code) if end_line_end < 0 else end_line_end + 1
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
        pos = end
        idx += 1
    return blocks


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
    to that file; unknown files can be created by `full` mode.
    """

    sections = _parse_file_sections(mutation_text)
    if not sections:
        code, err = apply_candidate_mutation(
            workspace.code, mutation_text, mutation_mode=mutation_mode
        )
        if err is not None:
            return workspace, err
        files = dict(workspace.files)
        files[workspace.primary_file] = code
        return CandidateWorkspace(files, workspace.primary_file), None

    files = dict(workspace.files)
    changed = False
    for rel_path, body in sections:
        raw_path = rel_path.strip()
        try:
            rel_path = normalize_candidate_path(raw_path)
        except ValueError:
            return workspace, f"{raw_path}:unsafe_path"
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
    return CandidateWorkspace(files, workspace.primary_file), None


def _parse_file_sections(mutation_text: str) -> list[tuple[str, str]]:
    text = _strip_fences(mutation_text.replace("\r\n", "\n"))
    return [(name.strip(), body.rstrip("\n")) for name, body in _FILE_SECTION_PATTERN.findall(text)]


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

    sections = {name: body.rstrip("\n") for name, body in _BLOCK_SECTION_PATTERN.findall(replacement)}
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
