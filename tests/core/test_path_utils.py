from types import SimpleNamespace

import pytest

from libreevolve.core import path_utils


def _force_python311_windows_probe(monkeypatch, lstat):
    monkeypatch.setattr(path_utils.Path, "is_symlink", lambda _path: False)
    monkeypatch.setattr(
        path_utils.Path,
        "is_junction",
        lambda _path: False,
        raising=False,
    )
    monkeypatch.setattr(
        path_utils,
        "os",
        SimpleNamespace(name="nt", lstat=lstat),
    )


def _raise_permission(_path):
    raise PermissionError("lstat denied")


def test_is_path_link_detects_python311_windows_reparse_point(tmp_path, monkeypatch):
    path = tmp_path / "junction"
    path.mkdir()

    _force_python311_windows_probe(
        monkeypatch,
        lambda _path: SimpleNamespace(st_file_attributes=0x0400),
    )

    assert path_utils.is_path_link(path) is True


@pytest.mark.parametrize(
    "lstat",
    [
        _raise_permission,
        lambda _path: SimpleNamespace(),
        lambda _path: SimpleNamespace(st_file_attributes="invalid"),
    ],
    ids=["permission", "missing_attributes", "malformed_attributes"],
)
def test_is_path_link_rejects_unclassifiable_windows_paths(lstat, tmp_path, monkeypatch):
    path = tmp_path / "unclassifiable"
    _force_python311_windows_probe(monkeypatch, lstat)

    assert path_utils.is_path_link(path) is True


def test_is_path_link_allows_genuinely_missing_windows_path(tmp_path, monkeypatch):
    path = tmp_path / "missing"

    def raise_missing(_path):
        raise FileNotFoundError("missing")

    _force_python311_windows_probe(
        monkeypatch,
        raise_missing,
    )

    assert path_utils.is_path_link(path) is False


def test_linked_existing_ancestor_returns_link_path(tmp_path, monkeypatch):
    linked = tmp_path / "linked"
    child = linked / "problem"

    monkeypatch.setattr(
        path_utils,
        "is_path_link",
        lambda path: path == linked,
    )

    assert path_utils.linked_existing_ancestor(child) == linked.absolute()
