"""Small path predicates shared by filesystem boundary checks."""

from __future__ import annotations

import os
from pathlib import Path
import stat


# ``Path.is_junction`` was added after the oldest supported Python version.
# On Python 3.11/Windows, junctions are exposed by ``lstat`` as reparse
# points, even though ``Path.is_symlink`` is false for them.
_WINDOWS_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)


def is_path_link(path: Path) -> bool:
    """Return whether *path* is a symlink or Windows directory junction.

    The reparse-point check is deliberately limited to Windows.  On other
    platforms ``Path.is_symlink`` is the complete link predicate, and
    ``st_file_attributes`` is not part of their stat contract.
    """

    path = Path(path)
    if path.is_symlink():
        return True

    is_junction = getattr(path, "is_junction", None)
    if is_junction is not None:
        try:
            if is_junction():
                return True
        except (AttributeError, OSError, TypeError, ValueError):
            # Fall through to the Python 3.11-compatible lstat check below.
            pass

    if os.name != "nt":
        return False
    try:
        attributes = os.lstat(path).st_file_attributes
        return bool(attributes & _WINDOWS_REPARSE_POINT)
    except FileNotFoundError:
        return False
    except (AttributeError, OSError, TypeError, ValueError):
        # An inaccessible or unclassifiable existing path must not pass a
        # link boundary check.  Callers turn this boolean into their normal
        # structured link rejection; only a genuinely missing path is safe to
        # classify as not linked.
        return True


def linked_existing_ancestor(path: Path) -> Path | None:
    """Return the first linked ancestor of *path*, if one exists."""

    current = Path(path).absolute().parent
    while current != current.parent:
        if is_path_link(current):
            return current
        current = current.parent
    if is_path_link(current):
        return current
    return None
