import json

import pytest

from libreevolve.alpha_share_io import PUBLIC_FILENAMES, export_public, load_record
from libreevolve.alpha_share_record import MAX_RECORD_BYTES, payload_sha256
from tests.test_alpha_share_record import record


def source(tmp_path):
    path = tmp_path / "record.json"
    path.write_text(json.dumps(record()), encoding="utf-8")
    return path


def test_export_only_public_files_and_no_overwrite(tmp_path):
    path = source(tmp_path)
    dest = tmp_path / "public"
    receipt = export_public(path, dest, approved_sha256=payload_sha256(record()), approved_by="private-person")
    assert {p.name for p in dest.iterdir()} == PUBLIC_FILENAMES
    assert receipt["approved_by"] == "private-person"
    original = {p.name: p.read_bytes() for p in dest.iterdir()}
    assert all(b"private-person" not in content for content in original.values())
    with pytest.raises(ValueError, match="exists"):
        export_public(path, dest, approved_sha256=payload_sha256(record()), approved_by="person")
    assert original == {p.name: p.read_bytes() for p in dest.iterdir()}


def test_missing_approval_creates_nothing(tmp_path):
    path = source(tmp_path)
    with pytest.raises(ValueError):
        export_public(path, tmp_path / "public", approved_sha256="", approved_by="person")
    assert not (tmp_path / "public").exists()


@pytest.mark.parametrize("content", ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":1e999}', '[]', '[[' * 1000, 'x' * (MAX_RECORD_BYTES + 1)])
def test_bad_json(tmp_path, content):
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        load_record(path)


def test_symlinks_and_traversal_rejected(tmp_path):
    path = source(tmp_path)
    link = tmp_path / "link.json"
    link.symlink_to(path)
    with pytest.raises(ValueError, match="Symlink"):
        load_record(link)
    directory = tmp_path / "linked"
    directory.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match="Symlink"):
        export_public(path, directory / "out", approved_sha256=payload_sha256(record()), approved_by="person")
    with pytest.raises(ValueError, match="traversal"):
        load_record(tmp_path / "other" / ".." / "record.json")


def test_lone_surrogate_rejected_before_any_output(tmp_path):
    data = record()
    data["limitations"] = ["\ud800"]
    path = tmp_path / "input.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        export_public(path, tmp_path / "public", approved_sha256="a" * 64, approved_by="person")
    assert not (tmp_path / "public").exists()
