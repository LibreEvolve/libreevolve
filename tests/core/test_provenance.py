import hashlib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType

import pytest

import libreevolve.core.provenance as provenance_module
from libreevolve.core.provenance import (
    git_state,
    plugin_provenance,
    problem_provenance,
    runtime_environment_provenance,
    source_provenance,
)


def test_problem_provenance_hash_changes_when_problem_file_changes(tmp_path):
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")
    (tmp_path / "metrics.yaml").write_text("metrics: []\n", encoding="utf-8")
    (tmp_path / "validate.py").write_text("def evaluate(c): pass\n", encoding="utf-8")
    (tmp_path / "runs").mkdir()
    (tmp_path / "runs" / "ignored.jsonl").write_text("ignored", encoding="utf-8")

    first = problem_provenance(tmp_path)
    (tmp_path / "task_description.txt").write_text("changed", encoding="utf-8")
    second = problem_provenance(tmp_path)

    assert first["tree_hash"] != second["tree_hash"]
    assert [record["path"] for record in second["files"]] == [
        "metrics.yaml",
        "runs/ignored.jsonl",
        "task_description.txt",
        "validate.py",
    ]
    assert second["skipped_count"] == 0
    assert second["skipped"] == []


def test_problem_provenance_hash_changes_for_fixture_under_runs_directory(tmp_path):
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")
    (tmp_path / "runs").mkdir()
    fixture = tmp_path / "runs" / "fixture.txt"
    fixture.write_text("first", encoding="utf-8")

    first = problem_provenance(tmp_path)
    fixture.write_text("second", encoding="utf-8")
    second = problem_provenance(tmp_path)

    assert first["tree_hash"] != second["tree_hash"]
    assert "runs/fixture.txt" in [record["path"] for record in second["files"]]


def test_problem_provenance_skips_generated_run_artifact_directories(tmp_path):
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")
    fixture = tmp_path / "runs" / "fixture.txt"
    old_run = tmp_path / "runs" / "old"
    active_run = tmp_path / "runs" / "active"
    old_run.mkdir(parents=True)
    active_run.mkdir(parents=True)
    fixture.write_text("fixture", encoding="utf-8")
    (old_run / "history.jsonl").write_text("{}\n", encoding="utf-8")
    (active_run / "history.jsonl").write_text("{}\n", encoding="utf-8")

    provenance = problem_provenance(
        tmp_path,
        generated_roots=[active_run],
    )

    paths = [record["path"] for record in provenance["files"]]
    assert "runs/fixture.txt" in paths
    assert "runs/old/history.jsonl" not in paths
    assert "runs/active/history.jsonl" not in paths
    assert "history.jsonl" in provenance["generated_run_artifact_markers"]
    assert "manifest.json" in provenance["generated_run_artifact_markers"]
    assert provenance["skipped"] == [
        {"path": "runs/active", "reason": "excluded_output_root"},
        {"path": "runs/old", "reason": "generated_run_artifacts"},
    ]


def test_problem_provenance_hash_ignores_stale_generated_run_artifact_changes(tmp_path):
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")
    old_run = tmp_path / "runs" / "old"
    old_run.mkdir(parents=True)
    (old_run / "manifest.json").write_text('{"runtime": {}}\n', encoding="utf-8")
    (old_run / "history.jsonl").write_text('{"id": "first"}\n', encoding="utf-8")

    first = problem_provenance(tmp_path)
    (old_run / "history.jsonl").write_text('{"id": "second"}\n', encoding="utf-8")
    second = problem_provenance(tmp_path)

    assert first["tree_hash"] == second["tree_hash"]
    assert first["skipped_hash"] == second["skipped_hash"]
    assert [record["path"] for record in first["files"]] == ["task_description.txt"]
    assert first["skipped"] == [
        {"path": "runs/old", "reason": "generated_run_artifacts"}
    ]


def test_problem_provenance_resolves_relative_generated_roots_from_problem_root(
    tmp_path,
    monkeypatch,
):
    problem_dir = tmp_path / "problem"
    unrelated_cwd = tmp_path / "elsewhere"
    active_run = problem_dir / "runs" / "demo"
    unrelated_cwd.mkdir(parents=True)
    active_run.mkdir(parents=True)
    (problem_dir / "task_description.txt").write_text("task", encoding="utf-8")
    (active_run / "history.jsonl").write_text("{}\n", encoding="utf-8")
    monkeypatch.chdir(unrelated_cwd)

    provenance = problem_provenance(
        problem_dir,
        generated_roots=[Path("runs") / "demo"],
    )

    assert [record["path"] for record in provenance["files"]] == ["task_description.txt"]
    assert provenance["skipped"] == [
        {"path": "runs/demo", "reason": "excluded_output_root"}
    ]


def test_problem_provenance_records_excluded_cache_directories(tmp_path):
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "ignored.pyc").write_bytes(b"cached")

    provenance = problem_provenance(tmp_path)

    assert [record["path"] for record in provenance["files"]] == ["task_description.txt"]
    assert provenance["skipped"] == [
        {"path": "__pycache__", "reason": "excluded_directory"}
    ]
    assert provenance["skipped_count"] == 1
    assert len(provenance["skipped_hash"]) == 64
    assert provenance["skipped_hash_scope"] == "skipped_diagnostic_records_v2"
    assert len(provenance["provenance_hash"]) == 64
    assert provenance["provenance_hash_scope"] == "included_files_and_skipped_diagnostics_v2"


def test_problem_provenance_skips_files_over_tree_provenance_limit(tmp_path):
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")
    large = tmp_path / "large_fixture.bin"
    large.write_bytes(b"x" * 1_000_001)

    provenance = problem_provenance(tmp_path)

    assert provenance["max_file_bytes"] == 1_000_000
    assert [record["path"] for record in provenance["files"]] == ["task_description.txt"]
    assert provenance["skipped"] == [
        {
            "path": "large_fixture.bin",
            "reason": "max_file_bytes",
            "bytes": 1_000_001,
            "max_bytes": 1_000_000,
        }
    ]


def test_problem_provenance_hashes_binary_files_within_limit(tmp_path):
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")
    binary = tmp_path / "fixture.bin"
    raw = b"\x00\xff\x10binary"
    binary.write_bytes(raw)

    provenance = problem_provenance(tmp_path)

    records = {record["path"]: record for record in provenance["files"]}
    assert records["fixture.bin"]["bytes"] == len(raw)
    assert records["fixture.bin"]["sha256"] == hashlib.sha256(raw).hexdigest()
    assert provenance["skipped"] == []


def test_problem_provenance_records_read_errors(tmp_path, monkeypatch):
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")
    unreadable = tmp_path / "unreadable.txt"
    unreadable.write_text("secret", encoding="utf-8")
    original = Path.read_bytes

    def fake_read_bytes(path):
        if path == unreadable:
            raise PermissionError("cannot read api_key=sk-proj_readsecret1234567890")
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", fake_read_bytes)

    provenance = problem_provenance(tmp_path)

    assert [record["path"] for record in provenance["files"]] == ["task_description.txt"]
    assert provenance["skipped"][0]["path"] == "unreadable.txt"
    assert provenance["skipped"][0]["reason"] == "read_error"
    assert provenance["skipped"][0]["error_type"] == "PermissionError"
    assert "sk-proj_readsecret1234567890" not in provenance["skipped"][0]["error"]


def test_problem_provenance_records_directory_listing_errors(tmp_path, monkeypatch):
    token = "sk-" + "proj_" + "dirlistsecret1234567890"  # pragma: allowlist secret
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")
    readable = tmp_path / "readable"
    blocked = tmp_path / "blocked"
    readable.mkdir()
    blocked.mkdir()
    (readable / "fixture.txt").write_text("fixture", encoding="utf-8")
    (blocked / "secret.txt").write_text("secret", encoding="utf-8")
    original_iterdir = Path.iterdir

    def fake_iterdir(path):
        if path == blocked:
            raise PermissionError(f"cannot list token={token}")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fake_iterdir)

    provenance = problem_provenance(tmp_path)

    assert [record["path"] for record in provenance["files"]] == [
        "readable/fixture.txt",
        "task_description.txt",
    ]
    assert provenance["skipped"] == [
        {
            "path": "blocked",
            "reason": "directory_listing_error",
            "error_type": "PermissionError",
            "error": "cannot list token=[REDACTED]",
        }
    ]
    assert token not in repr(provenance)
    assert provenance["skipped_count"] == 1
    assert len(provenance["skipped_hash"]) == 64
    assert len(provenance["provenance_hash"]) == 64


def test_problem_provenance_records_root_directory_listing_errors(tmp_path, monkeypatch):
    token = "sk-" + "proj_" + "rootlistsecret1234567890"  # pragma: allowlist secret
    original_iterdir = Path.iterdir

    def fake_iterdir(path):
        if path == tmp_path:
            raise PermissionError(f"cannot list root token={token}")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fake_iterdir)

    provenance = problem_provenance(tmp_path)

    assert provenance["files"] == []
    assert provenance["file_count"] == 0
    assert provenance["skipped"] == [
        {
            "path": ".",
            "reason": "directory_listing_error",
            "error_type": "PermissionError",
            "error": "cannot list root token=[REDACTED]",
        }
    ]
    assert token not in repr(provenance)
    assert provenance["skipped_count"] == 1


def test_source_provenance_records_directory_listing_errors(monkeypatch):
    token = "sk-" + "proj_" + "sourcelistsecret1234567890"  # pragma: allowlist secret
    import libreevolve.core.provenance as provenance_module

    source_root = Path(provenance_module.__file__).resolve().parents[1]
    blocked = source_root / "plugins"
    original_iterdir = Path.iterdir

    def fake_iterdir(path):
        if path == blocked:
            raise PermissionError(f"cannot list source token={token}")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fake_iterdir)

    provenance = source_provenance()

    skipped = [
        record for record in provenance["skipped"]
        if record["reason"] == "directory_listing_error"
    ]
    assert skipped == [
        {
            "path": "plugins",
            "reason": "directory_listing_error",
            "error_type": "PermissionError",
            "error": "cannot list source token=[REDACTED]",
        }
    ]
    assert token not in repr(provenance)
    assert provenance["file_count"] > 0
    assert len(provenance["tree_hash"]) == 64


def test_source_provenance_redacts_and_hashes_root():
    source_root = Path(provenance_module.__file__).resolve().parents[1]

    provenance = source_provenance()
    rendered = json.dumps(provenance, sort_keys=True)

    assert provenance["root"] == "<libreevolve-root>"
    assert provenance["root_scope"] == "local_root_label"
    assert provenance["root_redacted"] is True
    assert len(provenance["root_hash"]) == 64
    assert str(source_root) not in rendered


def test_problem_provenance_separates_included_and_skipped_digests(tmp_path):
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")
    baseline = problem_provenance(tmp_path)

    cache = tmp_path / "__pycache__"
    cache.mkdir()
    skipped_file = cache / "ignored.pyc"
    skipped_file.write_bytes(b"first")
    with_skipped = problem_provenance(tmp_path)

    skipped_file.write_bytes(b"second")
    changed_skipped_content = problem_provenance(tmp_path)

    assert baseline["tree_hash"] == with_skipped["tree_hash"]
    assert with_skipped["tree_hash"] == changed_skipped_content["tree_hash"]
    assert baseline["skipped_hash"] != with_skipped["skipped_hash"]
    assert with_skipped["skipped_hash"] == changed_skipped_content["skipped_hash"]
    assert baseline["provenance_hash"] != with_skipped["provenance_hash"]
    assert with_skipped["provenance_hash"] == changed_skipped_content["provenance_hash"]
    assert baseline["tree_hash_scope"] == "included_files"


def test_problem_provenance_records_file_symlink_target_identity(tmp_path):
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")
    outside = tmp_path.parent / "outside_secret.txt"
    outside.write_text("outside", encoding="utf-8")
    outside2 = tmp_path.parent / "outside_secret_2.txt"
    outside2.write_text("outside2", encoding="utf-8")
    link = tmp_path / "linked.txt"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"file symlink creation is unavailable: {exc}")

    provenance = problem_provenance(tmp_path)

    assert [record["path"] for record in provenance["files"]] == ["task_description.txt"]
    skipped = provenance["skipped"][0]
    assert skipped["path"] == "linked.txt"
    assert skipped["reason"] == "link_not_followed"
    assert skipped["is_symlink"] is True
    assert skipped["is_junction"] is False
    assert skipped["target_path_redacted"] is True
    assert skipped["link_target_status"] == "ok"
    assert skipped["link_target_hash"] == hashlib.sha256(str(outside).encode("utf-8")).hexdigest()
    assert skipped["target_resolved_hash"] == hashlib.sha256(
        str(outside.resolve()).encode("utf-8")
    ).hexdigest()
    assert skipped["target_within_root"] is False
    assert skipped["target_scope"] == "outside_root"
    assert provenance["skipped_count"] == 1

    link.unlink()
    link.symlink_to(outside2)
    changed = problem_provenance(tmp_path)

    assert changed["tree_hash"] == provenance["tree_hash"]
    assert changed["skipped_hash"] != provenance["skipped_hash"]
    assert changed["provenance_hash"] != provenance["provenance_hash"]


def test_problem_provenance_records_windows_junction_target_identity(tmp_path):
    if sys.platform != "win32":
        pytest.skip("Windows junction test")

    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")
    outside = tmp_path.parent / "outside_dir"
    outside.mkdir()
    (outside / "secret.txt").write_text("outside", encoding="utf-8")
    outside2 = tmp_path.parent / "outside_dir_2"
    outside2.mkdir()
    (outside2 / "secret.txt").write_text("outside2", encoding="utf-8")
    link = tmp_path / "linked_dir"
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(outside)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"junction creation is unavailable: {result.stderr or result.stdout}")

    provenance = problem_provenance(tmp_path)

    assert [record["path"] for record in provenance["files"]] == ["task_description.txt"]
    skipped = provenance["skipped"][0]
    assert skipped["path"] == "linked_dir"
    assert skipped["reason"] == "link_not_followed"
    assert skipped["is_junction"] is True
    assert skipped["target_path_redacted"] is True
    assert skipped["target_resolved_hash"] == hashlib.sha256(
        str(outside.resolve()).encode("utf-8")
    ).hexdigest()
    assert skipped["target_within_root"] is False
    assert skipped["target_scope"] == "outside_root"
    assert provenance["skipped_count"] == 1

    link.rmdir()
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(outside2)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"junction recreation is unavailable: {result.stderr or result.stdout}")
    changed = problem_provenance(tmp_path)

    assert changed["tree_hash"] == provenance["tree_hash"]
    assert changed["skipped_hash"] != provenance["skipped_hash"]
    assert changed["provenance_hash"] != provenance["provenance_hash"]


def test_problem_provenance_redacts_secret_like_file_paths(tmp_path):
    token = "sk-" + "proj_" + "treepathsecret1234567890"  # pragma: allowlist secret
    secret_path = f"nested/api_key={token}.txt"
    (tmp_path / "nested").mkdir()
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")
    (tmp_path / secret_path).write_text("secret name only", encoding="utf-8")

    provenance = problem_provenance(tmp_path)

    records = {record["path"]: record for record in provenance["files"]}
    rendered = "\n".join(records)
    assert token not in rendered
    redacted_path = "nested/api_key=[REDACTED]"
    assert redacted_path in records
    assert records[redacted_path]["path_redacted"] is True
    assert len(records[redacted_path]["path_hash"]) == 64


def test_problem_provenance_redacts_and_hashes_root(tmp_path):
    token = "sk-" + "proj_" + "provenancerootsecret1234567890"  # pragma: allowlist secret
    problem_root = tmp_path / f"api_key={token}"
    problem_root.mkdir()
    (problem_root / "task_description.txt").write_text("task", encoding="utf-8")

    provenance = problem_provenance(problem_root)
    rendered = json.dumps(provenance, sort_keys=True)

    assert provenance["root"] == "<problem-root>"
    assert provenance["root_scope"] == "local_root_label"
    assert provenance["root_redacted"] is True
    assert len(provenance["root_hash"]) == 64
    assert token not in rendered
    assert str(problem_root) not in rendered


def test_problem_provenance_normalizes_unicode_file_paths(tmp_path):
    decomposed_path = "nested/cafe\u0301.txt"
    canonical_path = "nested/caf\u00e9.txt"
    (tmp_path / "nested").mkdir()
    path = tmp_path / decomposed_path
    path.write_text("accented", encoding="utf-8")
    if path.name != "cafe\u0301.txt":
        pytest.skip("filesystem normalizes Unicode filenames")
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")

    provenance = problem_provenance(tmp_path)

    records = {record["path"]: record for record in provenance["files"]}
    assert canonical_path in records
    assert decomposed_path not in records
    assert records[canonical_path]["filesystem_path"] == decomposed_path
    assert records[canonical_path]["path_normalization"] == "NFC"
    assert records[canonical_path]["path_normalized"] is True
    assert len(records[canonical_path]["filesystem_path_hash"]) == 64
    json.dumps(provenance, sort_keys=True)


def test_problem_provenance_escapes_format_controls_in_file_paths(tmp_path):
    unsafe_path = "nested/evil\u202e.py"
    ordinary_unicode_path = "nested/caf\u00e9.py"
    (tmp_path / "nested").mkdir()
    (tmp_path / unsafe_path).write_text("unsafe", encoding="utf-8")
    (tmp_path / ordinary_unicode_path).write_text("ordinary", encoding="utf-8")

    provenance = problem_provenance(tmp_path)

    rendered = json.dumps(provenance, ensure_ascii=False, sort_keys=True)
    records = {record["path"]: record for record in provenance["files"]}
    safe_path = "nested/evil[U+202E].py"
    assert "\u202e" not in rendered
    assert ordinary_unicode_path in records
    assert safe_path in records
    assert records[safe_path]["filesystem_path"] == safe_path
    assert records[safe_path]["path_unsafe_chars_redacted"] is True
    assert len(records[safe_path]["filesystem_path_hash"]) == 64


def test_problem_provenance_rejects_unicode_equivalent_file_paths(tmp_path):
    (tmp_path / "caf\u00e9.txt").write_text("one", encoding="utf-8")
    (tmp_path / "cafe\u0301.txt").write_text("two", encoding="utf-8")
    if len([path for path in tmp_path.iterdir() if path.is_file()]) < 2:
        pytest.skip("filesystem normalizes Unicode filenames")

    with pytest.raises(
        ValueError,
        match="duplicate problem provenance path after Unicode normalization",
    ):
        problem_provenance(tmp_path)


def test_problem_provenance_normalizes_unicode_skipped_paths(tmp_path):
    decomposed_path = "runs/cafe\u0301"
    canonical_path = "runs/caf\u00e9"
    skipped_dir = tmp_path / decomposed_path
    skipped_dir.mkdir(parents=True)
    if skipped_dir.name != "cafe\u0301":
        pytest.skip("filesystem normalizes Unicode filenames")
    (skipped_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")

    provenance = problem_provenance(tmp_path, generated_roots=[skipped_dir])

    assert provenance["skipped"] == [
        {
            "path": canonical_path,
            "filesystem_path": decomposed_path,
            "filesystem_path_hash": provenance["skipped"][0]["filesystem_path_hash"],
            "path_normalization": "NFC",
            "path_normalized": True,
            "reason": "excluded_output_root",
        }
    ]
    assert len(provenance["skipped"][0]["filesystem_path_hash"]) == 64


def test_problem_provenance_escapes_format_controls_in_skipped_paths(tmp_path):
    skipped_dir = tmp_path / "runs" / "evil\u202e"
    skipped_dir.mkdir(parents=True)
    (skipped_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")

    provenance = problem_provenance(tmp_path, generated_roots=[skipped_dir])

    rendered = json.dumps(provenance, ensure_ascii=False, sort_keys=True)
    skipped = provenance["skipped"][0]
    assert "\u202e" not in rendered
    assert skipped["path"] == "runs/evil[U+202E]"
    assert skipped["filesystem_path"] == "runs/evil[U+202E]"
    assert skipped["path_unsafe_chars_redacted"] is True
    assert len(skipped["filesystem_path_hash"]) == 64


def test_tree_provenance_rejects_unicode_equivalent_source_paths(tmp_path):
    (tmp_path / "caf\u00e9.py").write_text("one", encoding="utf-8")
    (tmp_path / "cafe\u0301.py").write_text("two", encoding="utf-8")
    if len([path for path in tmp_path.iterdir() if path.is_file()]) < 2:
        pytest.skip("filesystem normalizes Unicode filenames")

    with pytest.raises(
        ValueError,
        match="duplicate libreevolve provenance path after Unicode normalization",
    ):
        provenance_module._tree_provenance(
            tmp_path,
            label="libreevolve",
            excluded_dirs=set(),
            excluded_roots=[],
        )


def test_problem_provenance_redacts_secret_like_skipped_paths(tmp_path):
    token = "sk-" + "proj_" + "skippedpathsecret1234567890"  # pragma: allowlist secret
    skipped_dir = tmp_path / f"api_key={token}"
    skipped_dir.mkdir()
    (skipped_dir / "artifact.txt").write_text("generated", encoding="utf-8")
    (tmp_path / "task_description.txt").write_text("task", encoding="utf-8")

    provenance = problem_provenance(tmp_path, generated_roots=[skipped_dir])

    skipped = provenance["skipped"][0]
    assert token not in skipped["path"]
    assert skipped["path"] == "api_key=[REDACTED]"
    assert skipped["path_redacted"] is True
    assert len(skipped["path_hash"]) == 64
    assert skipped["reason"] == "excluded_output_root"


def test_plugin_provenance_records_plugin_module_hash():
    class LocalPlugin:
        pass

    records = plugin_provenance([LocalPlugin()])
    assert records[0]["class"].endswith("LocalPlugin")
    assert records[0]["index"] == 0
    assert records[0]["instance_id"].startswith("plugin:0:")
    assert records[0]["instance_id"].endswith(records[0]["class"])
    assert records[0]["path"] == "tests/core/test_provenance.py"
    assert records[0]["path_scope"] == "project_relative"
    assert records[0]["path_redacted"] is True
    assert len(records[0]["path_hash"]) == 64
    assert records[0]["status"] == "ok"
    assert records[0]["max_file_bytes"] == 1_000_000
    assert len(records[0]["sha256"]) == 64
    assert records[0]["version"] == {"status": "missing"}


def test_plugin_provenance_records_instance_class_and_module_versions(tmp_path):
    class InstanceVersionPlugin:
        __version__ = "1.0-class"

        def __init__(self):
            self.__version__ = "2.0-instance"

    class ClassVersionPlugin:
        __version__ = "3.0-class"

    module_name = "versioned_plugin_for_test"
    module = ModuleType(module_name)
    module.__version__ = "4.0-module"
    sys.modules[module_name] = module
    try:
        ModuleVersionPlugin = type("ModuleVersionPlugin", (), {"__module__": module_name})
        records = plugin_provenance(
            [InstanceVersionPlugin(), ClassVersionPlugin(), ModuleVersionPlugin()]
        )
    finally:
        sys.modules.pop(module_name, None)

    assert records[0]["version"] == {
        "status": "present",
        "source": "instance",
        "value": "2.0-instance",
    }
    assert records[1]["version"] == {
        "status": "present",
        "source": "class",
        "value": "3.0-class",
    }
    assert records[2]["version"] == {
        "status": "present",
        "source": "module",
        "value": "4.0-module",
    }


def test_plugin_provenance_redacts_secret_like_plugin_versions():
    secret = "sk-proj_pluginversion_secret_1234567890"  # pragma: allowlist secret

    class VersionedPlugin:
        __version__ = f"api_key={secret}"

    record = plugin_provenance([VersionedPlugin()])[0]

    assert secret not in repr(record)
    assert record["version"]["status"] == "present"
    assert record["version"]["value"] == "api_key=[REDACTED]"
    assert record["version"]["version_secret_redacted"] is True
    assert len(record["version"]["version_hash"]) == 64


def test_plugin_provenance_redacts_external_module_paths(tmp_path):
    token = "sk-" + "proj_" + "pluginpathsecret1234567890"  # pragma: allowlist secret
    plugin_file = tmp_path / f"api_key={token}.py"
    plugin_file.write_text("class ExternalPlugin: pass\n", encoding="utf-8")
    module_name = "external_secret_plugin_for_test"
    module = ModuleType(module_name)
    module.__file__ = str(plugin_file)
    sys.modules[module_name] = module
    try:
        ExternalPlugin = type("ExternalPlugin", (), {"__module__": module_name})
        records = plugin_provenance([ExternalPlugin()])
    finally:
        sys.modules.pop(module_name, None)

    assert records[0]["path"].startswith("<external>/")
    assert records[0]["path_scope"] == "external_file_name"
    assert records[0]["path_redacted"] is True
    assert len(records[0]["path_hash"]) == 64
    assert records[0]["status"] == "ok"
    assert len(records[0]["sha256"]) == 64
    rendered = repr(records[0])
    assert token not in rendered
    assert str(tmp_path) not in rendered


def test_plugin_provenance_escapes_format_controls_in_external_module_path(tmp_path):
    plugin_file = tmp_path / "plugin\u202e.py"
    plugin_file.write_text("class ExternalPlugin: pass\n", encoding="utf-8")
    module_name = "external_unsafe_plugin_path_for_test"
    module = ModuleType(module_name)
    module.__file__ = str(plugin_file)
    sys.modules[module_name] = module
    try:
        ExternalPlugin = type("ExternalPlugin", (), {"__module__": module_name})
        records = plugin_provenance([ExternalPlugin()])
    finally:
        sys.modules.pop(module_name, None)

    rendered = json.dumps(records[0], ensure_ascii=False, sort_keys=True)
    assert "\u202e" not in rendered
    assert records[0]["path"] == "<external>/plugin[U+202E].py"
    assert records[0]["path_unsafe_chars_redacted"] is True
    assert len(records[0]["path_hash"]) == 64


def test_plugin_provenance_skips_large_external_module_files(tmp_path):
    plugin_file = tmp_path / "large_plugin.py"
    plugin_file.write_bytes(b"x" * 1_000_001)
    module_name = "large_external_plugin_for_test"
    module = ModuleType(module_name)
    module.__file__ = str(plugin_file)
    sys.modules[module_name] = module
    try:
        LargePlugin = type("LargePlugin", (), {"__module__": module_name})
        records = plugin_provenance([LargePlugin()])
    finally:
        sys.modules.pop(module_name, None)

    assert records[0]["status"] == "skipped_max_file_bytes"
    assert records[0]["bytes"] == 1_000_001
    assert records[0]["max_bytes"] == 1_000_000
    assert records[0]["max_file_bytes"] == 1_000_000
    assert "sha256" not in records[0]


def test_plugin_provenance_records_module_read_errors(tmp_path, monkeypatch):
    token = "sk-" + "proj_" + "pluginreadsecret1234567890"  # pragma: allowlist secret
    plugin_file = tmp_path / "unreadable_plugin.py"
    plugin_file.write_text("class UnreadablePlugin: pass\n", encoding="utf-8")
    module_name = "unreadable_external_plugin_for_test"
    module = ModuleType(module_name)
    module.__file__ = str(plugin_file)
    sys.modules[module_name] = module
    original = Path.read_bytes

    def fake_read_bytes(path):
        if path == plugin_file:
            raise PermissionError(f"cannot read token={token}")
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", fake_read_bytes)
    try:
        UnreadablePlugin = type("UnreadablePlugin", (), {"__module__": module_name})
        records = plugin_provenance([UnreadablePlugin()])
    finally:
        sys.modules.pop(module_name, None)

    assert records[0]["status"] == "read_error"
    assert records[0]["reason"] == "read_error"
    assert records[0]["error_type"] == "PermissionError"
    assert token not in repr(records[0])
    assert "sha256" not in records[0]


def test_plugin_provenance_handles_missing_module_file():
    MissingModulePlugin = type("MissingModulePlugin", (), {"__module__": "missing_plugin_module"})

    records = plugin_provenance([MissingModulePlugin()])

    assert records[0]["class"] == "missing_plugin_module.MissingModulePlugin"
    assert records[0]["path"] is None
    assert records[0]["status"] == "missing_module_file"
    assert "sha256" not in records[0]


def test_plugin_provenance_redacts_secret_like_identity_labels():
    secret = "sk-proj_pluginidentity_secret_1234567890"  # pragma: allowlist secret
    SecretPlugin = type(f"api_key={secret}", (), {"__module__": f"api_key={secret}"})

    records = plugin_provenance([SecretPlugin()])
    record = records[0]

    rendered = repr(record)
    assert secret not in rendered
    assert record["plugin"] == "api_key=[REDACTED]"
    assert record["module"] == "api_key=[REDACTED]"
    assert record["class"].startswith("api_key=[REDACTED]")
    assert record["plugin_secret_redacted"] is True
    assert record["module_secret_redacted"] is True
    assert record["class_secret_redacted"] is True
    assert record["instance_id_redacted"] is True
    assert len(record["plugin_hash"]) == 64
    assert len(record["module_hash"]) == 64
    assert len(record["class_hash"]) == 64
    assert len(record["instance_id_hash"]) == 64
    assert record["status"] == "missing_module_file"


def test_plugin_provenance_escapes_unicode_format_controls_in_identity_labels():
    UnsafePlugin = type("Safe\u202eName", (), {"__module__": "plugins.safe\u202emodule"})

    record = plugin_provenance([UnsafePlugin()])[0]

    assert "\u202e" not in repr(record)
    assert "[U+202E]" in record["plugin"]
    assert "[U+202E]" in record["module"]
    assert record["plugin_unsafe_chars_redacted"] is True
    assert record["module_unsafe_chars_redacted"] is True
    assert record["class_unsafe_chars_redacted"] is True
    assert len(record["class_hash"]) == 64


def test_plugin_provenance_truncates_long_identity_labels():
    long_name = "Plugin" + ("A" * 320)
    LongPlugin = type(long_name, (), {"__module__": "long_plugin_module"})

    record = plugin_provenance([LongPlugin()])[0]

    assert len(record["plugin"]) == 240
    assert record["plugin"].endswith("...<truncated>")
    assert record["plugin_truncated"] is True
    assert record["plugin_max_chars"] == 240
    assert record["class_truncated"] is True
    assert len(record["plugin_hash"]) == 64


def test_plugin_provenance_disambiguates_repeated_plugin_instances():
    class RepeatedPlugin:
        pass

    records = plugin_provenance([RepeatedPlugin(), RepeatedPlugin()])

    assert [record["index"] for record in records] == [0, 1]
    assert records[0]["class"] == records[1]["class"]
    assert records[0]["instance_id"] != records[1]["instance_id"]
    assert records[0]["instance_id"].startswith("plugin:0:")
    assert records[1]["instance_id"].startswith("plugin:1:")


def test_git_state_redacts_and_hashes_dirty_status_paths(tmp_path):
    result = subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, text=True)
    if result.returncode != 0:
        pytest.skip(f"git init unavailable: {result.stderr or result.stdout}")
    subprocess.run(["git", "config", "user.email", "test@example.test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True)
    ordinary = tmp_path / "ordinary.txt"
    renamed = tmp_path / "renamed.txt"
    ordinary.write_text("first", encoding="utf-8")
    subprocess.run(["git", "add", "ordinary.txt"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True)

    ordinary.write_text("changed", encoding="utf-8")
    subprocess.run(["git", "mv", "ordinary.txt", "renamed.txt"], cwd=tmp_path, check=True)
    renamed.write_text("renamed changed", encoding="utf-8")
    secret_token = "sk-" + "proj_" + "dirtysecret1234567890"  # pragma: allowlist secret
    secret_name = f"api_key={secret_token}.txt"
    (tmp_path / secret_name).write_text("local", encoding="utf-8")

    state = git_state(tmp_path)

    assert state["available"] is True
    assert state["dirty"] is True
    assert state["status_entry_count"] == len(state["status_entries"])
    assert state["status_entry_count"] == len(state["status_entry_hashes"])
    assert state["status_entries_redacted"] is True
    assert all(len(digest) == 64 for digest in state["status_entry_hashes"])
    rendered = "\n".join(state["status_entries"])
    assert secret_token not in rendered
    assert "[REDACTED]" in rendered
    assert "renamed.txt" in rendered


def test_git_state_escapes_format_controls_in_dirty_status_entries(monkeypatch, tmp_path):
    def fake_git(args, cwd):
        if args == ["rev-parse", "--show-toplevel"]:
            return str(tmp_path)
        if args == ["rev-parse", "HEAD"]:
            return "abc123"
        if args == ["status", "--porcelain"]:
            return "?? caf\u00e9.py\n?? evil\u202e.py"
        raise AssertionError(args)

    monkeypatch.setattr(provenance_module, "_git", fake_git)

    state = git_state(tmp_path)

    rendered = json.dumps(state, ensure_ascii=False, sort_keys=True)
    assert "\u202e" not in rendered
    assert state["status_entries"] == ["?? caf\u00e9.py", "?? evil[U+202E].py"]
    assert state["status_entries_redacted"] is True
    assert state["status_entries_unsafe_chars_redacted"] is True
    assert len(state["status_entry_hashes"]) == 2


def test_git_state_redacts_and_hashes_root(tmp_path):
    token = "sk-" + "proj_" + "gitrootsecret1234567890"  # pragma: allowlist secret
    repo = tmp_path / f"api_key={token}"
    repo.mkdir()
    result = subprocess.run(["git", "init"], cwd=repo, capture_output=True, text=True)
    if result.returncode != 0:
        pytest.skip(f"git init unavailable: {result.stderr or result.stdout}")

    state = git_state(repo)
    rendered = json.dumps(state, sort_keys=True)

    assert state["available"] is True
    assert state["root"] == "<git-root>"
    assert state["root_scope"] == "local_root_label"
    assert state["root_redacted"] is True
    assert len(state["root_hash"]) == 64
    assert token not in rendered
    assert str(repo) not in rendered


def test_runtime_environment_provenance_records_python_package_and_dependencies(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        """
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "sample-project"
version = "1.2.3"
requires-python = ">=3.12"
dependencies = ["click>=8.1", "missing-dep-for-test>=99"]
""".strip(),
        encoding="utf-8",
    )

    provenance = runtime_environment_provenance(tmp_path)

    assert provenance["python"]["version"]
    assert provenance["platform"]["system"]
    assert provenance["package"]["name"] == "sample-project"
    assert provenance["package"]["version"] == "1.2.3"
    assert provenance["package"]["requires_python"] == ">=3.12"
    assert provenance["package"]["pyproject"]["path"] == "pyproject.toml"
    assert provenance["package"]["pyproject"]["status"] == "ok"
    assert len(provenance["package"]["pyproject"]["sha256"]) == 64
    assert provenance["package"]["build_system"] == {
        "build_backend": "setuptools.build_meta",
        "requires": ["setuptools>=68"],
    }
    assert provenance["package"]["installed_version_name"] == "sample-project"
    deps = {dep["name"]: dep for dep in provenance["dependencies"]}
    assert deps["click"]["name_hash"] == hashlib.sha256(b"click").hexdigest()
    assert deps["click"]["name_redacted"] is False
    assert deps["click"]["installed_version_lookup_name"] == "click"
    assert deps["click"]["installed_version_lookup_redacted"] is False
    assert deps["click"]["spec"] == "click>=8.1"
    assert deps["click"]["installed_version"]
    assert deps["missing-dep-for-test"]["installed_version"] is None


def test_runtime_environment_provenance_records_extended_project_metadata(tmp_path):
    secret = "sk-proj_projectmeta_secret_1234567890"  # pragma: allowlist secret
    (tmp_path / "pyproject.toml").write_text(
        f"""
[project]
name = "sample-project"
version = "1.2.3"
license = {{text = "MIT api_key={secret}"}}
authors = [{{name = "Ada Lovelace", email = "ada@example.test"}}]
maintainers = [{{name = "Release Team"}}]
classifiers = ["Programming Language :: Python :: 3"]
keywords = ["evolution", "api_key={secret}"]
dependencies = []

[project.urls]
Homepage = "https://example.test"

[project.optional-dependencies]
test = ["pytest>=9"]

[project.scripts]
sample-tool = "sample:main"

[project.gui-scripts]
sample-gui = "sample:gui"

[project.entry-points."libreevolve.plugins"]
sample-plugin = "sample.plugin:Plugin"
""".strip(),
        encoding="utf-8",
    )

    package = runtime_environment_provenance(tmp_path)["package"]
    rendered = json.dumps(package, sort_keys=True)

    assert package["license"]["text"] == "MIT api_key=[REDACTED]"
    assert package["license"]["text_secret_redacted"] is True
    assert package["authors"] == [
        {"name": "Ada Lovelace", "email": "ada@example.test"}
    ]
    assert package["maintainers"] == [{"name": "Release Team"}]
    assert package["classifiers"][0]["value"] == "Programming Language :: Python :: 3"
    assert len(package["classifiers"][0]["hash"]) == 64
    assert package["keywords"][0]["value"] == "evolution"
    assert package["keywords"][1]["value"] == "api_key=[REDACTED]"
    assert package["keywords"][1]["keyword_secret_redacted"] is True
    assert package["urls"] == [
        {
            "label": "Homepage",
            "label_hash": hashlib.sha256(b"Homepage").hexdigest(),
            "value": "https://example.test",
            "value_hash": hashlib.sha256(b"https://example.test").hexdigest(),
        }
    ]
    assert package["optional_dependencies"] == [
        {
            "group": "test",
            "group_hash": hashlib.sha256(b"test").hexdigest(),
            "requirements": [
                {
                    "spec": "pytest>=9",
                    "spec_hash": hashlib.sha256(b"pytest>=9").hexdigest(),
                }
            ],
        }
    ]
    assert package["scripts"][0]["label"] == "sample-tool"
    assert package["scripts"][0]["value"] == "sample:main"
    assert package["gui_scripts"][0]["label"] == "sample-gui"
    assert package["gui_scripts"][0]["value"] == "sample:gui"
    assert package["entry_points"] == [
        {
            "group": "libreevolve.plugins",
            "group_hash": hashlib.sha256(b"libreevolve.plugins").hexdigest(),
            "entries": [
                {
                    "label": "sample-plugin",
                    "label_hash": hashlib.sha256(b"sample-plugin").hexdigest(),
                    "value": "sample.plugin:Plugin",
                    "value_hash": hashlib.sha256(b"sample.plugin:Plugin").hexdigest(),
                }
            ],
        }
    ]
    assert secret not in rendered


def test_runtime_environment_provenance_records_extra_project_metadata(
    tmp_path,
):
    secret = "sk-proj_extra_project_secret_1234567890"  # pragma: allowlist secret
    (tmp_path / "pyproject.toml").write_text(
        f"""
[project]
name = "sample-project"
version = "1.2.3"
description = "api_key={secret}"
dynamic = ["version", "classifiers"]
dependencies = []

[project.readme]
text = "README\\u202e"
content-type = "text/markdown"

[project.local-extra]
enabled = true
count = 7
labels = ["safe", "token={secret}"]
""".strip(),
        encoding="utf-8",
    )

    extra = runtime_environment_provenance(tmp_path)["package"]["extra_project_metadata"]
    entries = {record["label"]: record for record in extra["entries"]}
    rendered = json.dumps(extra, ensure_ascii=False, sort_keys=True)

    assert extra["policy"] == "bounded_pyproject_project_extra_metadata_v1"
    assert extra["key_count"] == 4
    assert extra["omitted_key_count"] == 0
    assert len(extra["hash"]) == 64
    assert extra["hash_scope"] == "raw_pyproject_project_extra_metadata_v1"
    assert entries["description"]["value"]["value"] == "api_key=[REDACTED]"
    assert entries["description"]["value"]["value_secret_redacted"] is True
    assert entries["dynamic"]["value"]["type"] == "list"
    assert entries["dynamic"]["value"]["items"][0]["value"] == "version"
    assert entries["readme"]["value"]["type"] == "table"
    readme_entries = {
        record["label"]: record
        for record in entries["readme"]["value"]["entries"]
    }
    assert readme_entries["text"]["value"]["value"] == "README[U+202E]"
    assert readme_entries["text"]["value"]["value_unsafe_chars_redacted"] is True
    local_extra = {
        record["label"]: record
        for record in entries["local-extra"]["value"]["entries"]
    }
    assert local_extra["enabled"]["value"] == {"type": "boolean", "value": True}
    assert local_extra["count"]["value"] == {"type": "integer", "value": 7}
    assert local_extra["labels"]["value"]["items"][1]["value"] == "token=[REDACTED]"
    assert secret not in rendered
    assert "\u202e" not in rendered


def test_runtime_environment_provenance_bounds_extra_project_metadata(
    tmp_path,
    monkeypatch,
):
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "sample-project"
version = "1.2.3"
dependencies = []
alpha = "one"
beta = ["first", "second"]
gamma = "three"
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(provenance_module, "_PYPROJECT_EXTRA_METADATA_MAX_KEYS", 2)
    monkeypatch.setattr(provenance_module, "_PYPROJECT_EXTRA_METADATA_MAX_ITEMS", 1)

    first = runtime_environment_provenance(tmp_path)["package"]["extra_project_metadata"]
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "sample-project"
version = "1.2.3"
dependencies = []
alpha = "changed"
beta = ["first", "second"]
gamma = "three"
""".strip(),
        encoding="utf-8",
    )
    second = runtime_environment_provenance(tmp_path)["package"]["extra_project_metadata"]

    entries = {record["label"]: record for record in first["entries"]}
    assert first["key_count"] == 3
    assert first["max_keys"] == 2
    assert first["omitted_key_count"] == 1
    assert [record["label"] for record in first["entries"]] == ["alpha", "beta"]
    assert entries["beta"]["value"]["item_count"] == 2
    assert entries["beta"]["value"]["max_items"] == 1
    assert entries["beta"]["value"]["omitted_item_count"] == 1
    assert first["hash"] != second["hash"]


def test_runtime_environment_provenance_records_known_lockfile_hashes(tmp_path):
    requirements = tmp_path / "requirements.txt"
    uv_lock = tmp_path / "uv.lock"
    requirements.write_text("click==8.1.8\n", encoding="utf-8")
    uv_lock.write_text("version = 1\n", encoding="utf-8")

    first = runtime_environment_provenance(tmp_path)
    uv_lock.write_text("version = 2\n", encoding="utf-8")
    second = runtime_environment_provenance(tmp_path)

    lockfiles = first["lockfiles"]
    records = {record["path"]: record for record in lockfiles["files"]}
    assert lockfiles["policy"] == "known_project_lockfiles_v1"
    assert lockfiles["candidate_paths"] == [
        "requirements.txt",
        "requirements.lock",
        "uv.lock",
        "poetry.lock",
        "pdm.lock",
        "Pipfile.lock",
    ]
    assert lockfiles["file_count"] == 2
    assert records["requirements.txt"]["status"] == "ok"
    assert records["requirements.txt"]["sha256"] == hashlib.sha256(
        requirements.read_bytes()
    ).hexdigest()
    assert records["uv.lock"]["status"] == "ok"
    assert first["lockfiles"]["hash"] != second["lockfiles"]["hash"]


def test_runtime_environment_provenance_records_installed_package_snapshot(
    tmp_path,
    monkeypatch,
):
    class FakeDistribution:
        def __init__(self, name, version):
            self.metadata = {"Name": name}
            self.version = version

    monkeypatch.setattr(
        provenance_module.metadata,
        "distributions",
        lambda: [
            FakeDistribution("pytest", "9.0.3"),
            FakeDistribution("scipy", "1.17.1"),
            FakeDistribution("caf\u00e9-lib", "1.0"),
        ],
    )

    first = runtime_environment_provenance(tmp_path)
    monkeypatch.setattr(
        provenance_module.metadata,
        "distributions",
        lambda: [
            FakeDistribution("pytest", "9.0.3"),
            FakeDistribution("scipy", "1.17.2"),
            FakeDistribution("caf\u00e9-lib", "1.0"),
        ],
    )
    second = runtime_environment_provenance(tmp_path)

    snapshot = first["installed_packages"]
    packages = {record["name"]: record for record in snapshot["packages"]}
    assert snapshot["policy"] == "installed_distribution_names_versions_wheel_source_metadata_v1"
    assert snapshot["package_count"] == 3
    assert snapshot["omitted_count"] == 0
    assert snapshot["diagnostics"] == []
    assert packages["pytest"]["version"] == "9.0.3"
    assert packages["pytest"]["wheel_metadata"]["status"] == "missing"
    assert packages["pytest"]["source_metadata"]["direct_url"]["status"] == "missing"
    assert packages["pytest"]["source_metadata"]["installer"]["status"] == "missing"
    assert packages["pytest"]["source_metadata"]["record"]["status"] == "missing"
    assert packages["scipy"]["version"] == "1.17.1"
    assert packages["caf\u00e9-lib"]["name"] == "caf\u00e9-lib"
    assert len(packages["pytest"]["name_hash"]) == 64
    assert len(packages["pytest"]["version_hash"]) == 64
    assert first["installed_packages"]["hash"] != second["installed_packages"]["hash"]


def test_runtime_environment_provenance_sanitizes_installed_package_snapshot(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_installedpkg_secret_1234567890"  # pragma: allowlist secret

    class FakeDistribution:
        metadata = {"Name": f"api-key-{secret}"}
        version = "1.0\u202e"

    monkeypatch.setattr(
        provenance_module.metadata,
        "distributions",
        lambda: [FakeDistribution()],
    )

    provenance = runtime_environment_provenance(tmp_path)

    package = provenance["installed_packages"]["packages"][0]
    rendered = json.dumps(provenance, ensure_ascii=False, sort_keys=True)
    assert secret not in rendered
    assert "\u202e" not in rendered
    assert package["name"] == "api-key-[REDACTED]"
    assert package["name_redacted"] is True
    assert package["name_secret_redacted"] is True
    assert package["version"] == "1.0[U+202E]"
    assert package["version_redacted"] is True
    assert package["version_unsafe_chars_redacted"] is True


def test_runtime_environment_provenance_records_distribution_wheel_metadata(
    tmp_path,
    monkeypatch,
):
    wheel_text = (
        "Wheel-Version: 1.0\n"
        "Generator: bdist_wheel 0.43.0\n"
        "Root-Is-Purelib: true\n"
        "Tag: py3-none-any\n"
        "Tag: cp312-cp312-win_amd64\n"
    )

    class FakeDistribution:
        metadata = {"Name": "demo"}
        version = "1.0"

        def read_text(self, name):
            if name == "WHEEL":
                return wheel_text
            return None

    monkeypatch.setattr(
        provenance_module.metadata,
        "distributions",
        lambda: [FakeDistribution()],
    )

    package = runtime_environment_provenance(tmp_path)["installed_packages"]["packages"][0]
    wheel = package["wheel_metadata"]

    assert wheel["status"] == "ok"
    assert wheel["metadata_sha256"] == hashlib.sha256(
        wheel_text.encode("utf-8")
    ).hexdigest()
    assert wheel["wheel_version"] == "1.0"
    assert wheel["generator"] == "bdist_wheel 0.43.0"
    assert wheel["root_is_purelib"] is True
    assert wheel["tag_count"] == 2
    assert wheel["omitted_tag_count"] == 0
    assert wheel["tags"] == [
        {
            "value": "py3-none-any",
            "hash": hashlib.sha256(b"py3-none-any").hexdigest(),
            "redacted": False,
        },
        {
            "value": "cp312-cp312-win_amd64",
            "hash": hashlib.sha256(b"cp312-cp312-win_amd64").hexdigest(),
            "redacted": False,
        },
    ]


def test_runtime_environment_provenance_records_distribution_source_metadata(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_directurl_secret_1234567890"  # pragma: allowlist secret
    direct_url = {
        "url": f"https://example.invalid/simple/demo?token={secret}",
        "vcs_info": {"vcs": "git", "commit_id": "abc123"},
        "dir_info": {"editable": True},
    }
    installer_text = "pip\n"
    record_text = "demo/__init__.py,sha256=abc,12\ndemo-1.0.dist-info/WHEEL,,\n"

    class FakeDistribution:
        metadata = {"Name": "demo"}
        version = "1.0"

        def read_text(self, name):
            if name == "direct_url.json":
                return json.dumps(direct_url)
            if name == "INSTALLER":
                return installer_text
            if name == "RECORD":
                return record_text
            return None

    monkeypatch.setattr(
        provenance_module.metadata,
        "distributions",
        lambda: [FakeDistribution()],
    )

    package = runtime_environment_provenance(tmp_path)["installed_packages"]["packages"][0]
    source = package["source_metadata"]
    rendered = json.dumps(source, sort_keys=True)

    assert source["policy"] == "installed_distribution_source_metadata_v1"
    assert source["direct_url"]["status"] == "ok"
    assert source["direct_url"]["url"] == "https://example.invalid/simple/demo?token=[REDACTED]"
    assert source["direct_url"]["url_secret_redacted"] is True
    assert source["direct_url"]["url_hash"] == hashlib.sha256(
        direct_url["url"].encode("utf-8")
    ).hexdigest()
    assert source["direct_url"]["vcs_info"]["status"] == "hash_only"
    assert source["direct_url"]["dir_info"]["status"] == "hash_only"
    assert source["installer"]["status"] == "ok"
    assert source["installer"]["installer"] == "pip"
    assert source["record"]["status"] == "ok"
    assert source["record"]["line_count"] == 2
    assert source["record"]["metadata_sha256"] == hashlib.sha256(
        record_text.encode("utf-8")
    ).hexdigest()
    assert secret not in rendered


def test_runtime_environment_provenance_sanitizes_and_bounds_wheel_metadata(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_wheel_secret_1234567890"  # pragma: allowlist secret
    wheel_text = (
        "Wheel-Version: 1.0\n"
        f"Generator: api_key={secret}\n"
        "Root-Is-Purelib: maybe\u202e\n"
        "Tag: py3-none-any\u202e\n"
        "Tag: cp312-cp312-win_amd64\n"
    )

    class FakeDistribution:
        metadata = {"Name": "demo"}
        version = "1.0"

        def read_text(self, name):
            if name == "WHEEL":
                return wheel_text
            return None

    monkeypatch.setattr(provenance_module, "_INSTALLED_PACKAGE_WHEEL_MAX_TAGS", 1)
    monkeypatch.setattr(
        provenance_module.metadata,
        "distributions",
        lambda: [FakeDistribution()],
    )

    wheel = runtime_environment_provenance(tmp_path)["installed_packages"]["packages"][0][
        "wheel_metadata"
    ]
    rendered = json.dumps(wheel, ensure_ascii=False, sort_keys=True)

    assert wheel["tag_count"] == 2
    assert wheel["omitted_tag_count"] == 1
    assert wheel["generator"] == "api_key=[REDACTED]"
    assert wheel["generator_secret_redacted"] is True
    assert wheel["root_is_purelib"] is None
    assert wheel["root_is_purelib_raw"] == "maybe[U+202E]"
    assert wheel["root_is_purelib_unsafe_chars_redacted"] is True
    assert wheel["tags"][0]["value"] == "py3-none-any[U+202E]"
    assert wheel["tags"][0]["tag_unsafe_chars_redacted"] is True
    assert secret not in rendered
    assert "\u202e" not in rendered


def test_runtime_environment_provenance_records_wheel_metadata_read_errors(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_wheelread_secret_1234567890"  # pragma: allowlist secret

    class FakeDistribution:
        metadata = {"Name": "demo"}
        version = "1.0"

        def read_text(self, name):
            if name == "WHEEL":
                raise OSError(f"cannot read token={secret}")
            return None

    monkeypatch.setattr(
        provenance_module.metadata,
        "distributions",
        lambda: [FakeDistribution()],
    )

    wheel = runtime_environment_provenance(tmp_path)["installed_packages"]["packages"][0][
        "wheel_metadata"
    ]
    rendered = json.dumps(wheel, sort_keys=True)

    assert wheel["status"] == "read_error"
    assert wheel["error_type"] == "OSError"
    assert wheel["error"] == "cannot read token=[REDACTED]"
    assert wheel["error_redacted"] is True
    assert secret not in rendered


def test_runtime_environment_provenance_bounds_wheel_metadata_file_size(
    tmp_path,
    monkeypatch,
):
    wheel_text = "Wheel-Version: 1.0\n" + ("X" * 32)

    class FakeDistribution:
        metadata = {"Name": "demo"}
        version = "1.0"

        def read_text(self, name):
            if name == "WHEEL":
                return wheel_text
            return None

    monkeypatch.setattr(provenance_module, "_INSTALLED_PACKAGE_WHEEL_MAX_CHARS", 20)
    monkeypatch.setattr(
        provenance_module.metadata,
        "distributions",
        lambda: [FakeDistribution()],
    )

    wheel = runtime_environment_provenance(tmp_path)["installed_packages"]["packages"][0][
        "wheel_metadata"
    ]

    assert wheel["status"] == "skipped_max_chars"
    assert wheel["chars"] == len(wheel_text)
    assert wheel["max_chars"] == 20
    assert wheel["metadata_sha256"] == hashlib.sha256(
        wheel_text.encode("utf-8")
    ).hexdigest()


def test_runtime_environment_provenance_bounds_installed_package_snapshot(
    tmp_path,
    monkeypatch,
):
    class FakeDistribution:
        def __init__(self, name):
            self.metadata = {"Name": name}
            self.version = "1.0"

    monkeypatch.setattr(provenance_module, "_INSTALLED_PACKAGE_SNAPSHOT_MAX_PACKAGES", 2)
    monkeypatch.setattr(
        provenance_module.metadata,
        "distributions",
        lambda: [
            FakeDistribution("pkg-c"),
            FakeDistribution("pkg-a"),
            FakeDistribution("pkg-b"),
        ],
    )

    snapshot = runtime_environment_provenance(tmp_path)["installed_packages"]

    assert snapshot["package_count"] == 3
    assert snapshot["omitted_count"] == 1
    assert [record["name"] for record in snapshot["packages"]] == ["pkg-a", "pkg-b"]
    assert len(snapshot["hash"]) == 64


def test_runtime_environment_provenance_records_distribution_snapshot_errors(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_distread_secret_1234567890"  # pragma: allowlist secret

    def broken_distributions():
        raise RuntimeError(f"cannot inspect api_key={secret}")

    monkeypatch.setattr(provenance_module.metadata, "distributions", broken_distributions)

    snapshot = runtime_environment_provenance(tmp_path)["installed_packages"]

    rendered = json.dumps(snapshot, sort_keys=True)
    assert snapshot["package_count"] == 0
    assert snapshot["packages"] == []
    assert snapshot["diagnostics"][0]["status"] == "unavailable"
    assert snapshot["diagnostics"][0]["error_type"] == "RuntimeError"
    assert snapshot["diagnostics"][0]["error"] == "cannot inspect api_key=[REDACTED]"
    assert snapshot["diagnostics"][0]["error_redacted"] is True
    assert secret not in rendered


def _fake_accelerator_probe_run(args):
    if args and args[0] in {"nvidia-smi", "rocm-smi"}:
        return subprocess.CompletedProcess(args, 1, stdout="", stderr="missing")
    return None


def test_runtime_environment_provenance_records_pip_freeze_snapshot(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_freeze_secret_1234567890"  # pragma: allowlist secret
    stdout = (
        "click==8.1.8\n"
        f"private @ https://user:{secret}@example.test/pkg.whl\n"
        "evil\u202e==1.0\n"
    )

    def fake_run(args, **kwargs):
        probe = _fake_accelerator_probe_run(args)
        if probe is not None:
            return probe
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        assert kwargs["check"] is False
        if args == [sys.executable, "-m", "pip", "config", "list"]:
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        assert args == [sys.executable, "-m", "pip", "freeze", "--all"]
        return subprocess.CompletedProcess(args, 0, stdout=stdout, stderr="")

    monkeypatch.setattr(provenance_module.subprocess, "run", fake_run)

    provenance = runtime_environment_provenance(tmp_path)
    freeze = provenance["pip_freeze"]
    rendered = json.dumps(freeze, ensure_ascii=False, sort_keys=True)

    assert freeze["policy"] == "pip_freeze_all_redacted_bounded_v1"
    assert freeze["status"] == "ok"
    assert freeze["command"] == "python -m pip freeze --all"
    assert freeze["line_count"] == 3
    assert freeze["omitted_line_count"] == 0
    assert freeze["stdout_sha256"] == hashlib.sha256(stdout.encode("utf-8")).hexdigest()
    assert freeze["hash_scope"] == "raw_pip_freeze_stdout_text_v1"
    assert freeze["lines"][0]["line"] == "click==8.1.8"
    assert "[REDACTED]" in freeze["lines"][1]["line"]
    assert freeze["lines"][1]["line_secret_redacted"] is True
    assert freeze["lines"][2]["line"] == "evil[U+202E]==1.0"
    assert freeze["lines"][2]["line_unsafe_chars_redacted"] is True
    assert secret not in rendered
    assert "\u202e" not in rendered


def test_runtime_environment_provenance_bounds_pip_freeze_snapshot(
    tmp_path,
    monkeypatch,
):
    stdout = "pkg-c==1\npkg-a==" + ("x" * 50) + "\npkg-b==1\n"

    def fake_run(args, **kwargs):
        probe = _fake_accelerator_probe_run(args)
        if probe is not None:
            return probe
        if args == [sys.executable, "-m", "pip", "config", "list"]:
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        return subprocess.CompletedProcess(args, 0, stdout=stdout, stderr="")

    monkeypatch.setattr(provenance_module, "_PIP_FREEZE_MAX_LINES", 2)
    monkeypatch.setattr(provenance_module, "_PIP_FREEZE_MAX_LINE_CHARS", 20)
    monkeypatch.setattr(provenance_module.subprocess, "run", fake_run)

    freeze = runtime_environment_provenance(tmp_path)["pip_freeze"]

    assert freeze["line_count"] == 3
    assert freeze["omitted_line_count"] == 1
    assert freeze["max_lines"] == 2
    assert len(freeze["lines"]) == 2
    assert freeze["lines"][1]["line"].endswith("...<truncated>")
    assert freeze["lines"][1]["line_truncated"] is True
    assert len(freeze["stdout_sha256"]) == 64


def test_runtime_environment_provenance_records_pip_freeze_failures(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_freezefail_secret_1234567890"  # pragma: allowlist secret

    def fake_run(args, **kwargs):
        probe = _fake_accelerator_probe_run(args)
        if probe is not None:
            return probe
        if args == [sys.executable, "-m", "pip", "config", "list"]:
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        return subprocess.CompletedProcess(
            args,
            1,
            stdout=f"visible @ https://example.test/pkg?token={secret}\n",
            stderr=f"failed api_key={secret}",
        )

    monkeypatch.setattr(provenance_module.subprocess, "run", fake_run)

    freeze = runtime_environment_provenance(tmp_path)["pip_freeze"]
    rendered = json.dumps(freeze, sort_keys=True)

    assert freeze["status"] == "error"
    assert freeze["returncode"] == 1
    assert len(freeze["stdout_sha256"]) == 64
    assert len(freeze["stderr_sha256"]) == 64
    assert freeze["stderr_preview"] == "failed api_key=[REDACTED]"
    assert secret not in rendered


def test_runtime_environment_provenance_records_pip_freeze_timeout(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_freezetimeout_secret_1234567890"  # pragma: allowlist secret

    def fake_run(args, **kwargs):
        probe = _fake_accelerator_probe_run(args)
        if probe is not None:
            return probe
        raise subprocess.TimeoutExpired(
            args,
            timeout=10.0,
            output=f"api_key={secret}",
            stderr=f"stderr token={secret}",
        )

    monkeypatch.setattr(provenance_module.subprocess, "run", fake_run)

    freeze = runtime_environment_provenance(tmp_path)["pip_freeze"]
    rendered = json.dumps(freeze, sort_keys=True)

    assert freeze["status"] == "timeout"
    assert freeze["timeout_sec"] == 10.0
    assert freeze["error_redacted"] is True
    assert secret not in rendered


def test_runtime_environment_provenance_records_pip_config_snapshot(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_pipconfig_secret_1234567890"  # pragma: allowlist secret
    stdout = (
        "global.index-url='https://pypi.org/simple'\n"
        f"global.extra-index-url='https://user:{secret}@example.test/simple'\n"
        "global.timeout='60\u202e'\n"
    )

    def fake_run(args, **kwargs):
        probe = _fake_accelerator_probe_run(args)
        if probe is not None:
            return probe
        if args == [sys.executable, "-m", "pip", "freeze", "--all"]:
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        assert args == [sys.executable, "-m", "pip", "config", "list"]
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        assert kwargs["check"] is False
        return subprocess.CompletedProcess(args, 0, stdout=stdout, stderr="")

    monkeypatch.setattr(provenance_module.subprocess, "run", fake_run)

    config = runtime_environment_provenance(tmp_path)["pip_config"]
    rendered = json.dumps(config, ensure_ascii=False, sort_keys=True)

    assert config["policy"] == "pip_config_list_redacted_bounded_v1"
    assert config["status"] == "ok"
    assert config["command"] == "python -m pip config list"
    assert config["line_count"] == 3
    assert config["omitted_line_count"] == 0
    assert config["stdout_sha256"] == hashlib.sha256(stdout.encode("utf-8")).hexdigest()
    assert config["hash_scope"] == "raw_pip_config_list_stdout_text_v1"
    assert config["lines"][0]["line"] == "global.index-url='https://pypi.org/simple'"
    assert "[REDACTED]" in config["lines"][1]["line"]
    assert config["lines"][1]["line_secret_redacted"] is True
    assert config["lines"][2]["line"] == "global.timeout='60[U+202E]'"
    assert config["lines"][2]["line_unsafe_chars_redacted"] is True
    assert secret not in rendered
    assert "\u202e" not in rendered


def test_runtime_environment_provenance_records_package_source_policy(
    tmp_path,
    monkeypatch,
):
    (tmp_path / "requirements.txt").write_text("click==8.1.8\n", encoding="utf-8")

    class FakeDistribution:
        metadata = {"Name": "click"}
        version = "8.1.8"

    freeze_stdout = "click==8.1.8\n"
    config_stdout = "global.index-url='https://pypi.org/simple'\n"

    def fake_run(args, **kwargs):
        probe = _fake_accelerator_probe_run(args)
        if probe is not None:
            return probe
        if args == [sys.executable, "-m", "pip", "freeze", "--all"]:
            return subprocess.CompletedProcess(args, 0, stdout=freeze_stdout, stderr="")
        if args == [sys.executable, "-m", "pip", "config", "list"]:
            return subprocess.CompletedProcess(args, 0, stdout=config_stdout, stderr="")
        raise AssertionError(f"unexpected command: {args!r}")

    monkeypatch.setattr(provenance_module.metadata, "distributions", lambda: [FakeDistribution()])
    monkeypatch.setattr(provenance_module.subprocess, "run", fake_run)

    policy = runtime_environment_provenance(tmp_path)["package_source_policy"]

    assert policy["policy"] == "bounded_redacted_package_source_evidence_v1"
    assert policy["status"] == "audit_only"
    assert policy["private_source_interpretation"] == (
        "redacted_retained_lines_plus_raw_stdout_hashes_only"
    )
    assert policy["retention"] == {
        "lockfiles": "hash_only_known_project_root_files",
        "pip_freeze": "bounded_redacted_lines_with_raw_stdout_hash",
        "pip_config": "bounded_redacted_lines_with_raw_stdout_hash",
        "installed_packages": "bounded_name_version_wheel_and_source_metadata_snapshot",
    }
    assert policy["unsupported"] == [
        "private_index_identity_resolution",
        "credential_retention",
        "remote_package_artifact_hash_verification",
        "live_index_availability_or_authentication_check",
        "non_pip_package_manager_source_interpretation",
    ]
    assert policy["evidence"]["lockfiles"]["file_count"] == 1
    assert policy["evidence"]["lockfiles"]["hash_present"] is True
    assert policy["evidence"]["installed_packages"]["package_count"] == 1
    assert policy["evidence"]["installed_packages"]["hash_present"] is True
    assert policy["evidence"]["pip_freeze"]["status"] == "ok"
    assert policy["evidence"]["pip_freeze"]["line_count"] == 1
    assert policy["evidence"]["pip_freeze"]["stdout_sha256_present"] is True
    assert policy["evidence"]["pip_config"]["status"] == "ok"
    assert policy["evidence"]["pip_config"]["line_count"] == 1
    assert policy["evidence"]["pip_config"]["stdout_sha256_present"] is True
    assert policy["hash_scope"] == "package_source_policy_evidence_v1"
    assert len(policy["hash"]) == 64


def test_runtime_environment_provenance_records_environment_reproducibility_policy(
    tmp_path,
    monkeypatch,
):
    (tmp_path / "requirements.txt").write_text("click==8.1.8\n", encoding="utf-8")

    class FakeDistribution:
        metadata = {"Name": "click"}
        version = "8.1.8"

    freeze_stdout = "click==8.1.8\n"
    config_stdout = "global.index-url='https://pypi.org/simple'\n"

    def fake_run(args, **kwargs):
        probe = _fake_accelerator_probe_run(args)
        if probe is not None:
            return probe
        if args == [sys.executable, "-m", "pip", "freeze", "--all"]:
            return subprocess.CompletedProcess(args, 0, stdout=freeze_stdout, stderr="")
        if args == [sys.executable, "-m", "pip", "config", "list"]:
            return subprocess.CompletedProcess(args, 0, stdout=config_stdout, stderr="")
        raise AssertionError(f"unexpected command: {args!r}")

    monkeypatch.setattr(provenance_module.metadata, "distributions", lambda: [FakeDistribution()])
    monkeypatch.setattr(provenance_module.subprocess, "run", fake_run)
    monkeypatch.setattr(
        provenance_module,
        "_llm_provider_sdk_provenance",
        lambda: {
            "policy": "llm_provider_sdk_versions_v1",
            "providers": [],
            "hash": "a" * 64,
            "hash_scope": "configured_builtin_llm_provider_sdk_version_records_v1",
        },
    )

    policy = runtime_environment_provenance(tmp_path)[
        "environment_reproducibility_policy"
    ]

    assert policy["schema"] == "libreevolve.environment_reproducibility_policy.v1"
    assert policy["policy"] == (
        "bounded_environment_evidence_with_explicit_unsupported_surfaces"
    )
    assert policy["status"] == "audit_only_not_complete_replay_environment"
    assert policy["evidence"]["lockfiles"]["file_count"] == 1
    assert len(policy["evidence"]["lockfiles"]["hash"]) == 64
    assert policy["evidence"]["pip_freeze"]["stdout_sha256"] == hashlib.sha256(
        freeze_stdout.encode("utf-8")
    ).hexdigest()
    assert policy["evidence"]["pip_config"]["stdout_sha256"] == hashlib.sha256(
        config_stdout.encode("utf-8")
    ).hexdigest()
    assert policy["evidence"]["package_source_policy"]["hash"]
    assert policy["evidence"]["llm_provider_sdks"]["hash"] == "a" * 64
    assert "live_provider_service_api_version_capture" in policy["unsupported_surfaces"]
    assert "provider_cost_capture" in policy["unsupported_surfaces"]
    assert policy["private_source_policy"] == (
        "bounded_redacted_pip_config_and_freeze_evidence_with_raw_hashes_only"
    )
    assert policy["live_provider_policy"] == (
        "installed_sdk_versions_only_no_live_service_or_account_lookup"
    )
    assert policy["accelerator_policy"] == (
        "bounded_runtime_hints_and_driver_probes_no_budget_accounting"
    )
    assert policy["hash_scope"] == "environment_reproducibility_policy_evidence_v1"
    assert len(policy["hash"]) == 64


def test_environment_reproducibility_policy_hash_changes_with_lockfile_evidence(
    tmp_path,
    monkeypatch,
):
    (tmp_path / "requirements.txt").write_text("click==8.1.8\n", encoding="utf-8")

    def fake_run(args, **kwargs):
        probe = _fake_accelerator_probe_run(args)
        if probe is not None:
            return probe
        if args == [sys.executable, "-m", "pip", "freeze", "--all"]:
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        if args == [sys.executable, "-m", "pip", "config", "list"]:
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        raise AssertionError(f"unexpected command: {args!r}")

    monkeypatch.setattr(provenance_module.metadata, "distributions", lambda: [])
    monkeypatch.setattr(provenance_module.subprocess, "run", fake_run)

    first = runtime_environment_provenance(tmp_path)[
        "environment_reproducibility_policy"
    ]
    (tmp_path / "requirements.txt").write_text("click==8.1.9\n", encoding="utf-8")
    second = runtime_environment_provenance(tmp_path)[
        "environment_reproducibility_policy"
    ]

    assert first["evidence"]["lockfiles"]["hash"] != second["evidence"]["lockfiles"]["hash"]
    assert first["hash"] != second["hash"]


def test_package_source_policy_records_degraded_pip_evidence_without_secrets(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_pkgsource_secret_1234567890"  # pragma: allowlist secret

    def fake_run(args, **kwargs):
        probe = _fake_accelerator_probe_run(args)
        if probe is not None:
            return probe
        if args == [sys.executable, "-m", "pip", "freeze", "--all"]:
            return subprocess.CompletedProcess(
                args,
                1,
                stdout=f"private @ https://example.test/pkg?token={secret}\n",
                stderr=f"failed token={secret}",
            )
        if args == [sys.executable, "-m", "pip", "config", "list"]:
            raise subprocess.TimeoutExpired(
                args,
                timeout=10.0,
                output=f"api_key={secret}",
                stderr=f"stderr token={secret}",
            )
        raise AssertionError(f"unexpected command: {args!r}")

    monkeypatch.setattr(provenance_module.metadata, "distributions", lambda: [])
    monkeypatch.setattr(provenance_module.subprocess, "run", fake_run)

    provenance = runtime_environment_provenance(tmp_path)
    policy = provenance["package_source_policy"]
    rendered = json.dumps(policy, sort_keys=True)

    assert policy["evidence"]["pip_freeze"]["status"] == "error"
    assert policy["evidence"]["pip_freeze"]["stdout_sha256_present"] is True
    assert policy["evidence"]["pip_config"]["status"] == "timeout"
    assert policy["evidence"]["pip_config"]["stdout_sha256_present"] is False
    assert policy["evidence"]["installed_packages"]["package_count"] == 0
    assert secret not in rendered


def test_runtime_environment_provenance_bounds_pip_config_snapshot(
    tmp_path,
    monkeypatch,
):
    stdout = "global.a='1'\nglobal.b='" + ("x" * 50) + "'\nglobal.c='1'\n"

    def fake_run(args, **kwargs):
        probe = _fake_accelerator_probe_run(args)
        if probe is not None:
            return probe
        if args == [sys.executable, "-m", "pip", "freeze", "--all"]:
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        return subprocess.CompletedProcess(args, 0, stdout=stdout, stderr="")

    monkeypatch.setattr(provenance_module, "_PIP_CONFIG_MAX_LINES", 2)
    monkeypatch.setattr(provenance_module, "_PIP_CONFIG_MAX_LINE_CHARS", 20)
    monkeypatch.setattr(provenance_module.subprocess, "run", fake_run)

    config = runtime_environment_provenance(tmp_path)["pip_config"]

    assert config["line_count"] == 3
    assert config["omitted_line_count"] == 1
    assert config["max_lines"] == 2
    assert len(config["lines"]) == 2
    assert config["lines"][1]["line"].endswith("...<truncated>")
    assert config["lines"][1]["line_truncated"] is True
    assert len(config["stdout_sha256"]) == 64


def test_runtime_environment_provenance_records_pip_config_failures(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_pipconfigfail_secret_1234567890"  # pragma: allowlist secret

    def fake_run(args, **kwargs):
        probe = _fake_accelerator_probe_run(args)
        if probe is not None:
            return probe
        if args == [sys.executable, "-m", "pip", "freeze", "--all"]:
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        return subprocess.CompletedProcess(
            args,
            1,
            stdout=f"global.index-url='https://example.test/simple?token={secret}'\n",
            stderr=f"failed api_key={secret}",
        )

    monkeypatch.setattr(provenance_module.subprocess, "run", fake_run)

    config = runtime_environment_provenance(tmp_path)["pip_config"]
    rendered = json.dumps(config, sort_keys=True)

    assert config["status"] == "error"
    assert config["returncode"] == 1
    assert len(config["stdout_sha256"]) == 64
    assert len(config["stderr_sha256"]) == 64
    assert config["stderr_preview"] == "failed api_key=[REDACTED]"
    assert secret not in rendered


def test_runtime_environment_provenance_records_llm_provider_sdk_versions(
    tmp_path,
    monkeypatch,
):
    versions = {
        "openai": "2.13.0",
        "anthropic": "0.75.0",
        "ollama": "0.13.0",
    }

    def fake_version(package_name):
        if package_name in versions:
            return versions[package_name]
        raise provenance_module.metadata.PackageNotFoundError(package_name)

    monkeypatch.setattr(provenance_module.metadata, "version", fake_version)

    first = runtime_environment_provenance(tmp_path)["llm_provider_sdks"]
    versions["openai"] = "2.14.0"
    second = runtime_environment_provenance(tmp_path)["llm_provider_sdks"]

    providers = {record["provider"]: record for record in first["providers"]}
    assert first["policy"] == "llm_provider_sdk_versions_v1"
    assert first["hash_scope"] == "configured_builtin_llm_provider_sdk_version_records_v1"
    assert providers["openai"]["status"] == "installed"
    assert providers["openai"]["package"] == "openai"
    assert providers["openai"]["adapter_module"] == "libreevolve.llm.openai"
    assert providers["openai"]["api_modes"] == ["chat_completions", "responses"]
    assert providers["openai"]["version"] == "2.13.0"
    assert providers["openai"]["version_hash"] == hashlib.sha256(b"2.13.0").hexdigest()
    assert providers["anthropic"]["api_modes"] == ["messages"]
    assert providers["ollama"]["api_modes"] == ["chat"]
    assert first["hash"] != second["hash"]


def test_runtime_environment_provenance_records_missing_and_failed_provider_sdks(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_sdklookup_secret_1234567890"  # pragma: allowlist secret

    def fake_version(package_name):
        if package_name == "openai":
            return "2.13.0\u202e"
        if package_name == "anthropic":
            raise provenance_module.metadata.PackageNotFoundError(package_name)
        if package_name == "ollama":
            raise RuntimeError(f"lookup failed token={secret}")
        raise provenance_module.metadata.PackageNotFoundError(package_name)

    monkeypatch.setattr(provenance_module.metadata, "version", fake_version)

    sdks = runtime_environment_provenance(tmp_path)["llm_provider_sdks"]
    providers = {record["provider"]: record for record in sdks["providers"]}
    rendered = json.dumps(sdks, ensure_ascii=False, sort_keys=True)

    assert providers["openai"]["status"] == "installed"
    assert providers["openai"]["version"] == "2.13.0[U+202E]"
    assert providers["openai"]["version_unsafe_chars_redacted"] is True
    assert providers["anthropic"]["status"] == "missing"
    assert providers["ollama"]["status"] == "lookup_error"
    assert providers["ollama"]["error_type"] == "RuntimeError"
    assert providers["ollama"]["error"] == "lookup failed token=[REDACTED]"
    assert providers["ollama"]["error_redacted"] is True
    assert secret not in rendered
    assert "\u202e" not in rendered


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/usr/bin/nvidia-smi", "nvidia-smi"),
        (r"C:\\Windows\\System32\\nvidia-smi.exe", "nvidia-smi.exe"),
        (r"\\\\server\\share\\nvidia-smi.exe", "nvidia-smi.exe"),
    ],
)
def test_portable_executable_basename_accepts_posix_and_windows_paths(
    path,
    expected,
):
    assert provenance_module._portable_executable_basename(path) == expected


def test_runtime_environment_provenance_records_accelerator_runtime(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_accel_secret_1234567890"  # pragma: allowlist secret
    probes = (
        {
            "name": "nvidia_smi",
            "executable": "nvidia-smi",
            "args": ["--query-gpu=driver_version,cuda_version,name"],
        },
    )
    monkeypatch.setattr(
        provenance_module,
        "_ACCELERATOR_ENV_CANDIDATES",
        ("CUDA_VISIBLE_DEVICES", "ROCM_PATH"),
    )
    monkeypatch.setattr(provenance_module, "_ACCELERATOR_COMMAND_PROBES", probes)
    monkeypatch.setattr(
        provenance_module,
        "_pip_freeze_snapshot",
        lambda: {"status": "stubbed"},
    )
    monkeypatch.setattr(
        provenance_module,
        "_pip_config_snapshot",
        lambda: {"status": "stubbed"},
    )
    monkeypatch.setattr(provenance_module.platform, "platform", lambda: "test-platform")
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", f"0,{secret}")
    provenance_module._accelerator_probe_record_cached.cache_clear()

    def fake_which(executable):
        assert executable == "nvidia-smi"
        return r"C:\Windows\System32\nvidia-smi.exe"

    def fake_run(command, **kwargs):
        assert command == [
            "nvidia-smi",
            "--query-gpu=driver_version,cuda_version,name",
        ]
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        assert kwargs["check"] is False
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="550.54.14, 12.4, NVIDIA RTX\n",
            stderr="",
        )

    monkeypatch.setattr(provenance_module.shutil, "which", fake_which)
    monkeypatch.setattr(provenance_module.subprocess, "run", fake_run)

    accelerator = runtime_environment_provenance(tmp_path)["accelerator_runtime"]
    env = {record["name"]: record for record in accelerator["environment"]}
    probe = accelerator["probes"][0]
    rendered = json.dumps(accelerator, sort_keys=True)

    assert accelerator["policy"] == "accelerator_runtime_env_and_driver_probe_v1"
    assert accelerator["hash_scope"] == (
        "accelerator_environment_and_driver_probe_records_v1"
    )
    assert env["CUDA_VISIBLE_DEVICES"]["present"] is True
    assert env["CUDA_VISIBLE_DEVICES"]["value"] == "0,[REDACTED]"
    assert env["CUDA_VISIBLE_DEVICES"]["value_secret_redacted"] is True
    assert env["CUDA_VISIBLE_DEVICES"]["value_hash"] == hashlib.sha256(
        f"0,{secret}".encode()
    ).hexdigest()
    assert env["ROCM_PATH"] == {"name": "ROCM_PATH", "present": False}
    assert probe["status"] == "ok"
    assert probe["executable_basename"] == "nvidia-smi.exe"
    assert len(probe["executable_path_hash"]) == 64
    assert probe["line_count"] == 1
    assert probe["lines"] == [
        {
            "line": "550.54.14, 12.4, NVIDIA RTX",
            "line_hash": hashlib.sha256(
                b"550.54.14, 12.4, NVIDIA RTX"
            ).hexdigest(),
            "line_redacted": False,
        }
    ]
    assert secret not in rendered


def test_runtime_environment_provenance_records_accelerator_probe_failures(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_accelerror_secret_1234567890"  # pragma: allowlist secret
    probes = (
        {"name": "missing_probe", "executable": "missing-tool", "args": []},
        {"name": "failing_probe", "executable": "failing-tool", "args": ["--version"]},
    )
    monkeypatch.setattr(provenance_module, "_ACCELERATOR_COMMAND_PROBES", probes)
    monkeypatch.setattr(
        provenance_module,
        "_pip_freeze_snapshot",
        lambda: {"status": "stubbed"},
    )
    monkeypatch.setattr(
        provenance_module,
        "_pip_config_snapshot",
        lambda: {"status": "stubbed"},
    )
    provenance_module._accelerator_probe_record_cached.cache_clear()

    def fake_which(executable):
        if executable == "missing-tool":
            return None
        return f"/usr/bin/{executable}"

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            2,
            stdout="",
            stderr=f"driver failed token={secret}",
        )

    monkeypatch.setattr(provenance_module.shutil, "which", fake_which)
    monkeypatch.setattr(provenance_module.subprocess, "run", fake_run)

    accelerator = runtime_environment_provenance(tmp_path)["accelerator_runtime"]
    probes_by_name = {record["name"]: record for record in accelerator["probes"]}
    rendered = json.dumps(accelerator, sort_keys=True)

    assert probes_by_name["missing_probe"]["status"] == "executable_missing"
    assert probes_by_name["failing_probe"]["status"] == "error"
    assert probes_by_name["failing_probe"]["returncode"] == 2
    assert probes_by_name["failing_probe"]["stderr_preview"] == (
        "driver failed token=[REDACTED]"
    )
    assert probes_by_name["failing_probe"]["stderr_secret_redacted"] is True
    assert secret not in rendered


def test_runtime_environment_provenance_records_numpy_numerical_runtime(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_numpyconfig_secret_1234567890"  # pragma: allowlist secret
    fake_numpy = ModuleType("numpy")
    fake_numpy.__version__ = "2.3.4"

    def show_config():
        print("blas=openblas")
        print(f"api_key={secret}")

    fake_numpy.show_config = show_config

    def fake_import_module(name):
        if name == "numpy":
            return fake_numpy
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(provenance_module.importlib, "import_module", fake_import_module)

    numerical = runtime_environment_provenance(tmp_path)["numerical_runtime"]
    numpy = numerical["numpy"]

    rendered = json.dumps(numerical, sort_keys=True)
    assert numerical["policy"] == "numpy_show_config_hash_v1"
    assert numpy["status"] == "ok"
    assert numpy["module"] == "numpy"
    assert numpy["version"] == "2.3.4"
    assert len(numpy["version_hash"]) == 64
    assert numpy["show_config"]["status"] == "ok"
    assert numpy["show_config"]["sha256"] == hashlib.sha256(
        f"blas=openblas\napi_key={secret}\n".encode()
    ).hexdigest()
    assert "blas=openblas" in numpy["show_config"]["preview"]
    assert "api_key=[REDACTED]" in numpy["show_config"]["preview"]
    assert numpy["show_config"]["redacted"] is True
    assert secret not in rendered


def test_runtime_environment_provenance_bounds_numpy_config_preview(
    tmp_path,
    monkeypatch,
):
    fake_numpy = ModuleType("numpy")
    fake_numpy.__version__ = "2.3.4"

    def show_config():
        print("x" * 100)

    fake_numpy.show_config = show_config
    monkeypatch.setattr(provenance_module, "_NUMERICAL_RUNTIME_CONFIG_MAX_CHARS", 20)
    monkeypatch.setattr(
        provenance_module.importlib,
        "import_module",
        lambda name: fake_numpy if name == "numpy" else None,
    )

    config = runtime_environment_provenance(tmp_path)["numerical_runtime"]["numpy"][
        "show_config"
    ]

    assert config["truncated"] is True
    assert config["preview"].endswith("...<truncated>")
    assert config["preview_chars"] == 20
    assert config["max_preview_chars"] == 20


def test_runtime_environment_provenance_records_numpy_unavailable(
    tmp_path,
    monkeypatch,
):
    def fake_import_module(name):
        if name == "numpy":
            raise ModuleNotFoundError("No module named 'numpy'")
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(provenance_module.importlib, "import_module", fake_import_module)

    numpy = runtime_environment_provenance(tmp_path)["numerical_runtime"]["numpy"]

    assert numpy == {
        "status": "unavailable",
        "module": "numpy",
        "reason": "module_not_installed",
    }


def test_runtime_environment_provenance_records_numpy_show_config_errors(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_numpyerror_secret_1234567890"  # pragma: allowlist secret
    fake_numpy = ModuleType("numpy")
    fake_numpy.__version__ = "2.3.4"

    def show_config():
        raise RuntimeError(f"failed api_key={secret}")

    fake_numpy.show_config = show_config
    monkeypatch.setattr(
        provenance_module.importlib,
        "import_module",
        lambda name: fake_numpy if name == "numpy" else None,
    )

    config = runtime_environment_provenance(tmp_path)["numerical_runtime"]["numpy"][
        "show_config"
    ]

    rendered = json.dumps(config, sort_keys=True)
    assert config["status"] == "error"
    assert config["error_type"] == "RuntimeError"
    assert config["error"] == "failed api_key=[REDACTED]"
    assert config["error_redacted"] is True
    assert secret not in rendered


def test_runtime_environment_provenance_records_missing_lockfiles(tmp_path):
    provenance = runtime_environment_provenance(tmp_path)

    lockfiles = provenance["lockfiles"]
    assert lockfiles["file_count"] == 0
    assert lockfiles["files"] == []
    assert len(lockfiles["hash"]) == 64


def test_runtime_environment_provenance_skips_oversized_lockfiles(tmp_path):
    lockfile = tmp_path / "poetry.lock"
    lockfile.write_bytes(b"x" * 5_000_001)

    provenance = runtime_environment_provenance(tmp_path)

    record = provenance["lockfiles"]["files"][0]
    assert record == {
        "path": "poetry.lock",
        "status": "skipped_max_file_bytes",
        "bytes": 5_000_001,
        "max_bytes": 5_000_000,
    }


def test_runtime_environment_provenance_redacts_unreadable_lockfile_diagnostics(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_lockfileread_secret_1234567890"  # pragma: allowlist secret
    lockfile = tmp_path / "uv.lock"
    lockfile.write_text("version = 1\n", encoding="utf-8")
    original_read_bytes = Path.read_bytes

    def unreadable_read_bytes(self):
        if self == lockfile:
            raise OSError(f"cannot read token={secret}")
        return original_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", unreadable_read_bytes)

    provenance = runtime_environment_provenance(tmp_path)

    record = provenance["lockfiles"]["files"][0]
    rendered = json.dumps(provenance, sort_keys=True)
    assert record["path"] == "uv.lock"
    assert record["status"] == "unreadable"
    assert record["error_type"] == "OSError"
    assert record["error"] == "cannot read token=[REDACTED]"
    assert record["error_redacted"] is True
    assert secret not in rendered


def test_runtime_environment_provenance_records_missing_pyproject(tmp_path):
    provenance = runtime_environment_provenance(tmp_path)

    pyproject = provenance["package"]["pyproject"]
    assert pyproject == {
        "path": "pyproject.toml",
        "status": "missing",
    }
    assert "name" not in provenance["package"]
    assert "version" not in provenance["package"]
    assert "requires_python" not in provenance["package"]
    assert provenance["package"]["installed_version_name"] == "libreevolve"
    assert provenance["package"]["build_system"] == {}
    assert provenance["dependencies"] == []


def test_runtime_environment_provenance_records_invalid_pyproject_toml(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project\nname = 'broken'\n", encoding="utf-8")

    provenance = runtime_environment_provenance(tmp_path)

    pyproject = provenance["package"]["pyproject"]
    assert pyproject["path"] == "pyproject.toml"
    assert pyproject["status"] == "invalid_toml"
    assert pyproject["error_type"] == "TOMLDecodeError"
    assert pyproject["sha256"]
    assert "name" not in provenance["package"]
    assert provenance["dependencies"] == []


def test_runtime_environment_provenance_redacts_invalid_pyproject_toml_diagnostics(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_pyprojectparse_secret_1234567890"  # pragma: allowlist secret
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'sample'\n", encoding="utf-8")

    def fake_loads(_text):
        raise provenance_module.tomllib.TOMLDecodeError(f"bad token api_key={secret}", "", 0)

    monkeypatch.setattr(provenance_module.tomllib, "loads", fake_loads)

    provenance = runtime_environment_provenance(tmp_path)

    pyproject = provenance["package"]["pyproject"]
    assert pyproject["status"] == "invalid_toml"
    assert pyproject["error_type"] == "TOMLDecodeError"
    assert secret not in pyproject["error"]
    assert "[REDACTED]" in pyproject["error"]
    assert pyproject["error_redacted"] is True
    assert secret not in json.dumps(provenance, sort_keys=True)


def test_runtime_environment_provenance_records_invalid_pyproject_encoding(tmp_path):
    (tmp_path / "pyproject.toml").write_bytes(b"[project]\nname = \xff\n")

    provenance = runtime_environment_provenance(tmp_path)

    pyproject = provenance["package"]["pyproject"]
    assert pyproject["path"] == "pyproject.toml"
    assert pyproject["status"] == "invalid_encoding"
    assert pyproject["encoding"] == "utf-8"
    assert pyproject["error_type"] == "UnicodeDecodeError"
    assert pyproject["sha256"]
    assert provenance["dependencies"] == []


def test_runtime_environment_provenance_bounds_invalid_pyproject_encoding_diagnostics(
    tmp_path,
    monkeypatch,
):
    (tmp_path / "pyproject.toml").write_bytes(b"[project]\nname = \xff\n")
    path = tmp_path / "pyproject.toml"
    original_read_bytes = Path.read_bytes

    class BadBytes(bytes):
        def decode(self, *args, **kwargs):
            raise UnicodeDecodeError("utf-8", b"x", 0, 1, "bad " + ("x" * 900))

    def fake_read_bytes(self):
        if self == path:
            return BadBytes(b"x")
        return original_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", fake_read_bytes)

    provenance = runtime_environment_provenance(tmp_path)

    pyproject = provenance["package"]["pyproject"]
    assert pyproject["status"] == "invalid_encoding"
    assert len(pyproject["error"]) == 512
    assert pyproject["error"].endswith("...<truncated>")
    assert pyproject["error_truncated"] is True
    assert pyproject["max_error_chars"] == 512


def test_runtime_environment_provenance_records_unreadable_pyproject(tmp_path, monkeypatch):
    path = tmp_path / "pyproject.toml"
    path.write_text("[project]\nname = 'sample'\n", encoding="utf-8")
    original_read_bytes = Path.read_bytes

    def unreadable_read_bytes(self):
        if self == path:
            raise OSError("permission denied")
        return original_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", unreadable_read_bytes)

    provenance = runtime_environment_provenance(tmp_path)

    pyproject = provenance["package"]["pyproject"]
    assert pyproject["path"] == "pyproject.toml"
    assert pyproject["status"] == "unreadable"
    assert pyproject["error_type"] == "OSError"
    assert "permission denied" in pyproject["error"]
    assert provenance["dependencies"] == []


def test_runtime_environment_provenance_redacts_unreadable_pyproject_diagnostics(
    tmp_path,
    monkeypatch,
):
    secret = "sk-proj_pyprojectread_secret_1234567890"  # pragma: allowlist secret
    path = tmp_path / "pyproject.toml"
    path.write_text("[project]\nname = 'sample'\n", encoding="utf-8")
    original_read_bytes = Path.read_bytes

    def unreadable_read_bytes(self):
        if self == path:
            raise OSError(f"cannot read api_key={secret}")
        return original_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", unreadable_read_bytes)

    provenance = runtime_environment_provenance(tmp_path)

    pyproject = provenance["package"]["pyproject"]
    assert pyproject["status"] == "unreadable"
    assert secret not in pyproject["error"]
    assert pyproject["error"] == "cannot read api_key=[REDACTED]"
    assert pyproject["error_redacted"] is True
    assert secret not in json.dumps(provenance, sort_keys=True)


def test_runtime_environment_provenance_bounds_unreadable_pyproject_diagnostics(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "pyproject.toml"
    path.write_text("[project]\nname = 'sample'\n", encoding="utf-8")
    original_read_bytes = Path.read_bytes

    def unreadable_read_bytes(self):
        if self == path:
            raise OSError("permission denied " + ("x" * 900))
        return original_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", unreadable_read_bytes)

    provenance = runtime_environment_provenance(tmp_path)

    pyproject = provenance["package"]["pyproject"]
    assert len(pyproject["error"]) == 512
    assert pyproject["error"].endswith("...<truncated>")
    assert pyproject["error_truncated"] is True
    assert pyproject["max_error_chars"] == 512


@pytest.mark.parametrize(
    ("body", "error_path"),
    [
        ("[project]\ndependencies = 'click>=8'\n", "project.dependencies"),
        ("[project]\ndependencies = [123]\n", "project.dependencies[0]"),
        ("[project]\ndependencies = ['bad req']\n", "project.dependencies[0]"),
        ("[project]\nlicense = {text = 123}\n", "project.license.text"),
        ("[project]\nauthors = [{name = 123}]\n", "project.authors[0].name"),
        ("[project]\nkeywords = [123]\n", "project.keywords[0]"),
        ("[project]\nclassifiers = [123]\n", "project.classifiers[0]"),
        ("[project.urls]\nHomepage = 123\n", "project.urls.Homepage"),
        ("[project.scripts]\ncli = 123\n", "project.scripts.cli"),
        ("[project.entry-points.demo]\nplugin = 123\n", "project.entry-points.demo.plugin"),
        ("[project.optional-dependencies]\ntest = [123]\n", "project.optional-dependencies.test[0]"),
        ("[build-system]\nrequires = 'setuptools>=68'\n", "build-system.requires"),
        ("[build-system]\nrequires = [123]\n", "build-system.requires[0]"),
        ("[build-system]\nrequires = ['bad req']\n", "build-system.requires[0]"),
    ],
)
def test_runtime_environment_provenance_records_invalid_pyproject_schema(
    tmp_path, body, error_path
):
    (tmp_path / "pyproject.toml").write_text(body, encoding="utf-8")

    provenance = runtime_environment_provenance(tmp_path)

    pyproject = provenance["package"]["pyproject"]
    assert pyproject["path"] == "pyproject.toml"
    assert pyproject["status"] == "invalid_pyproject_schema"
    assert pyproject["error_type"] == "InvalidPyprojectSchema"
    assert len(pyproject["sha256"]) == 64
    assert pyproject["bytes"] > 0
    assert pyproject["errors"][0]["path"] == error_path
    assert "name" not in provenance["package"]
    assert provenance["package"]["build_system"] == {}
    assert provenance["dependencies"] == []


def test_runtime_environment_provenance_records_private_source_dependency_safely(tmp_path):
    token = "sk-" + "proj_" + "abcdefghijklmnopqrstuvwxyz123456"  # pragma: allowlist secret
    (tmp_path / "pyproject.toml").write_text(
        f"""
[project]
name = "sample-project"
version = "1.0"
dependencies = ["private-lib @ https://user:{token}@example.test/pkg.whl"]
""".strip(),
        encoding="utf-8",
    )

    provenance = runtime_environment_provenance(tmp_path)

    dep = provenance["dependencies"][0]
    assert provenance["package"]["pyproject"]["status"] == "ok"
    assert dep["name"] == "private-lib"
    assert dep["name_redacted"] is False
    assert dep["name_hash"] == hashlib.sha256(b"private-lib").hexdigest()
    assert dep["installed_version_lookup_name"] == "private-lib"
    assert token not in dep["spec"]
    assert "[REDACTED]" in dep["spec"]


def test_runtime_environment_provenance_redacts_secret_like_dependency_names(tmp_path):
    secret_name = "api-key-sk-proj-dependencysecret1234567890"
    (tmp_path / "pyproject.toml").write_text(
        f"""
[project]
name = "sample-project"
version = "1.0"
dependencies = ["{secret_name}>=1.0"]
""".strip(),
        encoding="utf-8",
    )

    provenance = runtime_environment_provenance(tmp_path)

    dep = provenance["dependencies"][0]
    rendered = json.dumps(provenance)
    assert dep["name"] == "api-key-[REDACTED]"
    assert dep["name_redacted"] is True
    assert dep["name_hash"] == hashlib.sha256(secret_name.encode("utf-8")).hexdigest()
    assert dep["installed_version_lookup_name"] == "api-key-[REDACTED]"
    assert dep["installed_version_lookup_name_hash"] == dep["name_hash"]
    assert dep["installed_version_lookup_redacted"] is True
    assert dep["installed_version"] is None
    assert secret_name not in rendered
    assert "[REDACTED]" in rendered


def test_runtime_environment_provenance_escapes_dependency_spec_format_controls(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "sample-project"
version = "1.0"
dependencies = ["demo-lib>=1.0; python_version >= '3.12\u202e'"]
""".strip(),
        encoding="utf-8",
    )

    provenance = runtime_environment_provenance(tmp_path)

    dep = provenance["dependencies"][0]
    rendered = json.dumps(provenance, ensure_ascii=False, sort_keys=True)
    assert "\u202e" not in rendered
    assert dep["spec"] == "demo-lib>=1.0; python_version >= '3.12[U+202E]'"
    assert dep["spec_redacted"] is True
    assert dep["spec_unsafe_chars_redacted"] is True
    assert len(dep["spec_hash"]) == 64


def test_runtime_environment_provenance_redacts_secret_like_pyproject_metadata(tmp_path):
    secret = "sk-proj_pyprojectfield_secret_1234567890"  # pragma: allowlist secret
    package_name = f"api-key-{secret}"
    (tmp_path / "pyproject.toml").write_text(
        f"""
[build-system]
requires = ["setuptools @ https://example.test/pkg?token={secret}"]
build-backend = "api_key={secret}"

[project]
name = "{package_name}"
version = "1.0+{secret}"
requires-python = ">=3.12; api_key={secret}"
dependencies = []
""".strip(),
        encoding="utf-8",
    )

    provenance = runtime_environment_provenance(tmp_path)

    package = provenance["package"]
    build_system = package["build_system"]
    rendered = json.dumps(provenance, sort_keys=True)
    assert secret not in rendered
    assert package["name"] == "api-key-[REDACTED]"
    assert package["name_secret_redacted"] is True
    assert package["name_redacted"] is True
    assert package["installed_version_name"] == "api-key-[REDACTED]"
    assert package["installed_version_lookup_redacted"] is True
    assert package["installed_version"] is None
    assert "[REDACTED]" in package["version"]
    assert package["version_secret_redacted"] is True
    assert "[REDACTED]" in package["requires_python"]
    assert package["requires_python_secret_redacted"] is True
    assert build_system["build_backend"] == "api_key=[REDACTED]"
    assert build_system["build_backend_secret_redacted"] is True
    assert "[REDACTED]" in build_system["requires"][0]
    assert build_system["requires_redacted"] is True
    assert len(package["name_hash"]) == 64
    assert len(package["version_hash"]) == 64
    assert len(package["requires_python_hash"]) == 64
    assert len(build_system["build_backend_hash"]) == 64
    assert len(build_system["requires_hashes"][0]) == 64


def test_runtime_environment_provenance_escapes_pyproject_metadata_format_controls(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        """
[build-system]
requires = []
build-backend = "backend\u202e.name"

[project]
name = "sample-project"
version = "1.0\u202e"
requires-python = ">=3.12"
dependencies = []
""".strip(),
        encoding="utf-8",
    )

    provenance = runtime_environment_provenance(tmp_path)

    package = provenance["package"]
    assert "\u202e" not in json.dumps(provenance, ensure_ascii=False)
    assert package["version"] == "1.0[U+202E]"
    assert package["version_unsafe_chars_redacted"] is True
    assert package["build_system"]["build_backend"] == "backend[U+202E].name"
    assert package["build_system"]["build_backend_unsafe_chars_redacted"] is True


def test_runtime_environment_provenance_truncates_long_pyproject_metadata(tmp_path):
    long_version = "1.0+" + ("a" * 700)
    (tmp_path / "pyproject.toml").write_text(
        f"""
[project]
name = "sample-project"
version = "{long_version}"
dependencies = []
""".strip(),
        encoding="utf-8",
    )

    provenance = runtime_environment_provenance(tmp_path)

    package = provenance["package"]
    assert len(package["version"]) == 512
    assert package["version"].endswith("...<truncated>")
    assert package["version_truncated"] is True
    assert package["version_max_chars"] == 512
    assert len(package["version_hash"]) == 64


@pytest.mark.parametrize(
    ("body", "error_path"),
    [
        ("[project]\nname = 1\n", "project.name"),
        ("[project]\nversion = 1\n", "project.version"),
        ("[project]\nrequires-python = 1\n", "project.requires-python"),
        ("[build-system]\nbuild-backend = 1\nrequires = []\n", "build-system.build-backend"),
    ],
)
def test_runtime_environment_provenance_rejects_non_string_pyproject_metadata(
    tmp_path, body, error_path
):
    (tmp_path / "pyproject.toml").write_text(body, encoding="utf-8")

    provenance = runtime_environment_provenance(tmp_path)

    pyproject = provenance["package"]["pyproject"]
    assert pyproject["status"] == "invalid_pyproject_schema"
    assert pyproject["errors"][0]["path"] == error_path
    assert "name" not in provenance["package"]
    assert provenance["package"]["build_system"] == {}
