from __future__ import annotations
import re

DIFF_PATTERN = re.compile(r"<<<SEARCH\n(.*?)\n===\n(.*?)\n>>>REPLACE", re.DOTALL)

def apply_diff(code: str, diff_text: str) -> tuple[str, str | None]:
    """Apply SEARCH/REPLACE blocks. Returns (new_code, diff_error).
    diff_error is None on success.
    Error values: no_diff_blocks | search_not_found | no_valid_changes
    """
    diff_text = diff_text.replace("\r\n", "\n")
    blocks = [(s.rstrip("\n"), r.rstrip("\n")) for s, r in DIFF_PATTERN.findall(diff_text)]
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
