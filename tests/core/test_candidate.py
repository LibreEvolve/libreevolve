from libreevolve.core.candidate import (
    CandidateWorkspace,
    apply_candidate_mutation,
    apply_workspace_mutation,
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


def test_diff_mode_accepts_canonical_block_inside_evolve_block():
    code = "keep = 1\n# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"
    diff = "<<<<<<< SEARCH\nx = 1\n=======\nx = 2\n>>>>>>> REPLACE"
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


def test_workspace_diff_mutates_named_file_only():
    workspace = CandidateWorkspace(
        files={"main.py": "from helper import value\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE helper.py\n<<<SEARCH\nvalue = 1\n===\nvalue = 2\n>>>REPLACE\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="diff")
    assert err is None
    assert result.files["main.py"] == workspace.files["main.py"]
    assert result.files["helper.py"].strip() == "value = 2"


def test_workspace_diff_accepts_canonical_block_in_file_section():
    workspace = CandidateWorkspace(
        files={"main.py": "from helper import value\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = (
        "<<<FILE helper.py\n"
        "<<<<<<< SEARCH\nvalue = 1\n=======\nvalue = 2\n>>>>>>> REPLACE\n"
        ">>>FILE"
    )
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="diff")
    assert err is None
    assert result.files["main.py"] == workspace.files["main.py"]
    assert result.files["helper.py"].strip() == "value = 2"


def test_workspace_full_mode_can_create_file():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE helper.py\nvalue = 2\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert err is None
    assert result.files["helper.py"] == "value = 2"


def test_workspace_rejects_path_escape():
    try:
        CandidateWorkspace(files={"../bad.py": "x = 1"}, primary_file="../bad.py")
    except ValueError as exc:
        assert "Unsafe candidate path" in str(exc)
    else:
        raise AssertionError("expected unsafe path rejection")


def test_workspace_rejects_windows_drive_path():
    try:
        CandidateWorkspace(files={"C:/bad.py": "x = 1"}, primary_file="C:/bad.py")
    except ValueError as exc:
        assert "Unsafe candidate path" in str(exc)
    else:
        raise AssertionError("expected unsafe path rejection")


def test_workspace_rejects_colon_path_component():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE pkg:bad.py\nvalue = 2\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "pkg:bad.py:unsafe_path"
