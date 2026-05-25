from libreevolve.core.candidate import (
    CandidateWorkspace,
    apply_candidate_mutation,
    apply_workspace_mutation,
    extract_evolve_blocks,
    validate_evolve_blocks,
)


def test_extracts_named_evolve_blocks():
    code = "# header\n# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"
    blocks = extract_evolve_blocks(code)
    assert len(blocks) == 1
    assert blocks[0].name == "core"
    assert blocks[0].content == "x = 1"


def test_validates_anonymous_evolve_block_names():
    code = "# EVOLVE-BLOCK-START\nx = 1\n# EVOLVE-BLOCK-END\n"
    blocks = extract_evolve_blocks(code)
    assert validate_evolve_blocks(code) is None
    assert blocks[0].name == "block_0"


def test_rejects_missing_evolve_block_end_before_mutation():
    code = "keep = 1\n# EVOLVE-BLOCK-START core\nx = 1\n"
    diff = "<<<SEARCH\nkeep = 1\n===\nkeep = 2\n>>>REPLACE"
    result, err = apply_candidate_mutation(code, diff, mutation_mode="diff")
    assert result == code
    assert err == "malformed_evolve_blocks:missing_end"


def test_rejects_orphan_evolve_block_end_before_mutation():
    code = "keep = 1\n# EVOLVE-BLOCK-END\n"
    result, err = apply_candidate_mutation(code, "keep = 2", mutation_mode="full")
    assert result == code
    assert err == "malformed_evolve_blocks:orphan_end"


def test_rejects_nested_evolve_blocks_before_mutation():
    code = (
        "# EVOLVE-BLOCK-START outer\n"
        "x = 1\n"
        "# EVOLVE-BLOCK-START inner\n"
        "y = 2\n"
        "# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-END\n"
    )
    result, err = apply_candidate_mutation(code, "x = 3", mutation_mode="full")
    assert result == code
    assert err == "malformed_evolve_blocks:nested_start"


def test_rejects_duplicate_evolve_block_names_before_mutation():
    code = (
        "# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START core\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    result, err = apply_candidate_mutation(
        code,
        "<<<BLOCK core\nx = 3\n>>>BLOCK",
        mutation_mode="full",
    )
    assert result == code
    assert err == "malformed_evolve_blocks:duplicate_name"


def test_rejects_invalid_evolve_block_names_before_mutation():
    code = "# EVOLVE-BLOCK-START bad name\nx = 1\n# EVOLVE-BLOCK-END\n"
    result, err = apply_candidate_mutation(code, "x = 2", mutation_mode="full")
    assert result == code
    assert err == "malformed_evolve_blocks:invalid_name"


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


def test_full_mode_rejects_unclosed_block_section():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    response = "<<<BLOCK a\nx = 10\n>>>BLOCK\n<<<BLOCK b\ny = 20\n"
    result, err = apply_candidate_mutation(code, response, mutation_mode="full")
    assert result == code
    assert err == "malformed_block_sections:missing_end"


def test_full_mode_rejects_orphan_block_section_end():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    result, err = apply_candidate_mutation(code, ">>>BLOCK", mutation_mode="full")
    assert result == code
    assert err == "malformed_block_sections:orphan_end"


def test_full_mode_rejects_nested_block_sections():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    response = "<<<BLOCK a\nx = 10\n<<<BLOCK b\ny = 20\n>>>BLOCK\n>>>BLOCK"
    result, err = apply_candidate_mutation(code, response, mutation_mode="full")
    assert result == code
    assert err == "malformed_block_sections:nested_start"


def test_full_mode_rejects_empty_block_section_name():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    result, err = apply_candidate_mutation(
        code,
        "<<<BLOCK \nx = 10\n>>>BLOCK",
        mutation_mode="full",
    )
    assert result == code
    assert err == "malformed_block_sections:empty_name"


def test_full_mode_rejects_invalid_block_section_name():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    result, err = apply_candidate_mutation(
        code,
        "<<<BLOCK bad name\nx = 10\n>>>BLOCK",
        mutation_mode="full",
    )
    assert result == code
    assert err == "malformed_block_sections:invalid_name"


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


def test_workspace_file_section_accepts_hyphenated_paths():
    workspace = CandidateWorkspace(
        files={"main.py": "from my_module import value\n", "src/my-module.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE src/my-module.py\n<<<SEARCH\nvalue = 1\n===\nvalue = 2\n>>>REPLACE\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="diff")
    assert err is None
    assert result.files["src/my-module.py"].strip() == "value = 2"


def test_workspace_file_section_accepts_spaced_paths():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "data/test case.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE data/test case.py\nvalue = 2\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert err is None
    assert result.files["data/test case.py"] == "value = 2"


def test_workspace_file_section_normalizes_backslash_paths():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "pkg/helper.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE pkg\\helper.py\nvalue = 2\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert err is None
    assert result.files["pkg/helper.py"] == "value = 2"


def test_workspace_file_section_accepts_unicode_paths():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "src/cafe_é.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE src/cafe_é.py\nvalue = 2\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert err is None
    assert result.files["src/cafe_é.py"] == "value = 2"


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


def test_workspace_rejects_unclosed_file_section_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = (
        "<<<FILE helper.py\nvalue = 2\n>>>FILE\n"
        "<<<FILE extra.py\nvalue = 3\n"
    )
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "malformed_file_sections:missing_end"


def test_workspace_rejects_orphan_file_section_end():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = ">>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "malformed_file_sections:orphan_end"


def test_workspace_rejects_nested_file_sections_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE helper.py\nvalue = 2\n<<<FILE other.py\nvalue = 3\n>>>FILE\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "malformed_file_sections:nested_start"


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


def test_workspace_rejects_empty_file_section_path():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE \nvalue = 2\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "empty_path:unsafe_path"


def test_workspace_rejects_malformed_evolve_block_in_target_file():
    workspace = CandidateWorkspace(
        files={
            "main.py": "from helper import value\n",
            "helper.py": "# EVOLVE-BLOCK-START core\nvalue = 1\n",
        },
        primary_file="main.py",
    )
    response = "<<<FILE helper.py\nvalue = 2\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "helper.py:malformed_evolve_blocks:missing_end"
