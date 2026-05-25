from libreevolve.core.diff import apply_diff

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
