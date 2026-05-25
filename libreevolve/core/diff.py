"""SEARCH/REPLACE diff engine.

Inspired by AlphaEvolve (arXiv:2506.13131) SEARCH/REPLACE mutation. LibreEvolve
accepts both the AlphaEvolve-style fence spelling and the older compact local
format for backward compatibility.
"""
from __future__ import annotations
import re

DIFF_PATTERN = re.compile(r"<<<SEARCH\n(.*?)\n===\n(.*?)\n>>>REPLACE", re.DOTALL)
CANONICAL_DIFF_PATTERN = re.compile(
    r"<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE", re.DOTALL
)
PROPOSAL_SECTION_PATTERN = re.compile(
    r"(?im)^\s*(?:\[(IDEA|RATIONALE|HYPOTHESIS)\]|"
    r"(IDEA|RATIONALE|HYPOTHESIS)\s*:)\s*(.*?)\s*$"
)
_MAX_PROPOSAL_FIELD_CHARS = 2000

def _strip_fences(text: str) -> str:
    """Remove markdown code fences that models wrap around diffs."""
    text = re.sub(r"```(?:diff|python|text)?\s*\n?", "", text)
    return text


def apply_diff(code: str, diff_text: str) -> tuple[str, str | None]:
    """Apply SEARCH/REPLACE blocks. Returns (new_code, diff_error).
    diff_error is None on success.
    Error values: no_diff_blocks | search_not_found | no_valid_changes
    """
    blocks = parse_diff_blocks(diff_text)
    if not blocks:
        return code, "no_diff_blocks"
    result = code
    for search, replace in blocks:
        if not search.strip():
            return code, "search_not_found"
        if search not in result:
            return code, "search_not_found"
        result = result.replace(search, replace, 1)
    if result == code:
        return code, "no_valid_changes"
    return result, None


def parse_diff_blocks(diff_text: str) -> list[tuple[str, str]]:
    """Parse compact and AlphaEvolve-style SEARCH/REPLACE blocks."""
    diff_text = diff_text.replace("\r\n", "\n")
    diff_text = _strip_fences(diff_text)
    matches: list[tuple[int, str, str]] = []
    for pattern in (DIFF_PATTERN, CANONICAL_DIFF_PATTERN):
        matches.extend(
            (match.start(), match.group(1).rstrip("\n"), match.group(2).rstrip("\n"))
            for match in pattern.finditer(diff_text)
        )
    return [(search, replace) for _, search, replace in sorted(matches, key=lambda item: item[0])]


def extract_proposal_metadata(response_text: str) -> dict:
    """Extract optional IDEA/RATIONALE/HYPOTHESIS sections from a mutation response."""
    response_text = response_text.replace("\r\n", "\n")
    response_text = _strip_fences(response_text)
    metadata: dict[str, str] = {}
    for match in PROPOSAL_SECTION_PATTERN.finditer(response_text):
        label = (match.group(1) or match.group(2) or "").lower()
        value = _truncate_metadata_field(match.group(3).strip())
        if label and value and label not in metadata:
            metadata[label] = value
    return metadata


def strip_proposal_metadata(response_text: str) -> str:
    """Remove optional proposal sections, leaving only the mutation payload."""
    response_text = response_text.replace("\r\n", "\n")
    response_text = _strip_fences(response_text)
    return PROPOSAL_SECTION_PATTERN.sub("", response_text).lstrip("\n")


def _truncate_metadata_field(value: str) -> str:
    if len(value) <= _MAX_PROPOSAL_FIELD_CHARS:
        return value
    return value[: _MAX_PROPOSAL_FIELD_CHARS - 14].rstrip() + "\n...[truncated]"
