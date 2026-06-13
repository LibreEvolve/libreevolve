import json
import tarfile
import zipfile
from pathlib import Path

from libreevolve.tools.release_artifact_provenance import (
    RELEASE_ARTIFACT_PROVENANCE_SCHEMA,
    collect_release_artifact_provenance,
    validate_release_artifact_provenance,
    write_release_artifact_provenance,
)


def test_release_artifact_provenance_records_distribution_hashes(tmp_path):
    _write_source_files(tmp_path)
    dist = tmp_path / "dist"
    dist.mkdir()
    wheel = dist / "libreevolve-0.1.0-py3-none-any.whl"
    sdist = dist / "libreevolve-0.1.0.tar.gz"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("libreevolve/__init__.py", "")
    with tarfile.open(sdist, "w:gz") as archive:
        source = tmp_path / "pyproject.toml"
        archive.add(source, "libreevolve-0.1.0/pyproject.toml")

    record = collect_release_artifact_provenance(root=tmp_path)

    assert record["schema"] == RELEASE_ARTIFACT_PROVENANCE_SCHEMA
    assert record["dist_dir"] == "dist"
    assert record["artifact_count"] == 2
    assert {artifact["kind"] for artifact in record["artifacts"]} == {"wheel", "sdist"}
    assert {artifact["filename"] for artifact in record["artifacts"]} == {
        wheel.name,
        sdist.name,
    }
    assert all(len(artifact["sha256"]) == 64 for artifact in record["artifacts"])
    assert record["source"]["git_commit"] is None
    assert record["source"]["tracked_files_dirty"] is False
    assert set(record["source"]["source_file_sha256"]) == {
        ".github/workflows/tests.yml",
        "MANIFEST.in",
        "pyproject.toml",
    }
    assert validate_release_artifact_provenance(record) == []


def test_write_release_artifact_provenance_validates_before_writing(tmp_path):
    _write_source_files(tmp_path)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "libreevolve-0.1.0-py3-none-any.whl").write_bytes(b"wheel")
    (dist / "libreevolve-0.1.0.tar.gz").write_bytes(b"sdist")

    output = dist / "release_artifact_provenance.json"
    record = write_release_artifact_provenance(output=output, root=tmp_path)

    assert output.is_file()
    assert json.loads(output.read_text(encoding="utf-8")) == record


def test_release_artifact_provenance_requires_wheel_and_sdist(tmp_path):
    _write_source_files(tmp_path)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "libreevolve-0.1.0-py3-none-any.whl").write_bytes(b"wheel")

    issues = validate_release_artifact_provenance(
        collect_release_artifact_provenance(root=tmp_path)
    )

    assert "provenance must include at least one wheel and one sdist" in issues


def _write_source_files(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname = 'libreevolve'\n", encoding="utf-8")
    (root / "MANIFEST.in").write_text("recursive-include libreevolve *.py\n", encoding="utf-8")
    workflow = root / ".github" / "workflows"
    workflow.mkdir(parents=True)
    (workflow / "tests.yml").write_text("name: Tests\n", encoding="utf-8")
