import hashlib
import json

import pytest

from libreevolve.core.best_artifacts import (
    attach_best_artifact_export,
    export_best_artifacts,
)
from libreevolve.population.program import Program


def _workspace_program(files: dict[str, str]) -> Program:
    return Program(files=files, primary_file="main.py")


def test_export_best_artifacts_returns_canonical_pair_and_structured_records(tmp_path):
    program = _workspace_program(
        {
            "helper.txt": "helper\n",
            "main.py": "value = 1\n",
        }
    )

    record = export_best_artifacts(program, tmp_path / "run")

    assert record["status"] == "completed"
    assert list(record["paths"]) == ["best.py", "best_workspace"]

    best_py = record["paths"]["best.py"]
    best_py_bytes = (tmp_path / "run" / "best.py").read_bytes()
    assert best_py == {
        "path": "best.py",
        "exists": True,
        "present": True,
        "is_symlink": False,
        "is_junction": False,
        "kind": "file",
        "bytes": len(best_py_bytes),
        "sha256": hashlib.sha256(best_py_bytes).hexdigest(),
    }

    best_workspace = record["paths"]["best_workspace"]
    assert best_workspace["path"] == "best_workspace"
    assert best_workspace["kind"] == "directory"
    assert best_workspace["exists"] is True
    assert best_workspace["present"] is True
    assert best_workspace["is_symlink"] is False
    assert best_workspace["is_junction"] is False
    assert best_workspace["tree_hash_status"] == "ok"
    assert best_workspace["tree_hash_scope"] == "best_workspace_file_paths_and_sha256"
    assert best_workspace["file_count"] == 2

    run_dir = tmp_path / "run"
    assert (run_dir / "best.py").read_text(encoding="utf-8") == program.code
    assert (run_dir / "best_workspace" / "main.py").read_text(
        encoding="utf-8"
    ) == program.code
    assert (run_dir / "best_workspace" / "helper.txt").read_text(
        encoding="utf-8"
    ) == "helper\n"
    assert sorted(path.name for path in run_dir.iterdir()) == [
        "best.py",
        "best_workspace",
    ]


def test_repeated_export_has_identical_records_and_sorted_tree_hash_input(tmp_path):
    first_program = _workspace_program(
        {
            "z.txt": "z\n",
            "main.py": "value = 1\n",
            "a.txt": "a\n",
        }
    )
    second_program = _workspace_program(
        {
            "a.txt": "a\n",
            "z.txt": "z\n",
            "main.py": "value = 1\n",
        }
    )

    first_run = tmp_path / "first"
    second_run = tmp_path / "second"
    first_record = export_best_artifacts(first_program, first_run)
    repeated_record = export_best_artifacts(first_program, first_run)
    reordered_record = export_best_artifacts(second_program, second_run)

    assert first_record == repeated_record == reordered_record
    assert [
        path.relative_to(first_run / "best_workspace").as_posix()
        for path in sorted(
            (first_run / "best_workspace").rglob("*"),
            key=lambda item: item.as_posix(),
        )
        if path.is_file()
    ] == ["a.txt", "main.py", "z.txt"]
    assert not any(
        path.name.startswith(".best") for path in first_run.iterdir()
    )
    assert not any(
        path.name.startswith(".best") for path in second_run.iterdir()
    )


def test_attach_best_artifact_export_updates_only_best_runtime_pointers(tmp_path):
    record = export_best_artifacts(
        _workspace_program({"main.py": "value = 1\n"}),
        tmp_path / "run",
    )
    other_pointer = {"path": "history.jsonl", "present": True}
    runtime = {"artifacts": {"history.jsonl": other_pointer}}

    attach_best_artifact_export(runtime, record)

    assert runtime["best_artifact_export"] is record
    assert runtime["artifacts"]["best.py"] == record["paths"]["best.py"]
    assert runtime["artifacts"]["best_workspace"] == record["paths"]["best_workspace"]
    assert runtime["artifacts"]["history.jsonl"] is other_pointer

    unchanged = {"status": "unchanged"}
    attach_best_artifact_export(unchanged, None)
    assert unchanged == {"status": "unchanged"}


def test_export_best_artifacts_materializes_verified_source_copy_and_sidecar(
    tmp_path,
):
    source = tmp_path / "source.bin"
    raw = b"\x00\x01static-bytes"
    source.write_bytes(raw)
    static_record = {
        "path": "asset.bin",
        "kind": "binary",
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "source_kind": "copied_static_asset",
        "mutation_policy": "immutable",
        "source_copy_path": str(source),
    }
    program = Program(
        files={"main.py": "value = 1\n"},
        primary_file="main.py",
        static_files=(static_record,),
    )

    record = export_best_artifacts(program, tmp_path / "run")
    workspace = tmp_path / "run" / "best_workspace"
    sidecar = json.loads(
        (workspace / ".libreevolve_static_files.json").read_text(encoding="utf-8")
    )

    assert record["status"] == "completed"
    assert (workspace / "asset.bin").read_bytes() == raw
    assert sidecar["schema"] == "libreevolve.static_workspace_files.v1"
    assert sidecar["static_files"] == [
        {key: value for key, value in program.static_files[0].items()}
    ]


def test_export_best_artifacts_reports_source_copy_failure_and_cleans_staging(
    tmp_path,
):
    source = tmp_path / "source.bin"
    raw = b"actual-bytes"
    source.write_bytes(raw)
    program = Program(
        files={"main.py": "value = 1\n"},
        primary_file="main.py",
        static_files=(
            {
                "path": "asset.bin",
                "kind": "binary",
                "bytes": len(raw),
                "sha256": hashlib.sha256(b"different-bytes").hexdigest(),
                "source_copy_path": str(source),
            },
        ),
    )
    run_dir = tmp_path / "run"

    record = export_best_artifacts(program, run_dir)

    assert record["status"] == "failed"
    assert record["error_type"] == "BestArtifactExportError"
    assert record["original_error_type"] == "CandidateMaterializationError"
    assert record["paths"]["best.py"]["kind"] == "missing"
    assert record["paths"]["best_workspace"]["kind"] == "missing"
    assert list(run_dir.iterdir()) == []


@pytest.mark.parametrize(
    ("artifact_name", "target_is_directory"),
    (("best.py", False), ("best_workspace", True)),
)
def test_export_best_artifacts_rejects_linked_target_without_staging_artifacts(
    tmp_path, artifact_name, target_is_directory
):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    target = tmp_path / ("target-dir" if target_is_directory else "target.py")
    if target_is_directory:
        target.mkdir()
        (target / "keep.txt").write_text("keep\n", encoding="utf-8")
    else:
        target.write_text("keep\n", encoding="utf-8")
    link = run_dir / artifact_name
    try:
        link.symlink_to(target, target_is_directory=target_is_directory)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable: {exc.__class__.__name__}")

    record = export_best_artifacts(
        _workspace_program({"main.py": "value = 1\n"}),
        run_dir,
    )

    assert record["status"] == "failed"
    assert record["error_type"] == "OSError"
    assert record["paths"][artifact_name]["kind"] == "link"
    assert record["paths"][artifact_name]["present"] is True
    assert record["paths"][artifact_name]["is_symlink"] is True
    assert sorted(path.name for path in run_dir.iterdir()) == [artifact_name]
    if target_is_directory:
        assert (target / "keep.txt").read_text(encoding="utf-8") == "keep\n"
    else:
        assert target.read_text(encoding="utf-8") == "keep\n"
