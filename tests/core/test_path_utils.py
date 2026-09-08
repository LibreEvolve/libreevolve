from types import SimpleNamespace

from libreevolve.core import path_utils


def test_is_path_link_detects_python311_windows_reparse_point(tmp_path, monkeypatch):
    path = tmp_path / "junction"
    path.mkdir()

    monkeypatch.setattr(path_utils.Path, "is_symlink", lambda _path: False)
    monkeypatch.setattr(path_utils.os, "name", "nt")
    monkeypatch.setattr(
        path_utils.os,
        "lstat",
        lambda _path: SimpleNamespace(st_file_attributes=0x0400),
    )

    assert path_utils.is_path_link(path) is True


def test_linked_existing_ancestor_returns_link_path(tmp_path, monkeypatch):
    linked = tmp_path / "linked"
    child = linked / "problem"

    monkeypatch.setattr(
        path_utils,
        "is_path_link",
        lambda path: path == linked,
    )

    assert path_utils.linked_existing_ancestor(child) == linked.absolute()
