import pytest

from libreevolve.problems.benchmarks._path_policy import safe_relative_path


@pytest.mark.parametrize(
    "value",
    [
        "",
        "/tmp/artifact.json",
        "\\\\server\\share\\artifact.json",
        "C:/secret.json",
        "C:\\secret.json",
        "../secret.json",
        "nested/../secret.json",
        "nested\\..\\secret.json",
        "artifact\x00.json",
    ],
)
def test_safe_relative_path_rejects_absolute_and_traversal_grammars(value):
    assert safe_relative_path(value) is None


@pytest.mark.parametrize(
    "value",
    ["artifact.json", "nested/artifact.json", "nested\\artifact.json"],
)
def test_safe_relative_path_accepts_relative_paths(value):
    path = safe_relative_path(value)

    assert path is not None
    assert not path.is_absolute()
