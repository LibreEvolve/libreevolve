"""SEARCH/REPLACE diff engine.

Inspired by AlphaEvolve (arXiv:2506.13131) SEARCH/REPLACE mutation. LibreEvolve
accepts both the AlphaEvolve-style fence spelling and the older compact local
format for backward compatibility.
"""
from __future__ import annotations
import hashlib
import re

from libreevolve.core.redaction import redact_sensitive_text

DIFF_PATTERN = re.compile(r"<<<SEARCH\n(.*?)\n===\n(.*?)\n>>>REPLACE", re.DOTALL)
CANONICAL_DIFF_PATTERN = re.compile(
    r"<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE", re.DOTALL
)
PROPOSAL_SECTION_PATTERN = re.compile(
    r"(?im)^\s*(?:\[(IDEA|RATIONALE|HYPOTHESIS)\]|"
    r"(IDEA|RATIONALE|HYPOTHESIS)\s*:)\s*(.*?)\s*$"
)
PROPOSAL_BLOCK_OPEN_PATTERN = re.compile(r"(?im)^\s*\[(IDEA|RATIONALE|HYPOTHESIS)\]\s*$")
PROPOSAL_BLOCK_CLOSE_PATTERN = re.compile(
    r"(?im)^\s*\[/(IDEA|RATIONALE|HYPOTHESIS)\]\s*$"
)
_MAX_PROPOSAL_FIELD_CHARS = 2000
_MAX_EXPLANATORY_PREAMBLE_CHARS = 2000
_MUTATION_PAYLOAD_MARKERS = (
    "<<<SEARCH",
    "<<<<<<< SEARCH",
    "<<<FILE",
    "<<<BLOCK",
)

def _strip_fences(text: str) -> str:
    """Remove one markdown code fence only when it wraps the whole response."""
    stripped_start = len(text) - len(text.lstrip())
    stripped_end = len(text.rstrip())
    if stripped_start >= stripped_end:
        return text
    candidate = text[stripped_start:stripped_end]
    first_line_end = candidate.find("\n")
    if first_line_end == -1:
        return text
    first_line = candidate[:first_line_end]
    if not re.fullmatch(r"```[A-Za-z0-9_.:+-]*[ \t]*", first_line):
        return text
    before_closing = candidate.rfind("\n```")
    if before_closing == -1:
        return text
    closing = candidate[before_closing + 1 :]
    if not re.fullmatch(r"```[ \t]*", closing):
        return text
    return candidate[first_line_end + 1 : before_closing + 1]


def apply_diff(code: str, diff_text: str) -> tuple[str, str | None]:
    """Apply SEARCH/REPLACE blocks. Returns (new_code, diff_error).
    diff_error is None on success.
    Error values: no_diff_blocks | search_not_found | ambiguous_search_match |
    no_valid_changes
    """
    blocks = parse_diff_blocks(diff_text)
    consumed_error = validate_diff_payload_shape(diff_text)
    if consumed_error is not None:
        return code, consumed_error
    result = code
    for search, replace in blocks:
        if not search.strip():
            return code, "search_not_found"
        matches = _line_ending_tolerant_matches(result, search)
        if matches == 0:
            return code, "search_not_found"
        if matches > 1:
            return code, "ambiguous_search_match"
        result = _replace_line_ending_tolerant(result, search, replace)
    if result == code:
        return code, "no_valid_changes"
    return result, None


def validate_diff_payload_shape(diff_text: str) -> str | None:
    """Validate diff syntax without requiring SEARCH text to match a candidate."""
    if not parse_diff_blocks(diff_text):
        return "no_diff_blocks"
    return _validate_consumed_diff_text(diff_text)


def _line_ending_tolerant_matches(code: str, search: str) -> int:
    normalized_code, _starts, _ends = _normalize_line_endings_with_offsets(code)
    normalized_search = _normalize_line_endings(search)
    return normalized_code.count(normalized_search)


def _replace_line_ending_tolerant(code: str, search: str, replace: str) -> str:
    normalized_code, starts, ends = _normalize_line_endings_with_offsets(code)
    normalized_search = _normalize_line_endings(search)
    start = normalized_code.find(normalized_search)
    if start < 0:
        return code
    end = start + len(normalized_search)
    original_start = starts[start] if start < len(starts) else len(code)
    original_end = ends[end - 1] if end > 0 else original_start
    original_span = code[original_start:original_end]
    replacement = _adapt_line_endings(replace, _dominant_line_ending(original_span))
    return code[:original_start] + replacement + code[original_end:]


def _normalize_line_endings(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _normalize_line_endings_with_offsets(text: str) -> tuple[str, list[int], list[int]]:
    chars: list[str] = []
    starts: list[int] = []
    ends: list[int] = []
    index = 0
    while index < len(text):
        if text.startswith("\r\n", index):
            chars.append("\n")
            starts.append(index)
            ends.append(index + 2)
            index += 2
            continue
        char = text[index]
        chars.append("\n" if char == "\r" else char)
        starts.append(index)
        ends.append(index + 1)
        index += 1
    return "".join(chars), starts, ends


def _dominant_line_ending(text: str) -> str:
    crlf = text.count("\r\n")
    without_crlf = text.replace("\r\n", "")
    lf = without_crlf.count("\n")
    cr = without_crlf.count("\r")
    if crlf >= lf and crlf >= cr and crlf > 0:
        return "\r\n"
    if cr > lf and cr > 0:
        return "\r"
    return "\n"


def _adapt_line_endings(text: str, line_ending: str) -> str:
    normalized = _normalize_line_endings(text)
    if line_ending == "\n":
        return normalized
    return normalized.replace("\n", line_ending)


def parse_diff_blocks(diff_text: str) -> list[tuple[str, str]]:
    """Parse compact and AlphaEvolve-style SEARCH/REPLACE blocks."""
    diff_text = diff_text.replace("\r\n", "\n")
    diff_text = _strip_fences(diff_text)
    matches = _diff_matches(diff_text)
    return [(search, replace) for _, search, replace in sorted(matches, key=lambda item: item[0])]


def _diff_matches(diff_text: str) -> list[tuple[int, str, str]]:
    matches: list[tuple[int, str, str]] = []
    for pattern in (DIFF_PATTERN, CANONICAL_DIFF_PATTERN):
        matches.extend(
            (match.start(), match.group(1).rstrip("\n"), match.group(2).rstrip("\n"))
            for match in pattern.finditer(diff_text)
        )
    return matches


def _diff_match_spans(diff_text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for pattern in (DIFF_PATTERN, CANONICAL_DIFF_PATTERN):
        spans.extend(match.span() for match in pattern.finditer(diff_text))
    return sorted(spans)


def _validate_consumed_diff_text(diff_text: str) -> str | None:
    text = _strip_fences(diff_text.replace("\r\n", "\n"))
    spans = _diff_match_spans(text)
    if not spans:
        return None
    outside: list[str] = []
    cursor = 0
    for start, end in spans:
        outside.append(text[cursor:start])
        cursor = end
    outside.append(text[cursor:])
    leading = strip_allowed_leading_preamble(outside[0])
    remainder = leading + "".join(strip_proposal_metadata(segment) for segment in outside[1:])
    if remainder.strip():
        return "malformed_diff:unconsumed_text"
    return None


def extract_proposal_metadata(response_text: str) -> dict:
    """Extract optional IDEA/RATIONALE/HYPOTHESIS sections from a mutation response."""
    metadata: dict[str, str] = {}
    sections, _ = _proposal_sections_and_payload(response_text)
    for label, raw_value in sections:
        value = _truncate_metadata_field(raw_value.strip())
        if label and value and label not in metadata:
            metadata[label] = value
    return metadata


def strip_proposal_metadata(response_text: str) -> str:
    """Remove optional proposal sections, leaving only the mutation payload."""
    _, payload = _split_proposal_preamble(response_text)
    return payload.lstrip("\n")


def extract_explanatory_preamble(response_text: str) -> dict:
    """Return bounded freeform rationale before the first mutation marker."""
    if not isinstance(response_text, str):
        return {}
    text = response_text.replace("\r\n", "\n")
    text = _strip_fences(text)
    structured_preamble, payload = _split_proposal_preamble(text)
    if structured_preamble.strip() and payload.strip() and not payload.startswith("\n"):
        return {}
    marker_index = _first_mutation_marker_index(payload)
    if marker_index is None:
        return {}
    preamble = payload[:marker_index].strip()
    if not preamble or _contains_mutation_marker_fragment(preamble):
        return {}
    redacted = redact_sensitive_text(preamble)
    truncated = len(redacted) > _MAX_EXPLANATORY_PREAMBLE_CHARS
    preview = (
        redacted[: _MAX_EXPLANATORY_PREAMBLE_CHARS - 14].rstrip()
        + "\n...[truncated]"
        if truncated
        else redacted
    )
    return {
        "schema": "libreevolve.explanatory_preamble.v1",
        "source": "freeform_text_before_first_mutation_marker",
        "policy": "bounded_redacted_leading_preamble_only",
        "structured_proposal_preamble_present": bool(structured_preamble.strip()),
        "sha256": hashlib.sha256(redacted.encode("utf-8")).hexdigest(),
        "chars": len(redacted),
        "preview": preview,
        "preview_chars": len(preview),
        "truncated": truncated,
    }


def strip_allowed_leading_preamble(text: str) -> str:
    """Strip structured metadata plus safe freeform text before a payload marker."""
    structured_preamble, payload = _split_proposal_preamble(text)
    if not payload.strip():
        return ""
    if structured_preamble.strip() and not payload.startswith("\n"):
        return payload
    if _contains_mutation_marker_fragment(payload):
        return payload
    return ""


def validate_proposal_metadata_preamble(response_text: str) -> str | None:
    """Return an error for ambiguous proposal metadata before mutation payload."""
    text = response_text.replace("\r\n", "\n")
    text = _strip_fences(text)
    lines = text.splitlines(keepends=True)
    seen_metadata = False
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped_line = line.rstrip("\n")
        open_match = PROPOSAL_BLOCK_OPEN_PATTERN.match(stripped_line)
        if open_match:
            seen_metadata = True
            label = open_match.group(1).upper()
            index += 1
            closed = False
            while index < len(lines):
                close_match = PROPOSAL_BLOCK_CLOSE_PATTERN.match(lines[index].rstrip("\n"))
                if close_match and close_match.group(1).upper() == label:
                    closed = True
                    index += 1
                    break
                index += 1
            if not closed:
                return "malformed_proposal_metadata:unterminated_section"
            continue
        if PROPOSAL_SECTION_PATTERN.match(stripped_line):
            seen_metadata = True
            index += 1
            continue
        if not seen_metadata:
            return None
        if not stripped_line.strip():
            return None
        if any(
            PROPOSAL_SECTION_PATTERN.match(candidate.rstrip("\n"))
            or PROPOSAL_BLOCK_OPEN_PATTERN.match(candidate.rstrip("\n"))
            for candidate in lines[index + 1 :]
        ):
            return "malformed_proposal_metadata:multiline_continuation"
        return None
    return None


def _split_proposal_preamble(response_text: str) -> tuple[str, str]:
    _, payload = _proposal_sections_and_payload(response_text)
    response_text = response_text.replace("\r\n", "\n")
    response_text = _strip_fences(response_text)
    return response_text[: len(response_text) - len(payload)], payload


def _proposal_sections_and_payload(response_text: str) -> tuple[list[tuple[str, str]], str]:
    response_text = response_text.replace("\r\n", "\n")
    response_text = _strip_fences(response_text)
    cursor = 0
    sections: list[tuple[str, str]] = []
    while cursor < len(response_text):
        line_end = response_text.find("\n", cursor)
        if line_end == -1:
            line_end = len(response_text)
            line = response_text[cursor:line_end]
        else:
            line = response_text[cursor : line_end + 1]
        line_text = line.rstrip("\n")
        open_match = PROPOSAL_BLOCK_OPEN_PATTERN.match(line_text)
        if open_match:
            label = open_match.group(1).lower()
            content_start = cursor + len(line)
            close_match = _proposal_block_close_match(response_text, content_start, label)
            if close_match is None:
                break
            content = response_text[content_start : close_match.start()]
            sections.append((label, content.strip()))
            cursor = close_match.end()
            if cursor < len(response_text) and response_text[cursor : cursor + 1] == "\n":
                cursor += 1
            continue
        match = PROPOSAL_SECTION_PATTERN.match(line_text)
        if match:
            label = (match.group(1) or match.group(2) or "").lower()
            sections.append((label, match.group(3).strip()))
            cursor += len(line)
            continue
        break
    if not sections:
        return [], response_text
    return sections, response_text[cursor:]


def _proposal_block_close_match(
    response_text: str, start: int, label: str
) -> re.Match[str] | None:
    for match in PROPOSAL_BLOCK_CLOSE_PATTERN.finditer(response_text, start):
        if match.group(1).lower() == label:
            return match
    return None


def _truncate_metadata_field(value: str) -> str:
    if len(value) <= _MAX_PROPOSAL_FIELD_CHARS:
        return value
    return value[: _MAX_PROPOSAL_FIELD_CHARS - 14].rstrip() + "\n...[truncated]"


def _first_mutation_marker_index(text: str) -> int | None:
    indexes = [text.find(marker) for marker in _MUTATION_PAYLOAD_MARKERS]
    indexes = [index for index in indexes if index >= 0]
    return min(indexes) if indexes else None


def _contains_mutation_marker_fragment(text: str) -> bool:
    return "<<<" in text or ">>>>" in text or "=======" in text
