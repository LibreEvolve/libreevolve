import base64
import hashlib
import os
import subprocess

import pytest

from libreevolve.core.candidate import (
    CandidateMaterializationError,
    CandidateWorkspace,
    DEFAULT_MAX_CANDIDATE_FILE_CHARS,
    DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES,
    DEFAULT_MAX_CANDIDATE_TOTAL_CHARS,
    DEFAULT_MAX_CANDIDATE_TOTAL_STATIC_BYTES,
    DEFAULT_MAX_CANDIDATE_WORKSPACE_FILES,
    DEFAULT_MAX_MUTATION_PAYLOAD_CHARS,
    apply_candidate_mutation,
    apply_workspace_mutation,
    extract_evolve_blocks,
    normalize_candidate_path,
    validate_candidate_workspace_limits,
    validate_evolve_blocks,
    validate_workspace_evolve_blocks,
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


def test_accepts_whitespace_separated_evolve_block_name():
    code = "# EVOLVE-BLOCK-START\tcore\nx = 1\n# EVOLVE-BLOCK-END\n"
    blocks = extract_evolve_blocks(code)
    assert validate_evolve_blocks(code) is None
    assert blocks[0].name == "core"


def test_rejects_missing_evolve_block_end_before_mutation():
    code = "keep = 1\n# EVOLVE-BLOCK-START core\nx = 1\n"
    diff = "<<<SEARCH\nkeep = 1\n===\nkeep = 2\n>>>REPLACE"
    result, err = apply_candidate_mutation(code, diff, mutation_mode="diff")
    assert result == code
    assert err == "malformed_evolve_blocks:missing_end"


def test_candidate_mutation_rejects_non_text_payloads_before_parsing():
    code = "value = 1\n"

    for payload in (None, 7, ["bad"]):
        for mode in ("diff", "full"):
            result, err = apply_candidate_mutation(code, payload, mutation_mode=mode)
            assert result == code
            assert err == "non_text_mutation_payload"


def test_candidate_mutation_rejects_blank_payloads_before_parsing():
    code = "value = 1\n"

    for payload in ("", "   \n\t", "```python\n\n```"):
        for mode in ("diff", "full"):
            result, err = apply_candidate_mutation(code, payload, mutation_mode=mode)
            assert result == code
            assert err == "blank_mutation_payload"


def test_candidate_mutation_rejects_oversized_payloads_before_parsing():
    code = "value = 1\n"
    payload = "x" * (DEFAULT_MAX_MUTATION_PAYLOAD_CHARS + 1)

    for mode in ("diff", "full"):
        result, err = apply_candidate_mutation(code, payload, mutation_mode=mode)
        assert result == code
        assert err == "oversized_mutation_payload"


def test_workspace_mutation_rejects_non_text_payloads_before_parsing():
    workspace = CandidateWorkspace.from_code("value = 1\n")

    for payload in (None, 7, ["bad"]):
        for mode in ("diff", "full"):
            result, err = apply_workspace_mutation(workspace, payload, mutation_mode=mode)
            assert result is workspace
            assert err == "non_text_mutation_payload"


def test_workspace_mutation_rejects_blank_payloads_before_parsing():
    workspace = CandidateWorkspace.from_code("value = 1\n")

    for payload in ("", "   \n\t", "```python\n\n```"):
        for mode in ("diff", "full"):
            result, err = apply_workspace_mutation(workspace, payload, mutation_mode=mode)
            assert result is workspace
            assert err == "blank_mutation_payload"


def test_workspace_mutation_rejects_oversized_payloads_before_parsing():
    workspace = CandidateWorkspace.from_code("value = 1\n")
    payload = "x" * (DEFAULT_MAX_MUTATION_PAYLOAD_CHARS + 1)

    for mode in ("diff", "full"):
        result, err = apply_workspace_mutation(workspace, payload, mutation_mode=mode)
        assert result is workspace
        assert err == "oversized_mutation_payload"


def test_candidate_workspace_rejects_too_many_files():
    files = {
        f"f{i}.py": "x = 1\n"
        for i in range(DEFAULT_MAX_CANDIDATE_WORKSPACE_FILES + 1)
    }

    with pytest.raises(ValueError, match="max_candidate_workspace_files"):
        CandidateWorkspace(files=files, primary_file="f0.py")


def test_candidate_workspace_counts_static_files_against_member_budget():
    payload = b"x"
    static_files = [
        {
            "path": f"fixture{i}.bin",
            "kind": "binary",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "source_kind": "unknown",
            "mutation_policy": "immutable",
            "content_b64": base64.b64encode(payload).decode("ascii"),
        }
        for i in range(DEFAULT_MAX_CANDIDATE_WORKSPACE_FILES)
    ]

    with pytest.raises(ValueError, match="max_candidate_workspace_files"):
        CandidateWorkspace(
            files={"main.py": "x = 1\n"},
            primary_file="main.py",
            static_files=static_files,
        )


def test_candidate_workspace_rejects_oversized_file():
    code = "x" * (DEFAULT_MAX_CANDIDATE_FILE_CHARS + 1)

    with pytest.raises(ValueError, match="max_candidate_file_chars"):
        CandidateWorkspace.from_code(code)


def test_candidate_workspace_rejects_oversized_total_text():
    code = "x" * (DEFAULT_MAX_CANDIDATE_TOTAL_CHARS // 3 + 1)

    with pytest.raises(ValueError, match="max_candidate_total_chars"):
        CandidateWorkspace(
            files={"a.py": code, "b.py": code, "c.py": code},
            primary_file="a.py",
        )


def test_candidate_workspace_rejects_oversized_static_file_metadata():
    with pytest.raises(ValueError, match="max_candidate_static_file_bytes"):
        validate_candidate_workspace_limits(
            {"main.py": "x = 1\n"},
            static_files=[
                {
                    "path": "fixture.bin",
                    "kind": "binary",
                    "sha256": "a" * 64,
                    "bytes": DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES + 1,
                }
            ],
        )


def test_candidate_workspace_rejects_oversized_total_static_bytes():
    with pytest.raises(ValueError, match="max_candidate_total_static_bytes"):
        validate_candidate_workspace_limits(
            {"main.py": "x = 1\n"},
            static_files=[
                {
                    "path": "a.bin",
                    "kind": "binary",
                    "sha256": "a" * 64,
                    "bytes": DEFAULT_MAX_CANDIDATE_TOTAL_STATIC_BYTES // 2 + 1,
                },
                {
                    "path": "b.bin",
                    "kind": "binary",
                    "sha256": "b" * 64,
                    "bytes": DEFAULT_MAX_CANDIDATE_TOTAL_STATIC_BYTES // 2 + 1,
                },
            ],
            max_static_file_bytes=DEFAULT_MAX_CANDIDATE_TOTAL_STATIC_BYTES,
        )


def test_candidate_workspace_limit_helper_returns_size_policy():
    summary = validate_candidate_workspace_limits(
        {"main.py": "x = 1\n", "helper.py": "y = 2\n"},
        static_files=[
            {"path": "fixture.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 3}
        ],
        max_files=3,
        max_file_chars=10,
        max_total_chars=20,
        max_static_file_bytes=10,
        max_total_static_bytes=20,
    )

    assert summary == {
        "file_count": 3,
        "text_file_count": 2,
        "static_file_count": 1,
        "total_chars": 12,
        "total_static_bytes": 3,
        "largest_file": "main.py",
        "largest_file_chars": 6,
        "largest_static_file": "fixture.bin",
        "largest_static_file_bytes": 3,
        "max_files": 3,
        "max_file_chars": 10,
        "max_total_chars": 20,
        "max_static_file_bytes": 10,
        "max_total_static_bytes": 20,
        "policy": "reject_oversized_text_and_static_workspace",
    }


def test_workspace_mutation_rejects_oversized_created_file():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    payload = "<<<FILE new.py\n" + ("x" * (DEFAULT_MAX_CANDIDATE_FILE_CHARS + 1)) + "\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, payload, mutation_mode="full")

    assert result is workspace
    assert err is not None
    assert err.startswith("candidate_workspace_error:")
    assert "max_candidate_file_chars" in err


def test_workspace_validation_rejects_javascript_evolve_block_markers():
    files = {
        "script.js": (
            "function stable() { return 1; }\n"
            "// EVOLVE-BLOCK-START core\n"
            "function candidate() { return 1; }\n"
            "// EVOLVE-BLOCK-END\n"
        )
    }

    err = validate_workspace_evolve_blocks(files)

    assert err == "script.js:unsupported_evolve_block_marker_syntax"


def test_workspace_validation_rejects_text_file_evolve_block_markers():
    files = {
        "notes.txt": (
            "# EVOLVE-BLOCK-START core\n"
            "candidate body\n"
            "# EVOLVE-BLOCK-END\n"
        )
    }

    err = validate_workspace_evolve_blocks(files)

    assert err == "notes.txt:unsupported_evolve_block_marker_syntax"


def test_workspace_full_mode_rejects_unsupported_primary_markers_before_replacement():
    code = (
        "function stable() { return 1; }\n"
        "// EVOLVE-BLOCK-START core\n"
        "function candidate() { return 1; }\n"
        "// EVOLVE-BLOCK-END\n"
    )
    workspace = CandidateWorkspace(files={"script.js": code}, primary_file="script.js")

    result, err = apply_workspace_mutation(
        workspace,
        "function candidate() { return 2; }\n",
        mutation_mode="full",
    )

    assert result is workspace
    assert result.files["script.js"] == code
    assert err == "script.js:unsupported_evolve_block_marker_syntax"


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


def test_rejects_secret_like_evolve_block_names_before_mutation():
    name = "sk-proj_blocksecret_1234567890"  # pragma: allowlist secret
    code = f"# EVOLVE-BLOCK-START {name}\nx = 1\n# EVOLVE-BLOCK-END\n"

    assert extract_evolve_blocks(code) == []
    assert validate_evolve_blocks(code) == "unsafe_name"
    result, err = apply_candidate_mutation(code, "x = 2", mutation_mode="full")

    assert result == code
    assert err == "malformed_evolve_blocks:unsafe_name"


def test_rejects_format_control_evolve_block_names_before_mutation():
    code = "# EVOLVE-BLOCK-START core\u202e\nx = 1\n# EVOLVE-BLOCK-END\n"

    assert validate_evolve_blocks(code) == "unsafe_name"
    result, err = apply_candidate_mutation(code, "x = 2", mutation_mode="full")

    assert result == code
    assert err == "malformed_evolve_blocks:unsafe_name"


def test_rejects_ordinary_non_ascii_evolve_block_names_by_current_policy():
    code = "# EVOLVE-BLOCK-START café\nx = 1\n# EVOLVE-BLOCK-END\n"

    assert validate_evolve_blocks(code) == "invalid_name"
    result, err = apply_candidate_mutation(code, "x = 2", mutation_mode="full")

    assert result == code
    assert err == "malformed_evolve_blocks:invalid_name"


def test_full_mode_rejects_secret_like_block_section_names():
    name = "sk-proj_blocksectionsecret_1234567890"  # pragma: allowlist secret
    code = "# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"
    response = f"<<<BLOCK {name}\nx = 2\n>>>BLOCK"

    result, err = apply_candidate_mutation(code, response, mutation_mode="full")

    assert result == code
    assert err == "malformed_block_sections:unsafe_name"


def test_rejects_prefix_matched_evolve_block_start_markers():
    for marker in ("# EVOLVE-BLOCK-STARTED", "# EVOLVE-BLOCK-START_name"):
        code = f"{marker}\nx = 1\n# EVOLVE-BLOCK-END\n"
        result, err = apply_candidate_mutation(code, "x = 2", mutation_mode="full")
        assert result == code
        assert err == "malformed_evolve_blocks:invalid_start_marker"


def test_ignores_evolve_block_markers_inside_triple_quoted_string():
    code = (
        'template = """\n'
        "# EVOLVE-BLOCK-START literal\n"
        "string body\n"
        "# EVOLVE-BLOCK-END\n"
        '"""\n'
        "keep = 1\n"
    )
    diff = "<<<SEARCH\nkeep = 1\n===\nkeep = 2\n>>>REPLACE"

    assert extract_evolve_blocks(code) == []
    assert validate_evolve_blocks(code) is None
    result, err = apply_candidate_mutation(code, diff, mutation_mode="diff")

    assert err is None
    assert "keep = 2" in result
    assert "string body" in result


def test_full_mode_with_string_literal_markers_replaces_whole_candidate():
    code = (
        'template = """\n'
        "# EVOLVE-BLOCK-START literal\n"
        "string body\n"
        "# EVOLVE-BLOCK-END\n"
        '"""\n'
        "keep = 1\n"
    )

    result, err = apply_candidate_mutation(code, "replacement = True", mutation_mode="full")

    assert err is None
    assert result == "replacement = True"


def test_ignores_evolve_block_markers_inside_module_docstring():
    code = (
        '"""\n'
        "# EVOLVE-BLOCK-START literal\n"
        "documentation\n"
        "# EVOLVE-BLOCK-END\n"
        '"""\n'
        "value = 1\n"
    )

    assert extract_evolve_blocks(code) == []
    assert validate_evolve_blocks(code) is None


def test_evolve_block_markers_fail_closed_after_tokenizer_error():
    code = (
        'template = """unterminated\n'
        "# EVOLVE-BLOCK-START core\n"
        "x = 1\n"
        "# EVOLVE-BLOCK-END\n"
        "keep = 1\n"
    )

    assert extract_evolve_blocks(code) == []
    assert validate_evolve_blocks(code) == "tokenize_error"

    result, err = apply_candidate_mutation(code, "replacement = True", mutation_mode="full")
    assert result == code
    assert err == "malformed_evolve_blocks:tokenize_error"


def test_evolve_block_markers_fail_closed_after_indentation_error():
    code = (
        "if True:\n"
        "    x = 1\n"
        "  y = 2\n"
        "# EVOLVE-BLOCK-START core\n"
        "z = 3\n"
        "# EVOLVE-BLOCK-END\n"
    )

    assert extract_evolve_blocks(code) == []
    assert validate_evolve_blocks(code) == "tokenize_error"

    result, err = apply_candidate_mutation(code, "replacement = True", mutation_mode="full")
    assert result == code
    assert err == "malformed_evolve_blocks:tokenize_error"


def test_diff_mode_rejects_tokenizer_error_before_marker_lines():
    code = (
        'template = """unterminated\n'
        "# EVOLVE-BLOCK-START core\n"
        "x = 1\n"
        "# EVOLVE-BLOCK-END\n"
        "keep = 1\n"
    )
    diff = "<<<SEARCH\nkeep = 1\n===\nkeep = 2\n>>>REPLACE"

    result, err = apply_candidate_mutation(code, diff, mutation_mode="diff")

    assert result == code
    assert err == "malformed_evolve_blocks:tokenize_error"


def test_tokenizer_error_without_raw_marker_lines_remains_unmarked():
    code = 'template = """unterminated\nkeep = 1\n'

    assert validate_evolve_blocks(code) is None
    result, err = apply_candidate_mutation(code, "replacement = True", mutation_mode="full")

    assert err is None
    assert result == "replacement = True"


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


def test_diff_mode_matches_lf_patch_inside_crlf_evolve_block():
    code = (
        "keep = 1\r\n"
        "# EVOLVE-BLOCK-START core\r\n"
        "x = 1\r\n"
        "y = 2\r\n"
        "# EVOLVE-BLOCK-END\r\n"
    )
    diff = "<<<SEARCH\nx = 1\ny = 2\n===\nx = 10\ny = 20\n>>>REPLACE"

    result, err = apply_candidate_mutation(code, diff, mutation_mode="diff")

    assert err is None
    assert result == (
        "keep = 1\r\n"
        "# EVOLVE-BLOCK-START core\r\n"
        "x = 10\r\n"
        "y = 20\r\n"
        "# EVOLVE-BLOCK-END\r\n"
    )


def test_diff_mode_rejects_skeleton_edit_when_blocks_exist():
    code = "keep = 1\n# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"
    diff = "<<<SEARCH\nkeep = 1\n===\nkeep = 2\n>>>REPLACE"
    result, err = apply_candidate_mutation(code, diff, mutation_mode="diff")
    assert result == code
    assert err == "search_not_found"


def test_diff_mode_rejects_ambiguous_match_inside_evolve_block():
    code = (
        "# EVOLVE-BLOCK-START core\n"
        "x = 1\n"
        "x = 1\n"
        "# EVOLVE-BLOCK-END\n"
    )
    diff = "<<<SEARCH\nx = 1\n===\nx = 2\n>>>REPLACE"

    result, err = apply_candidate_mutation(code, diff, mutation_mode="diff")

    assert result == code
    assert err == "ambiguous_search_match"


def test_diff_mode_rejects_ambiguous_match_across_evolve_blocks():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\nx = 1\n# EVOLVE-BLOCK-END\n"
    )
    diff = "<<<SEARCH\nx = 1\n===\nx = 2\n>>>REPLACE"

    result, err = apply_candidate_mutation(code, diff, mutation_mode="diff")

    assert result == code
    assert err == "ambiguous_search_match"


def test_full_mode_replaces_single_evolve_block_only():
    code = "keep = 1\n# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"
    result, err = apply_candidate_mutation(code, "x = 9", mutation_mode="full")
    assert err is None
    assert "keep = 1" in result
    assert "x = 9" in result
    assert "x = 1" not in result


def test_full_mode_accepts_named_block_section_for_single_evolve_block():
    code = "keep = 1\n# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"
    response = "<<<BLOCK core\nx = 2\n>>>BLOCK"

    result, err = apply_candidate_mutation(code, response, mutation_mode="full")

    assert err is None
    assert result == "keep = 1\n# EVOLVE-BLOCK-START core\nx = 2\n# EVOLVE-BLOCK-END\n"


def test_full_mode_rejects_unknown_named_block_section_for_single_evolve_block():
    code = "keep = 1\n# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"
    response = "<<<BLOCK other\nx = 2\n>>>BLOCK"

    result, err = apply_candidate_mutation(code, response, mutation_mode="full")

    assert result == code
    assert err == "malformed_block_sections:unknown_name"


def test_full_mode_preserves_single_file_trailing_newlines():
    code = "x = 1"

    result, err = apply_candidate_mutation(code, "x = 2\n\n", mutation_mode="full")

    assert err is None
    assert result == "x = 2\n\n"


def test_full_mode_strips_only_outer_markdown_wrapper():
    result, err = apply_candidate_mutation(
        "x = 1\n",
        "```python\nx = 2\n```",
        mutation_mode="full",
    )

    assert err is None
    assert result == "x = 2\n"


def test_full_mode_preserves_markdown_fence_literal_in_replacement():
    response = "DOC = '''```python\nprint(1)\n```'''\n"

    result, err = apply_candidate_mutation("DOC = ''\n", response, mutation_mode="full")

    assert err is None
    assert result == response


def test_full_mode_preserves_marker_like_literals_in_whole_file_replacement():
    response = (
        'FILE_START = "<<<FILE not a section"\n'
        'FILE_END = ">>>FILE not an end"\n'
        'BLOCK_START = "<<<BLOCK not a section"\n'
        'BLOCK_END = ">>>BLOCK not an end"\n'
    )

    result, err = apply_candidate_mutation("x = 1\n", response, mutation_mode="full")

    assert err is None
    assert result == response


def test_full_mode_preserves_single_evolve_block_trailing_newline():
    code = "keep = 1\n# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"

    result, err = apply_candidate_mutation(code, "x = 9\n", mutation_mode="full")

    assert err is None
    assert result == "keep = 1\n# EVOLVE-BLOCK-START core\nx = 9\n\n# EVOLVE-BLOCK-END\n"


def test_full_mode_replaces_multiple_named_blocks():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    response = "<<<BLOCK a\nx = 10\n>>>BLOCK\n<<<BLOCK b\ny = 20\n>>>BLOCK"
    result, err = apply_candidate_mutation(code, response, mutation_mode="full")
    assert err is None
    assert "x = 10" in result and "y = 20" in result


def test_full_mode_preserves_markdown_fence_literal_in_block_section():
    code = "# EVOLVE-BLOCK-START core\nDOC = ''\n# EVOLVE-BLOCK-END\n"
    response = "<<<BLOCK core\nDOC = '''```python\nprint(1)\n```'''\n>>>BLOCK"

    result, err = apply_candidate_mutation(code, response, mutation_mode="full")

    assert err is None
    assert "DOC = '''```python\nprint(1)\n```'''\n# EVOLVE-BLOCK-END" in result


def test_full_mode_preserves_marker_like_literals_in_block_section():
    code = "# EVOLVE-BLOCK-START core\nTEXT = ''\n# EVOLVE-BLOCK-END\n"
    response = (
        "<<<BLOCK core\n"
        'FILE_START = "<<<FILE not a section"\n'
        'FILE_END = ">>>FILE not an end"\n'
        'BLOCK_START = "<<<BLOCK not a section"\n'
        'BLOCK_END = ">>>BLOCK not an end"\n'
        ">>>BLOCK"
    )

    result, err = apply_candidate_mutation(code, response, mutation_mode="full")

    assert err is None
    assert 'FILE_START = "<<<FILE not a section"\n' in result
    assert 'FILE_END = ">>>FILE not an end"\n' in result
    assert 'BLOCK_START = "<<<BLOCK not a section"\n' in result
    assert 'BLOCK_END = ">>>BLOCK not an end"\n' in result


def test_full_mode_preserves_multi_block_trailing_newlines():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    response = "<<<BLOCK a\nx = 10\n\n>>>BLOCK\n<<<BLOCK b\ny = 20\n>>>BLOCK"

    result, err = apply_candidate_mutation(code, response, mutation_mode="full")

    assert err is None
    assert "x = 10\n\n# EVOLVE-BLOCK-END" in result
    assert "y = 20\n# EVOLVE-BLOCK-END" in result


def test_full_mode_allows_explanatory_preamble_before_block_sections():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    response = "Here is the patch:\n<<<BLOCK a\nx = 10\n>>>BLOCK"

    result, err = apply_candidate_mutation(code, response, mutation_mode="full")

    assert err is None
    assert "x = 10\n# EVOLVE-BLOCK-END" in result
    assert "y = 2\n# EVOLVE-BLOCK-END" in result


def test_full_mode_rejects_trailing_prose_around_block_sections():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    response = "<<<BLOCK a\nx = 10\n>>>BLOCK\nThis is why it works."

    result, err = apply_candidate_mutation(code, response, mutation_mode="full")

    assert result == code
    assert err == "malformed_block_sections:unconsumed_text"


def test_full_mode_rejects_stray_diff_around_block_sections():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    response = (
        "<<<BLOCK a\nx = 10\n>>>BLOCK\n"
        "<<<SEARCH\nz = 1\n===\nz = 2\n>>>REPLACE"
    )

    result, err = apply_candidate_mutation(code, response, mutation_mode="full")

    assert result == code
    assert err == "malformed_block_sections:unconsumed_text"


def test_full_mode_allows_proposal_metadata_around_block_sections():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    response = (
        "IDEA: update a\n"
        "<<<BLOCK a\nx = 10\n>>>BLOCK\n"
        "RATIONALE: bounded change"
    )

    result, err = apply_candidate_mutation(code, response, mutation_mode="full")

    assert err is None
    assert "x = 10" in result
    assert "y = 2" in result


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


def test_full_mode_rejects_duplicate_block_section_names():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    response = (
        "<<<BLOCK a\nx = 10\n>>>BLOCK\n"
        "<<<BLOCK a\nx = 20\n>>>BLOCK\n"
        "<<<BLOCK b\ny = 30\n>>>BLOCK"
    )
    result, err = apply_candidate_mutation(code, response, mutation_mode="full")
    assert result == code
    assert err == "malformed_block_sections:duplicate_name"


def test_full_mode_rejects_unknown_block_section_name():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )

    result, err = apply_candidate_mutation(
        code,
        "<<<BLOCK c\nz = 3\n>>>BLOCK",
        mutation_mode="full",
    )

    assert result == code
    assert err == "malformed_block_sections:unknown_name"


def test_full_mode_rejects_mixed_known_and_unknown_block_sections_without_partial_apply():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )
    response = (
        "<<<BLOCK a\nx = 10\n>>>BLOCK\n"
        "<<<BLOCK c\nz = 30\n>>>BLOCK"
    )

    result, err = apply_candidate_mutation(code, response, mutation_mode="full")

    assert result == code
    assert err == "malformed_block_sections:unknown_name"


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
    assert result.files["data/test case.py"] == "value = 2\n"


def test_workspace_file_section_normalizes_backslash_paths():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "pkg/helper.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE pkg\\helper.py\nvalue = 2\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert err is None
    assert result.files["pkg/helper.py"] == "value = 2\n"


def test_workspace_file_section_accepts_unicode_paths():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "src/cafe_é.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE src/cafe_é.py\nvalue = 2\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert err is None
    assert result.files["src/cafe_é.py"] == "value = 2\n"


def test_candidate_mutation_rejects_non_utf8_full_replacement():
    result, err = apply_candidate_mutation(
        "x = 1\n",
        "x = '\ud800'\n",
        mutation_mode="full",
    )

    assert result == "x = 1\n"
    assert err == "non_utf8_content"


def test_workspace_mutation_rejects_non_utf8_new_file_without_partial_apply():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE bad.py\nx = '\ud800'\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "bad.py:non_utf8_content"


def test_candidate_paths_normalize_unicode_to_nfc():
    assert normalize_candidate_path("src/cafe\u0301.py") == "src/café.py"


def test_candidate_paths_reject_ambiguous_empty_and_dot_components():
    ambiguous_paths = [
        "",
        ".",
        "./main.py",
        "pkg/./mod.py",
        "pkg//mod.py",
        "a///b.py",
        "pkg/mod.py/",
    ]
    for path in ambiguous_paths:
        try:
            normalize_candidate_path(path)
        except ValueError as exc:
            assert "Unsafe candidate path" in str(exc)
        else:
            raise AssertionError(f"expected ambiguous path rejection for {path!r}")


def test_candidate_paths_reject_posix_absolute_inputs():
    for path in (
        "/abs.py",
        "//pkg/mod.py",
        "\\abs.py",
        "\\\\server\\share.py",
        "C:/drive.py",
        "C:\\drive.py",
        "pkg/../escape.py",
        "pkg\\..\\escape.py",
    ):
        try:
            normalize_candidate_path(path)
        except ValueError as exc:
            assert "Unsafe candidate path" in str(exc)
        else:
            raise AssertionError(f"expected unsafe path rejection for {path!r}")


def test_candidate_paths_reject_control_and_host_invalid_components():
    unsafe_paths = [
        "bad\nname.py",
        "bad\tname.py",
        "bad\x7fname.py",
        "bad\u202ename.py",
        "bad\u200dname.py",
        "bad?.py",
        "bad*.py",
        "bad<name>.py",
        'bad"name.py',
        "bad|name.py",
        " leading-space.py",
        "trailing-space.py ",
        "trailing-dot.",
        "CON",
        "con.txt",
        "pkg/NUL.py",
        "COM1",
        "LPT9.log",
    ]
    for path in unsafe_paths:
        try:
            normalize_candidate_path(path)
        except ValueError as exc:
            assert "Unsafe candidate path" in str(exc)
        else:
            raise AssertionError(f"expected unsafe path rejection for {path!r}")


def test_workspace_rejects_unicode_equivalent_paths_after_normalization():
    try:
        CandidateWorkspace(
            files={"src/café.py": "value = 1\n", "src/cafe\u0301.py": "value = 2\n"},
            primary_file="src/café.py",
        )
    except ValueError as exc:
        assert "Duplicate candidate path after normalization" in str(exc)
    else:
        raise AssertionError("expected Unicode-normalized duplicate path rejection")


def test_candidate_paths_accept_ordinary_non_ascii_nfc_names():
    path = "src/café.py"

    workspace = CandidateWorkspace(files={path: "value = 1\n"}, primary_file=path)

    assert workspace.primary_file == path
    assert workspace.files == {path: "value = 1\n"}


def test_candidate_paths_reject_nfkc_unstable_labels():
    unsafe_paths = [
        "safe\u00a0name.py",
        "safe\u2007name.py",
        "safe\u202fname.py",
        "safe\u3000name.py",
        "\uff21.py",
        "\u212a.py",
    ]
    for path in unsafe_paths:
        try:
            normalize_candidate_path(path)
        except ValueError as exc:
            assert "compatibility-normalized" in str(exc)
        else:
            raise AssertionError(f"expected NFKC-unstable path rejection for {path!r}")


def test_candidate_paths_reject_surrogate_code_points():
    path = "bad\ud800.py"

    try:
        normalize_candidate_path(path)
    except ValueError as exc:
        assert "Unsafe candidate path" in str(exc)
    else:
        raise AssertionError("expected surrogate path rejection")


def test_candidate_paths_reject_hidden_components():
    hidden_paths = [".env", ".git/config", "pkg/.hidden.py", "pkg/.well-known/config.py"]
    for path in hidden_paths:
        try:
            normalize_candidate_path(path)
        except ValueError as exc:
            assert "Unsafe candidate path" in str(exc)
        else:
            raise AssertionError(f"expected hidden path rejection for {path!r}")


def test_workspace_rejects_hidden_direct_workspace_paths():
    try:
        CandidateWorkspace(files={".env": "TOKEN=secret\n"}, primary_file=".env")
    except ValueError as exc:
        assert "Unsafe candidate path" in str(exc)
    else:
        raise AssertionError("expected hidden workspace path rejection")


def test_workspace_allows_explicit_reserved_seed_paths(tmp_path):
    workspace = CandidateWorkspace(
        files={".config.py": "VALUE = 1\n", "__pycache__/cached.py": "VALUE = 2\n"},
        primary_file=".config.py",
        allowed_reserved_paths=frozenset({".config.py", "__pycache__/cached.py"}),
    )

    primary_path = workspace.materialize(tmp_path / "candidate")

    assert workspace.allowed_reserved_paths == frozenset({".config.py", "__pycache__/cached.py"})
    assert primary_path.name == ".config.py"
    assert (tmp_path / "candidate" / "__pycache__" / "cached.py").read_text(encoding="utf-8") == "VALUE = 2\n"


def test_workspace_materializes_text_as_exact_utf8_bytes(tmp_path):
    content = "first\nsecond\r\nthird\r"
    workspace = CandidateWorkspace(files={"main.txt": content}, primary_file="main.txt")

    primary_path = workspace.materialize(tmp_path / "candidate")

    assert primary_path.read_bytes() == content.encode("utf-8")


def test_workspace_mutation_preserves_reserved_allowlist_without_broadening_it():
    workspace = CandidateWorkspace(
        files={".config.py": "VALUE = 1\n", "main.py": "VALUE = 0\n"},
        primary_file="main.py",
        allowed_reserved_paths=frozenset({".config.py"}),
    )
    response = "<<<FILE .config.py\nVALUE = 2\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.files[".config.py"] == "VALUE = 2\n"
    assert result.allowed_reserved_paths == frozenset({".config.py"})

    result, err = apply_workspace_mutation(
        result,
        "<<<FILE .env\nTOKEN = 'x'\n>>>FILE",
        mutation_mode="full",
    )

    assert result.files[".config.py"] == "VALUE = 2\n"
    assert err == ".env:unsafe_path"


def test_workspace_record_rejects_mapping_reserved_allowlist():
    try:
        CandidateWorkspace.from_dict(
            {
                "files": {".config.py": "VALUE = 1\n"},
                "primary_file": ".config.py",
                "allowed_reserved_paths": {".config.py": True},
            }
        )
    except ValueError as exc:
        assert "allowed_reserved_paths must be a list of paths" in str(exc)
    else:
        raise AssertionError("expected mapping allowlist rejection")


def test_candidate_paths_reject_secret_like_labels_without_echoing_value():
    path = "api_key=sk-proj_candidatepathsecret1234567890.py"  # pragma: allowlist secret

    try:
        normalize_candidate_path(path)
    except ValueError as exc:
        assert "secret-like text" in str(exc)
        assert "sk-proj_candidatepathsecret" not in str(exc)
    else:
        raise AssertionError("expected secret-like candidate path rejection")


def test_workspace_rejects_secret_like_direct_workspace_paths():
    path = "api_key=sk-proj_workspacepathsecret1234567890.py"  # pragma: allowlist secret

    try:
        CandidateWorkspace(files={path: "x = 1\n"}, primary_file=path)
    except ValueError as exc:
        assert "secret-like text" in str(exc)
        assert "sk-proj_workspacepathsecret" not in str(exc)
    else:
        raise AssertionError("expected secret-like workspace path rejection")


def test_candidate_paths_reject_pycache_components():
    cache_paths = [
        "__pycache__/cached.py",
        "pkg/__pycache__/cached.py",
        "pkg/__pycache__",
    ]
    for path in cache_paths:
        try:
            normalize_candidate_path(path)
        except ValueError as exc:
            assert "Unsafe candidate path" in str(exc)
        else:
            raise AssertionError(f"expected __pycache__ path rejection for {path!r}")


def test_workspace_rejects_pycache_direct_workspace_paths():
    try:
        CandidateWorkspace(
            files={"__pycache__/cached.py": "x = 1\n"},
            primary_file="__pycache__/cached.py",
        )
    except ValueError as exc:
        assert "Unsafe candidate path" in str(exc)
    else:
        raise AssertionError("expected __pycache__ workspace path rejection")


def test_workspace_mutation_rejects_pycache_file_sections():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE __pycache__/ghost.py\nx = 2\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "__pycache__/ghost.py:unsafe_path"


def test_workspace_mutation_rejects_secret_like_created_file_sections_without_leak():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE api_key=sk-proj_mutationpathsecret1234567890.py\nx = 2\n>>>FILE"  # pragma: allowlist secret

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "secret_like_path:unsafe_path"


def test_workspace_mutation_rejects_secret_like_move_targets_without_leak():
    workspace = CandidateWorkspace(files={"old.py": "x = 1\n"}, primary_file="old.py")
    response = "<<<FILE MOVE old.py -> api_key=sk-proj_movetargetsecret1234567890.py\n>>>FILE"  # pragma: allowlist secret

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "secret_like_path:unsafe_path"


def test_candidate_paths_reject_overlong_components_and_total_paths():
    long_component = "a" * 256
    long_total = "/".join(["segment"] * 147)
    for path in (f"{long_component}.py", long_total):
        try:
            normalize_candidate_path(path)
        except ValueError as exc:
            assert "Unsafe candidate path" in str(exc)
        else:
            raise AssertionError(f"expected overlong path rejection for {path!r}")


def test_candidate_paths_accept_component_at_length_limit():
    component = "a" * 252 + ".py"
    assert normalize_candidate_path(component) == component


def test_workspace_rejects_overlong_direct_workspace_paths():
    path = f"{'a' * 256}.py"
    try:
        CandidateWorkspace(files={path: "x = 1\n"}, primary_file=path)
    except ValueError as exc:
        assert "Unsafe candidate path" in str(exc)
    else:
        raise AssertionError("expected overlong workspace path rejection")


def test_workspace_rejects_missing_primary_file():
    try:
        CandidateWorkspace(files={"helper.py": "value = 1\n"}, primary_file="missing.py")
    except ValueError as exc:
        assert "Primary file 'missing.py' is not present" in str(exc)
    else:
        raise AssertionError("expected missing primary file rejection")


def test_empty_workspace_default_creates_primary_file():
    workspace = CandidateWorkspace()
    assert workspace.primary_file == "main.py"
    assert workspace.files == {"main.py": ""}


def test_workspace_rejects_non_mapping_files():
    try:
        CandidateWorkspace(files=[("main.py", "x = 1\n")], primary_file="main.py")
    except ValueError as exc:
        assert "files must be a mapping" in str(exc)
    else:
        raise AssertionError("expected non-mapping files rejection")


def test_workspace_rejects_non_string_file_paths_and_contents():
    try:
        CandidateWorkspace(files={1: "x = 1\n"}, primary_file="main.py")
    except ValueError as exc:
        assert "file paths must be strings" in str(exc)
    else:
        raise AssertionError("expected non-string path rejection")

    try:
        CandidateWorkspace(files={"main.py": 123}, primary_file="main.py")
    except ValueError as exc:
        assert "file content must be a string or bytes" in str(exc)
    else:
        raise AssertionError("expected non-string content rejection")


def test_workspace_rejects_non_utf8_encodable_contents():
    try:
        CandidateWorkspace(files={"bad.py": "x = '\ud800'\n"}, primary_file="bad.py")
    except ValueError as exc:
        assert "file content must be UTF-8 encodable" in str(exc)
    else:
        raise AssertionError("expected non-UTF-8-encodable content rejection")


def test_workspace_rejects_non_string_primary_file():
    try:
        CandidateWorkspace(files={"main.py": "x = 1\n"}, primary_file=1)
    except ValueError as exc:
        assert "primary_file must be a string" in str(exc)
    else:
        raise AssertionError("expected non-string primary rejection")


def test_workspace_static_files_round_trip_typed_metadata():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {
                "path": "fixtures/input.bin",
                "kind": "binary",
                "sha256": "A" * 64,
                "bytes": 3,
            }
        ],
    )

    assert workspace.static_files == (
        {
            "path": "fixtures/input.bin",
            "kind": "binary",
            "sha256": "a" * 64,
            "bytes": 3,
            "source_kind": "unknown",
            "mutation_policy": "immutable",
        },
    )
    assert CandidateWorkspace.from_dict(workspace.to_dict()).static_files == workspace.static_files


def test_workspace_raw_binary_file_content_becomes_static_member(tmp_path):
    payload = b"\xff\x00raw fixture"
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "fixtures/input.bin": payload},
        primary_file="main.py",
    )

    assert workspace.files == {"main.py": "x = 1\n"}
    assert workspace.static_files == (
        {
            "path": "fixtures/input.bin",
            "kind": "binary",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "source_kind": "direct_workspace_record",
            "mutation_policy": "immutable",
            "content_b64": base64.b64encode(payload).decode("ascii"),
        },
    )
    assert CandidateWorkspace.from_dict(workspace.to_dict()).static_files == (
        workspace.static_files
    )

    workspace.materialize(tmp_path / "candidate")

    assert (tmp_path / "candidate" / "main.py").read_text(encoding="utf-8") == "x = 1\n"
    assert (tmp_path / "candidate" / "fixtures" / "input.bin").read_bytes() == payload


def test_workspace_rejects_raw_binary_primary_file():
    with pytest.raises(ValueError, match="primary_file cannot be a binary member"):
        CandidateWorkspace(files={"main.py": b"\x00"}, primary_file="main.py")


def test_workspace_rejects_raw_binary_duplicate_static_path():
    payload = b"\x00fixture"
    with pytest.raises(ValueError, match="Duplicate candidate static file path"):
        CandidateWorkspace(
            files={"main.py": "x = 1\n", "fixture.bin": payload},
            primary_file="main.py",
            static_files=[
                {
                    "path": "fixture.bin",
                    "kind": "binary",
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "bytes": len(payload),
                }
            ],
        )


def test_workspace_materializes_encoded_static_file_content(tmp_path):
    payload = b"\xff\x00fixture"
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {
                "path": "fixtures/input.bin",
                "kind": "binary",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "source_kind": "unknown",
                "mutation_policy": "immutable",
                "content_b64": base64.b64encode(payload).decode("ascii"),
            }
        ],
    )

    workspace.materialize(tmp_path / "candidate")

    assert (tmp_path / "candidate" / "fixtures" / "input.bin").read_bytes() == payload


def test_workspace_materializes_source_copy_static_file_content(tmp_path):
    payload = b"\xff\x00external fixture"
    source = tmp_path / "external.bin"
    source.write_bytes(payload)
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {
                "path": "fixtures/input.bin",
                "kind": "binary",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "source_kind": "copied_static_asset",
                "source_path": "fixtures/input.bin",
                "source_copy_path": str(source),
                "mutation_policy": "immutable",
            }
        ],
    )

    workspace.materialize(tmp_path / "candidate")

    assert (tmp_path / "candidate" / "fixtures" / "input.bin").read_bytes() == payload
    assert workspace.static_files[0]["source_copy_path"] == str(source)
    assert "content_b64" not in workspace.static_files[0]


def test_workspace_rejects_source_copy_static_file_hash_mismatch(tmp_path):
    source = tmp_path / "external.bin"
    source.write_bytes(b"actual")
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {
                "path": "fixtures/input.bin",
                "kind": "binary",
                "sha256": hashlib.sha256(b"expected").hexdigest(),
                "bytes": len(b"actual"),
                "source_kind": "copied_static_asset",
                "source_copy_path": str(source),
            }
        ],
    )

    with pytest.raises(
        CandidateMaterializationError,
        match="source_copy_path sha256 does not match",
    ) as excinfo:
        workspace.materialize(tmp_path / "candidate")
    assert excinfo.value.reason == "static_source_copy_sha256_mismatch"
    assert excinfo.value.paths == ("fixtures/input.bin", str(source))


@pytest.mark.parametrize(
    ("static_files", "message"),
    [
        ({"path": "fixtures/input.bin"}, "static_files must be a list"),
        ([["not", "mapping"]], "static_files\\[0\\] must be a mapping"),
        ([{"path": 1, "kind": "binary", "sha256": "a" * 64, "bytes": 1}], "path must be a string"),
        ([{"path": "../bad.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 1}], "Unsafe candidate path"),
        ([{"path": "data.bin", "kind": "other", "sha256": "a" * 64, "bytes": 1}], "kind must be one of"),
        ([{"path": "data.bin", "kind": "binary", "sha256": "bad", "bytes": 1}], "64 hex characters"),
        ([{"path": "data.bin", "kind": "binary", "sha256": "a" * 64, "bytes": -1}], "non-negative integer"),
        ([{"path": "data.bin", "kind": "binary", "sha256": "a" * 64, "bytes": True}], "non-negative integer"),
        ([{"path": "data.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 1, "content_b64": 1}], "content_b64 must be a string"),
        ([{"path": "data.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 1, "content_b64": "not base64"}], "valid base64"),
        ([{"path": "data.bin", "kind": "binary", "sha256": hashlib.sha256(b'x').hexdigest(), "bytes": 2, "content_b64": base64.b64encode(b'x').decode("ascii")}], "byte count does not match"),
        ([{"path": "data.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 1, "content_b64": base64.b64encode(b'x').decode("ascii")}], "sha256 does not match"),
        ([{"path": "data.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 1, "source_kind": "outside"}], "source_kind must be one of"),
        ([{"path": "data.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 1, "mutation_policy": "mutable"}], "mutation_policy must be one of"),
        ([{"path": "data.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 1, "source_path": "api_key=sk-proj_static_source_secret_1234567890"}], "source_path must not contain secret-like text"),  # pragma: allowlist secret
        ([{"path": "data.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 1, "source_copy_path": "api_key=sk-proj_static_source_secret_1234567890"}], "source_copy_path must not contain secret-like text"),  # pragma: allowlist secret
    ],
)
def test_workspace_rejects_invalid_static_file_metadata(static_files, message):
    with pytest.raises(ValueError, match=message):
        CandidateWorkspace(
            files={"main.py": "x = 1\n"},
            primary_file="main.py",
            static_files=static_files,
        )


def test_workspace_rejects_static_files_that_collide_with_text_files():
    with pytest.raises(ValueError, match="collides with text file"):
        CandidateWorkspace(
            files={"main.py": "x = 1\n"},
            primary_file="main.py",
            static_files=[
                {"path": "main.py", "kind": "static", "sha256": "a" * 64, "bytes": 1}
            ],
        )

    with pytest.raises(ValueError, match="Duplicate candidate static file path"):
        CandidateWorkspace(
            files={"main.py": "x = 1\n"},
            primary_file="main.py",
            static_files=[
                {"path": "fixture.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 1},
                {"path": "fixture.bin", "kind": "binary", "sha256": "b" * 64, "bytes": 2},
            ],
        )


def test_workspace_mutation_preserves_static_file_metadata():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {"path": "fixture.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 1}
        ],
    )

    mutated, error = apply_workspace_mutation(
        workspace,
        "<<<SEARCH\nx = 1\n===\nx = 2\n>>>REPLACE",
    )

    assert error is None
    assert mutated.files["main.py"] == "x = 2\n"
    assert mutated.static_files == workspace.static_files


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        ("<<<FILE fixture.bin\nnew text\n>>>FILE", "fixture.bin:static_member_immutable"),
        ("<<<FILE DELETE fixture.bin\n>>>FILE", "fixture.bin:static_member_immutable"),
        (
            "<<<FILE MOVE helper.py -> fixture.bin\n>>>FILE",
            "fixture.bin:static_member_immutable",
        ),
    ],
)
def test_workspace_rejects_mutations_targeting_immutable_static_members(response, expected):
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
        static_files=[
            {"path": "fixture.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 1}
        ],
    )

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result is workspace
    assert err == expected


def test_workspace_rejects_text_mutation_targeting_llm_editable_static_member():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {
                "path": "fixture.bin",
                "kind": "binary",
                "sha256": "a" * 64,
                "bytes": 1,
                "mutation_policy": "llm_editable",
            }
        ],
    )

    result, err = apply_workspace_mutation(
        workspace,
        "<<<FILE fixture.bin\nnew text\n>>>FILE",
        mutation_mode="full",
    )

    assert result is workspace
    assert err == "fixture.bin:static_member_llm_editing_not_supported"


def test_workspace_replaces_llm_editable_static_member_with_file_static_section(tmp_path):
    old_payload = b"old"
    new_payload = b"new bytes"
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {
                "path": "fixture.bin",
                "kind": "binary",
                "sha256": hashlib.sha256(old_payload).hexdigest(),
                "bytes": len(old_payload),
                "source_kind": "seed_workspace_file",
                "source_path": "initial_programs/fixture.bin",
                "mutation_policy": "llm_editable",
                "content_b64": base64.b64encode(old_payload).decode("ascii"),
            }
        ],
    )
    response = (
        "<<<FILE STATIC fixture.bin\n"
        f"{base64.b64encode(new_payload).decode('ascii')}\n"
        ">>>FILE"
    )

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.files == workspace.files
    assert result.static_files == (
        {
            "path": "fixture.bin",
            "kind": "binary",
            "sha256": hashlib.sha256(new_payload).hexdigest(),
            "bytes": len(new_payload),
            "source_kind": "generated_artifact",
            "mutation_policy": "llm_editable",
            "content_b64": base64.b64encode(new_payload).decode("ascii"),
        },
    )
    result.materialize(tmp_path)
    assert (tmp_path / "fixture.bin").read_bytes() == new_payload


def test_workspace_rejects_static_replace_for_immutable_static_member():
    payload = b"old"
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {
                "path": "fixture.bin",
                "kind": "binary",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "mutation_policy": "immutable",
                "content_b64": base64.b64encode(payload).decode("ascii"),
            }
        ],
    )

    result, err = apply_workspace_mutation(
        workspace,
        "<<<FILE STATIC fixture.bin\nbmV3\n>>>FILE",
        mutation_mode="full",
    )

    assert result is workspace
    assert err == "fixture.bin:static_member_immutable"


def test_workspace_creates_generated_static_member_with_file_static_section(tmp_path):
    payload = b"new static"
    workspace = CandidateWorkspace.from_code("x = 1\n")

    result, err = apply_workspace_mutation(
        workspace,
        "<<<FILE STATIC fixture.bin\n"
        f"{base64.b64encode(payload).decode('ascii')}\n"
        ">>>FILE",
        mutation_mode="full",
    )

    assert err is None
    assert result.files == workspace.files
    assert result.static_files == (
        {
            "path": "fixture.bin",
            "kind": "static",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "source_kind": "generated_artifact",
            "mutation_policy": "llm_editable",
            "content_b64": base64.b64encode(payload).decode("ascii"),
        },
    )
    result.materialize(tmp_path)
    assert (tmp_path / "fixture.bin").read_bytes() == payload


def test_workspace_creates_generated_binary_member_with_file_binary_section():
    payload = b"new binary"
    workspace = CandidateWorkspace.from_code("x = 1\n")

    result, err = apply_workspace_mutation(
        workspace,
        "<<<FILE BINARY fixture.bin\n"
        f"{base64.b64encode(payload).decode('ascii')}\n"
        ">>>FILE",
        mutation_mode="full",
    )

    assert err is None
    assert result.static_files == (
        {
            "path": "fixture.bin",
            "kind": "binary",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "source_kind": "generated_artifact",
            "mutation_policy": "llm_editable",
            "content_b64": base64.b64encode(payload).decode("ascii"),
        },
    )


def test_workspace_rejects_static_create_over_text_file():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")

    result, err = apply_workspace_mutation(
        workspace,
        "<<<FILE STATIC main.py\nbmV3\n>>>FILE",
        mutation_mode="full",
    )

    assert result is workspace
    assert err == "main.py:target_exists"


def test_workspace_rejects_static_replace_invalid_base64():
    payload = b"old"
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {
                "path": "fixture.bin",
                "kind": "binary",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "mutation_policy": "llm_editable",
                "content_b64": base64.b64encode(payload).decode("ascii"),
            }
        ],
    )

    result, err = apply_workspace_mutation(
        workspace,
        "<<<FILE STATIC fixture.bin\nnot valid base64\n>>>FILE",
        mutation_mode="full",
    )

    assert result is workspace
    assert err == "fixture.bin:content_b64 must be valid base64"


def test_workspace_static_replace_rejects_no_valid_changes():
    payload = b"old"
    encoded = base64.b64encode(payload).decode("ascii")
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {
                "path": "fixture.bin",
                "kind": "binary",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "source_kind": "generated_artifact",
                "mutation_policy": "llm_editable",
                "content_b64": encoded,
            }
        ],
    )

    result, err = apply_workspace_mutation(
        workspace,
        f"<<<FILE STATIC fixture.bin\n{encoded}\n>>>FILE",
        mutation_mode="full",
    )

    assert result is workspace
    assert err == "no_valid_changes"


def test_workspace_access_revalidates_mutated_primary_file():
    workspace = CandidateWorkspace(files={"main.py": "x = 1\n"}, primary_file="main.py")
    workspace.primary_file = "missing.py"

    for access in (lambda: workspace.code, workspace.to_dict):
        try:
            access()
        except ValueError as exc:
            assert "Primary file 'missing.py' is not present" in str(exc)
        else:
            raise AssertionError("expected mutated primary rejection")


def test_workspace_materialize_revalidates_mutated_files(tmp_path):
    workspace = CandidateWorkspace(files={"main.py": "x = 1\n"}, primary_file="main.py")

    workspace.files["../escape.py"] = "x = 2\n"
    try:
        workspace.materialize(tmp_path / "unsafe")
    except ValueError as exc:
        assert "Unsafe candidate path" in str(exc)
    else:
        raise AssertionError("expected unsafe mutated path rejection")

    workspace = CandidateWorkspace(files={"main.py": "x = 1\n"}, primary_file="main.py")
    workspace.files["bad.py"] = 123
    try:
        workspace.materialize(tmp_path / "non_text")
    except ValueError as exc:
        assert "file content must be a string or bytes" in str(exc)
    else:
        raise AssertionError("expected non-text mutated content rejection")

    workspace = CandidateWorkspace(files={"main.py": "x = 1\n"}, primary_file="main.py")
    workspace.files["bad.py"] = "x = '\ud800'\n"
    try:
        workspace.materialize(tmp_path / "non_utf8")
    except ValueError as exc:
        assert "file content must be UTF-8 encodable" in str(exc)
    else:
        raise AssertionError("expected non-UTF-8 mutated content rejection")

    workspace = CandidateWorkspace(files={"src/café.py": "x = 1\n"}, primary_file="src/café.py")
    workspace.files["src/cafe\u0301.py"] = "x = 2\n"
    try:
        workspace.materialize(tmp_path / "duplicate")
    except ValueError as exc:
        assert "Duplicate candidate path after normalization" in str(exc)
    else:
        raise AssertionError("expected duplicate mutated path rejection")


def test_workspace_from_dict_validates_serialized_shape():
    invalid_records = [
        ["not", "mapping"],
        {"files": ["not", "mapping"], "primary_file": "main.py"},
        {"files": {1: "x = 1\n"}, "primary_file": "main.py"},
        {"files": {"main.py": ["not", "text"]}, "primary_file": "main.py"},
        {"files": {"helper.py": "x = 1\n"}, "primary_file": "missing.py"},
        {"files": {"main.py": "x = 1\n"}, "primary_file": 1},
    ]
    for record in invalid_records:
        try:
            CandidateWorkspace.from_dict(record)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected serialized workspace rejection for {record!r}")


def test_workspace_rejects_duplicate_file_edit_sections_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = (
        "<<<FILE helper.py\nvalue = 2\n>>>FILE\n"
        "<<<FILE helper.py\nvalue = 3\n>>>FILE"
    )
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "helper.py:duplicate_file_section"


def test_workspace_allows_explanatory_preamble_before_file_sections():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "Please update this file.\n<<<FILE main.py\nx = 2\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.files["main.py"] == "x = 2\n"


def test_workspace_rejects_stray_diff_around_file_sections():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = (
        "<<<FILE main.py\nx = 2\n>>>FILE\n"
        "<<<SEARCH\nvalue = 1\n===\nvalue = 2\n>>>REPLACE"
    )

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "malformed_file_sections:unconsumed_text"


def test_workspace_rejects_block_payload_around_file_sections():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE main.py\nx = 2\n>>>FILE\n<<<BLOCK core\nx = 3\n>>>BLOCK"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "malformed_file_sections:unconsumed_text"


def test_workspace_allows_proposal_metadata_around_file_sections():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = (
        "IDEA: Replace the primary file.\n"
        "RATIONALE: It is shorter.\n"
        "HYPOTHESIS: Score should improve.\n"
        "<<<FILE main.py\nx = 2\n>>>FILE"
    )

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.files["main.py"] == "x = 2\n"


def test_workspace_full_mode_strips_only_outer_markdown_wrapper_for_file_sections():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "```text\n<<<FILE main.py\nx = 2\n>>>FILE\n```"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.files["main.py"] == "x = 2\n"


def test_workspace_full_mode_preserves_markdown_fence_literal_in_file_section():
    workspace = CandidateWorkspace.from_code("DOC = ''\n", "main.py")
    response = "<<<FILE main.py\nDOC = '''```python\nprint(1)\n```'''\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.files["main.py"] == "DOC = '''```python\nprint(1)\n```'''\n"


def test_workspace_full_mode_preserves_marker_like_literals_in_file_section():
    workspace = CandidateWorkspace.from_code("TEXT = ''\n", "main.py")
    expected = (
        'FILE_START = "<<<FILE not a section"\n'
        'FILE_END = ">>>FILE not an end"\n'
        'BLOCK_START = "<<<BLOCK not a section"\n'
        'BLOCK_END = ">>>BLOCK not an end"\n'
    )
    response = f"<<<FILE main.py\n{expected}>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.files["main.py"] == expected


def test_workspace_rejects_edit_delete_conflict_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = (
        "<<<FILE helper.py\nvalue = 2\n>>>FILE\n"
        "<<<FILE DELETE helper.py\n>>>FILE"
    )
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "helper.py:conflicting_file_operations"


def test_workspace_rejects_edit_move_conflict_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = (
        "<<<FILE MOVE helper.py -> moved.py\n>>>FILE\n"
        "<<<FILE moved.py\nvalue = 2\n>>>FILE"
    )
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "moved.py:conflicting_file_operations"


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


def test_workspace_diff_matches_lf_patch_against_crlf_file_section():
    workspace = CandidateWorkspace(
        files={
            "main.py": "from helper import value\r\n",
            "helper.py": "value = 1\r\nother = 2\r\n",
        },
        primary_file="main.py",
    )
    response = (
        "<<<FILE helper.py\n"
        "<<<SEARCH\nvalue = 1\nother = 2\n===\nvalue = 3\nother = 4\n>>>REPLACE\n"
        ">>>FILE"
    )

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="diff")

    assert err is None
    assert result.files["main.py"] == workspace.files["main.py"]
    assert result.files["helper.py"] == "value = 3\r\nother = 4\r\n"


def test_workspace_full_mode_accepts_named_block_section_for_single_block_file():
    workspace = CandidateWorkspace(
        files={
            "main.py": "from helper import value\n",
            "helper.py": "# EVOLVE-BLOCK-START core\nvalue = 1\n# EVOLVE-BLOCK-END\n",
        },
        primary_file="main.py",
    )
    response = (
        "<<<FILE helper.py\n"
        "<<<BLOCK core\nvalue = 2\n>>>BLOCK\n"
        ">>>FILE"
    )

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.files["helper.py"] == (
        "# EVOLVE-BLOCK-START core\nvalue = 2\n# EVOLVE-BLOCK-END\n"
    )


def test_workspace_full_mode_accepts_named_sections_for_multi_block_file():
    workspace = CandidateWorkspace(
        files={
            "main.py": "from helper import value\n",
            "helper.py": (
                "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
                "# EVOLVE-BLOCK-START b\ny = 1\n# EVOLVE-BLOCK-END\n"
            ),
        },
        primary_file="main.py",
    )
    response = (
        "<<<FILE helper.py\n"
        "<<<BLOCK a\nx = 2\n>>>BLOCK\n"
        "<<<BLOCK b\ny = 2\n>>>BLOCK\n"
        ">>>FILE"
    )

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.files["helper.py"] == (
        "# EVOLVE-BLOCK-START a\nx = 2\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 2\n# EVOLVE-BLOCK-END\n"
    )


def test_workspace_full_mode_can_create_file():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE helper.py\nvalue = 2\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert err is None
    assert result.files["helper.py"] == "value = 2\n"


def test_workspace_full_mode_preserves_file_section_trailing_blank_lines():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE helper.py\nvalue = 2\n\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.files["helper.py"] == "value = 2\n\n"


def test_workspace_full_mode_can_create_empty_file():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE empty.py\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.files["empty.py"] == ""


def test_workspace_full_mode_can_create_empty_file_from_blank_body():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE empty.py\n\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.files["empty.py"] == "\n"


def test_workspace_full_mode_empty_existing_file_still_requires_change():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "empty.py": ""},
        primary_file="main.py",
    )
    response = "<<<FILE empty.py\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "empty.py:no_valid_changes"


def test_workspace_path_prefix_can_create_command_leading_filenames():
    for path in ("DELETE helper.py", "MOVE file.py", "PRIMARY config.py"):
        workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
        response = f"<<<FILE PATH {path}\nvalue = 2\n>>>FILE"

        result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

        assert err is None
        assert result.files[path] == "value = 2\n"


def test_workspace_path_prefix_can_edit_command_leading_filenames():
    for path in ("DELETE helper.py", "MOVE file.py", "PRIMARY config.py"):
        workspace = CandidateWorkspace(
            files={"main.py": "x = 1\n", path: "value = 1\n"},
            primary_file="main.py",
        )
        response = f"<<<FILE PATH {path}\nvalue = 2\n>>>FILE"

        result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

        assert err is None
        assert result.files[path] == "value = 2\n"


def test_workspace_path_prefix_rejects_empty_path():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE PATH\nvalue = 2\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "empty_path:unsafe_path"


def test_workspace_rejects_same_line_file_envelope():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE main.py>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "malformed_file_sections:same_line"


def test_workspace_rejects_mixed_valid_and_same_line_file_envelopes():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = (
        "<<<FILE helper.py\nvalue = 2\n>>>FILE\n"
        "<<<FILE main.py>>>FILE"
    )

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "malformed_file_sections:same_line"


def test_full_mode_rejects_same_line_block_envelope_in_single_block_candidate():
    code = "# EVOLVE-BLOCK-START core\nx = 1\n# EVOLVE-BLOCK-END\n"

    result, err = apply_candidate_mutation(
        code, "<<<BLOCK core>>>BLOCK", mutation_mode="full"
    )

    assert result == code
    assert err == "malformed_block_sections:same_line"


def test_full_mode_rejects_mixed_valid_and_same_line_block_envelopes():
    code = (
        "# EVOLVE-BLOCK-START a\nx = 1\n# EVOLVE-BLOCK-END\n"
        "# EVOLVE-BLOCK-START b\ny = 1\n# EVOLVE-BLOCK-END\n"
    )
    response = "<<<BLOCK a\nx = 2\n>>>BLOCK\n<<<BLOCK b>>>BLOCK"

    result, err = apply_candidate_mutation(code, response, mutation_mode="full")

    assert result == code
    assert err == "malformed_block_sections:same_line"


def test_workspace_can_delete_non_primary_file():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE DELETE helper.py\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert err is None
    assert "helper.py" not in result.files
    assert result.primary_file == "main.py"


def test_workspace_can_move_file_and_update_primary():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="old.py",
    )
    response = "<<<FILE MOVE old.py -> pkg/new.py\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert err is None
    assert "old.py" not in result.files
    assert result.files["pkg/new.py"] == "value = 1\n"
    assert result.primary_file == "pkg/new.py"


def test_workspace_rename_alias_moves_file():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE RENAME old.py -> renamed.py\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert err is None
    assert "old.py" not in result.files
    assert result.files["renamed.py"] == "value = 1\n"


def test_workspace_can_change_primary_file_explicitly():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "alt.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE PRIMARY alt.py\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert err is None
    assert result.primary_file == "alt.py"
    assert result.code == "value = 1\n"


def test_workspace_primary_can_target_same_mutation_move_target_order_independent():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = (
        "<<<FILE PRIMARY pkg/new.py\n>>>FILE\n"
        "<<<FILE MOVE old.py -> pkg/new.py\n>>>FILE"
    )

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.primary_file == "pkg/new.py"
    assert result.files["pkg/new.py"] == "value = 1\n"


def test_workspace_primary_can_target_same_mutation_created_file():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = (
        "<<<FILE PRIMARY helper.py\n>>>FILE\n"
        "<<<FILE helper.py\nvalue = 2\n>>>FILE"
    )

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert result.primary_file == "helper.py"
    assert result.files["helper.py"] == "value = 2\n"


def test_workspace_rejects_delete_primary_without_explicit_replacement():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "a.py": "a = 1\n", "z.py": "z = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE DELETE main.py\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "main.py:primary_deleted_requires_primary"


def test_workspace_delete_primary_accepts_explicit_replacement():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "a.py": "a = 1\n", "z.py": "z = 1\n"},
        primary_file="main.py",
    )
    response = (
        "<<<FILE DELETE main.py\n>>>FILE\n"
        "<<<FILE PRIMARY z.py\n>>>FILE"
    )

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert err is None
    assert "main.py" not in result.files
    assert result.primary_file == "z.py"


def test_workspace_rejects_duplicate_primary_sections_without_partial_apply():
    workspace = CandidateWorkspace(
        files={
            "main.py": "x = 1\n",
            "alt.py": "alt = 1\n",
            "third.py": "third = 1\n",
        },
        primary_file="main.py",
    )
    response = (
        "<<<FILE PRIMARY alt.py\n>>>FILE\n"
        "<<<FILE PRIMARY third.py\n>>>FILE"
    )

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "primary:duplicate_primary_section"


def test_workspace_rejects_non_empty_delete_command_body_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE DELETE helper.py\nthis body is ignored\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "helper.py:unexpected_command_body"


def test_workspace_rejects_non_empty_move_command_body_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE MOVE old.py -> new.py\nthis body is ignored\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "old.py:unexpected_command_body"


def test_workspace_rejects_non_empty_rename_command_body_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE RENAME old.py -> new.py\nthis body is ignored\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "old.py:unexpected_command_body"


def test_workspace_rejects_non_empty_primary_command_body_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "alt.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE PRIMARY alt.py\nthis body is ignored\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "alt.py:unexpected_command_body"


def test_workspace_rejects_delete_missing_file_without_partial_apply():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = (
        "<<<FILE extra.py\nvalue = 2\n>>>FILE\n"
        "<<<FILE DELETE missing.py\n>>>FILE"
    )
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "missing.py:missing_source"


def test_workspace_rejects_move_to_existing_target_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE MOVE old.py -> main.py\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "main.py:target_exists"


def test_workspace_rejects_casefold_file_creation_collision_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"README.md": "upper\n", "main.py": "x = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE readme.md\nlower\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "readme.md:host_path_collision"


def test_workspace_rejects_casefold_move_target_collision_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"README.md": "upper\n", "old.py": "value = 1\n"},
        primary_file="README.md",
    )
    response = "<<<FILE MOVE old.py -> readme.md\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "readme.md:host_path_collision"


def test_workspace_rejects_duplicate_move_targets_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "a.py": "a = 1\n", "b.py": "b = 1\n"},
        primary_file="main.py",
    )
    response = (
        "<<<FILE MOVE a.py -> target.py\n>>>FILE\n"
        "<<<FILE MOVE b.py -> target.py\n>>>FILE"
    )
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "target.py:duplicate_move_target"


def test_workspace_rejects_casefold_duplicate_move_targets_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "a.py": "a = 1\n", "b.py": "b = 1\n"},
        primary_file="main.py",
    )
    response = (
        "<<<FILE MOVE a.py -> Target.py\n>>>FILE\n"
        "<<<FILE MOVE b.py -> target.py\n>>>FILE"
    )
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "target.py:host_path_collision"


def test_workspace_rejects_chained_topology_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "a.py": "a = 1\n"},
        primary_file="main.py",
    )
    response = (
        "<<<FILE MOVE a.py -> b.py\n>>>FILE\n"
        "<<<FILE MOVE b.py -> c.py\n>>>FILE"
    )
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "b.py:conflicting_file_operations"


def test_workspace_rejects_unsafe_move_target():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE MOVE old.py -> ../new.py\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "../new.py:unsafe_path"


def test_workspace_rejects_absolute_file_section_without_partial_apply():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE /new.py\nvalue = 2\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "/new.py:unsafe_path"


def test_workspace_rejects_absolute_move_target_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE MOVE old.py -> /new.py\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "/new.py:unsafe_path"


def test_workspace_rejects_absolute_primary_target_without_partial_apply():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE PRIMARY /main.py\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "/main.py:unsafe_path"


def test_workspace_rejects_ambiguous_file_section_without_partial_apply():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE pkg//new.py\nvalue = 2\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "pkg//new.py:unsafe_path"


def test_workspace_rejects_ambiguous_move_target_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE MOVE old.py -> pkg/./new.py\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "pkg/./new.py:unsafe_path"


def test_workspace_rejects_ambiguous_primary_target_without_partial_apply():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE PRIMARY ./main.py\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "./main.py:unsafe_path"


def test_workspace_rejects_hidden_file_section_without_partial_apply():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE .env\nTOKEN = 'secret'\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == ".env:unsafe_path"


def test_workspace_rejects_hidden_move_target_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE MOVE old.py -> .git/config\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == ".git/config:unsafe_path"


def test_workspace_rejects_hidden_primary_target_without_partial_apply():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE PRIMARY pkg/.hidden.py\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "pkg/.hidden.py:unsafe_path"


def test_workspace_rejects_overlong_file_section_without_partial_apply():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    path = f"{'a' * 256}.py"
    response = f"<<<FILE {path}\nvalue = 2\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == f"{path}:unsafe_path"


def test_workspace_rejects_overlong_move_target_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="main.py",
    )
    path = f"pkg/{'a' * 256}.py"
    response = f"<<<FILE MOVE old.py -> {path}\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == f"{path}:unsafe_path"


def test_workspace_rejects_overlong_primary_target_without_partial_apply():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    path = f"{'a' * 256}.py"
    response = f"<<<FILE PRIMARY {path}\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == f"{path}:unsafe_path"


def test_workspace_rejects_host_invalid_file_section_without_partial_apply():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE bad?.py\nvalue = 2\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "bad?.py:unsafe_path"


def test_workspace_rejects_control_character_file_section_without_partial_apply():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE bad\tname.py\nvalue = 2\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "bad\tname.py:unsafe_path"


def test_workspace_rejects_unicode_format_control_file_section_without_partial_apply():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE src/rtl\u202egnp.py\nvalue = 2\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "src/rtl\u202egnp.py:unsafe_path"


def test_workspace_rejects_reserved_name_move_target_without_partial_apply():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE MOVE old.py -> CON.txt\n>>>FILE"

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "CON.txt:unsafe_path"


def test_workspace_rejects_noop_move():
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = "<<<FILE MOVE old.py -> old.py\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "old.py:no_valid_changes"


def test_workspace_rejects_missing_primary_target():
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    response = "<<<FILE PRIMARY missing.py\n>>>FILE"
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert result == workspace
    assert err == "missing.py:missing_primary"


def test_workspace_materializes_after_topology_changes(tmp_path):
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "old.py": "value = 1\n"},
        primary_file="main.py",
    )
    response = (
        "<<<FILE MOVE old.py -> pkg/new.py\n>>>FILE\n"
        "<<<FILE DELETE main.py\n>>>FILE\n"
        "<<<FILE PRIMARY pkg/new.py\n>>>FILE"
    )
    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")
    assert err is None

    primary_path = result.materialize(tmp_path)
    assert primary_path == tmp_path / "pkg" / "new.py"
    assert primary_path.read_text(encoding="utf-8") == "value = 1\n"
    assert not (tmp_path / "main.py").exists()


def test_workspace_materialize_replaces_existing_root_with_exact_snapshot(tmp_path):
    (tmp_path / "old.py").write_text("old\n", encoding="utf-8")
    stale_dir = tmp_path / "pkg"
    stale_dir.mkdir()
    (stale_dir / "stale.py").write_text("stale\n", encoding="utf-8")
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "pkg/helper.py": "value = 1\n"},
        primary_file="main.py",
    )

    primary_path = workspace.materialize(tmp_path)

    assert primary_path == tmp_path / "main.py"
    assert (tmp_path / "main.py").read_text(encoding="utf-8") == "x = 1\n"
    assert (tmp_path / "pkg" / "helper.py").read_text(encoding="utf-8") == "value = 1\n"
    assert not (tmp_path / "old.py").exists()
    assert not (tmp_path / "pkg" / "stale.py").exists()


def test_workspace_materialize_backup_failure_preserves_existing_root(
    tmp_path, monkeypatch
):
    from libreevolve.core import candidate as candidate_module

    root = tmp_path / "workspace"
    root.mkdir()
    (root / "old.py").write_text("old\n", encoding="utf-8")
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    original_rename = candidate_module.Path.rename

    def fail_existing_root_backup(self, target):
        if self == root.resolve():
            raise OSError("backup failed")
        return original_rename(self, target)

    monkeypatch.setattr(candidate_module.Path, "rename", fail_existing_root_backup)

    try:
        workspace.materialize(root)
    except CandidateMaterializationError as exc:
        assert "backup failed" in str(exc)
        assert exc.reason == "materialization_existing_root_backup_failed"
        assert exc.paths[0] == str(root.resolve())
    else:
        raise AssertionError("expected backup failure")

    assert (root / "old.py").read_text(encoding="utf-8") == "old\n"
    assert not (root / "main.py").exists()


def test_workspace_materialize_swap_failure_restores_existing_root(
    tmp_path, monkeypatch
):
    from libreevolve.core import candidate as candidate_module

    root = tmp_path / "workspace"
    root.mkdir()
    (root / "old.py").write_text("old\n", encoding="utf-8")
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")
    original_rename = candidate_module.Path.rename

    def fail_temp_root_swap(self, target):
        if self.name.startswith(".workspace.tmp-"):
            raise OSError("swap failed")
        return original_rename(self, target)

    monkeypatch.setattr(candidate_module.Path, "rename", fail_temp_root_swap)

    try:
        workspace.materialize(root)
    except CandidateMaterializationError as exc:
        assert "swap failed" in str(exc)
        assert exc.reason == "materialization_swap_failed"
        assert exc.paths[1] == str(root.resolve())
    else:
        raise AssertionError("expected swap failure")

    assert (root / "old.py").read_text(encoding="utf-8") == "old\n"
    assert not (root / "main.py").exists()


def test_workspace_materialize_preflight_failure_preserves_existing_root(tmp_path):
    (tmp_path / "old.py").write_text("old\n", encoding="utf-8")
    workspace = CandidateWorkspace(
        files={"Readme.md": "lower\n", "README.md": "upper\n"},
        primary_file="Readme.md",
    )
    try:
        workspace.materialize(tmp_path)
    except CandidateMaterializationError as exc:
        assert "Candidate paths collide when materialized" in str(exc)
        assert exc.reason == "candidate_path_collision"
        assert exc.paths == ("Readme.md", "README.md")
    else:
        raise AssertionError("expected case-folded materialization collision")

    assert (tmp_path / "old.py").read_text(encoding="utf-8") == "old\n"
    assert not (tmp_path / "Readme.md").exists()
    assert not (tmp_path / "README.md").exists()


def test_workspace_materialize_write_failure_preserves_existing_root(
    tmp_path, monkeypatch
):
    from libreevolve.core import candidate as candidate_module

    (tmp_path / "old.py").write_text("old\n", encoding="utf-8")
    workspace = CandidateWorkspace(
        files={"a.py": "a = 1\n", "b.py": "b = 2\n"},
        primary_file="a.py",
    )
    original_write_bytes = candidate_module.Path.write_bytes

    def fail_second_file(self, data, *args, **kwargs):
        if self.name == "b.py":
            raise OSError("disk failed")
        return original_write_bytes(self, data, *args, **kwargs)

    monkeypatch.setattr(candidate_module.Path, "write_bytes", fail_second_file)

    try:
        workspace.materialize(tmp_path)
    except CandidateMaterializationError as exc:
        assert "disk failed" in str(exc)
        assert exc.reason == "candidate_file_write_failed"
        assert exc.paths == ("b.py",)
    else:
        raise AssertionError("expected write failure")

    assert (tmp_path / "old.py").read_text(encoding="utf-8") == "old\n"
    assert not (tmp_path / "a.py").exists()
    assert not (tmp_path / "b.py").exists()


def test_workspace_materialize_rejects_file_root_without_writes(tmp_path):
    root = tmp_path / "workspace"
    root.write_text("not a directory\n", encoding="utf-8")
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")

    try:
        workspace.materialize(root)
    except CandidateMaterializationError as exc:
        assert "Candidate workspace root must be a directory" in str(exc)
        assert exc.reason == "candidate_root_not_directory"
        assert exc.paths == (str(root.resolve()),)
    else:
        raise AssertionError("expected file root rejection")

    assert root.read_text(encoding="utf-8") == "not a directory\n"


def test_workspace_materialize_rejects_symlink_ancestor(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    linked_parent = tmp_path / "linked_parent"
    try:
        linked_parent.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        return
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")

    try:
        workspace.materialize(linked_parent / "workspace")
    except CandidateMaterializationError as exc:
        assert "linked ancestor" in str(exc)
        assert exc.reason == "candidate_root_linked_ancestor"
        assert exc.paths == (str(linked_parent.absolute()),)
    else:
        raise AssertionError("expected linked ancestor rejection")

    assert not (outside / "workspace").exists()


def test_workspace_materialize_rejects_nested_symlink_before_cleanup(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "marker.txt").write_text("outside\n", encoding="utf-8")
    root = tmp_path / "workspace"
    nested = root / "nested"
    nested.mkdir(parents=True)
    link = nested / "outside_link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        return
    (root / "old.py").write_text("old\n", encoding="utf-8")
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")

    try:
        workspace.materialize(root)
    except CandidateMaterializationError as exc:
        assert "contains a link" in str(exc)
        assert exc.reason == "candidate_root_contains_link"
        assert exc.paths == (str(link),)
    else:
        raise AssertionError("expected nested symlink rejection")

    assert link.is_symlink()
    assert (outside / "marker.txt").read_text(encoding="utf-8") == "outside\n"
    assert (root / "old.py").read_text(encoding="utf-8") == "old\n"
    assert not (root / "main.py").exists()


def test_workspace_materialize_rejects_windows_junction_ancestor(tmp_path):
    if os.name != "nt":
        return
    outside = tmp_path / "outside_junction"
    outside.mkdir()
    junction_parent = tmp_path / "junction_parent"
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction_parent), str(outside)],
        capture_output=True,
        text=True,
    )
    if created.returncode != 0:
        return
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")

    try:
        try:
            workspace.materialize(junction_parent / "workspace")
        except CandidateMaterializationError as exc:
            assert "linked ancestor" in str(exc)
            assert exc.reason == "candidate_root_linked_ancestor"
            assert exc.paths == (str(junction_parent.absolute()),)
        else:
            raise AssertionError("expected junction ancestor rejection")
        assert not (outside / "workspace").exists()
    finally:
        if junction_parent.exists():
            junction_parent.rmdir()


def test_workspace_materialize_rejects_nested_windows_junction_before_cleanup(tmp_path):
    if os.name != "nt":
        return
    outside = tmp_path / "outside_junction"
    outside.mkdir()
    (outside / "marker.txt").write_text("outside\n", encoding="utf-8")
    root = tmp_path / "workspace"
    nested = root / "nested"
    nested.mkdir(parents=True)
    junction = nested / "outside_link"
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
        capture_output=True,
        text=True,
    )
    if created.returncode != 0:
        return
    (root / "old.py").write_text("old\n", encoding="utf-8")
    workspace = CandidateWorkspace.from_code("x = 1\n", "main.py")

    try:
        try:
            workspace.materialize(root)
        except CandidateMaterializationError as exc:
            assert "contains a link" in str(exc)
            assert exc.reason == "candidate_root_contains_link"
            assert exc.paths == (str(junction),)
        else:
            raise AssertionError("expected nested junction rejection")
        assert (outside / "marker.txt").read_text(encoding="utf-8") == "outside\n"
        assert (root / "old.py").read_text(encoding="utf-8") == "old\n"
        assert not (root / "main.py").exists()
    finally:
        if junction.exists():
            junction.rmdir()


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


def test_workspace_rejects_duplicate_paths_after_normalization():
    try:
        CandidateWorkspace(
            files={"pkg\\helper.py": "value = 1\n", "pkg/helper.py": "value = 2\n"},
            primary_file="pkg/helper.py",
        )
    except ValueError as exc:
        assert "Duplicate candidate path after normalization" in str(exc)
    else:
        raise AssertionError("expected duplicate normalized path rejection")


def test_workspace_rejects_case_collisions_before_materialization(tmp_path):
    workspace = CandidateWorkspace(
        files={"Readme.md": "lower\n", "README.md": "upper\n"},
        primary_file="Readme.md",
    )
    try:
        workspace.materialize(tmp_path)
    except CandidateMaterializationError as exc:
        assert "Candidate paths collide when materialized" in str(exc)
        assert exc.reason == "candidate_path_collision"
        assert exc.paths == ("Readme.md", "README.md")
    else:
        raise AssertionError("expected case-folded materialization collision")
    assert not (tmp_path / "Readme.md").exists()
    assert not (tmp_path / "README.md").exists()


def test_workspace_materialize_rejects_casefold_static_collision(tmp_path):
    raw = b"static\n"
    workspace = CandidateWorkspace(
        files={"README.md": "text\n"},
        primary_file="README.md",
        static_files=[
            {
                "path": "readme.md",
                "kind": "binary",
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "content_b64": base64.b64encode(raw).decode("ascii"),
            }
        ],
    )

    with pytest.raises(CandidateMaterializationError) as excinfo:
        workspace.materialize(tmp_path / "candidate")

    assert excinfo.value.reason == "candidate_path_collision"
    assert excinfo.value.paths == ("README.md", "readme.md")
    assert not (tmp_path / "candidate").exists()


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


def test_workspace_rejects_malformed_evolve_block_in_created_file():
    workspace = CandidateWorkspace.from_code("x = 1\n")
    response = (
        "<<<FILE helper.py\n"
        "# EVOLVE-BLOCK-START bad name\n"
        "value = 1\n"
        "# EVOLVE-BLOCK-END\n"
        ">>>FILE"
    )

    result, err = apply_workspace_mutation(workspace, response, mutation_mode="full")

    assert result == workspace
    assert err == "helper.py:malformed_evolve_blocks:invalid_name"


def test_workspace_rejects_malformed_evolve_block_in_untouched_sibling():
    workspace = CandidateWorkspace(
        files={
            "main.py": "x = 1\n",
            "helper.py": "# EVOLVE-BLOCK-START bad name\nvalue = 1\n# EVOLVE-BLOCK-END\n",
        },
        primary_file="main.py",
    )

    result, err = apply_workspace_mutation(
        workspace,
        "<<<SEARCH\nx = 1\n===\nx = 2\n>>>REPLACE",
    )

    assert result == workspace
    assert err == "helper.py:malformed_evolve_blocks:invalid_name"


def test_workspace_revalidates_evolve_blocks_after_topology_move():
    workspace = CandidateWorkspace(
        files={
            "main.py": "x = 1\n",
            "old.py": "# EVOLVE-BLOCK-END\n",
        },
        primary_file="main.py",
    )

    result, err = apply_workspace_mutation(
        workspace,
        "<<<FILE MOVE old.py -> moved.py\n>>>FILE",
        mutation_mode="full",
    )

    assert result == workspace
    assert err == "moved.py:malformed_evolve_blocks:orphan_end"
