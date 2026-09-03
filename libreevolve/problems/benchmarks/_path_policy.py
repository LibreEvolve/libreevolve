"""Shared path-shape checks for benchmark records and artifact metadata."""

from pathlib import Path, PurePosixPath, PureWindowsPath


def safe_relative_path(value: object) -> Path | None:
    """Return a relative path accepted under both POSIX and Windows grammar.

    Validation runs on more than one host platform, so ``Path.is_absolute``
    alone is insufficient: on POSIX it accepts values such as ``C:/file`` and
    ``C:\\file`` as relative strings.
    """

    if not isinstance(value, str) or not value or "\x00" in value:
        return None
    posix_path = PurePosixPath(value)
    windows_path = PureWindowsPath(value)
    if (
        value.startswith(("/", "\\"))
        or posix_path.is_absolute()
        or windows_path.is_absolute()
        or windows_path.drive
        or ".." in posix_path.parts
        or ".." in windows_path.parts
    ):
        return None
    return Path(value)
