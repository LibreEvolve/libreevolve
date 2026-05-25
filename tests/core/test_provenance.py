from pathlib import Path

from libreevolve.core.provenance import plugin_provenance, problem_provenance


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
        "task_description.txt",
        "validate.py",
    ]


def test_plugin_provenance_records_plugin_module_hash():
    class LocalPlugin:
        pass

    records = plugin_provenance([LocalPlugin()])
    assert records[0]["class"].endswith("LocalPlugin")
    assert records[0]["path"] == str(Path(__file__).resolve())
    assert len(records[0]["sha256"]) == 64


def test_plugin_provenance_handles_missing_module_file():
    MissingModulePlugin = type("MissingModulePlugin", (), {"__module__": "missing_plugin_module"})

    records = plugin_provenance([MissingModulePlugin()])

    assert records[0]["class"] == "missing_plugin_module.MissingModulePlugin"
    assert records[0]["path"] is None
    assert "sha256" not in records[0]
