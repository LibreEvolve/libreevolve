from __future__ import annotations

from dataclasses import dataclass
import re

from libreevolve.core.diff import apply_diff, _strip_fences

EVOLVE_BLOCK_START = "# EVOLVE-BLOCK-START"
EVOLVE_BLOCK_END = "# EVOLVE-BLOCK-END"

_BLOCK_SECTION_PATTERN = re.compile(
    r"<<<BLOCK\s+([A-Za-z0-9_.:-]+)\s*\n(.*?)\n>>>BLOCK", re.DOTALL
)


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
    from libreevolve.core.diff import DIFF_PATTERN

    diff_text = _strip_fences(diff_text.replace("\r\n", "\n"))
    return [(s.rstrip("\n"), r.rstrip("\n")) for s, r in DIFF_PATTERN.findall(diff_text)]


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
