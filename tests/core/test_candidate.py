from libreevolve.core.candidate import (
    apply_candidate_mutation,
    extract_evolve_blocks,
)


def test_extracts_named_evolve_blocks():
    code = "# header\n# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"
    blocks = extract_evolve_blocks(code)
    assert len(blocks) == 1
    assert blocks[0].name == "core"
    assert blocks[0].content == "x = 1"


def test_diff_mode_preserves_skeleton_around_evolve_block():
    code = "keep = 1\n# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"
    diff = "<<<SEARCH\nx = 1\n===\nx = 2\n>>>REPLACE"
    result, err = apply_candidate_mutation(code, diff, mutation_mode="diff")
    assert err is None
    assert "keep = 1" in result
    assert "x = 2" in result


def test_diff_mode_rejects_skeleton_edit_when_blocks_exist():
    code = "keep = 1\n# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"
    diff = "<<<SEARCH\nkeep = 1\n===\nkeep = 2\n>>>REPLACE"
    result, err = apply_candidate_mutation(code, diff, mutation_mode="diff")
    assert result == code
    assert err == "search_not_found"


def test_full_mode_replaces_single_evolve_block_only():
    code = "keep = 1\n# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"
    result, err = apply_candidate_mutation(code, "x = 9", mutation_mode="full")
    assert err is None
    assert "keep = 1" in result
    assert "x = 9" in result
    assert "x = 1" not in result


def test_full_mode_replaces_multiple_named_blocks():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    response = "<<<BLOCK a\nx = 10\n>>>BLOCK\n<<<BLOCK b\ny = 20\n>>>BLOCK"
    result, err = apply_candidate_mutation(code, response, mutation_mode="full")
    assert err is None
    assert "x = 10" in result and "y = 20" in result

