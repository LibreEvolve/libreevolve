from libreevolve.core.diff import (
    apply_diff,
    extract_explanatory_preamble,
    extract_proposal_metadata,
    strip_proposal_metadata,
    validate_proposal_metadata_preamble,
)

def test_no_blocks():
    code, err = apply_diff("x = 1", "no diff here")
    assert code == "x = 1" and err == "no_diff_blocks"

def test_empty_is_no_blocks():
    _, err = apply_diff("x = 1", "")
    assert err == "no_diff_blocks"

def test_search_not_found():
    diff = "<<<SEARCH\ny = 2\n===\ny = 3\n>>>REPLACE"
    code, err = apply_diff("x = 1", diff)
    assert code == "x = 1" and err == "search_not_found"

def test_no_valid_changes():
    diff = "<<<SEARCH\nx = 1\n===\nx = 1\n>>>REPLACE"
    _, err = apply_diff("x = 1", diff)
    assert err == "no_valid_changes"

def test_successful_single_block():
    code = "x = 1\ny = 2"
    diff = "<<<SEARCH\nx = 1\n===\nx = 10\n>>>REPLACE"
    new_code, err = apply_diff(code, diff)
    assert err is None and "x = 10" in new_code and "y = 2" in new_code


def test_outer_markdown_fence_wrapped_diff_applies():
    code = "x = 1\n"
    diff = "```diff\n<<<SEARCH\nx = 1\n===\nx = 2\n>>>REPLACE\n```"

    new_code, err = apply_diff(code, diff)

    assert err is None
    assert new_code == "x = 2\n"


def test_search_replace_preserves_markdown_fence_literals_in_replacement():
    code = 'DOC = ""\n'
    diff = (
        "<<<SEARCH\n"
        'DOC = ""\n'
        "===\n"
        "DOC = '''```python\n"
        "print(1)\n"
        "```'''\n"
        ">>>REPLACE"
    )

    new_code, err = apply_diff(code, diff)

    assert err is None
    assert new_code == "DOC = '''```python\nprint(1)\n```'''\n"


def test_search_replace_preserves_file_and_block_marker_literals_in_replacement():
    code = 'TEXT = ""\n'
    diff = (
        "<<<SEARCH\n"
        'TEXT = ""\n'
        "===\n"
        'TEXT = "<<<FILE not a section >>>FILE <<<BLOCK not a section >>>BLOCK"\n'
        ">>>REPLACE"
    )

    new_code, err = apply_diff(code, diff)

    assert err is None
    assert new_code == 'TEXT = "<<<FILE not a section >>>FILE <<<BLOCK not a section >>>BLOCK"\n'


def test_allows_explanatory_preamble_before_valid_diff_block():
    code = "x = 1"
    diff = "Here is the patch:\n<<<SEARCH\nx = 1\n===\nx = 2\n>>>REPLACE"

    result, err = apply_diff(code, diff)
    preamble = extract_explanatory_preamble(diff)

    assert err is None
    assert result == "x = 2"
    assert preamble["schema"] == "libreevolve.explanatory_preamble.v1"
    assert preamble["preview"] == "Here is the patch:"
    assert preamble["policy"] == "bounded_redacted_leading_preamble_only"


def test_rejects_trailing_prose_after_valid_diff_block():
    code = "x = 1"
    diff = "<<<SEARCH\nx = 1\n===\nx = 2\n>>>REPLACE\nThis is why it works."

    result, err = apply_diff(code, diff)

    assert result == code
    assert err == "malformed_diff:unconsumed_text"


def test_rejects_malformed_trailing_diff_after_valid_block():
    code = "x = 1\ny = 1"
    diff = (
        "<<<SEARCH\nx = 1\n===\nx = 2\n>>>REPLACE\n"
        "<<<SEARCH\ny = 1\n===\ny = 2\n"
    )

    result, err = apply_diff(code, diff)

    assert result == code
    assert err == "malformed_diff:unconsumed_text"


def test_allows_proposal_metadata_around_valid_diff_block():
    code = "x = 1"
    diff = (
        "IDEA: Replace x.\n"
        "RATIONALE: The target value is higher.\n"
        "HYPOTHESIS: Score should improve.\n"
        "<<<SEARCH\nx = 1\n===\nx = 2\n>>>REPLACE"
    )

    result, err = apply_diff(code, diff)

    assert err is None
    assert result == "x = 2"


def test_search_replace_matches_lf_patch_against_crlf_candidate():
    code = "x = 1\r\ny = 2\r\n"
    diff = "<<<SEARCH\nx = 1\ny = 2\n===\nx = 10\ny = 20\n>>>REPLACE"

    new_code, err = apply_diff(code, diff)

    assert err is None
    assert new_code == "x = 10\r\ny = 20\r\n"


def test_search_replace_preserves_unedited_mixed_line_endings():
    code = "a = 1\r\nb = 2\nc = 3\r\n"
    diff = "<<<SEARCH\nb = 2\nc = 3\n===\nb = 20\nc = 30\n>>>REPLACE"

    new_code, err = apply_diff(code, diff)

    assert err is None
    assert new_code == "a = 1\r\nb = 20\nc = 30\r\n"

def test_successful_canonical_alphaevolve_block():
    code = "x = 1\ny = 2"
    diff = "<<<<<<< SEARCH\nx = 1\n=======\nx = 10\n>>>>>>> REPLACE"
    new_code, err = apply_diff(code, diff)
    assert err is None and "x = 10" in new_code and "y = 2" in new_code

def test_multiple_blocks():
    code = "a = 1\nb = 2"
    diff = "<<<SEARCH\na = 1\n===\na = 10\n>>>REPLACE\n<<<SEARCH\nb = 2\n===\nb = 20\n>>>REPLACE"
    new_code, err = apply_diff(code, diff)
    assert err is None and "a = 10" in new_code and "b = 20" in new_code


def test_rejects_ambiguous_search_match_without_partial_apply():
    code = "x = 1\nx = 1\n"
    diff = "<<<SEARCH\nx = 1\n===\nx = 2\n>>>REPLACE"

    result, err = apply_diff(code, diff)

    assert result == code
    assert err == "ambiguous_search_match"


def test_mixed_compact_and_canonical_blocks():
    code = "a = 1\nb = 2"
    diff = (
        "<<<SEARCH\na = 1\n===\na = 10\n>>>REPLACE\n"
        "<<<<<<< SEARCH\nb = 2\n=======\nb = 20\n>>>>>>> REPLACE"
    )
    new_code, err = apply_diff(code, diff)
    assert err is None and "a = 10" in new_code and "b = 20" in new_code

def test_mixed_formats_apply_in_document_order():
    code = "x = 1"
    diff = (
        "<<<<<<< SEARCH\nx = 1\n=======\nx = 2\n>>>>>>> REPLACE\n"
        "<<<SEARCH\nx = 2\n===\nx = 3\n>>>REPLACE"
    )
    new_code, err = apply_diff(code, diff)
    assert err is None
    assert new_code == "x = 3"

def test_original_unchanged_on_error():
    original = "def foo():\n    pass"
    code, _ = apply_diff(original, "no blocks")
    assert code == original

def test_partial_apply_is_atomic():
    """If the second block fails, the first block's changes must be rolled back."""
    code = "a = 1\nb = 2"
    diff = "<<<SEARCH\na = 1\n===\na = 10\n>>>REPLACE\n<<<SEARCH\nZZZZ\n===\nno\n>>>REPLACE"
    result, err = apply_diff(code, diff)
    assert result == code and err == "search_not_found"


def test_extract_proposal_metadata_from_response_with_diff():
    response = """IDEA: Replace the constant with the expected value.
RATIONALE: The validator rewards returning two.
HYPOTHESIS: Score should increase.
<<<SEARCH
x = 1
===
x = 2
>>>REPLACE"""

    metadata = extract_proposal_metadata(response)

    assert metadata == {
        "idea": "Replace the constant with the expected value.",
        "rationale": "The validator rewards returning two.",
        "hypothesis": "Score should increase.",
    }


def test_extract_proposal_metadata_ignores_diff_only_response():
    assert extract_proposal_metadata("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE") == {}


def test_extract_proposal_metadata_ignores_marker_literals_after_payload_start():
    response = """IDEA: Replace the full file.
def solve():
    return '''IDEA: this is candidate data'''
"""

    assert extract_proposal_metadata(response) == {"idea": "Replace the full file."}


def test_strip_proposal_metadata_leaves_patch_payload():
    response = """IDEA: Replace the full file.
RATIONALE: It is shorter.
HYPOTHESIS: Equivalent behavior.
def solve():
    return 2
"""

    assert strip_proposal_metadata(response) == "def solve():\n    return 2\n"


def test_strip_proposal_metadata_preserves_marker_literals_after_payload_start():
    response = """IDEA: Replace the full file.
RATIONALE: Keep marker-looking literals.
def solve():
    return '''IDEA: this is candidate data'''
"""

    assert strip_proposal_metadata(response) == (
        "def solve():\n    return '''IDEA: this is candidate data'''\n"
    )


def test_multiline_proposal_continuation_is_payload_not_metadata():
    response = """IDEA: Improve helper
with second line detail
RATIONALE: First reason
<<<SEARCH
x = 1
===
x = 2
>>>REPLACE"""

    assert extract_proposal_metadata(response) == {"idea": "Improve helper"}
    assert strip_proposal_metadata(response).startswith(
        "with second line detail\nRATIONALE: First reason\n"
    )


def test_wrapped_proposal_metadata_before_diff_is_rejected_as_unconsumed_text():
    response = """IDEA: Improve helper
with second line detail
<<<SEARCH
x = 1
===
x = 2
>>>REPLACE"""

    result, err = apply_diff("x = 1\n", response)

    assert result == "x = 1\n"
    assert err == "malformed_diff:unconsumed_text"


def test_extracts_bounded_multiline_proposal_sections():
    response = """[IDEA]
Improve helper
with second line detail
[/IDEA]
[RATIONALE]
The validator repeats this branch.
[/RATIONALE]
<<<SEARCH
x = 1
===
x = 2
>>>REPLACE"""

    assert extract_proposal_metadata(response) == {
        "idea": "Improve helper\nwith second line detail",
        "rationale": "The validator repeats this branch.",
    }
    assert strip_proposal_metadata(response).startswith("<<<SEARCH\n")
    assert validate_proposal_metadata_preamble(response) is None


def test_proposal_metadata_validation_rejects_wrapped_colon_sections():
    response = """IDEA: Improve helper
with second line detail
RATIONALE: The validator repeats this branch.
x = 2
"""

    assert (
        validate_proposal_metadata_preamble(response)
        == "malformed_proposal_metadata:multiline_continuation"
    )


def test_proposal_metadata_validation_rejects_unterminated_multiline_section():
    response = """[IDEA]
Improve helper
<<<SEARCH
x = 1
===
x = 2
>>>REPLACE"""

    assert (
        validate_proposal_metadata_preamble(response)
        == "malformed_proposal_metadata:unterminated_section"
    )
